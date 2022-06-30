"""
Copyright 2021 Objectiv B.V.
"""
from enum import Enum

import bach
from bach.partitioning import WindowFrameBoundary, WindowFrameMode
from typing import TYPE_CHECKING, Dict, List


from modelhub.decorators import use_only_required_objectiv_series

if TYPE_CHECKING:
    from modelhub import ModelHub


class _CalculatedConversionSeries(str, Enum):
    IS_CONVERSION_EVENT = 'is_conversion_event'
    CONVERSIONS_IN_TIME = 'conversions_in_time'
    CONVERSIONS_COUNTER = 'converted'
    PRE_CONVERSION_HIT_NUMBER = 'pre_conversion_hit_number'

    @property
    def private_name(self) -> str:
        return f'__{self}'

    @property
    def public_name(self) -> str:
        return self.value


_DEPENDENCIES_PER_CONVERSION_SERIES: Dict[_CalculatedConversionSeries, List[_CalculatedConversionSeries]] = {
    _CalculatedConversionSeries.CONVERSIONS_IN_TIME: [
        _CalculatedConversionSeries.IS_CONVERSION_EVENT,
    ],
    _CalculatedConversionSeries.CONVERSIONS_COUNTER: [
        _CalculatedConversionSeries.IS_CONVERSION_EVENT,
        _CalculatedConversionSeries.CONVERSIONS_IN_TIME,
    ],
    _CalculatedConversionSeries.PRE_CONVERSION_HIT_NUMBER: [
        _CalculatedConversionSeries.IS_CONVERSION_EVENT,
        _CalculatedConversionSeries.CONVERSIONS_IN_TIME,
    ]
}


