"""
Copyright 2022 Objectiv B.V.
"""
import datetime
from uuid import UUID

import bach
import pandas as pd
from sql_models.util import is_bigquery
from tests.functional.bach.test_data_and_utils import assert_equals_data

from modelhub import SessionizedDataPipeline
from tests_modelhub.data_and_utils.utils import create_engine_from_db_params, get_parsed_objectiv_data


def _get_sessionized_data_pipeline(db_params) -> SessionizedDataPipeline:
    engine = create_engine_from_db_params(db_params)
    return SessionizedDataPipeline(engine=engine, table_name=db_params.table_name)


def test_get_pipeline_result(db_params, monkeypatch) -> None:
    pipeline = _get_sessionized_data_pipeline(db_params)
    engine = pipeline._engine
    pdf = pd.DataFrame(get_parsed_objectiv_data(engine))[['event_id', 'cookie_id', 'moment']]
    pdf = pdf.rename(columns={'cookie_id': 'user_id'})

    user_id = UUID('b2df75d2-d7ca-48ac-9747-af47d7a4a2b1')
    pdf = pdf[pdf['user_id'] == user_id]

    if is_bigquery(engine):
        pdf['user_id'] = pdf['user_id'].astype(str)
        pdf['event_id'] = pdf['event_id'].astype(str)

    context_df = bach.DataFrame.from_pandas(df=pdf, engine=engine, convert_objects=True).reset_index(drop=True)

    monkeypatch.setattr(
        'modelhub.stack.sessionized_data.get_extracted_contexts_df',
        lambda *args, **kwargs: context_df,
    )

    result = pipeline._get_pipeline_result()

    assert_equals_data(
        result,
        expected_columns=['event_id', 'user_id', 'moment', 'session_id', 'session_hit_number'],
        expected_data=[
            [
                UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'),
                user_id,
                datetime.datetime.fromisoformat('2021-11-30 10:23:36.267000'),
                1,
                1,
            ],
            [
                UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac305'),
                user_id,
                datetime.datetime.fromisoformat('2021-12-01 10:23:36.276000'),
                2,
                1,
            ],
            [
                UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac306'),
                user_id,
                datetime.datetime.fromisoformat('2021-12-01 10:23:36.279000'),
                2,
                2,
            ],
        ],
        convert_uuid=True,
        use_to_pandas=True,
        order_by=['event_id'],
    )



