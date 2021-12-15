"""
Copyright 2021 Objectiv B.V.
"""
import re
from typing import Dict, NamedTuple, TYPE_CHECKING, List, Tuple, Union, Optional

from sqlalchemy.engine import Engine

from sql_models.model import Materialization, SqlModel, CustomSqlModel
from sql_models.sql_generator import to_sql_materialized_nodes
from sql_models.util import quote_identifier

if TYPE_CHECKING:
    from bach import DataFrame


class SavepointInfo(NamedTuple):
    """
    Class to represent a savepoint
    """
    name: str
    df: 'DataFrame'
    materialization: Materialization
    state: str  # TODO: enum


class ExecutedStatement(NamedTuple):
    """
    INTERNAL: class to represent an executed statement inside the Savepoints class
    """
    name: str
    sql: str
    materialization: Materialization
    node_hash: str


class Savepoints:
    """
    TODO: comments
    """

    def __init__(self):
        self._entries: Dict[str, 'DataFrame'] = {}
        self._executed_statements: Dict[str, ExecutedStatement] = {}

    @property
    def created(self) -> List[Tuple[str, Materialization]]:
        """ List of all created database objects, in order of creation. """
        return [
            (name, exec_statement.materialization)
            for name, exec_statement in self._executed_statements.items()
            if self._executed_statements[name].materialization.modifies_db
        ]

    @property
    def tables_created(self) -> List[str]:
        return [name for name, materialization in self.created if materialization == Materialization.TABLE]

    @property
    def views_created(self) -> List[str]:
        return [name for name, materialization in self.created if materialization == Materialization.VIEW]

    def add_df(self, df: 'DataFrame'):
        """
        Add the DataFrame as a savepoint. Assumes df.is_materialized.
        Uses
        """
        name = df.base_node.materialization_name
        materialization = df.base_node.materialization
        df_copy = df.copy()
        # TODO: make sure the dataframe wasn't materialized for nothing in dataframe.add_savepoint if
        #  any of these checks fail
        if not materialization.is_statement:
            raise ValueError(f'Materialization type not supported: {materialization}')
        if name in self._entries:
            raise ValueError(f'Savepoint with name "{name}" already exists.')
        if name is None or not re.match('^[a-zA-Z0-9_]+$', name):
            raise ValueError(f'Name must match ^[a-zA-Z0-9_]+$, name: "{name}"')
        self._entries[name] = df_copy

    # todo: also support removing saveponts

    def get_df(self, savepoint_name: str) -> 'DataFrame':
        return self._entries[savepoint_name].copy()

    def update_materialization(self, savepoint_name: str, materialization: Materialization):
        self._entries[savepoint_name].base_node.set_materialization(materialization)

    def list(self) -> List[SavepointInfo]:
        """
        Get information on all savepoints, in order that they should be executed
        """
        result = []
        for name, sql in self.to_sql().items():
            df = self.get_df(name)
            state = 'not executed'  # todo: use an enum?
            if name in self._executed_statements:
                # todo: track hash and materialization, and use that to determine whether sql changed
                if self._executed_statements[name] == sql:
                    state = 'executed'
                else:
                    state = 'executed, out of sync'
            result.append(
                SavepointInfo(
                    name=name,
                    df=df,
                    materialization=df.base_node.materialization,
                    state=state
                )
            )
        return result

    def to_sql(self, name_filter: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Generate the sql for all save-points

        :return: dictionary mapping the name of each savepoint to the sql for that savepoint.
        """
        references: Dict[str, SqlModel] = {
            f'ref_{name}': entry.base_node for name, entry in self._entries.items()
            if name_filter is None or name in name_filter
        }
        # TODO: move this to sqlmodel?
        graph = get_virtual_node(references)
        sqls = to_sql_materialized_nodes(start_node=graph, include_start_node=False)
        return sqls

    def execute(
            self,
            engine: Engine,
            savepoint_names: Union[List[str], str] = None,
            overwrite_existing: bool = False
    ) -> Dict[str, List[tuple]]:
        """
        Execute the savepoints:
            * Create all tables and views that do not yet exist or have been changed since the last time
                that execute() was invoked
            * Run all queries and return the results
        :param engine: engine to execute the sql statements
        :overwrite_existing: If True, then any savepoint that creates a table or view will be reexecuted,
            even if nothing changed in the sql of that table/view.
        :return: The result of all savepoints with materialization type QUERY. A dictionary mapping
            the savepoint name to a List of tuples representing the rows that the queries returned.
        """
        # todo: store engine as part of __init__?
        if isinstance(savepoint_names, str):
            savepoint_names = [savepoint_names]
        sql_statements = self.to_sql(name_filter=savepoint_names)
        return self._execute_sql(engine, sql_statements, overwrite_existing)

    def _has_changed(self, name) -> bool:
        if name not in self._executed_statements:
            # If this savepoint has not been executed yet, then it has changed since last time when it
            # didn't exist
            return True
        current_df = self._entries[name]
        executed_stmt = self._executed_statements[name]
        if executed_stmt.materialization != current_df.base_node.materialization:
            return True
        if executed_stmt.node_hash != current_df.base_node.hash:
            return True
        return False

    def _execute_sql(
            self,
            engine: Engine,
            sql_statements: Dict[str, str],
            overwrite_existing: bool = False

    ) -> Dict[str, List[tuple]]:
        """
        Execute the savepoints:
            * Create all tables and views that do not yet exist or have been changed since the last time
                that execute() was invoked
            * Run all queries and return the results
        :param engine: engine to execute the sql statements
        :param sql_statements: dict of savepoint name to a sql statement.
            The savepoint name must exist
            The sql-statement must match the materialization and query of the savepoint.
        :return: The result of all savepoints with materialization type QUERY. A dictionary mapping
            the savepoint name to a List of tuples representing the rows that the queries returned.
        """
        # todo: store engine as part of __init__? advantage of having it as a parameter is that we can
        # switch DB, e.g. to the production DB at some point

        drop_statements = []  # drop table/view statements that should run first
        for name, previous_materialization in self.created:
            if name not in sql_statements:
                continue
            if not overwrite_existing and not self._has_changed(name):
                continue
            if previous_materialization == Materialization.TABLE:
                drop_statements.append(f'drop table if exists {quote_identifier(name)}')
            elif previous_materialization == Materialization.VIEW:
                drop_statements.append(f'drop view if exists {quote_identifier(name)}')

        filtered_statements = {}  # sql statements, without the statements that don't need to run again
        for name, sql in sql_statements.items():
            materialization = self._entries[name].base_node.materialization
            if not materialization.modifies_db or self._has_changed(name) or overwrite_existing:
                filtered_statements[name] = sql

        result = {}
        with engine.connect() as conn:
            with conn.begin() as transaction:
                # This is a bit fragile. Drop statements might fail if other objects (which we might not
                # consider) depend on a view/table. TODO: we need to do this smarter
                drop_sql = '; '.join(reversed(drop_statements))

                if drop_sql:
                    conn.execute(drop_sql)
                for name, sql in filtered_statements.items():
                    query_result = conn.execute(sql)

                    sql_model = self._entries[name].base_node
                    self._executed_statements[name] = ExecutedStatement(
                        name=name,
                        sql=sql,
                        materialization=sql_model.materialization,
                        node_hash=sql_model.hash
                    )

                    if sql_model.materialization == Materialization.QUERY:
                        # We return the combined result of all sql statements with QUERY materialization
                        # TODO: change format so it includes column names?
                        #  Perhaps return full pandas DFs, similar to what to_pandas() does?
                        result[name] = list(query_result)
                transaction.commit()
        return result

    def reset_executed_state(self):
        """
        todo: not needed?
        """
        # TODO: support checking the state in the database. Add an engine parameter and query which tables
        #  and views actually exists in the db??? Might be hard to detect changes tho
        self._executed_statements = {}


def get_virtual_node(references: Dict[str, SqlModel]) -> SqlModel:
    # TODO: move this to sqlmodel?
    # reference_sql is of form "{{ref_0}}, {{1}}, ..., {{n}}"
    reference_sql = ', '.join(f'{{{{{ref_name}}}}}' for ref_name in references.keys())
    sql = f'select * from {reference_sql}'
    return CustomSqlModel(name='virtual_node', sql=sql)\
        .set_materialization(Materialization.VIRTUAL_NODE)\
        .set_values(**references)\
        .instantiate()
