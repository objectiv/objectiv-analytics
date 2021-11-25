"""
Copyright 2021 Objectiv B.V.
"""
from enum import Enum
from typing import Dict, NamedTuple, Union, List

from bach import DataFrame


class Materialization(Enum):
    CTE = 'cte'
    VIEW = 'view'
    TABLE = 'table'


class Entry(NamedTuple):
    name: str
    df: DataFrame
    materialization: Materialization


class DataCollection:

    def __init__(self):
        self._frames: Dict[str, Entry] = {}

    def add(self,
            df: DataFrame,
            name: str,
            materialization: Union[str, Materialization] = Materialization.CTE):
        """

        """
        if isinstance(materialization, str):
            materialization = Materialization(materialization)
        self._frames[name] = Entry(name=name, df=df.copy(), materialization=materialization)

    def get(self, name: str) -> DataFrame:
        return self._frames[name].df.copy()

    # todo: delete, modify

    def to_sql(self) -> List[str]:
        # todo: implement properly
        result = []
        for entry in self._frames.values():
            result.append(entry.df.view_sql())
        return result
