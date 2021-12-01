"""
Copyright 2021 Objectiv B.V.
"""
import re
from typing import Dict, NamedTuple, Union

from bach import DataFrame
from sql_models.model import Materialization, SqlModel, CustomSqlModel
from sql_models.sql_generator import to_sql_materialized_nodes


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
            materialization: Union[str, Materialization] = Materialization.QUERY) -> DataFrame:
        """
        TODO: comments
        """
        if not re.match('^[a-zA-Z0-9_]+$', name):
            raise ValueError(f'Name must match ^[a-zA-Z0-9_]+$, name: "{name}"')
        if isinstance(materialization, str):
            materialization = Materialization[materialization.upper()]
        if not materialization.is_statement:
            raise ValueError(f'Materialization type not supported: {materialization}')

        df_copy = df.materialize(node_name=name)
        materialized_node = df_copy.base_node.copy_set_materialization(materialization=materialization)
        df_copy = df_copy.copy_override(base_node=materialized_node)
        self._frames[name] = Entry(name=name, df=df_copy, materialization=materialization)
        return df_copy
        # TODO: add a function in DataFrame for this too?
        # TODO: removing savepoints from the DataCollection and from all involved DFs might be hard to
        #   implement, and still annoying to use for the user.
        # TODO: add function to elegantly update base_node of a dataframe

    def get(self, name: str) -> DataFrame:
        return self._frames[name].df.copy()

    # todo: delete, modify

    def to_sql(self) -> Dict[str, str]:
        """
        TODO: comments
        """
        references: Dict[str, SqlModel] = {
            f'ref_{entry.name}': entry.df.base_node for entry in self._frames.values()
        }
        graph = get_virtual_node(references)
        # for entry in self._frames.values():
        #     reference_path = (f'ref_{entry.name}', )
        #     graph = graph.set_materialization(
        #         reference_path=reference_path,
        #         materialization=entry.materialization
        #     )
        sqls = to_sql_materialized_nodes(start_node=graph, include_start_node=False)
        return sqls


def get_virtual_node(references: Dict[str, SqlModel]) -> SqlModel:
    # reference_sql is of form "{{ref_0}}, {{1}}, ..., {{n}}"
    reference_sql = ', '.join(f'{{{{{ref_name}}}}}' for ref_name in references.keys())
    sql = f'select * from {reference_sql}'
    return CustomSqlModel(name='virtual_node', sql=sql)\
        .set_materialization(Materialization.VIRTUAL_NODE)\
        .set_values(**references)\
        .instantiate()
