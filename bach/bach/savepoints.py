"""
Copyright 2021 Objectiv B.V.
"""
import re
from typing import Dict, NamedTuple, TYPE_CHECKING, List, Tuple

from sqlalchemy.engine import Engine

from sql_models.model import Materialization, SqlModel, CustomSqlModel
from sql_models.sql_generator import to_sql_materialized_nodes
from sql_models.util import quote_identifier

if TYPE_CHECKING:
    from bach import DataFrame


class Entry(NamedTuple):
    """
    INTERNAL: class to represent a savepoint in the Savepoints class
    """
    # todo: don't need to track this anymore, just the df is enough?
    name: str
    df: 'DataFrame'
    materialization: Materialization


class ExecutedStatement(NamedTuple):
    """
    INTERNAL: class to represent a savepoint in the Savepoints class
    """
    name: str
    sql: str
    materialization: Materialization


class Savepoints:

    def __init__(self):
        self._entries: Dict[str, Entry] = {}
        self._executed_statements: Dict[str, ExecutedStatement] = {}


    @property
    def created(self) -> List[Tuple[str, Materialization]]:
        return reversed([
            (name, exec_statement.materialization)
            for name, exec_statement in self._executed_statements.items()
            if self._executed_statements[name].materialization.modifies_db
        ])

    @property
    def tables_created(self) -> List[str]:
        return reversed(
            name for name in self._executed_statements.keys()
            if self._executed_statements[name].materialization == Materialization.TABLE
        )

    @property
    def views_created(self) -> List[str]:
        return reversed(
            name for name in self._executed_statements.keys()
            if self._executed_statements[name].materialization == Materialization.VIEW
        )

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

        entry = Entry(
            name=name,
            df=df_copy,
            materialization=materialization,
        )
        self._entries[name] = entry
        # TODO: should we execute the

    def get_df(self, savepoint_name: str) -> 'DataFrame':
        return self._entries[savepoint_name].df.copy()

    def to_sql(self, savepoint_names: List[str] = None) -> Dict[str, str]:
        """
        Generate the sql for all save-points

        :return: dictionary mapping the name of each savepoint to the sql for that savepoint.
        """
        references: Dict[str, SqlModel] = {
            f'ref_{name}': entry.df.base_node for name, entry in self._entries.items()
            if savepoint_names is None or name in savepoint_names
        }
        # TODO: move this to sqlmodel?
        graph = get_virtual_node(references)
        sqls = to_sql_materialized_nodes(start_node=graph, include_start_node=False)
        return sqls

    def execute(self, engine: Engine, savepoint_names: List[str] = None) -> Dict[str, List[tuple]]:
        """
        Execute the savepoints:
            * Create all tables and views that do not yet exist or have been changed since the last time
                that execute() was invoked
            * Run all queries and return the results
        :param engine: engine to execute the sql statements
        :return: The result of all savepoints with materialization type QUERY. A dictionary mapping
            the savepoint name to a List of tuples representing the rows that the queries returned.
        """
        # todo: store engine as part of __init__?
        # todo: support removing created views/tables that have been created but have changed later
        sql_statements = self.to_sql(savepoint_names)
        return self._execute_sql(engine, sql_statements)

    def _execute_sql(self, engine: Engine, sql_statements: Dict[str, str]) -> Dict[str, List[tuple]]:
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
        # todo: store engine as part of __init__?
        # todo: support removing created views/tables that have been created but have changed later
        result = {}
        with engine.connect() as conn:
            with conn.begin() as transaction:
                for name, sql in sql_statements.items():
                    materialization = self._entries[name].materialization
                    if materialization.modifies_db:
                        # sql is a non-idempotent statement
                        if name not in self._executed_statements or \
                                not self._executed_statements[name].materialization.modifies_db:
                            # First time we execute this statement, or previously it didn't modifiy the db
                            conn.execute(sql)
                        elif self._executed_statements[name].sql != sql:
                            previous_materialization = self._executed_statements[name].materialization
                            # The SQL has changed: drop old table/view and recreate
                            if previous_materialization == Materialization.TABLE:
                                drop_create_sql = f'drop table if exists {quote_identifier(name)}; {sql}'
                            elif previous_materialization == Materialization.VIEW:
                                drop_create_sql = f'drop view if exists {quote_identifier(name)}; {sql}'
                            else:
                                raise Exception(f'Materialization not supported: {materialization}')
                            conn.execute(drop_create_sql)
                        self._executed_statements[name] = \
                            ExecutedStatement(name=name, sql=sql, materialization=materialization)
                    else:
                        # sql is an idempotent statement
                        query_result = conn.execute(sql)
                        if materialization == Materialization.QUERY:
                            # We return the combined result of all sql statements with QUERY materialization
                            # TODO: change format so it includes column names?
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
