"""
Copyright 2022 Objectiv B.V.
"""
import pytest

from modelhub.stack.base_pipeline import BaseDataPipeline
from tests_modelhub.data_and_utils.utils import create_engine_from_db_params


def test_base_pipeline_validate_data_dtypes(db_params) -> None:
    engine = create_engine_from_db_params(db_params)

    pipeline = BaseDataPipeline(engine, db_params.table_name)

    expected_dtypes = {'a': 'int64', 'b': ['float64'], 'c': 'json'}
    with pytest.raises(KeyError, match=r'expects mandatory columns'):
        pipeline._validate_data_dtypes(
            expected_dtypes=expected_dtypes,
            current_dtypes={'a': 'int64', 'b': ['float64']},
        )

    with pytest.raises(ValueError, match='"c" must be json dtype, got string'):
        pipeline._validate_data_dtypes(
            expected_dtypes=expected_dtypes,
            current_dtypes={'a': 'int64', 'b': ['float64'], 'c': 'string'},
        )

    pipeline._validate_data_dtypes(
        expected_dtypes=expected_dtypes,
        current_dtypes={'a': 'int64', 'b': ['float64'], 'c': 'objectiv_location_stack'},
    )
