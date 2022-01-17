from dataclasses import dataclass
from typing import List

from bach import Series, DataFrame, SeriesString
from bach.expression import Expression
from bach.sql_model import BachSqlModelBuilder
from sql_models.util import quote_identifier


def value_counts(
    frame: DataFrame,
    subset: List[str],
    normalize: bool = False,
    sort: bool = True,
    ascending: bool = False,
    dropna: bool = True
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
            return

        for sub_series in self.subset:
            if sub_series not in self.df.data:
                raise ValueError(f'{sub_series} was not found in dataframe.')

    def _generate_hashed_subset_df(self) -> DataFrame:
        subset_df = self.df[self.subset].reset_index(drop=True)

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

    def _generate_counts_df(self, hashed_df: DataFrame) -> DataFrame:
        counts_per_hash = hashed_df.copy_override()
        counts_per_hash['row_count'] = 1
        if not self.normalize:
            counts_per_hash = counts_per_hash.groupby(by=self.ROW_HASH_COLUMN_NAME).agg({'row_count': 'sum'})
            counts_per_hash = counts_per_hash.rename({'row_count_sum': self.COUNT_COLUMN_NAME})
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
