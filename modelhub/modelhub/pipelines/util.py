from typing import Optional

from sqlalchemy.engine import Engine

from modelhub.util import ObjectivSupportedColumns, check_objectiv_dataframe

import bach


def get_objectiv_data(
    *,
    engine: Engine,
    table_name: str,
    session_gap_seconds: int = 1800,
    set_index: bool = True,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    with_sessionized_data: bool = True,
    identity_resolution: Optional[str] = None,
    anonymize_unidentified_users: bool = True,
) -> bach.DataFrame:
    """
        :param engine: db_connection
        :param table_name: the name of the sql table where the data is stored. Will default to 'events' for
            bigquery and 'data' for other engines.
        :param start_date: start_date to filter data from ExtractedContextsPipeline
        :param end_date: end_date to filter data from ExtractedContextsPipeline
        :param with_sessionized_data: If true, SessionizedDataPipeline will be applied on
            ExtractedContextsPipeline (or IdentityResolutionPipeline) result.
        :param session_gap_seconds: Maximum time between two consecutive
            events from the same user, for the events to be considered part of the same session.
            This is used by SessionizedDataPipeline, thus only relevant if `with_sessionized_data=True`.
        :param identity_resolution: If value provided, IdentityResolutionPipeline will be applied
            on ExtractedContextsPipeline result
        :param anonymize_unidentified_users: If True, unidentified user_ids will be set to NULL.
            This step is performed after applying IdentityResolutionPipeline and SessionizedDataPipeline.

        :returns: initial bach DataFrame required by ModelHub.
    """
    from modelhub.pipelines import (
        ExtractedContextsPipeline, SessionizedDataPipeline, IdentityResolutionPipeline
    )

    contexts_pipeline = ExtractedContextsPipeline(engine=engine, table_name=table_name)
    sessionized_pipeline = SessionizedDataPipeline(session_gap_seconds=session_gap_seconds)
    identity_pipeline = IdentityResolutionPipeline(identity_id=identity_resolution)

    data = contexts_pipeline(start_date=start_date, end_date=end_date)

    # resolve user ids
    if identity_resolution:
        data = identity_pipeline(extracted_contexts_df=data)

    # calculate sessionized data from events
    if with_sessionized_data:
        data = sessionized_pipeline(extracted_contexts_df=data)

    # Anonymizing users must be done after getting sessionized data, this way we don't aggregate
    # events on a single unknown user
    if identity_resolution and anonymize_unidentified_users:
        data = IdentityResolutionPipeline.anonymize_user_ids_without_identity(data)

    columns_to_check = ObjectivSupportedColumns.get_extracted_context_columns()
    if with_sessionized_data:
        columns_to_check += ObjectivSupportedColumns.get_sessionized_columns()

    check_objectiv_dataframe(
        df=data,
        columns_to_check=columns_to_check,
        check_dtypes=True,
        infer_identity_resolution=identity_resolution is not None,
    )
    data = data[columns_to_check]

    if set_index:
        data = data.set_index(keys=ObjectivSupportedColumns.get_index_columns())

    return data
