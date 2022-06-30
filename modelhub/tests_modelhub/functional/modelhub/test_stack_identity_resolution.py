"""
Copyright 2022 Objectiv B.V.
"""
import json
import datetime
from uuid import UUID

import bach
import numpy as np
import pandas as pd
import pytest
from tests.functional.bach.test_data_and_utils import assert_equals_data

from modelhub.stack.identity_resolution import IdentityResolutionPipeline
from tests_modelhub.data_and_utils.utils import create_engine_from_db_params

_FAKE_DATA = [
    {
        'event_id': '12b55ed5-4295-4fc1-bf1f-88d64d1ac301',
        'user_id': 'b2df75d2-d7ca-48ac-9747-af47d7a4a2b1',
        'moment': datetime.datetime(2021, 12, 1, 10, 23, 36),
        'global_contexts': json.dumps([
            {
                "_type": "ApplicationContext",
                "id": "objectiv-website",
                "_types": ["AbstractContext", "AbstractGlobalContext", "ApplicationContext"],
            },
        ])
    },
    {
        'event_id': '12b55ed5-4295-4fc1-bf1f-88d64d1ac302',
        'user_id': 'b2df75d2-d7ca-48ac-9747-af47d7a4a2b1',
        'moment': datetime.datetime(2021, 12, 1, 10, 23, 36),
        'global_contexts': json.dumps([
            {
                "_type": "ApplicationContext",
                "id": "objectiv-website",
                "_types": ["AbstractContext", "AbstractGlobalContext", "ApplicationContext"],
            },
            {
                "_type": "IdentityContext",
                "id": "user_1@objectiv.io",
                "name": "email",
            },
            {
                "_type": "HttpContext",
                "_types": ["AbstractContext", "AbstractGlobalContext", "HttpContext"],
            },
        ])
    },
    {
        'event_id': '12b55ed5-4295-4fc1-bf1f-88d64d1ac303',
        'user_id': 'b2df75d2-d7ca-48ac-9747-af47d7a4a2b1',
        'moment': datetime.datetime(2021, 12, 1, 10, 23, 36),
        'global_contexts': '[]',
    },
    {
        'event_id': '12b55ed5-4295-4fc1-bf1f-88d64d1ac304',
        'user_id': 'b2df75d2-d7ca-48ac-9747-af47d7a4a2b1',
        'moment': datetime.datetime(2021, 12, 2, 11, 23, 36),
        'global_contexts': json.dumps(
            [{
                "_type": "IdentityContext",
                "id": "user_2@objectiv.io",
                "name": "email",
            }]
        ),
    },
    {
        'event_id': '12b55ed5-4295-4fc1-bf1f-88d64d1ac305',
        'user_id': 'b2df75d2-d7ca-48ac-9747-af47d7a4a2b2',
        'moment': datetime.datetime(2021, 12, 1, 1, 23, 36),
        'global_contexts': '[]',
    },
]


def _get_identity_resolution_pipeline(db_params) -> IdentityResolutionPipeline:
    engine = create_engine_from_db_params(db_params)
    return IdentityResolutionPipeline(
        engine=engine,
        table_name=db_params.table_name,
    )


@pytest.mark.parametrize('with_sessionized_data', [False, True])
def test_get_pipeline_result(db_params, monkeypatch, with_sessionized_data: bool) -> None:
    pipeline = _get_identity_resolution_pipeline(db_params)
    engine = pipeline._engine

    pdf = pd.DataFrame(_FAKE_DATA)

    context_df = bach.DataFrame.from_pandas(
        df=pdf, engine=engine, convert_objects=True
    ).reset_index(drop=True)
    context_df['user_id'] = context_df['user_id'].astype('uuid')
    context_df['event_id'] = context_df['event_id'].astype('uuid')
    context_df['global_contexts'] = context_df['global_contexts'].astype('json')

    monkeypatch.setattr(
        'modelhub.stack.identity_resolution.get_extracted_contexts_df',
        lambda *args, **kwargs: context_df,
    )
    monkeypatch.setattr(
        'modelhub.stack.sessionized_data.SessionizedDataPipeline.validate_pipeline_result',
        lambda *args, **kwargs: None,
    )

    result = pipeline._get_pipeline_result(
        with_sessionized_data=with_sessionized_data,
        session_gap_seconds=1800,
    )

    expected_columns = ['event_id', 'user_id', 'moment', 'global_contexts']
    expected_data = [
        [
            UUID(_FAKE_DATA[0]['event_id']),
            'user_2@objectiv.io|email',
            _FAKE_DATA[0]['moment'],
            json.loads(_FAKE_DATA[0]['global_contexts']),
        ],
        [
            UUID(_FAKE_DATA[1]['event_id']),
            'user_2@objectiv.io|email',
            _FAKE_DATA[1]['moment'],
            json.loads(_FAKE_DATA[1]['global_contexts']),
        ],
        [
            UUID(_FAKE_DATA[2]['event_id']),
            'user_2@objectiv.io|email',
            _FAKE_DATA[2]['moment'],
            json.loads(_FAKE_DATA[2]['global_contexts']),
        ],
        [
            UUID(_FAKE_DATA[3]['event_id']),
            'user_2@objectiv.io|email',
            _FAKE_DATA[3]['moment'],
            json.loads(_FAKE_DATA[3]['global_contexts']),
        ],
        [
            UUID(_FAKE_DATA[4]['event_id']),
            None,
            _FAKE_DATA[4]['moment'],
            json.loads(_FAKE_DATA[4]['global_contexts']),
        ],
    ]
    if with_sessionized_data:
        expected_columns += ['session_id', 'session_hit_number']
        expected_session_data = [[2, 1], [2, 2], [2, 3], [3, 1], [1, 1]]
        expected_data = np.c_[
            # specify dtype for getting rid of numpy's VisibleDeprecationWarning
            np.array(expected_data, dtype=object),
            np.array(expected_session_data, dtype=object)
        ].tolist()

    assert_equals_data(
        result,
        expected_columns=expected_columns,
        expected_data=expected_data,
        use_to_pandas=True,
        order_by=['event_id'],
    )


