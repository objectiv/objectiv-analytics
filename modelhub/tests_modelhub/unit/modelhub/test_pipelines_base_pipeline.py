"""
Copyright 2022 Objectiv B.V.
"""
import pytest

from modelhub.pipelines.base_pipeline import BaseDataPipeline


def test_base_pipeline_validate_data_dtypes() -> None:
    pipeline = BaseDataPipeline()

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
