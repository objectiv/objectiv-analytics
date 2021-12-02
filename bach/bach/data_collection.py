"""
Copyright 2021 Objectiv B.V.
"""
import re
from typing import Dict, NamedTuple, Union

from sqlalchemy.engine import Engine

from bach import DataFrame
from sql_models.model import Materialization, SqlModel, CustomSqlModel
from sql_models.sql_generator import to_sql_materialized_nodes


class Entry(NamedTuple):
    name: str
    df: DataFrame
    materialization: Materialization
    executed: bool = False


class DataCollection:

    def __init__(self):
        self._entries: Dict[str, Entry] = {}

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
        # TODO: also update base_node of series. this is BROKEN
        df_copy = df_copy.copy_override(base_node=materialized_node)
        self._entries[name] = Entry(name=name, df=df_copy, materialization=materialization)
        return df_copy
        # TODO: add a function in DataFrame for this too?
        # TODO: removing savepoints from the DataCollection and from all involved DFs might be hard to
        #   implement, and still annoying to use for the user.
        # TODO: add function to elegantly update base_node of a dataframe

    def get(self, name: str) -> DataFrame:
        return self._entries[name].df.copy()

    # todo: delete, modify

    def to_sql(self) -> Dict[str, str]:
        """
        TODO: comments
        """
        references: Dict[str, SqlModel] = {
            f'ref_{entry.name}': entry.df.base_node for entry in self._entries.values()
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

    def execute(self, engine: Engine):
        sql_statements = self.to_sql()
        not_executed = {
            name: sql for name, sql in sql_statements.items() if not self._entries[name].executed
        }
        if not not_executed:
            # nothing to do
            return

        for name, sql in not_executed:
            # TODO: update DAG

        with engine.connect() as conn:
            with conn.begin() as transaction:
                for name, sql in not_executed:
                    conn.execute(sql)
                    item = self._entries[name]
                    new_entry = Entry(
                        name=item.name,
                        df=item.df,
                        materialization=item.materialization,
                        executed=True
                    )
                    self._entries[name] = new_entry


def get_virtual_node(references: Dict[str, SqlModel]) -> SqlModel:
    # reference_sql is of form "{{ref_0}}, {{1}}, ..., {{n}}"
    reference_sql = ', '.join(f'{{{{{ref_name}}}}}' for ref_name in references.keys())
    sql = f'select * from {reference_sql}'
    return CustomSqlModel(name='virtual_node', sql=sql)\
        .set_materialization(Materialization.VIRTUAL_NODE)\
        .set_values(**references)\
        .instantiate()
