"""
Copyright 2021 Objectiv B.V.
"""
import bach
from bach import SeriesBoolean
from bach.expression import Expression
from bach.partitioning import WindowFrameBoundary, WindowFrameMode
from typing import TYPE_CHECKING

from sql_models.util import is_bigquery

if TYPE_CHECKING:
    from modelhub import ModelHub


class Map:
    """
    Methods in this class can be used to map data in a DataFrame with Objectiv data to series values.

    Always returns Series with same index as the DataFrame the method is applied to, so the result can be set
    as columns to that DataFrame.
    """

    def __init__(self, mh: 'ModelHub'):
        self._mh = mh

    def is_first_session(self, data: bach.DataFrame) -> bach.SeriesBoolean:
        """
        Labels all hits in a session True if that session is the first session of that user in the data.

        :param data: :py:class:`bach.DataFrame` to apply the method on.
        :returns: :py:class:`bach.SeriesBoolean` with the same index as ``data``.
        """

        self._mh._check_data_is_objectiv_data(data)
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

    def is_new_user(self, data: bach.DataFrame, time_aggregation: str = None) -> bach.SeriesBoolean:
        """
        Labels all hits True if the user is first seen in the period given `time_aggregation`.

        :param data: :py:class:`bach.DataFrame` to apply the method on.
        :param time_aggregation: if None, it uses the :py:attr:`ModelHub.time_aggregation` set in ModelHub
            instance.
        :returns: :py:class:`bach.SeriesBoolean` with the same index as ``data``.
        """

        self._mh._check_data_is_objectiv_data(data)
        frame_args = {
            'mode': WindowFrameMode.ROWS,
            'start_boundary': WindowFrameBoundary.PRECEDING,
            'end_boundary': WindowFrameBoundary.FOLLOWING,
        }
        data_cp = data[['session_id', 'user_id']]
        data_cp['time_agg'] = self._mh.time_agg(data, time_aggregation)

        window = data_cp.groupby('user_id').window(**frame_args)
        window_ta = data_cp.groupby(['time_agg', 'user_id']).window(**frame_args)

        # for BigQuery, window.base_node != ta_window.base_node
        # as bach.DataFrame.groupby materializes for this engine
        # therefore time_agg will be referenced as a column in window expression
        # materialization is needed since time_agg is not a column in  current data_cp.base_node
        if window.base_node != window_ta.base_node:
            data_cp = data_cp.materialize(node_name='time_agg_window')

        session_id_series = data_cp['session_id']
        is_first_session = session_id_series.min(partition=window)
        is_first_session_time_aggregation = session_id_series.min(partition=window_ta)

        is_new_user_series = is_first_session_time_aggregation == is_first_session
        is_new_user_series = is_new_user_series.copy_override_type(bach.SeriesBoolean)
        return is_new_user_series.copy_override(name='is_new_user').materialize()

    def is_conversion_event(self, data: bach.DataFrame, name: str) -> bach.SeriesBoolean:
        """
        Labels a hit True if it is a conversion event, all other hits are labeled False.

        :param data: :py:class:`bach.DataFrame` to apply the method on.
        :param name: the name of the conversion to label as set in
            :py:attr:`ModelHub.conversion_events`.
        :returns: :py:class:`bach.SeriesBoolean` with the same index as ``data``.
        """

        self._mh._check_data_is_objectiv_data(data)

        if name not in self._mh._conversion_events:
            raise KeyError(f"Key {name} is not labeled as a conversion")

        conversion_stack, conversion_event = self._mh._conversion_events[name]

        if conversion_stack is None:
            series = data.event_type == conversion_event
        elif conversion_event is None:
            series = conversion_stack.json.get_array_length() > 0
        else:
            series = ((conversion_stack.json.get_array_length() > 0) & (data.event_type == conversion_event))
        return series.copy_override(name='is_conversion_event')

    def conversions_counter(self,
                            data: bach.DataFrame,
                            name: str,
                            partition: str = 'session_id'):
        """
        Counts the total number of conversions given a partition (ie session_id
        or user_id).

        :param name: the name of the conversion to label as set in
            :py:attr:`ModelHub.conversion_events`.
        :param partition: the partition over which the number of conversions are counted. Can be any column
            of the ObjectivFrame
        :returns: :py:class:`bach.SeriesBoolean` with the same index as ``data``.
        """

        self._mh._check_data_is_objectiv_data(data)

        data['__conversions'] = self._mh.map.conversions_in_time(data, name=name)

        window = data.groupby(partition).window(end_boundary=WindowFrameBoundary.FOLLOWING)
        converted = window['__conversions'].max()
        data = data.drop(columns=['__conversions'])

        new_series = converted.copy_override(name='converted',
                                             index=data.index).materialize()

        return new_series

    def conversion_count(self, *args, **kwargs):
        raise NotImplementedError('function is renamed please use `conversions_in_time`')

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

        self._mh._check_data_is_objectiv_data(data)

        data = data.copy()
        data['__conversion'] = self._mh.map.is_conversion_event(data, name)
        data['__conversion_counter'] = 0
        data.loc[data['__conversion'], '__conversion_counter'] = 1

        # make the query more clean, just require these series
        data = data[[partition, 'moment', '__conversion_counter']]
        if is_bigquery(data.engine):
            # group by materializes for BQ, window will make reference to column
            data = data.materialize(node_name='conversion_counter_bq')

        window = data.sort_values([partition, 'moment']).groupby(partition).window()
        data['conversions_in_time'] = (
            data['__conversion_counter'].copy_override_type(bach.SeriesInt64).sum(window)
        )
        return data.conversions_in_time.materialize(node_name='conversions_in_time')

    def pre_conversion_hit_number(self,
                                  data: bach.DataFrame,
                                  name: str,
                                  partition: str = 'session_id') -> bach.SeriesInt64:
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

        self._mh._check_data_is_objectiv_data(data)

        data = data.copy()
        data['__conversions'] = self._mh.map.conversions_in_time(data, name=name)

        # make the query more clean, just require these series
        required_series = [partition, 'session_id', 'session_hit_number', '__conversions']
        data = data[required_series]

        # sort all windows by session id and hit number
        sort_by = ['session_id', 'session_hit_number']

        window = data.sort_values(sort_by, ascending=False).groupby(partition).window()
        max_number_of_conversions = data['__conversions'].max(window)
        data['__is_converted'] = True
        data.loc[max_number_of_conversions == 0, '__is_converted'] = False

        pre_conversion_hits = data.materialize()

        window = pre_conversion_hits.sort_values(sort_by, ascending=False).groupby(partition).window()

        # number all rows except where __is_converted is NULL and _conversions == 0
        pch_mask = (pre_conversion_hits['__is_converted']) & (pre_conversion_hits['__conversions'] == 0)
        pre_conversion_hits['pre_conversion_hit_number'] = 1
        pre_conversion_hits.loc[~pch_mask, 'pre_conversion_hit_number'] = None
        pre_conversion_hit_number = (
            pre_conversion_hits['pre_conversion_hit_number']
            .astype('int64').copy_override_type(bach.SeriesInt64)  # None is parsed as string
        )
        pre_conversion_hit_number = pre_conversion_hit_number.sum(window)
        return pre_conversion_hit_number.materialize().copy_override_type(bach.SeriesInt64)

    def retention_matrix(self,
                         data: bach.DataFrame,
                         time_period: str = 'monthly',
                         event_type: str = None,
                         start_date: str = None,
                         end_date: str = None,
                         percentage=False,
                         display=True) -> bach.DataFrame:

        """
        It finds the number of users in a given cohort who are active at a given time
        period, where time is computed with respect to the beginning of each cohort.
        The "active user" is the user who made an action that we are interested in
        that time period.
        Users are divided into mutually exclusive cohorts, which are then
        tracked over time. In our case users are assigned to a cohort based on
        when they made their first action that we are interested in.

        Returns the retention matrix dataframe, it represents users retained across cohorts:
            - index value represents the cohort
            - columns represent the number of given date period since the current cohort
            - values represent number of unique active users of a given cohort

        One can calculate the retention matrix for a given time range, for that
        one can specify start_date a/o end_date.
        N.B. the users' activity starts to be traced from start_date specified in
        modelhub where we load the data.

        :param data: :py:class:`bach.DataFrame` to apply the method on.
        :param time_period: can be 'daily', 'weekly', 'monthly' or 'yearly'.
        :param event_type: the event/action that we are interested in.
            Must be a valid event_type (either parent or child).
            if None we take all the events generated by the user.
        :param start_date: start date of the retention matrix, e.g. '2022-04-01'
            if None take all the data.
        :param end_date: end date of the retention matrix, e.g. '2022-05-01'
            if None take all the data.
        :param percentage: if True calculate percentage with respect to the number of a users
            in the cohort, otherwise it leaves the absolute values.
        :param display: if display==True visualize the retention matrix as a heat map

        :returns: retention matrix bach DataFrame.
        """

        available_formats = {'daily', 'weekly', 'monthly', 'yearly'}

        if time_period not in available_formats:
            raise ValueError(f'{time_period} time_period is not available.')

        from datetime import datetime
        if start_date is not None:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            except Exception as e:
                print('Please provide correct start_date.')
                raise e

        if end_date is not None:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
            except Exception as e:
                print('Please provide correct end_date.')
                raise e

        self._mh._check_data_is_objectiv_data(data)

        data = data.copy()

        # filtering data with the event that we are interested in
        if event_type is not None:
            data = data[data['event_type'] == event_type]

        data['timestamp'] = data.day.dt.strftime('%Y%m%d').astype('timestamp')

        # for retention matrix calculation we need only event date and user_id
        columns = ['user_id', 'day']
        data = data[columns]

        data['cohort'] = data.day.astype('timestamp')

        # get the first cohort
        cohorts = data.groupby('user_id')['cohort'].min().reset_index()
        cohorts = cohorts.rename(columns={'cohort': 'first_cohort'})

        # add first cohort to our data DataFrame
        data = data.merge(cohorts, on='user_id', how='left')

        # calculate cohort distance
        if time_period == "yearly":
            data['cohort'] = data['cohort'].dt.strftime('%Y').astype(dtype=int)
            data['first_cohort'] = data['first_cohort'].dt.strftime('%Y').astype(dtype=int)
            data['cohort_distance'] = data['cohort'] - data['first_cohort']

        elif time_period == "monthly":
            data['cohort_year'] = data['cohort'].dt.strftime('%Y').astype(dtype=int)
            data['first_cohort_year'] = data['first_cohort'].dt.strftime('%Y').astype(dtype=int)
            data['cohort_year_diff'] = data['cohort_year'] - data['first_cohort_year']

            data['cohort_month'] = data['cohort'].dt.strftime('%m').astype(dtype=int)
            data['first_cohort_month'] = data['first_cohort'].dt.strftime('%m').astype(dtype=int)
            data['cohort_month_diff'] = data['cohort_month'] - data['first_cohort_month']

            n_months = 12
            data['cohort_distance'] = data['cohort_year_diff'] * n_months + data['cohort_month_diff']

        elif time_period == 'weekly' or time_period == 'biweekly':
            n_days = 7.0 if time_period == 'weekly' else 14.0

            data['cohort'] = data.day.dt.date_trunc('week').astype('timestamp')
            data['first_cohort'] = data['first_cohort'].dt.date_trunc('week')
            data['cohort_distance'] = (data['cohort'] - data['first_cohort']).dt.days
            data['cohort_distance'] = data['cohort_distance'] / n_days

        else:
            # daily
            data['cohort_distance'] = data['cohort'] - data['first_cohort']
            data['cohort_distance'] = data['cohort_distance'].dt.days

        # applying start_date filter
        if start_date is not None:
            first_cohort_start_date = start_date
            if time_period == 'yearly':
                _filter = data['first_cohort'] >= first_cohort_start_date.year
            else:
                _filter = data['first_cohort'] >= first_cohort_start_date
            data = data[_filter]

        # applying end_date filter
        if end_date is not None:
            data = data[data['cohort'] < end_date]

        # make the first_cohort pretty
        if time_period == 'monthly':
            data['first_cohort'] = data['first_cohort'].dt.strftime('%Y-%m')
        if time_period == 'weekly' or time_period == 'daily':
            data['first_cohort'] = data['first_cohort'].dt.strftime('%Y-%m-%d')
        data['first_cohort'] = data['first_cohort'].astype(dtype=str)
        data['cohort_distance'] = data['cohort_distance'].astype(dtype=str)

        # in BigQuery columns cannot start with numbers
        data['cohort_distance_prefix'] = '_'
        data['cohort_distance'] = data['cohort_distance_prefix'] + data['cohort_distance']

        retention_matrix = data.groupby(['first_cohort',
                                         'cohort_distance']).agg({'user_id': 'nunique'}).unstack(
            level='cohort_distance')

        # renaming columns, removing string attached after unstacking
        column_name_map = {col: col.replace('__user_id_nunique', '').replace('.0', '')
                           for col in retention_matrix.columns}
        retention_matrix = retention_matrix.rename(columns=column_name_map)

        # 'sort' with column names (numerical sorting, even though the columns are strings)
        columns = [f'_{j}' for j in sorted([int(i.replace('_', ''))
                                            for i in retention_matrix.columns])]
        retention_matrix = retention_matrix[columns]

        if percentage:
            first_column = retention_matrix[columns[0]]
            for col in columns:
                retention_matrix[col] /= first_column

        if display:
            import matplotlib.pyplot as plt
            import seaborn as sns
            fig, ax = plt.subplots(figsize=(20, 8))
            fmt = '.1%' if percentage else ''
            sns.heatmap(retention_matrix.to_pandas(), annot=True, square=True, ax=ax,
                        linewidths=.5, cmap=sns.cubehelix_palette(rot=-.4), fmt=fmt)
            plt.title('Cohort Analysis')

            nice_name = {
                'daily': 'Days',
                'weekly': 'Weeks',
                'monthly': 'Months',
                'yearly': 'Years'
            }

            plt.xlabel(f'{nice_name[time_period]} After First Event')
            plt.ylabel('First Event Cohort')
            plt.show()

        return retention_matrix
