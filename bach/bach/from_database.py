"""
Copyright 2022 Objectiv B.V.
"""
from typing import Dict

from sqlalchemy.engine import Engine

from bach.types import get_dtype_from_db_dtype
from bach.utils import escape_parameter_characters
from sql_models.constants import DBDialect
from sql_models.model import SqlModel, CustomSqlModelBuilder
from sql_models.sql_generator import to_sql
from sql_models.util import is_postgres, DatabaseNotSupportedException


def get_dtypes_from_model(engine: Engine, node: SqlModel) -> Dict[str, str]:
    """ Create a temporary database table from model and use it to deduce the model's dtypes. """
    if not is_postgres(engine):
        raise DatabaseNotSupportedException(engine)
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


def get_dtypes_from_table(engine: Engine, table_name: str) -> Dict[str, str]:
    """ Query database to get dtypes of the given table. """
    # using `INFORMATION_SCHEMA.COLUMNS` in capitals, as that way it works on both Postgres and BigQuery
    sql = f"""
        select column_name, data_type
        from INFORMATION_SCHEMA.COLUMNS
        where table_name = '{table_name}'
        order by ordinal_position;
    """
    return _get_dtypes_from_information_schema_query(engine=engine, query=sql)


def _get_dtypes_from_information_schema_query(engine: Engine, query: str) -> Dict[str, str]:
    """ Parse information_schema.columns to dtypes. """
    with engine.connect() as conn:
        sql = escape_parameter_characters(conn, query)
        res = conn.execute(sql)
        rows = res.fetchall()

    db_dialect = DBDialect.from_engine(engine)
    return {row[0]: get_dtype_from_db_dtype(db_dialect, row[1]) for row in rows}