def test_extract_identities_from_global_contexts(db_params) -> None:
    pipeline = _get_identity_resolution_pipeline(db_params)
    engine = pipeline._engine

    pdf = pd.DataFrame(_FAKE_DATA)

    context_df = bach.DataFrame.from_pandas(
        df=pdf, engine=engine, convert_objects=True
    ).reset_index(drop=True)
    context_df['global_contexts'] = context_df['global_contexts'].astype('json')

    result = pipeline._extract_identities_from_global_contexts(context_df)

    assert_equals_data(
        result,
        expected_columns=['user_id', 'identity_user_id'],
        expected_data=[
            [
                'b2df75d2-d7ca-48ac-9747-af47d7a4a2b1', 'user_2@objectiv.io|email',
            ],
        ],
    )


def test_resolve_original_user_ids(db_params) -> None:
    pipeline = _get_identity_resolution_pipeline(db_params)
    engine = pipeline._engine

    pdf_to_resolve = pd.DataFrame(
        [
            {'event_id': '1', 'user_id': '1'},
            {'event_id': '2', 'user_id': '1'},
            {'event_id': '3', 'user_id': '2'},
            {'event_id': '4', 'user_id': '3'},
            {'event_id': '5', 'user_id': '4'},
        ]
    )
    identity_context_pdf = pd.DataFrame(
        [
            {'user_id': '2', 'identity_user_id': 'new_identity_2'},
            {'user_id': '3', 'identity_user_id': 'new_identity_2'},
            {'user_id': '4', 'identity_user_id': 'new_identity_4'},
        ]
    )

    df_to_resolve = bach.DataFrame.from_pandas(engine, pdf_to_resolve, True).reset_index(drop=True)
    identity_context_df = bach.DataFrame.from_pandas(engine, identity_context_pdf, True).reset_index(drop=True)

    result = pipeline._resolve_original_user_ids(df_to_resolve, identity_context_df)
    assert_equals_data(
        result,
        expected_columns=['event_id', 'user_id', 'identity_user_id'],
        expected_data=[
            ['1', '1', None],
            ['2', '1', None],
            ['3', 'new_identity_2', 'new_identity_2'],
            ['4', 'new_identity_2', 'new_identity_2'],
            ['5', 'new_identity_4', 'new_identity_4'],
        ],
        order_by=['event_id'],
    )


def test_anonymize_user_ids_without_identity(db_params) -> None:
    pipeline = _get_identity_resolution_pipeline(db_params)
    engine = pipeline._engine

    pdf = pd.DataFrame(
        [
            {'event_id': '1', 'user_id': '1', 'identity_user_id': None},
            {'event_id': '2', 'user_id': '1', 'identity_user_id': None},
            {'event_id': '3', 'user_id': 'new_identity_2', 'identity_user_id': 'new_identity_2'},
            {'event_id': '4', 'user_id': 'new_identity_2', 'identity_user_id': 'new_identity_2'},
            {'event_id': '5', 'user_id': 'new_identity_4', 'identity_user_id': 'new_identity_4'},
        ]
    )
    df = bach.DataFrame.from_pandas(engine, pdf, True).reset_index(drop=True)
    result = pipeline._anonymize_user_ids_without_identity(df)
    assert_equals_data(
        result,
        expected_columns=['event_id', 'user_id', 'identity_user_id'],
        expected_data=[
            ['1', None, None],
            ['2', None, None],
            ['3', 'new_identity_2', 'new_identity_2'],
            ['4', 'new_identity_2', 'new_identity_2'],
            ['5', 'new_identity_4', 'new_identity_4'],
        ],
        order_by=['event_id'],
    )
