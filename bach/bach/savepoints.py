"""
Copyright 2021 Objectiv B.V.
"""
import re
from typing import NamedTuple, Dict, List, Union, cast

from sqlalchemy.engine import Engine, Dialect

from bach import DataFrame
from bach.sql_model import BachSqlModel
from sql_models.model import Materialization, SqlModel, CustomSqlModelBuilder
from sql_models.sql_generator import to_sql_materialized_nodes, GeneratedSqlStatement
from sql_models.util import quote_identifier


class SavepointEntry(NamedTuple):
    """
    Class to represent a savepoint
    """
    name: str
    df_original: 'DataFrame'
    materialization: Materialization


class CreatedObject(NamedTuple):
    """
    Class representing a created database object (view/table)
    """
    name: str
    materialization: Materialization


class Savepoints:
    """
    Class to store a collection of savepoints. A savepoint represents the state of a DataFrame instance at
    the moment it is being added to a Savepoints object.

    Functionality:
    - Convert the savepoints to SQL using :meth:`Savepoints.to_sql()`
    - Materialize as tables or views in a database using :meth:`Savepoints.write_to_databse()`.
    - TODO: serialize to a file, and later restored by deserializing
    - TODO: export as a DBT project
    - TODO: export to BI tools
    """

    def __init__(self):
        self._entries: Dict[str, SavepointEntry] = {}

    @property
    def all(self) -> List[SavepointEntry]:
        return list(self._entries.values())

    @property
    def names(self) -> List[str]:
        return [entry.name for entry in self._entries.values()]

    def merge(self, other: 'Savepoints'):
        """
        INTERNAL
        Update this Savepoints object by adding all savepoints from other.
        """
        for name, entry in other._entries.items():
            if name in self._entries:
                existing = self._entries[name]
                if existing.df_original != entry.df_original \
                        or existing.materialization != entry.materialization:
                    raise ValueError(f'Conflicting savepoints. The savepoint "{name}" exists in both '
                                     f'Savepoints objects, but is different.')
            else:
                self._entries[name] = SavepointEntry(
                    name=name,
                    df_original=entry.df_original.copy(),
                    materialization=entry.materialization,
                )

    def add_savepoint(self, name: str, df: DataFrame, materialization: Materialization):
        """
        Add the DataFrame as a savepoint.

        Generally one would use :py:meth:`bach.DataFrame.set_savepoint()`
        """
        if name is None or not re.match('^[a-zA-Z0-9_]+$', name):
            raise ValueError(f'Name must match ^[a-zA-Z0-9_]+$, name: "{name}"')
        if name in self._entries:
            existing = self._entries[name]
            if existing.df_original != df or existing.materialization != materialization:
                raise ValueError(f'A different savepoint with the name "{name}" already exists.')
            # Nothing to do, we already have this entry
            return
        if not df.is_materialized:
            raise ValueError('Can only create a savepoint from materialized DataFrames.')
        existing_basenodes = {entry.df_original.base_node: entry.name for entry in self._entries.values()}
        if df.base_node in existing_basenodes:
            # We cannot support having the same base_node as multiple savepoints. This will give problems
            # if the different savepoints have different materialization
            raise ValueError(f'Another savepoint has the same base_node, not allowed. Other savepont: '
                             f'{existing_basenodes[df.base_node]}')

        self._entries[name] = SavepointEntry(
            name=name,
            df_original=df.copy(),
            materialization=materialization
        )

    def set_materialization(self, name: str, materialization: Union[Materialization, str]):
        """
        Set the materialization of a savepoint, prior to calling :meth:`write_to_db()`. Calling this function
        does not materialize anything to the database by itself.

        NOTE: This alos does not undo any side-effects from earlier called functions, such as
            :meth:`write_to_db()` i.e. if materialization was 'table' before and is changed to 'view', then
            an existing table in the database is not updated into a view.

        :param name: name of savepoint
        :param materialization: materialization value
        """
        materialization = Materialization.normalize(materialization)
        current = self._entries[name]
        if current.materialization == materialization:
            return
        self._entries[name] = SavepointEntry(
            name=current.name,
            df_original=current.df_original,
            materialization=materialization
        )

    def remove_savepoint(self, name: str):
        """
        Discard the savepoint.
        NOTE: This does not undo any side-effects from earlier called function, such as :meth:`write_to_db()`
        """
        del self._entries[name]

    def get_df(self, savepoint_name: str) -> 'DataFrame':
        """
        Return a copy of the original DataFrame that was saved with the given name.
        """
        return self._entries[savepoint_name].df_original.copy()

    def get_materialized_df(self, savepoint_name: str, engine_override: Engine = None) -> 'DataFrame':
        """
        Return the DataFrame that was saved with the given name, but with an updated base_node.
        The updated base_node assumes that :meth:`write_to_db()` has been executed. Where possible it
        will query one of the created tables or views, instead of the original source tables.
        :param savepoint_name: name of the savepoint
        :param engine_override: optional, allows overriding the 'engine' of the returned dataframe. This is
            useful if the savepoints were persisted to a different database than from which they originally
            came (typically if write_to_db() was invoked with a different `engine` argument than the
            original_df's engine).
        """
        info = self._entries[savepoint_name]
        full_graph = self._get_combined_graph()
        graph = full_graph.references[f'ref_{info.name}']
        bach_graph = cast(BachSqlModel, graph)  # help mypy, see _get_virtual_node() for why this is correct
        new_df = info.df_original.copy_override_base_node(base_node=bach_graph)
        if engine_override is not None:
            new_df = new_df.copy_override(engine=engine_override)
        return new_df

    def write_to_db(self, engine_override: Engine = None, overwrite: bool = False) -> List[CreatedObject]:
        """
        Create the tables and views for all of the savepoints that have a table or view materialization.

        :param engine_override: optional. If not set this will use the engine of the original dataframes in
            the savepoints. If the savepoints do not all share the same engine, then this parameter is
            mandatory.
        :param overwrite: If true, drop table/view statements will be run first
        :return: List of all created objects
        """
        if not self._entries:
            return []  # nothing to do
        if engine_override:
            engine = engine_override
        else:
            engines = {entry.df_original.engine for entry in self._entries.values()}
            if len(engines) != 1:
                raise ValueError("engine_override cannot be None if the savepoints's entries don't all "
                                 "share the same engine.")
            engine = list(engines)[0]
        result_created = []
        drop_statements = self.get_drop_statements(dialect=engine.dialect)
        create_statements = self.get_create_statements(dialect=engine.dialect)

        with engine.connect() as conn:
            with conn.begin() as transaction:
                if overwrite:
                    # This is a bit fragile. Drop statements might fail if other objects (which we might not
                    # consider) depend on a view/table, or if the object type (view/table) is different than
                    # we assume. For now that's just the way it is, the user will get an error.
                    if drop_statements:
                        drop_sql = '; '.join(drop_statements.values())
                        conn.execute(drop_sql)

                for name, statement in create_statements.items():
                    info = self._entries[name]
                    conn.execute(statement)
                    result_created.append(CreatedObject(name=name, materialization=info.materialization))
                transaction.commit()
        return result_created

    def get_drop_statements(self, dialect: Dialect) -> Dict[str, str]:
        """
        Get the drop statements to remove all savepoints that are marked as table or view.
        The returned dictionary is sorted, such that depending tables/views are deleted before dependencies.
        :param dialect: SQL Dialect
        :return: dict with as key the savepoint name, and as value the drop statement for that table/view
        """
        sql_statements = self.to_sql(dialect)
        drop_statements = {}
        for sql_stat in reversed(sql_statements):
            name = sql_stat.name
            if sql_stat.materialization == Materialization.TABLE:
                drop_statements[name] = f'drop table if exists {quote_identifier(dialect, name)}'
            elif sql_stat.materialization == Materialization.VIEW:
                drop_statements[name] = f'drop view if exists {quote_identifier(dialect, name)}'
        return drop_statements

    def get_create_statements(self, dialect: Dialect) -> Dict[str, str]:
        """
        Get the create statements to create savepoints that are marked as table or view.
        The returned dictionary is sorted, such that dependencies are created before tables/views that
        depend on them.
        :param dialect: SQL Dialect
        :return: dict with as key the savepoint name, and as value the create statement for that table/view
        """
        sql_statements = self.to_sql(dialect)
        return {
            sql_stat.name: sql_stat.sql for sql_stat in sql_statements
            if sql_stat.materialization in (Materialization.TABLE, Materialization.VIEW)
        }

    def to_sql(self, dialect: Dialect) -> List[GeneratedSqlStatement]:
        """
        Generate the sql for all save-points
        :param dialect: SQL Dialect
        :return: List of GeneratedSqlStatement, each representing one savepoint
        """
        graph = self._get_combined_graph()
        sqls = to_sql_materialized_nodes(dialect=dialect, start_node=graph, include_start_node=False)
        return sqls

    def _get_combined_graph(self) -> SqlModel:
        """
        Get a single graph that contains all savepoints.

        The savepoints are referred by the returned sql-model as 'ref_{name}'.
        """
        entries = list(self._entries.values())
        references: Dict[str, BachSqlModel] = {
            f'ref_{entry.name}': entry.df_original.base_node for entry in entries
        }
        # Create one graph with all entries
        graph = _get_virtual_node(references)

        # Now update all the nodes that represent an entry, to have the correct materialization
        for entry in entries:
            reference_path = (f'ref_{entry.name}', )
            graph = graph.set_materialization_name(reference_path, materialization_name=entry.name)
            graph = graph.set_materialization(reference_path, materialization=entry.materialization)
        return graph

    def __str__(self) -> str:
        """ Give string with overview of all savepoints per materialization. """
        tables = [entry for entry in self.all if entry.materialization == Materialization.TABLE]
        views = [entry for entry in self.all if entry.materialization == Materialization.VIEW]
        others = [entry for entry in self.all if entry.materialization
                  not in (Materialization.TABLE, Materialization.VIEW)]
        result = [f'Savepoint, entries: {len(self.all)}']

        result.append(f'\tTables, entries: {len(tables)}')
        for table in tables:
            result.append(f'\t\t{table.name}')

        result.append(f'\tViews, entries: {len(views)}')
        for view in views:
            result.append(f'\t\t{view.name}')

        result.append(f'\tOther, entries: {len(others)}')
        for other in others:
            result.append(f'\t\t{other.name}')

        string = '\n'.join(result)
        return string


def _get_virtual_node(references: Dict[str, BachSqlModel]) -> SqlModel:
    # TODO: move this to sqlmodel?
    # reference_sql is of form "{{ref_0}}, {{1}}, ..., {{n}}"
    reference_sql = ', '.join(f'{{{{{ref_name}}}}}' for ref_name in references.keys())
    sql = f'select * from {reference_sql}'
    return CustomSqlModelBuilder(name='virtual_node', sql=sql)\
        .set_materialization(Materialization.VIRTUAL_NODE)\
        .set_values(**references)\
        .instantiate()
