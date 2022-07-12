"""
Copyright 2022 Objectiv B.V.
"""
import bach
import pandas as pd
import pytest

from modelhub.pipelines.identity_resolution import IdentityResolutionPipeline
from tests_modelhub.data_and_utils.utils import create_engine_from_db_params


def test_convert_dtypes(db_params) -> None:
    engine = create_engine_from_db_params(db_params)

    pipeline = IdentityResolutionPipeline()

    pdf = pd.DataFrame({'user_id': ['1']})
    df = bach.DataFrame.from_pandas(
        engine=engine,
        df=pdf,
        convert_objects=True,
    ).reset_index(drop=True)
    df['user_id'] = df['user_id'].astype('uuid')

    result = pipeline._convert_dtypes(df)
    assert result['user_id'].dtype == 'string'


def test_anonymize_user_ids_without_identity(db_params) -> None:
    engine = create_engine_from_db_params(db_params)

    pdf = pd.DataFrame({'user_id': ['1']})
    df = bach.DataFrame.from_pandas(
        engine=engine,
        df=pdf,
        convert_objects=True,
    ).reset_index(drop=True)

    with pytest.raises(Exception, match=r'Cannot anonymize'):
        IdentityResolutionPipeline.anonymize_user_ids_without_identity(df)
