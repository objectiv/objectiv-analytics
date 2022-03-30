"""
Copyright 2022 Objectiv B.V.

tests for:
 * DataFrame.from_table()
 * DataFrame.from_model()

"""
import sqlalchemy
from sqlalchemy.engine import Engine

from bach import DataFrame
from sql_models.model import CustomSqlModelBuilder, SqlModel
from sql_models.util import is_postgres, is_bigquery
from tests.functional.bach.test_data_and_utils import DB_TEST_URL


def _create_test_table(engine: Engine, table_name: str):
    if is_postgres(engine):
        sql = f'drop table if exists {table_name}; ' \
              f'create table {table_name}(a bigint, b text, c double precision, d date, e timestamp); '
    elif is_bigquery(engine):
        sql = f'drop table if exists {table_name}; ' \
              f'create table {table_name}(a int64, b string, c float64, d date, e datetime); '
    else:
        raise Exception('Incomplete tests')
    with engine.connect() as conn:
        conn.execute(sql)


def test_from_table_basic(engine):
    table_name = 'test_df_from_table'
    _create_test_table(engine, table_name)

    df = DataFrame.from_table(engine=engine, table_name=table_name, index=['a'])
    assert df.index_dtypes == {'a': 'int64'}
    assert df.dtypes == {'b': 'string', 'c': 'float64', 'd': 'date', 'e': 'timestamp'}
    assert df.is_materialized
    assert df.base_node.columns == ('a', 'b', 'c', 'd', 'e')
    # there should only be a single model that selects from the table, not a whole tree
    # todo: in the future introduce a special SqlModel type 'source', so we don't even need a first model
    # with a query and we can just query directly from the source table.
    assert df.base_node.references == {}
    df.to_pandas()  # test that the main function works on the created DataFrame

    # now create same DataFrame, but specify all_dtypes.
    df_all_dtypes = DataFrame.from_table(
        engine=engine, table_name=table_name, index=['a'],
        all_dtypes={'a': 'int64', 'b': 'string', 'c': 'float64', 'd': 'date', 'e': 'timestamp'}
    )
    assert df == df_all_dtypes


def test_from_model_basic():
    # This is essentially the same test as test_from_table_basic(), but tests creating the dataframe with
    # from_model instead of from_table
    engine = sqlalchemy.create_engine(DB_TEST_URL)
    table_name = 'test_df_from_table'
    _create_test_table(engine, table_name)
    sql_model: SqlModel = CustomSqlModelBuilder(sql=f'select * from {table_name}')()

    df = DataFrame.from_model(engine=engine, model=sql_model, index=['a'])
    assert df.index_dtypes == {'a': 'int64'}
    assert df.dtypes == {'b': 'string', 'c': 'float64', 'd': 'date', 'e': 'timestamp'}
    assert df.is_materialized
    assert df.base_node.columns == ('a', 'b', 'c', 'd', 'e')
    # there should only be a single model that selects from the table, not a whole tree
    # todo: in the future introduce a special SqlModel type 'source', so we don't even need a first model
    # with a query and we can just query directly from the source table.
    assert df.base_node.references == {}
    df.to_pandas()  # test that the main function works on the created DataFrame

    # now create same DataFrame, but specify all_dtypes.
    df_all_dtypes = DataFrame.from_model(
        engine=engine, model=sql_model, index=['a'],
        all_dtypes={'a': 'int64', 'b': 'string', 'c': 'float64', 'd': 'date', 'e': 'timestamp'}
    )
    assert df == df_all_dtypes


def test_from_table_column_ordering(engine):
    # Create a Dataframe in which the index is not the first column in the table.
    table_name = 'test_df_from_table'
    _create_test_table(engine, table_name)

    df = DataFrame.from_table(engine=engine, table_name=table_name, index=['b'])
    assert df.index_dtypes == {'b': 'string'}
    assert df.dtypes == {'a': 'int64', 'c': 'float64', 'd': 'date', 'e': 'timestamp'}
    assert df.is_materialized
    # We should have an extra model in the sql-model graph, because 'b' is the index and should thus be the
    # first column.
    assert df.base_node.columns == ('b', 'a', 'c', 'd', 'e')
    assert 'prev' in df.base_node.references
    assert df.base_node.references['prev'].references == {}
    df.to_pandas()  # test that the main function works on the created DataFrame

    df_all_dtypes = DataFrame.from_table(
        engine=engine, table_name=table_name, index=['b'],
        all_dtypes={'a': 'int64', 'b': 'string', 'c': 'float64', 'd': 'date', 'e': 'timestamp'}
    )
    assert df == df_all_dtypes


def test_from_model_column_ordering():
    # This is essentially the same test as test_from_table_model_ordering(), but tests creating the dataframe with
    # from_model instead of from_table

    # Create a Dataframe in which the index is not the first column in the table.
    engine = sqlalchemy.create_engine(DB_TEST_URL)
    table_name = 'test_df_from_table'
    _create_test_table(engine, table_name)
    sql_model: SqlModel = CustomSqlModelBuilder(sql=f'select * from {table_name}')()

    df = DataFrame.from_model(engine=engine, model=sql_model, index=['b'])
    assert df.index_dtypes == {'b': 'string'}
    assert df.dtypes == {'a': 'int64', 'c': 'float64', 'd': 'date', 'e': 'timestamp'}
    assert df.is_materialized
    # We should have an extra model in the sql-model graph, because 'b' is the index and should thus be the
    # first column.
    assert df.base_node.columns == ('b', 'a', 'c', 'd', 'e')
    assert 'prev' in df.base_node.references
    assert df.base_node.references['prev'].references == {}
    df.to_pandas()  # test that the main function works on the created DataFrame

    df_all_dtypes = DataFrame.from_model(
        engine=engine, model=sql_model, index=['b'],
        all_dtypes={'a': 'int64', 'b': 'string', 'c': 'float64', 'd': 'date', 'e': 'timestamp'}
    )
    assert df == df_all_dtypes
