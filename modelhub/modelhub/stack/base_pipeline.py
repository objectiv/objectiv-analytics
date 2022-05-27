"""
Copyright 2022 Objectiv B.V.
"""
from abc import abstractmethod
from typing import List

import bach
from sqlalchemy.engine import Engine


class BaseDataPipeline:
    """
    Abstract class that specifies the engine and table from where the pipeline will extract the data.
    Child classes are in charge of implementing:
     - _get_pipeline_result method, which is in charge of generating the correct bach DataFrame
     - validate_pipeline_result method, which is in charge of verifying that the
       pipeline is generating the expected result.
    """
    def __init__(self, engine: Engine, table_name: str):
        self._engine = engine
        self._table_name = table_name

    def __call__(self, **kwargs) -> bach.DataFrame:
        result = self._get_pipeline_result(**kwargs)
        self.validate_pipeline_result(result)
        return result

    @classmethod
    @abstractmethod
    def validate_pipeline_result(cls, result: bach.DataFrame) -> None:
        raise NotImplementedError()

    @abstractmethod
    def _get_pipeline_result(self, **kwargs) -> bach.DataFrame:
        raise NotImplementedError()

    def _validate_data_columns(self, expected_columns: List[str], current_columns: List[str]) -> None:
        missing_columns = set(expected_columns) - set(current_columns)
        if missing_columns:
            raise KeyError(
                f'{self.__class__.__name__} expects mandatory columns: {expected_columns}, '
                f'missing: {",".join(missing_columns)}.'
            )
