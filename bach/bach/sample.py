"""
Copyright 2021 Objectiv B.V.
"""
from typing import TYPE_CHECKING

from bach import DataFrame
from bach.dataframe import escape_parameter_characters
from bach.sql_model import SampleSqlModel
from sql_models.graph_operations import find_node, replace_node_in_graph
from sql_models.model import CustomSqlModelBuilder, Materialization
from sql_models.sql_generator import to_sql
from sql_models.util import quote_identifier, is_postgres, is_bigquery, DatabaseNotSupportedException

if TYPE_CHECKING:
    from bach import SeriesBoolean


def get_sample(df: DataFrame,
               table_name: str,
               filter: 'SeriesBoolean' = None,
               sample_percentage: int = None,
               *,
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

    if seed is not None and not is_postgres(dialect):
        message_override = f'The `seed` parameter is not supported for database dialect "{dialect.name}".'
        raise DatabaseNotSupportedException(dialect, message_override=message_override)

    if not df.is_materialized:
        df = df.materialize('get_sample')

    original_node = df.base_node
    if filter is not None:
        sample_percentage = None
        from bach.series import SeriesBoolean
        if not isinstance(filter, SeriesBoolean):
            raise TypeError('Filter parameter needs to be a SeriesBoolean instance.')
        df = df[filter]
    if sample_percentage is not None:
        if seed is not None:
            # We'll use `tablesample bernoulli` with `repeatable`. This can only be used when selecting from
            # a table, so we have to take some extra steps:
            # 1. Materializes the state of the DataFrame as a temporary table
            # 2. Get SqlModel that queries that temporary table with `tablesample`
            # 3. Build a new DataFrame that uses the model from step 2 as base_node.
            temp_table_model = original_node.copy_set_materialization(Materialization.TEMP_TABLE)
            model_builder = CustomSqlModelBuilder(
                sql='select * from {{table}} tablesample bernoulli({sample_percentage}) repeatable ({seed})',
                name='get_sample'
            )
            model = model_builder(table=temp_table_model, sample_percentage=sample_percentage, seed=seed)

            all_dtypes = {**df.index_dtypes, **df.dtypes}
            df = DataFrame.from_model(
                engine=df.engine,
                model=model,
                index=df.index_columns,
                all_dtypes=all_dtypes
            )
        else:
            # We use random floats for the row selection. This works cross database unlike
            # `tablesample bernoulli`, which is not supported on BigQuery[1]. Additionally, this is simpler
            # and doesn't require us to create a temporary table like `tablesample` does.
            from bach import SeriesFloat64
            sample_cutoff = sample_percentage / 100
            df = df[SeriesFloat64.random(base=df) < sample_cutoff]
    if_exists = 'replace' if overwrite else 'fail'
    df.database_create_table(table_name=table_name, if_exists=if_exists)

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
