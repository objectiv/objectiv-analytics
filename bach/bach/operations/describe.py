"""
Copyright 2022 Objectiv B.V.
"""
from abc import abstractmethod
from collections import abc
from enum import Enum
from typing import Optional, Union, Sequence, List, Set, Generic, TypeVar

from bach import (
    DataFrame, SeriesAbstractNumeric, DataFrameOrSeries, get_series_type_from_dtype, Series,
)
from bach.operations.concat import DataFrameConcatOperation
from bach.expression import Expression


class SupportedStats(Enum):
    COUNT = 'count'
    MEAN = 'mean'
    STD = 'std'
    MIN = 'min'
    MAX = 'max'
    NUNIQUE = 'nunique'
    MODE = 'mode'


TDataFrameOrSeries = TypeVar('TDataFrameOrSeries', bound='DataFrameOrSeries')


class DescribeOperation(Generic[TDataFrameOrSeries]):
    """
    Abstract class that can describe a DataFrame or Series.

    In order to instantiate this class you should provide the following params:
    obj: a DataFrame or Series to be described. If a series is give, it will be transformed into a DataFrame
    include: A dtype or list of dtypes to be described. Will default to all numerical series if there are
        numerical series, and in case there are no numerical series this will default to all series.
    exclude: A dtype or list of dtype to be excluded from analysis. Should not overlap with include if
        include is specifed.
    datetime_is_numeric: A boolean specifying if datetime series should be treated as numeric columns
        (not supported)
    percentiles: List-like of numbers between 0-1. If nothing is provided, defaults to [.25, .5, .75]

    Child classes are in charge of specifying the correct sorting of final result.
    """
    df: DataFrame
    series_to_describe: List[str]
    datetime_is_numeric: bool
    percentiles: Sequence[float]

    STAT_SERIES_NAME = '__stat'
    RESULT_DECIMALS = 2

    def __init__(
        self,
        obj: TDataFrameOrSeries,
        include: Optional[Union[str, Sequence[str]]] = None,
        exclude: Optional[Union[str, Sequence[str]]] = None,
        datetime_is_numeric: bool = False,
        percentiles: Optional[Sequence[float]] = None,
    ) -> None:
        self.df = obj.copy() if isinstance(obj, DataFrame) else obj.to_frame()
        if not self.df.data:
            raise ValueError('Cannot describe a Dataframe without columns')

        self.series_to_describe = self.determine_series_to_describe(self.df, include, exclude)

        self.datetime_is_numeric = datetime_is_numeric
        self.percentiles = percentiles or [0.25, 0.5, 0.75]

        if self.percentiles and any(pt < 0 or pt > 1 for pt in self.percentiles):
            raise ValueError('percentiles should be between 0 and 1.')

    @classmethod
    def determine_series_to_describe(
        cls,
        df: DataFrame,
        include: Optional[Union[str, Sequence[str]]],
        exclude: Optional[Union[str, Sequence[str]]],
    ) -> List[str]:
        """
        Process the include and exclude parameters and determine which series of the dataframe should be
        described.
        Validates that include and exclude don't overlap, if they are both explicitly set.
        :return: The names of the series from the dataframe to describe
        """
        include_dtypes: Set[str]
        exclude_dtypes: Set[str]

        numeric_dtypes = {col.dtype for col in df.data.values() if isinstance(col, SeriesAbstractNumeric)}
        all_dtypes = {col.dtype for col in df.data.values()}

        # process `include` parameter
        if include is None:
            include_dtypes = numeric_dtypes or all_dtypes
        elif include == 'all':
            include_dtypes = all_dtypes
        else:
            include_dtypes = cls.str_or_sequence_to_dtypes(include)

        # process `exclude` parameter
        if exclude is None:
            exclude_dtypes = set()
        else:
            exclude_dtypes = cls.str_or_sequence_to_dtypes(exclude)

        # validate combination of `include` and `exclude`
        if include is not None and exclude is not None and (set(include_dtypes) & set(exclude_dtypes)):
            raise ValueError(f'Include and exclude should not overlap. '
                             f'include: {include_dtypes}, exclude: {exclude_dtypes}')

        # determine series
        final_dtypes = include_dtypes - exclude_dtypes
        return [series.name for series in df.data.values() if series.dtype in final_dtypes]

    @staticmethod
    def str_or_sequence_to_dtypes(value: Union[str, Sequence[str]]) -> Set[str]:
        """
        Given a single dtype (or dtype alias), or a list of dtype (or aliasses), return a set of dtypes.
        Validates that value has the correct python types, and that the dtypes are valid.
        """
        dtypes: Set[str]
        if isinstance(value, str):
            dtypes = {value}
        elif isinstance(value, abc.Sequence) and all(isinstance(item, str) for item in value):
            dtypes = set(value)
        else:
            raise ValueError(f'Unexpected dtype value: {value}')
        return {get_series_type_from_dtype(dtype).dtype for dtype in dtypes}

    @abstractmethod
    def _get_final_described_result(self, describe_df: DataFrame) -> TDataFrameOrSeries:
        """
        returns final described object with correct sorted stats
        """
        raise NotImplementedError()

    def __call__(self) -> TDataFrameOrSeries:
        """
        Generates an aggregated dataframe per stat and concatenates all results into a new dataframe
        containing all descriptive statistics of the dataset.

        Values are sorted based on the position of the stat in SupportedStats.
        """
        all_stats_df = []
        for pos, stat in enumerate(SupportedStats):
            stat_df = self._calculate_stat(stat=stat, stat_position=pos)
            if stat_df:
                all_stats_df.append(stat_df)

        percentiles_df = self._calculate_percentiles()
        if percentiles_df:
            all_stats_df.append(percentiles_df)

        describe_df = DataFrameConcatOperation(objects=all_stats_df)()
        describe_df = describe_df.round(decimals=self.RESULT_DECIMALS)
        describe_df = describe_df.set_index(self.STAT_SERIES_NAME)

        return self._get_final_described_result(describe_df)

    def _calculate_stat(
        self,
        stat: SupportedStats,
        stat_position: int,
    ) -> Optional[DataFrame]:
        """
        Returns an aggregated dataframe based on the stat to be calculated.
        :param series_to_aggregate: List of series names that stat supports
        :param stat: aggregation to be calculated
        :param stat_position: position of the stat in the final result
        """
        # filter series that can perform the aggregation
        series_to_aggregate = []
        for s in self.series_to_describe:
            # check one: function exists on Series
            if not hasattr(self.df[s], stat.value):
                continue
            # check two: function doesn't raise NotImplementedError
            try:
                self.df[s].apply_func(stat.value)
            except NotImplementedError:
                continue
            series_to_aggregate.append(s)

        if not series_to_aggregate:
            return None

        stat_df = self.df.copy_override(
            series={
                s: self.df[s].copy_override(index={})
                for s in series_to_aggregate
            }, index={}

        )
        original_series_names = stat_df.data_columns
        stat_df = stat_df.agg(func=stat.value).materialize(node_name='describe_calculate_stat')

        # original column names should remain
        stat_df = stat_df.rename(
            columns=dict(zip(stat_df.data_columns, original_series_names)),
        )
        stat_df[self.STAT_SERIES_NAME] = stat.value
        stat_df[f'{self.STAT_SERIES_NAME}_position'] = stat_position
        return stat_df

    def _calculate_percentiles(self) -> Optional[DataFrame]:
        """
        Returns dataframe containing percentiles per each numerical series.
        """
        # filter series that can perform the aggregation 'quantile' operation
        series_to_aggregate = {
            s: self.df[s] for s in self.series_to_describe if hasattr(self.df[s], 'quantile')
        }
        if not series_to_aggregate:
            return None

        percentile_df: DataFrame = self.df.copy_override(series=series_to_aggregate)
        percentile_df = percentile_df.reset_index(drop=True)

        percentile_df = percentile_df.quantile(q=list(self.percentiles))
        has_q_index = 'quantile' in percentile_df.all_series

        columns_rename = {
            col: col.replace('_quantile', '')
            for col in percentile_df.data_columns
        }
        percentile_df = percentile_df.reset_index(drop=not has_q_index)

        if not has_q_index:
            percentile_df['quantile'] = self.percentiles[0]

        # original column names should remain
        columns_rename['quantile'] = self.STAT_SERIES_NAME
        percentile_df = percentile_df.rename(columns=columns_rename)
        current_position = len(SupportedStats)

        # SeriesFloat64 + int is not supported, need an expression
        percentile_df[f'{self.STAT_SERIES_NAME}_position'] = (
            percentile_df[self.STAT_SERIES_NAME].copy_override(
                expression=Expression.construct(
                    f'{current_position} + {{}}', percentile_df.all_series[self.STAT_SERIES_NAME],
                ),
            )
        )

        return percentile_df


class DataFrameDescribeOperation(DescribeOperation[DataFrame]):
    """
    To use: first instantiate this class,  then call the instantiated object as a function,
    e.g. `df_described = DataFrameDescribeOperation(obj=df)()`
    """
    def _get_final_described_result(self, describe_df: DataFrame) -> DataFrame:
        describe_df = describe_df.sort_values(by=f'{self.STAT_SERIES_NAME}_position')
        return describe_df[self.series_to_describe]


class SeriesDescribeOperation(DescribeOperation[Series]):
    """
    To use: first instantiate this class,  then call the instantiated object as a function,
    e.g. `series_described = SeriesFrameDescribeOperation(obj=series)()`
    """
    def _get_final_described_result(self, describe_df: DataFrame) -> Series:
        describe_series = describe_df[self.df.data_columns[0]]
        return describe_series.sort_by_series(by=[describe_df[f'{self.STAT_SERIES_NAME}_position']])
