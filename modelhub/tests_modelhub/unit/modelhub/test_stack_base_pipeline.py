"""
Copyright 2022 Objectiv B.V.
"""
import pytest

from modelhub.stack.base_pipeline import BaseDataPipeline
from tests_modelhub.data_and_utils.utils import create_engine_from_db_params


def test_base_pipeline_validate_data_columns(db_params) -> None:
    engine = create_engine_from_db_params(db_params)

    pipeline = BaseDataPipeline(engine, db_params.table_name)

    with pytest.raises(KeyError, match=r'expects mandatory columns'):
        pipeline._validate_data_columns(
            expected_columns=['a', 'b', 'c'],
            current_columns=['b', 'a'],
        )

    pipeline._validate_data_columns(
        expected_columns=['a', 'b', 'c'],
        current_columns=['a', 'c', 'b'],
    )
