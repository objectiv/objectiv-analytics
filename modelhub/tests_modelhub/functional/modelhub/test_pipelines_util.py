import pandas as pd

from modelhub.pipelines.util import get_objectiv_data
from tests_modelhub.data_and_utils.utils import create_engine_from_db_params
from tests_modelhub.functional.modelhub.test_pipelines_extracted_contexts import get_expected_context_pandas_df

_SESSION_GAP_SECONDS = 180


def test_get_objectiv_data_only_context_data(db_params) -> None:
    engine = create_engine_from_db_params(db_params)

    result = get_objectiv_data(
        engine=engine, table_name=db_params.table_name, with_sessionized_data=False,
    )
    result = result.sort_index()
    expected = get_expected_context_pandas_df(engine).set_index('event_id')
    pd.testing.assert_frame_equal(expected, result.to_pandas())


def test_get_objectiv_data_w_sessionized_data(db_params) -> None:
    engine = create_engine_from_db_params(db_params)

    result = get_objectiv_data(
        engine=engine,
        table_name=db_params.table_name,
        session_gap_seconds=_SESSION_GAP_SECONDS,
        with_sessionized_data=True,
    )
    result = result.sort_index()

    expected = get_expected_context_pandas_df(engine)
    expected['session_id'] = pd.Series([3, 3, 3, 2, 4, 4, 5, 5, 6, 7, 1, 1])
    expected['session_hit_number'] = pd.Series([1, 2, 3, 1, 1, 2, 1, 2, 1, 1, 1, 2])
    expected = expected.set_index('event_id')
    pd.testing.assert_frame_equal(expected, result.to_pandas())


def test_get_objectiv_data_w_identity_data(db_params) -> None:
    engine = create_engine_from_db_params(db_params)

    result = get_objectiv_data(
        engine=engine,
        table_name=db_params.table_name,
        session_gap_seconds=_SESSION_GAP_SECONDS,
        with_sessionized_data=False,
        identity_resolution='email',
        anonymize_unidentified_users=False,
    )
    result = result.sort_index()

    expected = get_expected_context_pandas_df(engine)
    expected['user_id'] = pd.Series(
        [
            'fake2@objectiv.io|email',
            'fake2@objectiv.io|email',
            'fake2@objectiv.io|email',
            'b2df75d2-d7ca-48ac-9747-af47d7a4a2b1',
            'b2df75d2-d7ca-48ac-9747-af47d7a4a2b1',
            'b2df75d2-d7ca-48ac-9747-af47d7a4a2b1',
            'fake3@objectiv.io|email',
            'fake3@objectiv.io|email',
            'fake3@objectiv.io|email',
            'b2df75d2-d7ca-48ac-9747-af47d7a4a2b4',
            'fake2@objectiv.io|email',
            'fake2@objectiv.io|email',
        ]
    )
    expected = expected.set_index('event_id')
    pd.testing.assert_frame_equal(expected, result.to_pandas())


def test_get_objectiv_data_w_identity_data_w_anonymized_users(db_params) -> None:
    engine = create_engine_from_db_params(db_params)

    result = get_objectiv_data(
        engine=engine,
        table_name=db_params.table_name,
        session_gap_seconds=_SESSION_GAP_SECONDS,
        with_sessionized_data=False,
        identity_resolution='phone',
        anonymize_unidentified_users=True,
    )
    result = result.sort_index()

    expected = get_expected_context_pandas_df(engine)
    expected['user_id'] = pd.Series(
        [
            '123456789|phone',
            '123456789|phone',
            '123456789|phone',
            '123456789|phone',
            '123456789|phone',
            '123456789|phone',
            None,
            None,
            None,
            None,
            '123456789|phone',
            '123456789|phone',
        ]
    )

    expected = expected.set_index('event_id')
    pd.testing.assert_frame_equal(expected, result.to_pandas())


def test_get_objectiv_data_w_identity_n_session_data(db_params) -> None:
    engine = create_engine_from_db_params(db_params)

    result = get_objectiv_data(
        engine=engine,
        table_name=db_params.table_name,
        session_gap_seconds=_SESSION_GAP_SECONDS,
        with_sessionized_data=True,
        identity_resolution='phone',
        anonymize_unidentified_users=True,
    )
    result = result.sort_index()

    expected = get_expected_context_pandas_df(engine)
    expected['user_id'] = pd.Series(
        [
            '123456789|phone',
            '123456789|phone',
            '123456789|phone',
            '123456789|phone',
            '123456789|phone',
            '123456789|phone',
            None,
            None,
            None,
            None,
            '123456789|phone',
            '123456789|phone',
        ]
    )
    expected['session_id'] = pd.Series([2, 2, 2, 2, 3, 3, 4, 4, 5, 6, 1, 1])
    expected['session_hit_number'] = pd.Series([2, 3, 4, 1, 1, 2, 1, 2, 1, 1, 1, 2])
    expected = expected.set_index('event_id')

    pd.testing.assert_frame_equal(expected, result.to_pandas())
