"""
Copyright 2022 Objectiv B.V.
"""
from typing import Dict, Optional

from sqlalchemy.engine import Engine

from bach.types import get_dtype_from_db_dtype, StructuredDtype
from bach.utils import escape_parameter_characters
from sql_models.constants import DBDialect
from sql_models.model import SqlModel, CustomSqlModelBuilder
from sql_models.sql_generator import to_sql
from sql_models.util import is_postgres, DatabaseNotSupportedException, is_bigquery


def get_dtypes_from_model(engine: Engine, node: SqlModel) -> Dict[str, StructuredDtype]:
    """ Create a temporary database table from model and use it to deduce the model's dtypes. """
    if not is_postgres(engine):
        message_override = f'We cannot automatically derive dtypes from a SqlModel for database ' \
                           f'dialect "{engine.name}".'
        raise DatabaseNotSupportedException(engine, message_override=message_override)
    new_node = CustomSqlModelBuilder(sql='select * from {{previous}} limit 0')(previous=node)
    select_statement = to_sql(dialect=engine.dialect, model=new_node)
    sql = f"""
        create temporary table tmp_table_name on commit drop as
        ({select_statement});
        select column_name, data_type
        from information_schema.columns
        where table_name = 'tmp_table_name'
        order by ordinal_position;
    """
    return _get_dtypes_from_information_schema_query(engine=engine, query=sql)


def get_dtypes_from_table(
    engine: Engine,
    table_name: str,
    *,
    bq_dataset: Optional[str] = None,
    bq_project_id: Optional[str] = None
) -> Dict[str, StructuredDtype]:
    """
    Query database to get dtypes of the given table.
    :param engine: sqlalchemy engine for the database.
    :param table_name: the table name for which to get the dtypes
    :param bq_dataset: BigQuery-only. Dataset in which the table resides, if different from engine.url
    :param bq_project_id: BigQuery-only. Project of dataset, if different from engine.url
    :return: Dictionary with as key the column names of the table, and as values the dtype of the column.
    """
    if bq_project_id and not bq_dataset:
        raise ValueError('Cannot specify bq_project_id without setting bq_dataset.')
    if bq_dataset and not is_bigquery(engine):
        raise ValueError('bq_dataset is a BigQuery-only option.')

    if is_postgres(engine):
        meta_data_table = 'INFORMATION_SCHEMA.COLUMNS'
    elif is_bigquery(engine):
        meta_data_table = 'INFORMATION_SCHEMA.COLUMNS'
        if bq_dataset:
            meta_data_table = f'{bq_dataset}.{meta_data_table}'
        if bq_project_id:
            meta_data_table = f'{bq_project_id}.{meta_data_table}'
    else:
        raise DatabaseNotSupportedException(engine)
    sql = f"""
        select column_name, data_type
        from {meta_data_table}
        where table_name = '{table_name}'
        order by ordinal_position;
    """
    return _get_dtypes_from_information_schema_query(engine=engine, query=sql)


def _get_dtypes_from_information_schema_query(engine: Engine, query: str) -> Dict[str, StructuredDtype]:
    """ Parse information_schema.columns to dtypes. """
    with engine.connect() as conn:
        sql = escape_parameter_characters(conn, query)
        res = conn.execute(sql)
        rows = res.fetchall()

    db_dialect = DBDialect.from_engine(engine)
    return {row[0]: get_dtype_from_db_dtype(db_dialect, row[1]) for row in rows}
