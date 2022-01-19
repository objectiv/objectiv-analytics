from dataclasses import dataclass
from typing import List, Optional

import numpy as np

from bach import Series, DataFrame, SeriesString, SeriesAbstractNumeric, SeriesInt64
from bach.expression import Expression
from bach.partitioning import WindowFrameBoundary, WindowFrameMode, Window
from bach.sql_model import BachSqlModel, construct_references
from sql_models.model import CustomSqlModelBuilder, Materialization
from sql_models.util import quote_identifier


def value_counts(
    frame: DataFrame,
    subset: List[str],
    normalize: bool = False,
    sort: bool = True,
    ascending: bool = False,
    dropna: bool = True,
    bins: Optional[int] = None,
) -> Series:
    ...


@dataclass
class ValueCounter:
    df: DataFrame
    subset: List[str]
    normalize: bool = False
    sort: bool = True
    ascending: bool = False
    dropna: bool = True
    bins: Optional[int] = None

    ROW_HASH_COLUMN_NAME = 'row_hash'
    COUNT_COLUMN_NAME = 'row_hash_agg_count'

    def __post_init__(self) -> None:
        self._process_params()

    def get_value_counts(self) -> Series:
        hashed_df = self._generate_hashed_subset_df()
        counts_per_hash = self._generate_counts_df(hashed_df)

        merged_counts_df = self._merge_counts_by_hash(hashed_df, counts_per_hash)

        if self.sort:
            merged_counts_df = merged_counts_df.sort_values(by=self.COUNT_COLUMN_NAME, ascending=self.ascending)
        counts = merged_counts_df[self.COUNT_COLUMN_NAME].copy_override()

        return counts

    def _process_params(self) -> None:
        if not self.subset:
            self.subset = list(self.df.data.keys())

        for sub_series in self.subset:
            if sub_series not in self.df.data:
                raise ValueError(f'{sub_series} was not found in dataframe.')

        if self.bins and len(self.subset) > 1:
            raise ValueError('Can only group bins for a single series.')

        if self.bins and not isinstance(self.df.data[self.subset[0]], SeriesAbstractNumeric):
            raise ValueError('Can only group bins for numerical series.')

    def _generate_hashed_subset_df(self) -> DataFrame:
        subset_df = self.df[self.subset].reset_index(drop=True)
        rows_to_hash = self.subset
        if self.bins:
            subset_df = self._generate_bins(subset_df)
            rows_to_hash = ['bin_range']

        row_hash_expr = Expression.construct(fmt=f"md5(row({','.join(rows_to_hash)})::text)")
        subset_df[self.ROW_HASH_COLUMN_NAME] = SeriesString(
            expression=row_hash_expr,
            engine=subset_df.engine,
            base_node=subset_df.base_node,
            index=subset_df.index,
            name=self.ROW_HASH_COLUMN_NAME,
            group_by=subset_df.group_by,
        )
        subset_df = subset_df[rows_to_hash + [self.ROW_HASH_COLUMN_NAME]].materialize()
        return subset_df

    def _generate_bins(self, subset_df: DataFrame) -> DataFrame:
        subset_series = subset_df[self.subset[0]]

        min_max_totals = subset_df.agg(['min', 'max']).materialize()
        min_max_totals['bin_size'] = (
                min_max_totals[f'{subset_series.name}_max'] - min_max_totals[f'{subset_series.name}_min']
        ) / self.bins
        # TODO: Implement Series.ceil method

        min_max_totals['casted_bin_size'] = min_max_totals['bin_size'].copy_override(
            expression=Expression.construct(
                'cast(floor({}) as int)',
                min_max_totals['bin_size'],
            ),
        )
        min_max_totals['adjustment'] = min_max_totals['bin_size'] - min_max_totals['casted_bin_size']
        min_max_totals = min_max_totals.materialize()

        bin_gen_expr_str = (
            'distinct cast(generate_series({}, {}, {}) + {} '
            f'* generate_series(0, {self.bins}) as numeric)'
        )
        bin_ranges_df = SeriesInt64(
            engine=min_max_totals.engine,
            index={},
            name='bin_inbound',
            base_node=min_max_totals.base_node,
            expression=Expression.construct(
                bin_gen_expr_str,
                min_max_totals[f'{subset_series.name}_min'],
                min_max_totals[f'{subset_series.name}_max'],
                min_max_totals['casted_bin_size'],
                min_max_totals['adjustment'],

            ),
            group_by=None,
        ).to_frame().materialize()

        bin_ranges_df['bin_outbound'] = bin_ranges_df.bin_inbound.copy_override(
            expression=Expression.construct(
                'lag({}, 1) over (order by {} desc)',
                bin_ranges_df.bin_inbound,
                bin_ranges_df.bin_inbound,
            )
        )

        bin_ranges_df = bin_ranges_df.materialize()
        subset_df = subset_df.merge(bin_ranges_df, how='cross')
        node = subset_df.get_current_node(
            name='filtered_subset',
            where_clause=Expression.construct(
                "where {} >= {} and {} < {}",
                subset_df[subset_series.name],
                subset_df.bin_inbound,
                subset_df[subset_series.name],
                subset_df.bin_outbound,
            )
        )
        subset_df = subset_df.copy_override(base_node=node)

        subset_df['bin_range'] = SeriesInt64(
            base_node=node,
            engine=subset_df.engine,
            name='bin_range',
            expression=Expression.construct(
                'numrange({}, {})',
                subset_df.bin_inbound,
                subset_df.bin_outbound,
            ),
            group_by=None,
            index=subset_df.index,
        )
        return subset_df.materialize()

    def _generate_counts_df(self, hashed_df: DataFrame) -> DataFrame:
        counts_per_hash = hashed_df.copy_override()
        counts_per_hash['row_count'] = 1

        counts_per_hash = (
            counts_per_hash.groupby(by=self.ROW_HASH_COLUMN_NAME).agg({'row_count': 'sum'})
            .materialize()
            .rename(columns={'row_count_sum': self.COUNT_COLUMN_NAME})
        )
        if self.normalize:
            counts_per_hash[self.COUNT_COLUMN_NAME] /= counts_per_hash[self.COUNT_COLUMN_NAME].sum()

        counts_per_hash = counts_per_hash.reset_index(drop=False)
        counts_per_hash = counts_per_hash[[self.ROW_HASH_COLUMN_NAME, self.COUNT_COLUMN_NAME]]
        return counts_per_hash.materialize(node_name='counts_per_row_hash')

    def _merge_counts_by_hash(self, hashed_df: DataFrame, counts_per_hash_df: DataFrame) -> DataFrame:
        # TODO: Move this to DataFrame drop_duplicates
        duplicated_series = self.subset if not self.bins else ['bin_range']
        model = BachSqlModel(
            model_spec=CustomSqlModelBuilder(sql='select distinct * from {{base_node}}', name='unique_rows_sql'),
            materialization=Materialization.CTE,
            materialization_name=None,
            references=construct_references(
                base_references={'base_node': hashed_df.base_node},
                expressions=[],
            ),
            properties={},
            columns=tuple(duplicated_series + [self.ROW_HASH_COLUMN_NAME]),
        )
        unique_hash_df = hashed_df.copy_override(
            engine=hashed_df.engine,
            base_node=model,
            index_dtypes={},
            series_dtypes=hashed_df.dtypes,
            savepoints=hashed_df.savepoints,
        )

        merged_counts_df = unique_hash_df.merge(
            right=counts_per_hash_df,
            how='inner',
            on=self.ROW_HASH_COLUMN_NAME,
        )
        merged_counts_df = merged_counts_df.set_index(duplicated_series)
        return merged_counts_df
