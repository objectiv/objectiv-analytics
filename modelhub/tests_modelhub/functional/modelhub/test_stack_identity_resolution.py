import json
import datetime
from uuid import UUID

import bach
import pandas as pd
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
        'moment': datetime.datetime(2021, 12, 2, 10, 23, 36),
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
        'moment': datetime.datetime(2021, 12, 1, 10, 23, 36),
        'global_contexts': '[]',
    },
]


def _get_identity_resolution_pipeline(db_params) -> IdentityResolutionPipeline:
    engine = create_engine_from_db_params(db_params)
    return IdentityResolutionPipeline(
        engine=engine,
        table_name=db_params.table_name,
    )


def test_get_pipeline_result(db_params, monkeypatch) -> None:
    pipeline = _get_identity_resolution_pipeline(db_params)
    engine = pipeline._engine

    pdf = pd.DataFrame(_FAKE_DATA)
    pdf = pdf.rename(columns={'cookie_id': 'user_id'})

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

    result = pipeline._get_pipeline_result(with_sessionized_data=False)

    assert_equals_data(
        result,
        expected_columns=['event_id', 'user_id', 'moment', 'global_contexts'],
        expected_data=[
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
        ],
        use_to_pandas=True,
        order_by=['event_id'],
    )
