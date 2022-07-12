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
    from modelhub.pipelines import (
        ExtractedContextsPipeline, SessionizedDataPipeline, IdentityResolutionPipeline
    )

    contexts_pipeline = ExtractedContextsPipeline(engine=engine, table_name=table_name)
    sessionized_pipeline = SessionizedDataPipeline(session_gap_seconds=session_gap_seconds)
    identity_pipeline = IdentityResolutionPipeline()

    data = contexts_pipeline(start_date=start_date, end_date=end_date)

    # resolve user ids
    if identity_resolution:
        data = identity_pipeline(
            extracted_contexts_df=data,
            identity_id=identity_resolution,
        )

    # calculate sessionized data from events
    if with_sessionized_data:
        data = sessionized_pipeline(extracted_contexts_df=data)

    # Autonomizing users must be done after getting sessionized data, this way we don't aggregate
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
