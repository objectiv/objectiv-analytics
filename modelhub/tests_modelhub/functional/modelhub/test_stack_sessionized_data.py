"""
Copyright 2022 Objectiv B.V.
"""
import datetime
from uuid import UUID

import bach
import pandas as pd
from sql_models.util import is_bigquery
from tests.functional.bach.test_data_and_utils import assert_equals_data

from modelhub import SessionizedDataPipeline, get_extracted_contexts_df, get_sessionized_data
from tests_modelhub.data_and_utils.utils import create_engine_from_db_params, get_parsed_objectiv_data
from tests_modelhub.functional.modelhub.test_stack_extracted_contexts import get_expected_context_pandas_df

_SESSION_GAP_SECONDS = 180

_FAKE_SESSIONIZED_DATA = [
    {
        'user_id': '1',
        'event_id': '1',
        'moment': datetime.datetime(2021, 12, 1, 10, 23, 36),
        'is_start_of_session': True,
    },
    {
        'user_id': '1',
        'event_id': '2',
        'moment': datetime.datetime(2021, 12, 1, 10, 24, 40),
        'is_start_of_session': None,
    },
    {
        'user_id': '1',
        'event_id': '3',
        'moment': datetime.datetime(2021, 12, 1, 10, 28, 40),
        'is_start_of_session': True,
    },
    {
        'user_id': '1',
        'event_id': '4',
        'moment': datetime.datetime(2021, 12, 2, 10, 23, 36),
        'is_start_of_session': True,
    },
    {
        'user_id': '2',
        'event_id': '5',
        'moment': datetime.datetime(2021, 12, 2, 10, 23, 36),
        'is_start_of_session': True,
    },
    {
        'user_id': '2',
        'event_id': '6',
        'moment': datetime.datetime(2021, 12, 2, 10, 24, 23),
        'is_start_of_session': None,
    },
]


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

    # bq doesn't support uuids, cast it later
    pdf['user_id'] = pdf['user_id'].astype(str)
    pdf['event_id'] = pdf['event_id'].astype(str)

    context_df = bach.DataFrame.from_pandas(df=pdf, engine=engine, convert_objects=True).reset_index(drop=True)
    context_df['user_id'] = context_df['user_id'].astype('uuid')
    context_df['event_id'] = context_df['event_id'].astype('uuid')

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
        use_to_pandas=True,
        order_by=['event_id'],
    )


def test_calculate_session_start(db_params) -> None:
    pipeline = _get_sessionized_data_pipeline(db_params)
    engine = pipeline._engine

    context_pdf = pd.DataFrame(_FAKE_SESSIONIZED_DATA)
    context_pdf = context_pdf[['user_id', 'event_id', 'moment']]
    context_df = bach.DataFrame.from_pandas(engine=engine, df=context_pdf, convert_objects=True)
    result = pipeline._calculate_session_start(context_df, session_gap_seconds=_SESSION_GAP_SECONDS)

    assert_equals_data(
        result.sort_index(),
        expected_columns=['_index_0', 'is_start_of_session'],
        expected_data=[
            [0, True],
            [1, None],
            [2, True],
            [3, True],
            [4, True],
            [5, None],
        ]
    )


def test_calculate_session_start_id(db_params) -> None:
    pipeline = _get_sessionized_data_pipeline(db_params)
    engine = pipeline._engine
    context_pdf_w_session_start = pd.DataFrame(_FAKE_SESSIONIZED_DATA)
    context_df_w_session_start = bach.DataFrame.from_pandas(
        engine=engine, df=context_pdf_w_session_start, convert_objects=True,
    )

    result = pipeline._calculate_session_start_id(context_df_w_session_start)

    assert_equals_data(
        result.sort_index(),
        expected_columns=['_index_0', 'session_start_id'],
        expected_data=[
            [0, 1],
            [1, None],
            [2, 2],
            [3, 3],
            [4, 4],
            [5, None],
        ]
    )


def test_calculate_session_count(db_params) -> None:
    pipeline = _get_sessionized_data_pipeline(db_params)
    engine = pipeline._engine
    context_pdf_w_session_start = pd.DataFrame(_FAKE_SESSIONIZED_DATA)
    context_df_w_session_start = bach.DataFrame.from_pandas(
        engine=engine, df=context_pdf_w_session_start, convert_objects=True,
    )

    result = pipeline._calculate_session_count(context_df_w_session_start)
    assert_equals_data(
        result.sort_index(),
        expected_columns=['_index_0', 'is_one_session'],
        expected_data=[
            [0, 1],
            [1, 1],
            [2, 2],
            [3, 3],
            [4, 4],
            [5, 4],
        ]
    )


