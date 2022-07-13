"""
Copyright 2021 Objectiv B.V.
"""
from enum import Enum
from typing import Dict, Optional

import bach

from modelhub.util import (
    ObjectivSupportedColumns, get_supported_dtypes_per_objectiv_column, check_objectiv_dataframe
)
from modelhub.pipelines.base_pipeline import BaseDataPipeline


class _BaseCalculatedSessionSeries(Enum):
    IS_START_OF_SESSION = 'is_start_of_session'
    SESSION_START_ID = 'session_start_id'
    SESSION_COUNT = 'is_one_session'


class SessionizedDataPipeline(BaseDataPipeline):
    """
    Pipeline in charge of calculating Objectiv sessionized columns.
    This pipeline is dependent on the result from ExtractedContextsPipeline, therefore it expects that
    the result from the latter is generated correctly.

    The steps followed in this pipeline are the following:
        1. _validate_extracted_context_df: Validates if provided DataFrame contains event_id, user_id and
            moment series.
        2. _calculate_base_session_series: Calculates `is_start_of_session`, `session_start_id` and
            `is_one_session` series.
        3. _calculate_objectiv_session_series: Calculates final sessionized series:
            `session_id` and `session_hit_number`
        4. _convert_dtypes: Will convert all required sessionized series to their correct dtype

    Final bach DataFrame will be later validated, it must include:
        - session_id and session_hit_number series
        - correct dtypes for sessionized series
    """

    def __init__(self, session_gap_seconds: int):
        self._session_gap_seconds = session_gap_seconds

    def _get_pipeline_result(
        self, extracted_contexts_df: Optional[bach.DataFrame] = None, **kwargs
    ) -> bach.DataFrame:
        """
        Contains steps for calculating sessionized series for provided dataframe.
        :param extracted_contexts_df: bach DataFrame containing `user_id`, `event_id` and `moment` series.

        returns a bach DataFrame with session_id and session_hit_number series
            and all series from provided extracted_contexts_df.
        """
        if not extracted_contexts_df:
            raise ValueError(f'{self.__class__.__name__} requires dataframe with extracted contexts.')

        context_df = extracted_contexts_df.copy()
        self._validate_extracted_context_df(context_df)

        # calculate series that are needed for the final result
        sessionized_df = self._calculate_base_session_series(context_df)

        # adds required objectiv session series
        sessionized_df = self._calculate_objectiv_session_series(sessionized_df)

        sessionized_df = self._convert_dtypes(df=sessionized_df)

        final_columns = context_df.data_columns + ObjectivSupportedColumns.get_sessionized_columns()
        return sessionized_df[final_columns]

    def _validate_extracted_context_df(self, df: bach.DataFrame) -> None:
        # make sure the result has AT LEAST the following series
        # even though the ExtractedContextsPipeline already validates series
        with_identity_resolution = (
            ObjectivSupportedColumns.IDENTITY_USER_ID.value in df.data_columns
        )
        supported_dtypes = get_supported_dtypes_per_objectiv_column(
            with_identity_resolution=with_identity_resolution
        )
        expected_context_columns = [
            ObjectivSupportedColumns.EVENT_ID.value,
            ObjectivSupportedColumns.USER_ID.value,
            ObjectivSupportedColumns.MOMENT.value,
        ]

        self._validate_data_dtypes(
            expected_dtypes={col: supported_dtypes[col] for col in expected_context_columns},
            current_dtypes=df.dtypes,
        )

    @classmethod
    def validate_pipeline_result(cls, result: bach.DataFrame) -> None:
        """
        Checks if we are returning all sessionized series with respective dtype.
        """
        check_objectiv_dataframe(
            result,
            columns_to_check=ObjectivSupportedColumns.get_sessionized_columns(),
            check_dtypes=True,
            infer_identity_resolution=True,
        )

    @property
    def result_series_dtypes(self) -> Dict[str, str]:
        sessionized_columns = ObjectivSupportedColumns.get_sessionized_columns()
        return {
            col: dtype for col, dtype in get_supported_dtypes_per_objectiv_column().items()
            if col in sessionized_columns
        }

    def _calculate_base_session_series(self, df: bach.DataFrame) -> bach.DataFrame:
        """
        Calculates each series required for calculating the final sessionized series.

        Series to calculate:
            - is_start_of_session: boolean series that defines if an event/row
                is the start of a user's session
            - session_start_id: Session number in the whole dataset,
                only rows where is_start_of_session is True are numbered.
            - is_one_session: amount of observed session starts before current session start

        Returns a bach DataFrame
        """
        sessionized_df = df.copy()

        is_session_start_series = self._calculate_session_start(sessionized_df, self._session_gap_seconds)
        sessionized_df[is_session_start_series.name] = is_session_start_series
        # materialize since rest of series are dependant and it uses a window function
        sessionized_df = sessionized_df.materialize(node_name='session_starts')

        session_start_id_series = self._calculate_session_start_id(sessionized_df)
        sessionized_df[session_start_id_series.name] = session_start_id_series

        session_count_series = self._calculate_session_count(sessionized_df)
        sessionized_df[session_count_series.name] = session_count_series
        return sessionized_df.materialize(node_name='session_id_and_count')

    @staticmethod
    def _calculate_objectiv_session_series(df: bach.DataFrame) -> bach.DataFrame:
        """
        Calculates all Sessionized Objectiv series expected by Modelhub. df MUST contain all
        calculated series from _calculate_base_session_series step.

        Series to calculate:
           - session_id: correct session_id for all rows with the same value for is_one_session
           - session_hit_number: event's number in respective session
        Returns a bach DataFrame
        """
        sort_by = [ObjectivSupportedColumns.MOMENT.value, ObjectivSupportedColumns.EVENT_ID.value]
        group_by = [_BaseCalculatedSessionSeries.SESSION_COUNT.value]
        window = df.sort_values(by=sort_by).groupby(group_by).window()

        df_cp = df.copy()
        session_start_id_series = df_cp[_BaseCalculatedSessionSeries.SESSION_START_ID.value]

        session_id_series_name = ObjectivSupportedColumns.SESSION_ID.value
        df_cp[session_id_series_name] = session_start_id_series.copy_override(
            expression=session_start_id_series.window_first_value(window=window).expression,
            name=session_id_series_name,
        )

        session_hit_number_series_name = ObjectivSupportedColumns.SESSION_HIT_NUMBER.value
        df_cp[session_hit_number_series_name] = session_start_id_series.copy_override(
            expression=session_start_id_series.window_row_number(window=window).expression,
            name=session_hit_number_series_name,
        )

        return df_cp.materialize(node_name='objectiv_sessionized_data')

    @staticmethod
    def _calculate_session_start(df: bach.DataFrame, session_gap_seconds: int) -> bach.SeriesBoolean:
        """
        Generates is_session_start series which determines if an event is the first event of a user's session.

        This is performed by:
          1. Grouping events by user ids and ordering by moment and event id

          2. Calculate the amount of time between previous and current event.
            (event_lapsed_time = events[n][moment] - events[n-1][moment])

          3. How to determine if the event is start of a session:
            a) If the row is the first observed event for the user's entire history, then by default it is a
                session start.

            b) Identify which event is the end of the session by comparing time differences.
                If the event_lapsed time is greater than session_gap_seconds, then we can deduct the current
                event is a session start.

        Returns bach SeriesBoolean
        """
        sort_by = [ObjectivSupportedColumns.MOMENT.value, ObjectivSupportedColumns.EVENT_ID.value]
        group_by = [ObjectivSupportedColumns.USER_ID.value]
        window = df.sort_values(by=sort_by).groupby(by=group_by).window()

        moment_series = df[ObjectivSupportedColumns.MOMENT.value]

        previous_moment_series = moment_series.window_lag(window=window)
        previous_moment_series = previous_moment_series.copy_override_type(bach.SeriesTimestamp)

        event_lapsed_time = moment_series - previous_moment_series
        assert isinstance(event_lapsed_time, bach.SeriesTimedelta)  # help mypy

        result_series_name = _BaseCalculatedSessionSeries.IS_START_OF_SESSION.value
        df_cp = df.copy()
        # let's assume all events are session starts
        df_cp[result_series_name] = True

        session_gap_mask = event_lapsed_time.dt.total_seconds <= session_gap_seconds
        # set None to those events with lapse time less than or equal to the session_gap_seconds
        # we can assume those are part of a same session
        # We use None instead of False because _calculate_session_count will count the values
        # from the resultant series, therefore we want to ignore non session start events
        df_cp.loc[session_gap_mask, result_series_name] = bach.SeriesBoolean.from_value(
            base=df_cp,
            value=None,
            name=result_series_name,
        )
        return df_cp[result_series_name].copy_override_type(bach.SeriesBoolean)

    @staticmethod
    def _calculate_session_start_id(df: bach.DataFrame) -> bach.SeriesInt64:
        """
        Calculates session_start_id by numbering each event that is a session start.
        Returns a bach SeriesInt64
        """
        sort_by = [ObjectivSupportedColumns.MOMENT.value, ObjectivSupportedColumns.EVENT_ID.value]
        group_by = [_BaseCalculatedSessionSeries.IS_START_OF_SESSION.value]
        window = df.sort_values(by=sort_by).groupby(by=group_by).window()

        is_start_session_series = df[_BaseCalculatedSessionSeries.IS_START_OF_SESSION.value]
        # group all rows by is_start_of_session and number each event
        session_start_id = is_start_session_series.window_row_number(window=window)
        session_start_id = session_start_id.copy_override_type(bach.SeriesInt64)

        result_series_name = _BaseCalculatedSessionSeries.SESSION_START_ID.value
        df_cp = df.copy()
        df_cp[result_series_name] = bach.SeriesInt64.from_value(
            base=df_cp, value=None, name=result_series_name,
        )
        # consider only events that are start of session
        df_cp.loc[is_start_session_series, result_series_name] = session_start_id
        return df_cp[result_series_name]

    @staticmethod
    def _calculate_session_count(df: bach.DataFrame) -> bach.SeriesInt64:
        """
        generates a unique number for each session, but not in the right order,
        by calculating the amount of observed session starts before current session start.
        For example:
           event_id  is_start_of_session   is_one_session
              1            True                1
              2            None                1
              3            True                2
              4            True                3
              5            None                3

        Returns a bach SeriesInt64
        """
        sort_by = [
            ObjectivSupportedColumns.USER_ID.value,
            ObjectivSupportedColumns.MOMENT.value,
            ObjectivSupportedColumns.EVENT_ID.value,
        ]
        window = df.sort_values(by=sort_by).groupby().window()

        start_session_series = df[_BaseCalculatedSessionSeries.IS_START_OF_SESSION.value]
        session_count_series = start_session_series.count(partition=window)
        return session_count_series.copy_override(
            name=_BaseCalculatedSessionSeries.SESSION_COUNT.value,
        ).copy_override_type(bach.SeriesInt64)
