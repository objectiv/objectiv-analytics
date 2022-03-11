"""
Copyright 2021 Objectiv B.V.
"""
from bach.expression import Expression
from typing import TYPE_CHECKING
from bach.partitioning import WindowFrameBoundary

if TYPE_CHECKING:
    from bach.series import SeriesBoolean


class Map:
    """
    Methods in this class can be used to map data in the Objectiv Frame to series values.

    Always returns Series with same index as the ObjectivFrame the method is applied to, so the can be set
    as columns to that ObjectivFrame
    """

    def __init__(self, mh):
        self._mh = mh

    def is_first_session(self, df) -> 'SeriesBoolean':
        """
        Labels all hits in a session True if that session is the first session of that user in the data.

        :returns: SeriesBoolean with the same index as the ObjectivFrame this method is applied to.
        """

        self._mh._check_data_is_objectiv_data(df)

        window = df.groupby('user_id').window(end_boundary=WindowFrameBoundary.FOLLOWING)
        first_session = window['session_id'].min()
        series = first_session == df.session_id

        new_series = series.copy_override(name='is_first_session',
                                          index=df.index).to_frame().materialize().is_first_session

        return new_series

    def is_new_user(self, df, time_aggregation=None) -> 'SeriesBoolean':
        """
        Labels all hits True if the user is first seen in the period given time_aggregation.

        :param time_aggregation: if None, it uses the time_aggregation set in ObjectivFrame.
        :returns: SeriesBoolean with the same index as the ObjectivFrame this method is applied to.
        """

        self._mh._check_data_is_objectiv_data(df)

        window = df.groupby('user_id').window(end_boundary=WindowFrameBoundary.FOLLOWING)
        is_first_session = window['session_id'].min()

        window = df.groupby([self._mh.time_agg(df, time_aggregation),
                             'user_id']).window(end_boundary=WindowFrameBoundary.FOLLOWING)
        is_first_session_time_aggregation = window['session_id'].min()

        series = is_first_session_time_aggregation == is_first_session

        new_series = series.copy_override(name='is_new_user',
                                          index=df.index).to_frame().materialize().is_new_user

        return new_series

    def is_conversion_event(self, df, name: str):
        """
        Labels a hit True if it is a conversion event, all other hits are labeled False.

        :param name: the name of the conversion to label as set in
            :py:attr:`ObjectivFrame.conversion_events`.
        :returns: SeriesBoolean with same index as the ObjectivFrame this method is applied to.
        """

        self._mh._check_data_is_objectiv_data(df)

        conversion_stack, conversion_event = self._mh._conversion_events[name]

        if conversion_stack is None:
            series = df.event_type == conversion_event
        elif conversion_event is None:
            series = conversion_stack.notnull()
        else:
            series = ((conversion_stack.notnull()) & (df.event_type == conversion_event))
        return series.copy_override(name='is_conversion_event')

    def conversions_counter(self, df, name: str, partition='session_id'):
        """
        Counts the total number of conversions given a partition (ie session_id
        or user_id).

        :param name: the name of the conversion to label as set in
            :py:attr:`ObjectivFrame.conversion_events`.
        :param partition: the partition over which the number of conversions are counted. Can be any column
            of the ObjectivFrame
        :returns: SeriesBoolean with same index as the ObjectivFrame this method is applied to.
        """

        self._mh._check_data_is_objectiv_data(df)

        df['__conversions'] = self._mh.map.conversions_in_time(df, name=name)

        window = df.groupby(partition).window(end_boundary=WindowFrameBoundary.FOLLOWING)
        converted = window['__conversions'].max()
        df = df.drop(columns=['__conversions'])

        new_series = converted.copy_override(name='converted',
                                             index=df.index).to_frame().materialize().converted

        return new_series

    def conversion_count(self, *args, **kwargs):
        raise NotImplementedError('function is depecrecated please use `conversions_in_time`')

    def conversions_in_time(self, df, name: str, partition='session_id'):
        """
        Counts the number of time a user is converted at a moment in time given a partition (ie session_id
        or user_id).

        :param name: the name of the conversion to label as set in
            :py:attr:`ObjectivFrame.conversion_events`.
        :param partition: the partition over which the number of conversions are counted. Can be any column
            of the ObjectivFrame
        :returns: SeriesInt64 with same index as the ObjectivFrame this method is applied to.
        """

        self._mh._check_data_is_objectiv_data(df)

        df = df.copy_override()
        df['__conversion'] = self._mh.map.is_conversion_event(df, name)
        exp = f"case when {{}} then row_number() over (partition by {{}}, {{}}) end"
        expression = Expression.construct(exp, df['__conversion'], df[partition], df['__conversion'])
        df['__conversion_counter'] = df['__conversion']\
            .copy_override_dtype(dtype='int64')\
            .copy_override(expression=expression)
        df = df.materialize()
        exp = f"count({{}}) over (partition by {{}} order by {{}}, {{}})"
        expression = Expression.construct(exp,
                                          df['__conversion_counter'],
                                          df[partition],
                                          df[partition],
                                          df['moment'])
        df['conversions_in_time'] = df['__conversion_counter']\
            .copy_override_dtype('int64')\
            .copy_override(expression=expression)

        return df.conversions_in_time

    def pre_conversion_hit_number(self,
                                  df,
                                  name: str,
                                  partition: str = 'session_id'):
        """
        Returns a count backwards from the first conversion, given the partition. I.e. first hit before
        converting is 1, second hit before converting 2, etc. Returns None if there are no conversions in the
        partition or after the first conversion.

        :param name: the name of the conversion to label as set in
            :py:attr:`ObjectivFrame.conversion_events`.
        :param partition: the partition over which the number of conversions are counted. Can be any column
            of the ObjectivFrame
        :returns: SeriesInt64 with same index as the ObjectivFrame this method is applied to.
        """

        self._mh._check_data_is_objectiv_data(df)

        df = df.copy_override()
        df['__conversions'] = self._mh.map.conversions_in_time(df, name=name)

        window = df.groupby(partition).window()
        converted = window['__conversions'].max()

        df['__is_converted'] = converted != 0
        df = df.materialize()
        pre_conversion_hits = df[df['__is_converted']]
        pre_conversion_hits = pre_conversion_hits[pre_conversion_hits['__conversions'] == 0]

        window = pre_conversion_hits.sort_values(['session_id',
                                                  'session_hit_number'],
                                                 ascending=False).groupby(partition).window()
        pre_conversion_hits['pre_conversion_hit_number'] = pre_conversion_hits.session_hit_number.\
            window_row_number(window)

        pre_conversion_hits = pre_conversion_hits.materialize()
        df['pre_conversion_hit_number'] = pre_conversion_hits['pre_conversion_hit_number']

        return df['pre_conversion_hit_number']