class Map:
    """
    Methods in this class can be used to map data in a DataFrame with Objectiv data to series values.

    Always returns Series with same index as the DataFrame the method is applied to, so the result can be set
    as columns to that DataFrame.
    """

    def __init__(self, mh: 'ModelHub'):
        self._mh = mh

    @use_only_required_objectiv_series(required_series=['user_id', 'session_id'])
    def is_first_session(self, data: bach.DataFrame) -> bach.SeriesBoolean:
        """
        Labels all hits in a session True if that session is the first session of that user in the data.

        :param data: :py:class:`bach.DataFrame` to apply the method on.
        :returns: :py:class:`bach.SeriesBoolean` with the same index as ``data``.
        """

        window = data.groupby('user_id').window(
            mode=WindowFrameMode.ROWS,
            start_boundary=WindowFrameBoundary.PRECEDING,
            start_value=None,
            end_boundary=WindowFrameBoundary.FOLLOWING,
            end_value=None)

        first_session = window['session_id'].min()
        series = first_session == data.session_id

        new_series = series.copy_override(name='is_first_session',
                                          index=data.index).materialize()

        return new_series

    @use_only_required_objectiv_series(required_series=['user_id', 'session_id', 'moment'])
    def is_new_user(self, data: bach.DataFrame, time_aggregation: str = None) -> bach.SeriesBoolean:
        """
        Labels all hits True if the user is first seen in the period given `time_aggregation`.

        :param data: :py:class:`bach.DataFrame` to apply the method on.
        :param time_aggregation: if None, it uses the :py:attr:`ModelHub.time_aggregation` set in ModelHub
            instance.
        :returns: :py:class:`bach.SeriesBoolean` with the same index as ``data``.
        """

        frame_args = {
            'mode': WindowFrameMode.ROWS,
            'start_boundary': WindowFrameBoundary.PRECEDING,
            'end_boundary': WindowFrameBoundary.FOLLOWING,
        }
        data_cp = data.copy()
        data_cp['time_agg'] = self._mh.time_agg(data, time_aggregation)

        window = data_cp.groupby('user_id').window(**frame_args)
        window_ta = data_cp.groupby(['time_agg', 'user_id']).window(**frame_args)

        session_id_series = data_cp['session_id']
        is_first_session = session_id_series.min(partition=window)
        is_first_session_time_aggregation = session_id_series.min(partition=window_ta)

        is_new_user_series = is_first_session_time_aggregation == is_first_session
        is_new_user_series = is_new_user_series.copy_override_type(bach.SeriesBoolean)
        return is_new_user_series.copy_override(name='is_new_user').materialize()

    @use_only_required_objectiv_series(required_series=['event_type'])
    def is_conversion_event(self, data: bach.DataFrame, name: str) -> bach.SeriesBoolean:
        """
        Labels a hit True if it is a conversion event, all other hits are labeled False.

        :param data: :py:class:`bach.DataFrame` to apply the method on.
        :param name: the name of the conversion to label as set in
            :py:attr:`ModelHub.conversion_events`.
        :returns: :py:class:`bach.SeriesBoolean` with the same index as ``data``.
        """

        series_to_calculate = _CalculatedConversionSeries.IS_CONVERSION_EVENT
        conversion_df = self._get_calculated_conversion_df(
            series_to_calculate=series_to_calculate,
            data=data,
            name=name,
        )

        series = conversion_df[series_to_calculate.private_name]
        return (
            series
            .copy_override(name=series_to_calculate.public_name)
            .copy_override_type(bach.SeriesBoolean)
        )

    @use_only_required_objectiv_series(
        required_series=['session_id', 'moment', 'event_type'],
        include_series_from_params=['partition'],
    )
    def conversions_counter(self,
                            data: bach.DataFrame,
                            name: str,
                            partition: str = 'session_id') -> bach.SeriesInt64:
        """
        Counts the total number of conversions given a partition (ie session_id
        or user_id).

        :param name: the name of the conversion to label as set in
            :py:attr:`ModelHub.conversion_events`.
        :param partition: the partition over which the number of conversions are counted. Can be any column
            of the ObjectivFrame
        :returns: :py:class:`bach.SeriesBoolean` with the same index as ``data``.
        """

        series_to_calculate = _CalculatedConversionSeries.CONVERSIONS_COUNTER
        conversion_df = self._get_calculated_conversion_df(
            series_to_calculate=series_to_calculate,
            data=data,
            name=name,
            partition=partition,
        )

        series = conversion_df[series_to_calculate.private_name]
        return (
            series
            .copy_override(name=series_to_calculate.public_name)
            .copy_override_type(bach.SeriesInt64)
        )

    def conversion_count(self, *args, **kwargs):
        raise NotImplementedError('function is renamed please use `conversions_in_time`')

    @use_only_required_objectiv_series(
        required_series=['session_id', 'moment', 'event_type'],
        include_series_from_params=['partition'],
    )
    def conversions_in_time(self,
                            data: bach.DataFrame,
                            name: str,
                            partition: str = 'session_id') -> bach.SeriesInt64:
        """
        Counts the number of time a user is converted at a moment in time given a partition (ie 'session_id'
        or 'user_id').

        :param data: :py:class:`bach.DataFrame` to apply the method on.
        :param name: the name of the conversion to label as set in
            :py:attr:`ModelHub.conversion_events`.
        :param partition: the partition over which the number of conversions are counted. Can be any column
            in ``data``.
        :returns: :py:class:`bach.SeriesInt64` with the same index as ``data``.
        """
        series_to_calculate = _CalculatedConversionSeries.CONVERSIONS_IN_TIME
        conversion_df = self._get_calculated_conversion_df(
            series_to_calculate=series_to_calculate,
            data=data,
            name=name,
            partition=partition,
        )

        series = conversion_df[series_to_calculate.private_name]
        return (
            series
            .copy_override(name=series_to_calculate.public_name)
            .copy_override_type(bach.SeriesInt64)
        )

    @use_only_required_objectiv_series(
        required_series=['session_id', 'session_hit_number', 'moment', 'event_type'],
        include_series_from_params=['partition'],
    )
    def pre_conversion_hit_number(
        self,
        data: bach.DataFrame,
        name: str,
        partition: str = 'session_id',
    ) -> bach.SeriesInt64:
        """
        Returns a count backwards from the first conversion, given the partition. I.e. first hit before
        converting is 1, second hit before converting 2, etc. Returns None if there are no conversions
        in the partition or after the first conversion.

        :param data: :py:class:`bach.DataFrame` to apply the method on.
        :param name: the name of the conversion to label as set in
            :py:attr:`ModelHub.conversion_events`.
        :param partition: the partition over which the number of conversions are counted. Can be any column
            in ``data``.
        :returns: :py:class:`bach.SeriesInt64` with the same index as ``data``.
        """

        series_to_calculate = _CalculatedConversionSeries.PRE_CONVERSION_HIT_NUMBER
        conversion_df = self._get_calculated_conversion_df(
            series_to_calculate=series_to_calculate,
            data=data,
            name=name,
            partition=partition,
        )

        series = conversion_df[series_to_calculate.private_name]

        return (
            series.copy_override(name=series_to_calculate.public_name).
            copy_override_type(bach.SeriesInt64)
        )

    @staticmethod
    def _check_conversion_dependencies(
        data: bach.DataFrame, series_to_calculate: _CalculatedConversionSeries
    ) -> None:
        """
        Helper function that checks if dataframe contains all dependent series required
        for calculating series_to_calculate
        """
        if series_to_calculate not in _DEPENDENCIES_PER_CONVERSION_SERIES:
            return None

        for dep in _DEPENDENCIES_PER_CONVERSION_SERIES[series_to_calculate]:
            if dep.private_name not in data.data_columns:
                raise Exception(f'{dep} is required for calculating {series_to_calculate} series')

    def _get_calculated_conversion_df(
        self,
        *,
        series_to_calculate: _CalculatedConversionSeries,
        data: bach.DataFrame,
        **kwargs,
    ) -> bach.DataFrame:
        """
        Generates a dataframe containing all required conversion series based on series_to_calculate param.
        All new series will contain private names.
        """
        dependencies = _DEPENDENCIES_PER_CONVERSION_SERIES.get(series_to_calculate, [])
        variables_to_calc = dependencies + [series_to_calculate]

        # independent variables
        if _CalculatedConversionSeries.IS_CONVERSION_EVENT in variables_to_calc:
            data = self._calculate_is_conversion_event(data, **kwargs)

        # dependent variables (order matters)
        if _CalculatedConversionSeries.CONVERSIONS_IN_TIME in variables_to_calc:
            data = self._calculate_conversions_in_time(data, **kwargs)

        if _CalculatedConversionSeries.CONVERSIONS_COUNTER in variables_to_calc:
            data = self._calculate_conversions_counter(data, **kwargs)

        if _CalculatedConversionSeries.PRE_CONVERSION_HIT_NUMBER in variables_to_calc:
            data = self._calculate_pre_conversion_hit_number(data, **kwargs)

        calculated_series = [var.private_name for var in variables_to_calc]
        return data[calculated_series]

    def _calculate_is_conversion_event(self, data: bach.DataFrame, name: str, **kwargs) -> bach.DataFrame:
        """ For documentation, see function :meth:`Map.is_conversion_event()` """

        series_to_calculate = _CalculatedConversionSeries.IS_CONVERSION_EVENT
        self._check_conversion_dependencies(data, series_to_calculate)

        if name not in self._mh._conversion_events:
            raise KeyError(f"Key {name} is not labeled as a conversion")

        conversion_stack, conversion_event = self._mh._conversion_events[name]

        if conversion_stack is None:
            series = data.event_type == conversion_event
        elif conversion_event is None:
            series = conversion_stack.json.get_array_length() > 0
        else:
            series = ((conversion_stack.json.get_array_length() > 0) & (data.event_type == conversion_event))

        data[series_to_calculate.private_name] = series
        return data

    def _calculate_conversions_in_time(
        self, data: bach.DataFrame, partition: str, *args, **kwargs,
    ) -> bach.DataFrame:
        """ For documentation, see function :meth:`Map.conversions_in_time()` """
        series_to_calculate = _CalculatedConversionSeries.CONVERSIONS_IN_TIME
        self._check_conversion_dependencies(data, series_to_calculate)

        is_conversion_event_column = _CalculatedConversionSeries.IS_CONVERSION_EVENT.private_name
        column_name_to_add_conversion_counter = '__conversion_counter'
        data[column_name_to_add_conversion_counter] = 0
        data.loc[data[is_conversion_event_column], column_name_to_add_conversion_counter] = 1

        window = data.sort_values([partition, 'moment']).groupby(partition).window()

        series = (
            data[column_name_to_add_conversion_counter]
            .copy_override_type(bach.SeriesInt64).sum(window)
        )
        data[series_to_calculate.private_name] = series

        # conversions_in_time requires materialization due to window
        return data.materialize(f'{series_to_calculate}_calculation')

    def _calculate_conversions_counter(
        self, data: bach.DataFrame, partition: str, **kwargs,
    ) -> bach.DataFrame:
        """ For documentation, see function :meth:`Map.conversions_counter()` """

        series_to_calculate = _CalculatedConversionSeries.CONVERSIONS_COUNTER
        self._check_conversion_dependencies(data, series_to_calculate)

        conversions_in_time_column = _CalculatedConversionSeries.CONVERSIONS_IN_TIME.private_name
        window = data.groupby(partition).window(end_boundary=WindowFrameBoundary.FOLLOWING)
        data[series_to_calculate.private_name] = window[conversions_in_time_column].max()

        # conversions_counter requires materialization due to window
        return data.materialize(node_name=f'{series_to_calculate}_calculation')

    def _calculate_pre_conversion_hit_number(
        self, data: bach.DataFrame, partition: str, **kwargs,
    ) -> bach.DataFrame:
        """ For documentation, see function :meth:`Map.pre_conversion_hit_number()` """

        series_to_calculate = _CalculatedConversionSeries.PRE_CONVERSION_HIT_NUMBER
        self._check_conversion_dependencies(data, series_to_calculate)

        conversions_in_time_column = _CalculatedConversionSeries.CONVERSIONS_IN_TIME.private_name

        # sort all windows by session id and hit number
        sort_by = ['session_id', 'session_hit_number']

        window = data.sort_values(sort_by, ascending=False).groupby(partition).window()
        max_number_of_conversions = data[conversions_in_time_column].max(window)
        data['__is_converted'] = True
        data.loc[max_number_of_conversions == 0, '__is_converted'] = False

        data.materialize(inplace=True)

        window = data.sort_values(sort_by, ascending=False).groupby(partition).window()

        # number all rows except where __is_converted is NULL and _conversions == 0
        pch_mask = (data['__is_converted']) & (data[conversions_in_time_column] == 0)

        calc_series_name = series_to_calculate.private_name
        data[calc_series_name] = 1
        data.loc[~pch_mask, calc_series_name] = None

        pre_conversion_hit_number = (
            data[calc_series_name].astype('int64')
            .copy_override_type(bach.SeriesInt64)  # None is parsed as string
        )
        data[calc_series_name] = pre_conversion_hit_number.sum(window)

        # pre_conversion_hit_number requires materialization due to window
        return data.materialize(node_name=f'{series_to_calculate}_calculation')
