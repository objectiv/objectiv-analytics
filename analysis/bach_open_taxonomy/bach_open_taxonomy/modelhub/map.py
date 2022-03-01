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

    def __init__(self, df):
        self._df = df

    def is_first_session(self) -> 'SeriesBoolean':
        """
        Labels all hits in a session True if that session is the first session of that user in the data.

        :returns: SeriesBoolean with the same index as the ObjectivFrame this method is applied to.
        """

        window = self._df.groupby('user_id').window(end_boundary=WindowFrameBoundary.FOLLOWING)
        first_session = window['session_id'].min()
        series = first_session == self._df.session_id
        return series.copy_override(name='is_first_session', index=self._df.index)

    def is_new_user(self, time_aggregation: str = None) -> 'SeriesBoolean':
        """
        Labels all hits True if the user is first seen in the period given time_aggregation.

        :param time_aggregation: if None, it uses the time_aggregation set in ObjectivFrame.
        :returns: SeriesBoolean with the same index as the ObjectivFrame this method is applied to.
        """

        window = self._df.groupby('user_id').window(end_boundary=WindowFrameBoundary.FOLLOWING)
        is_first_session = window['session_id'].min()

        window = self._df.groupby([self._df.mh.time_agg(),
                                   'user_id']).window(end_boundary=WindowFrameBoundary.FOLLOWING)
        is_first_session_time_aggregation = window['session_id'].min()

        series = is_first_session_time_aggregation == is_first_session

        return series.copy_override(name='is_new_user', index=self._df.index)

    def is_conversion_event(self, name: str):
        """
        Labels a hit True if it is a conversion event, all other hits are labeled False.

        :param name: the name of the conversion to label as set in
            :py:attr:`ObjectivFrame.conversion_events`.
        :returns: SeriesBoolean with same index as the ObjectivFrame this method is applied to.
        """

        conversion_stack, conversion_event = self._df._conversion_events[name]

        if conversion_stack is None:
            series = self._df.event_type == conversion_event
        elif conversion_event is None:
            series = conversion_stack.notnull()
        else:
            series = ((conversion_stack.notnull()) & (self._df.event_type == conversion_event))
        return series.copy_override(name='is_conversion_event')

    def conversion_count(self, name: str, partition='session_id'):
        """
        Counts the number of time a user is converted at a moment in time given a partition (ie session_id
        or user_id).

        :param name: the name of the conversion to label as set in
            :py:attr:`ObjectivFrame.conversion_events`.
        :param partition: the partition over which the number of conversions are counted. Can be any column
            of the ObjectivFrame
        :returns: SeriesInt64 with same index as the ObjectivFrame this method is applied to.
        """

        df = self._df.copy_override()
        df['__conversion'] = df.mh.map.is_conversion_event(name)
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
        df['conversion_count'] = df['__conversion_counter']\
            .copy_override_dtype('int64')\
            .copy_override(expression=expression)

        return df.conversion_count

    def pre_conversion_hit_number(self,
                                  name: str,
                                  filter: 'SeriesBoolean' = None,
                                  partition: str = 'session_id'):
        """
        Returns a count backwards from the first conversion, given the partition. I.e. first hit before
        converting is 1, second hit before converting 2, etc. Returns None if there are no conversions in the
        partition or after the first conversion.

        :param name: the name of the conversion to label as set in
            :py:attr:`ObjectivFrame.conversion_events`.
        :param filter: filters hits from being counted. Returns None for filtered hits.
        :param partition: the partition over which the number of conversions are counted. Can be any column
            of the ObjectivFrame
        :returns: SeriesInt64 with same index as the ObjectivFrame this method is applied to.
        """
        df = self._df.copy_override()
        if filter:
            # todo when bach supports boolean indexing with series with the same index but different base
            #  nodes, this is not longer necessary
            df['__filter'] = filter

        df['__conversions'] = df.mh.map.conversion_count(name=name)

        window = df.groupby(partition).window()
        converted = window['__conversions'].max()

        df['__is_converted'] = converted != 0
        df = df.materialize()
        pre_conversion_hits = df[df['__is_converted']]
        pre_conversion_hits = pre_conversion_hits[pre_conversion_hits['__conversions'] == 0]

        if filter:
            pre_conversion_hits = pre_conversion_hits[pre_conversion_hits['__filter']]

        window = pre_conversion_hits.sort_values(['session_id',
                                                  'session_hit_number'],
                                                 ascending=[True,
                                                            False]).groupby('session_id').window()
        pre_conversion_hits['pre_conversion_hit_number'] = pre_conversion_hits.session_hit_number.\
            window_row_number(window)

        pre_conversion_hits = pre_conversion_hits.materialize()
        df['pre_conversion_hit_number'] = pre_conversion_hits['pre_conversion_hit_number']

        return df['pre_conversion_hit_number']
