"""
Copyright 2022 Objectiv B.V.
"""
import pandas as pd
import pytest
from bach import DataFrame
from sql_models.util import is_postgres, is_bigquery

from modelhub.stack.extracted_contexts import ExtractedContextsPipeline
from tests_modelhub.data_and_utils.utils import create_engine_from_db_params, get_parsed_objectiv_data


@pytest.fixture(autouse=True)
def patch_extracted_contexts_validations(monkeypatch):
    monkeypatch.setattr(
        'modelhub.stack.extracted_contexts.bach.from_database.get_dtypes_from_table',
        lambda *args, **kwargs: {},
    )

    monkeypatch.setattr(
        'modelhub.stack.extracted_contexts.ExtractedContextsPipeline._validate_data_dtypes',
        lambda *args, **kwargs: None,
    )


def test_get_base_dtypes(db_params) -> None:
    engine = create_engine_from_db_params(db_params)

    pipeline = ExtractedContextsPipeline(engine, db_params.table_name)
    result = pipeline._get_base_dtypes()

    if is_postgres(engine):
        expected = {
            'value': 'json',
            'event_id': 'uuid',
            'day': 'date',
            'moment': 'timestamp',
            'cookie_id': 'uuid'
        }
    elif is_bigquery(engine):
        expected = {
            'contexts_io_objectiv_taxonomy_1_0_0': [
                {
                    'event_id': 'uuid',
                    'cookie_id': 'uuid',
                    '_type': 'string',
                    '_types': 'json',
                    'global_contexts': 'json',
                    'location_stack': 'json',
                    'time': 'int64',
                }
            ]
        }
    else:
        raise Exception()

    assert expected == result


def test_convert_dtypes(db_params) -> None:
    engine = create_engine_from_db_params(db_params)

    pipeline = ExtractedContextsPipeline(engine, db_params.table_name)

    event = get_parsed_objectiv_data(engine)[0]
    pdf = pd.DataFrame(
        [
            {
                'event_id': str(event['event_id']),
                'day': str(event['day']),
                'moment': str(event['moment']),
                'user_id': str(event['cookie_id']),
            }
        ]
    )
    df = DataFrame.from_pandas(
        engine=engine,
        df=pdf,
        convert_objects=True,
    ).reset_index(drop=True)

    result = pipeline._convert_dtypes(df)
    assert result['event_id'].dtype == 'uuid'
    assert result['day'].dtype == 'date'
    assert result['moment'].dtype == 'timestamp'
    assert result['user_id'].dtype == 'uuid'
