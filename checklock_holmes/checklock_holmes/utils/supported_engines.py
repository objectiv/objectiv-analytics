"""
Copyright 2022 Objectiv B.V.
"""
from enum import Enum
from typing import List


class SupportedEngine(str, Enum):
    POSTGRES = 'postgres'
    BIGQUERY = 'bigquery'

    @classmethod
    def get_supported_engines(cls, engines_to_check: List[str]) -> List['SupportedEngine']:
        """
        Returns supported engines based on cli provided param
        """
        if len(engines_to_check) == 1 and engines_to_check[0] == 'all':
            return [cls(eng) for eng in cls]

        return [cls(e_check) for e_check in engines_to_check]
