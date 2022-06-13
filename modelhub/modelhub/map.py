"""
Copyright 2021 Objectiv B.V.
"""
import bach
from bach import SeriesBoolean
from bach.expression import Expression
from bach.partitioning import WindowFrameBoundary, WindowFrameMode
from typing import TYPE_CHECKING


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
        exp = f"case when {{}} then row_number() over (partition by {{}}, {{}}) end"
        expression = Expression.construct(exp,
                                          data.all_series['__conversion'],
                                          data.all_series[partition],
                                          data.all_series['__conversion'])
        data['__conversion_counter'] = data['__conversion']\
            .copy_override_dtype(dtype='int64')\
            .copy_override(expression=expression)
        data = data.materialize()
        data['conversions_in_time'] = data.sort_values([partition, 'moment'])\
            .groupby(partition)\
            .window()['__conversion_counter'].count()

        return data.conversions_in_time

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

        window = data.groupby(partition).window()
        converted = window['__conversions'].max()

        data['__is_converted'] = converted != 0
        data = data.materialize()
        assert(isinstance(data['__is_converted'], SeriesBoolean))  # help mypy to overcome generic Series type
        pre_conversion_hits = data[data['__is_converted']]
        pre_conversion_hits = pre_conversion_hits[pre_conversion_hits['__conversions'] == 0]

        window = pre_conversion_hits.sort_values(['session_id',
                                                  'session_hit_number'],
                                                 ascending=False).groupby(partition).window()
        pre_conversion_hits['pre_conversion_hit_number'] = pre_conversion_hits.session_hit_number.\
            window_row_number(window)

        pre_conversion_hits = pre_conversion_hits.materialize()
        data['pre_conversion_hit_number'] = pre_conversion_hits['pre_conversion_hit_number']

        return data.pre_conversion_hit_number

    def retention_matrix(self,
                         data: bach.DataFrame,
                         time_period: str = 'monthly',
                         event_type: str = None,
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
            - columns represent the number of given date period (default - monthly) since the current cohort
            - values represent number of unique active users of a given cohort

        :param data: :py:class:`bach.DataFrame` to apply the method on.
        :param time_period: can be 'daily', 'monthly' or 'yearly'.
        :param event_type: the event/action that we are interested in.
            Must be a valid event_type (either parent or child).
            if None we take all the events generated by the user.
        :param percentage: if True calculate percentage with respect to the number of a users
            in the cohort, otherwise it leaves the absolute values.
        :param display: if display==True visualize the retention matrix as a heat map
        :returns: retention matrix bach DataFrame.
        """

        available_formats = {
            'daily': '%Y%m%d',
            'monthly': '%Y%m',
            'yearly': '%Y',
        }
        time_format = available_formats.get(time_period)
        if time_format is None:
            raise ValueError(f'{time_period} time_period is not available.')

        self._mh._check_data_is_objectiv_data(data)

        data = data.copy()

        # filtering data with the event that we are interested in
        if event_type is not None:
            data = data[data['event_type'] == event_type]

        columns = ['user_id', 'day']
        data = data[columns]

        if time_format == '%Y%m%d':
            data['cohort'] = data.day.dt.strftime(time_format).astype('timestamp')
        else:
            data['cohort'] = data.day.dt.strftime(time_format).astype(dtype=int)
        data['cohort_year'] = data.day.dt.strftime('%Y').astype(dtype=int)
        data['cohort_month'] = data.day.dt.strftime('%m').astype(dtype=int)
        data['timestamp'] = data.day.dt.strftime('%Y%m%d').astype('timestamp')

        # get the first cohort
        cohorts = data.groupby('user_id')['cohort'].min().reset_index()
        cohorts = cohorts.rename(columns={'cohort': 'first_cohort'})

        # add first cohort to our data DataFrame
        data = data.merge(cohorts, on='user_id', how='left')

        # year
        # first_cohort column is SeriesInt64 type
        data['first_cohort_year'] = data['first_cohort'].astype(dtype=str)
        data['first_cohort_year'] = data['first_cohort_year'].str[:4].astype(dtype=int)
        data['cohort_year_diff'] = data['cohort_year'] - data['first_cohort_year']
        # month
        data['first_cohort_month'] = data['first_cohort'].astype(dtype=str).str[4:6].astype(dtype=int)
        data['cohort_month_diff'] = data['cohort_month'] - data['first_cohort_month']

        # cohort distance - the amount of year/months/days (depending on time_format)
        # between the current event and the first event from the user
        if time_format == '%Y':
            data['cohort_distance'] = data['cohort_year_diff']
            data['first_cohort'] = data['first_cohort'].astype(dtype=str)
        elif time_format == '%Y%m':
            n_months = 12
            data['cohort_distance'] = data['cohort_year_diff'] * n_months + data['cohort_month_diff']
            data['first_cohort'] = data['first_cohort'].astype(dtype=str)
            data['first_cohort'] = data['first_cohort'].str[:4] + '-' + data['first_cohort'].str[4:]
        else:
            data['cohort_distance'] = data['cohort'] - data['first_cohort']
            data['cohort_distance'] = data['cohort_distance'].astype(dtype=str)
            data['first_cohort'] = data['first_cohort'].dt.strftime('%Y-%m-%d').astype(dtype=str)

        retention_matrix = data.groupby(['first_cohort',
                                         'cohort_distance']).agg({'user_id': 'nunique'}).unstack(
            level='cohort_distance')

        # renaming columns: removing string attached after unstacking
        # need to split the column name string because in case of time_format='%Y%m%d'
        # we have "n days" string, where n - is number of the days.
        column_name_map = {col: col.replace('__user_id_nunique', '').split()[0]
                           for col in retention_matrix.columns}
        retention_matrix = retention_matrix.rename(columns=column_name_map)

        # if days are used the first cohort name is '00:00:00', need to rename it to 0
        if '00:00:00' in retention_matrix.columns:
            retention_matrix = retention_matrix.rename(columns={'00:00:00': '0'})

        # 'sort' with column names (numerical sorting, even though the columns are strings)
        columns = [str(j) for j in sorted([int(i) for i in retention_matrix.columns])]
        retention_matrix = retention_matrix[columns]

        if percentage:
            first_column = retention_matrix[columns[0]]
            for col in columns:
                retention_matrix[col] /= first_column
        else:
            for col in columns:
                retention_matrix[col] = retention_matrix[col].astype(dtype=int)

        if display:
            import matplotlib.pyplot as plt
            import seaborn as sns
            fig, ax = plt.subplots(figsize=(20, 8))
            fmt = '.1%' if percentage else ''
            sns.heatmap(retention_matrix.to_pandas(), annot=True, square=True, ax=ax,
                        linewidths=.5, cmap=sns.cubehelix_palette(rot=-.4), fmt=fmt)
            plt.title('Cohort Analysis')

            if time_format == '%Y%m%d':
                x_sub_title = 'Days'
            elif time_format == '%Y%m':
                x_sub_title = 'Months'
            elif time_format == '%Y':
                x_sub_title = 'Years'
            else:
                x_sub_title = 'Days'
            plt.xlabel(f'{x_sub_title} After First Event')
            plt.ylabel('First Event Cohort')
            plt.show()

        return retention_matrix