def test_calculate_base_session_series(db_params) -> None:
    pipeline = _get_sessionized_data_pipeline(db_params)
    engine = pipeline._engine
    context_pdf = pd.DataFrame(_FAKE_SESSIONIZED_DATA)
    context_pdf = context_pdf[['user_id', 'event_id', 'moment']]
    context_df = bach.DataFrame.from_pandas(
        engine=engine, df=context_pdf, convert_objects=True,
    ).reset_index(drop=True)

    tz_info = datetime.timezone.utc if is_bigquery(engine) else None

    result = pipeline._calculate_base_session_series(context_df, _SESSION_GAP_SECONDS)
    assert_equals_data(
        result,
        expected_columns=[
            'user_id', 'event_id', 'moment', 'is_start_of_session', 'session_start_id', 'is_one_session',
        ],
        expected_data=[
            ['1', '1', datetime.datetime(2021, 12, 1, 10, 23, 36, tzinfo=tz_info), True, 1,    1],
            ['1', '2', datetime.datetime(2021, 12, 1, 10, 24, 40, tzinfo=tz_info), None, None, 1],
            ['1', '3', datetime.datetime(2021, 12, 1, 10, 28, 40, tzinfo=tz_info), True, 2,    2],
            ['1', '4', datetime.datetime(2021, 12, 2, 10, 23, 36, tzinfo=tz_info), True, 3,    3],
            ['2', '5', datetime.datetime(2021, 12, 2, 10, 23, 36, tzinfo=tz_info), True, 4,    4],
            ['2', '6', datetime.datetime(2021, 12, 2, 10, 24, 23, tzinfo=tz_info), None, None, 4],
        ],
        order_by=['user_id', 'event_id'],
    )


def test_calculate_objectiv_session_series(db_params) -> None:
    pipeline = _get_sessionized_data_pipeline(db_params)
    engine = pipeline._engine
    context_pdf = pd.DataFrame(_FAKE_SESSIONIZED_DATA)
    context_pdf['session_start_id'] = pd.Series([1, None, 2, 3, 4, None])
    context_pdf['is_one_session'] = pd.Series([1, 1, 2, 3, 4, 4])

    context_df = bach.DataFrame.from_pandas(
        engine=engine, df=context_pdf, convert_objects=True,
    ).reset_index(drop=True)

    tz_info = datetime.timezone.utc if is_bigquery(engine) else None

    result = pipeline._calculate_objectiv_session_series(context_df)
    assert_equals_data(
        result,
        expected_columns=[
            'user_id',
            'event_id',
            'moment',
            'is_start_of_session',
            'session_start_id',
            'is_one_session',
            'session_id',
            'session_hit_number',
        ],
        expected_data=[
            ['1', '1', datetime.datetime(2021, 12, 1, 10, 23, 36, tzinfo=tz_info), True, 1,    1, 1, 1],
            ['1', '2', datetime.datetime(2021, 12, 1, 10, 24, 40, tzinfo=tz_info), None, None, 1, 1, 2],
            ['1', '3', datetime.datetime(2021, 12, 1, 10, 28, 40, tzinfo=tz_info), True, 2,    2, 2, 1],
            ['1', '4', datetime.datetime(2021, 12, 2, 10, 23, 36, tzinfo=tz_info), True, 3,    3, 3, 1],
            ['2', '5', datetime.datetime(2021, 12, 2, 10, 23, 36, tzinfo=tz_info), True, 4,    4, 4, 1],
            ['2', '6', datetime.datetime(2021, 12, 2, 10, 24, 23, tzinfo=tz_info), None, None, 4, 4, 2],
        ],
        order_by=['user_id', 'event_id'],
    )


def test_get_sessionized_data_df(db_params) -> None:
    engine = create_engine_from_db_params(db_params)

    result = get_sessionized_data(engine=engine, table_name=db_params.table_name)
    result = result.sort_index()

    expected = get_expected_context_pandas_df(engine)
    expected['session_id'] = pd.Series([3, 3, 3, 2, 4, 4, 5, 5, 6, 7, 1, 1])
    expected['session_hit_number'] = pd.Series([1, 2, 3, 1, 1, 2, 1, 2, 1, 1, 1, 2])
    expected = expected.set_index('event_id')
    pd.testing.assert_frame_equal(expected, result.to_pandas())

    result = get_sessionized_data(engine=engine, table_name=db_params.table_name, set_index=False)
    assert 'event_id' not in result.index
    assert 'event_id' in result.data
