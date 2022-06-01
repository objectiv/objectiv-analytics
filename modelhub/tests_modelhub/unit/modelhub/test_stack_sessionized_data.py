"""
Copyright 2022 Objectiv B.V.
"""
import bach
import pandas as pd
import pytest

from modelhub import SessionizedDataPipeline
from tests_modelhub.data_and_utils.utils import create_engine_from_db_params


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


def test_convert_dtypes(db_params) -> None:
    engine = create_engine_from_db_params(db_params)

    pipeline = SessionizedDataPipeline(engine, db_params.table_name)

    pdf = pd.DataFrame({'session_id': ['1'], 'session_hit_number': ['2']})
    df = bach.DataFrame.from_pandas(
        engine=engine,
        df=pdf,
        convert_objects=True,
    ).reset_index(drop=True)

    assert df['session_id'].dtype == 'string'
    assert df['session_hit_number'].dtype == 'string'

    result = pipeline._convert_dtypes(df)
    assert result['session_id'].dtype == 'int64'
    assert result['session_hit_number'].dtype == 'int64'
