from dataclasses import dataclass
from typing import List, Optional

from bach import Series, DataFrame, SeriesString, SeriesAbstractNumeric
from bach.expression import Expression
from bach.sql_model import BachSqlModelBuilder
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
        if self.bins:
            subset_df = self._generate_bins(subset_df)

        row_hash_expr = Expression.construct(fmt=f"md5(row({','.join(self.subset)})::text)")
        subset_df[self.ROW_HASH_COLUMN_NAME] = SeriesString(
            expression=row_hash_expr,
            engine=self.df.engine,
            base_node=self.df.base_node,
            index=self.df.index,
            name=self.ROW_HASH_COLUMN_NAME,
            group_by=self.df.group_by,
        )
        subset_df = subset_df.materialize()
        return subset_df

    def _generate_bins(self, subset_df: DataFrame) -> DataFrame:
        subset_series = subset_df[self.subset[0]]
        min_max_totals = subset_df.agg(['min', 'max', 'count']).materialize()
        bins_df = subset_df.copy_override()
        bins_df['bin'] = subset_series.copy_override(
            name='bin',
            expression=Expression.construct(
                f'width_bucket({{}}, {{}}, {{}}, {self.bins})',
                subset_series,
                Series.as_independent_subquery(min_max_totals[f'{subset_series.name}_min']),
                Series.as_independent_subquery(min_max_totals[f'{subset_series.name}_max']),
            ),
        )
        '''
        def range(series, partition):
            return series._derived_agg_func(
                partition=partition,
                expression=AggregateFunctionExpression.construct("int8range(min({}), max({}), '[]')",
                                                                 series, series),
                dtype='string'
            )
        '''
        print('hola')

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
        model_builder = BachSqlModelBuilder(
            name='unique_rows_sql',
            sql='select distinct * from {{base_node}}',
            columns=tuple(self.subset + [self.ROW_HASH_COLUMN_NAME]),
        )
        model = model_builder(base_node=hashed_df.base_node)
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
        merged_counts_df = merged_counts_df.set_index(self.subset)
        return merged_counts_df
