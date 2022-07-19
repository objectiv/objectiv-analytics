"""
Copyright 2022 Objectiv B.V.
"""
import bach
import pandas as pd

from modelhub import SessionizedDataPipeline
from tests_modelhub.data_and_utils.utils import create_engine_from_db_params


def test_convert_dtypes(db_params) -> None:
    engine = create_engine_from_db_params(db_params)

    pipeline = SessionizedDataPipeline(session_gap_seconds=1)
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
