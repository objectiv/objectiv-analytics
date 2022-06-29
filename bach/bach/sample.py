"""
Copyright 2021 Objectiv B.V.
"""
from typing import TYPE_CHECKING

from bach import DataFrame
from bach.dataframe import escape_parameter_characters
from bach.sql_model import SampleSqlModel
from sql_models.graph_operations import find_node, replace_node_in_graph
from sql_models.model import CustomSqlModelBuilder
from sql_models.sql_generator import to_sql
from sql_models.util import quote_identifier, is_postgres, is_bigquery, DatabaseNotSupportedException

if TYPE_CHECKING:
    from bach import SeriesBoolean


def get_sample(df: DataFrame,
               table_name: str,
               filter: 'SeriesBoolean' = None,
               sample_percentage: int = None,
               overwrite: bool = False,
               seed: int = None) -> 'DataFrame':
    """
    See :py:meth:`bach.DataFrame.get_sample` for more information.
    """
    dialect = df.engine.dialect

    if sample_percentage is None and filter is None:
        raise ValueError('Either sample_percentage or filter must be set')

    if sample_percentage is None and seed is not None:
        raise ValueError('`sample_percentage` must be set when using `seed`')

    if sample_percentage is not None and (sample_percentage < 0 or sample_percentage > 100):
        raise ValueError(f'sample_percentage must be in range 0-100. Actual value: {sample_percentage}')

    if seed and not is_postgres(dialect):
        message_override = f'The `seed` parameter is not supported for database dialect "{dialect.name}".'
        raise DatabaseNotSupportedException(dialect, message_override=message_override)

    original_node = df.base_node
    if filter is not None:
        sample_percentage = None
        from bach.series import SeriesBoolean
        if not isinstance(filter, SeriesBoolean):
            raise TypeError('Filter parameter needs to be a SeriesBoolean instance.')
        df = df[filter]

    if is_postgres(dialect):
        with df.engine.connect() as conn:
            if overwrite:
                sql = f'DROP TABLE IF EXISTS {quote_identifier(dialect, table_name)}'
                sql = escape_parameter_characters(conn, sql)
                conn.execute(sql)

            if sample_percentage:
                repeatable = f'repeatable ({seed})' if seed else ''

                sql = f'''
                    create temporary table tmp_table_name on commit drop as
                    ({to_sql(dialect, df.base_node)});
                    create temporary table {quote_identifier(dialect, table_name)} as
                    (select * from tmp_table_name
                    tablesample bernoulli({sample_percentage}) {repeatable})
                '''
            else:
                sql = f'create temporary table {quote_identifier(dialect, table_name)} as ({df.view_sql()})'
            sql = escape_parameter_characters(conn, sql)
            conn.execute(sql)
    elif is_bigquery(dialect):
        with df.engine.connect() as conn:
            if overwrite:
                sql = f'DROP TABLE IF EXISTS {quote_identifier(dialect, table_name)}'
                sql = escape_parameter_characters(conn, sql)
                conn.execute(sql)
            if sample_percentage:
                # BigQuery does support ` TABLESAMPLE SYSTEM({sample_percentage} PERCENT)`, but that
                # does not work on 'small' tables according to [1]:
                #       "Typically, BigQuery splits tables or table partitions into blocks if they are
                #       larger than about 1 GB. Smaller tables might consist of a single data block. In that
                #       case, the TABLESAMPLE clause reads the entire table"
                # We want reliable sampling for 'small' tables too, so we use RAND() instead.
                #
                # [1] https://cloud.google.com/bigquery/docs/table-sampling

                # TODO: supprort SeriesFloat64.get_random() or something like that, and use that instead of
                #   raw sql here
                # TODO: add function for creating tables directly in DataFrame.
                model_builder = CustomSqlModelBuilder(
                    sql='SELECT * FROM {{dataframe}} WHERE RAND() < {sample_cutoff}', name='filtered_model'
                )
                filtered_model = model_builder(dataframe=df.base_node, sample_cutoff=sample_percentage / 100)
                sql = f'''
                    CREATE TABLE {quote_identifier(dialect, table_name)} AS
                    ({to_sql(dialect, filtered_model)})
                '''

            else:
                sql = f'CREATE TABLE {quote_identifier(dialect, table_name)} AS ({df.view_sql()})'
            sql = escape_parameter_characters(conn, sql)
            conn.execute(sql)
    else:
        raise DatabaseNotSupportedException(dialect)

    # Use SampleSqlModel, that way we can keep track of the current_node and undo this sampling
    # in get_unsampled() by switching this new node for the old node again.
    new_base_node = SampleSqlModel.get_instance(
        dialect=dialect,
        table_name=table_name,
        previous=original_node,
        column_expressions=original_node.column_expressions,
    )
    return df.copy_override_base_node(base_node=new_base_node)


def get_unsampled(df: DataFrame) -> 'DataFrame':
    """
    See :py:meth:`bach.DataFrame.get_unsampled` for more information.
    """
    # The returned DataFrame has a modified base_node graph, in which the node that introduced the
    # sampling is removed.
    sampled_node_tuple = find_node(
        start_node=df.base_node,
        function=lambda node: isinstance(node, SampleSqlModel)
    )
    if sampled_node_tuple is None:
        raise ValueError('No sampled node found. Cannot un-sample data that has not been sampled.')

    # help mypy: sampled_node_tuple.model is guaranteed to be a SampleSqlModel, as that is what the
    # filter function for find_node() above filtered on
    assert isinstance(sampled_node_tuple.model, SampleSqlModel)

    updated_graph = replace_node_in_graph(
        start_node=df.base_node,
        reference_path=sampled_node_tuple.reference_path,
        replacement_model=sampled_node_tuple.model.previous
    )
    return df.copy_override_base_node(base_node=updated_graph)
