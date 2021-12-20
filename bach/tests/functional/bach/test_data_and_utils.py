"""
Copyright 2021 Objectiv B.V.

Utilities and a very simple dataset for testing Bach DataFrames.

This file does not contain any test, but having the file's name start with `test_` makes pytest treat it
as a test file. This makes pytest rewrite the asserts to give clearer errors.
"""
import os
from typing import List, Union, Type, Dict, Any

import pandas
import sqlalchemy
from sqlalchemy.engine import ResultProxy

from bach import DataFrame, Series
from bach.types import get_series_type_from_db_dtype

DB_TEST_URL = os.environ.get('OBJ_DB_TEST_URL', 'postgresql://objectiv:@localhost:5432/objectiv')

# Three data tables for testing are defined here that can be used in tests
# 1. cities: 3 rows (or 11 for the full dataset) of data on cities
# 2. food: 3 rows of food data
# 3. railways: 7 rows of data on railway stations

# cities is the main table and should be used when sufficient. The other tables can be used in addition
# for more complex scenarios (e.g. merging)

TEST_DATA_CITIES_FULL = [
    [1, 'Ljouwert', 'Leeuwarden', 93485, 1285],
    [2, 'Snits', 'Súdwest-Fryslân', 33520, 1456],
    [3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268],
    [4, 'Sleat', 'De Friese Meren', 700, 1426],
    [5, 'Starum', 'Súdwest-Fryslân', 960, 1061],
    [6, 'Hylpen', 'Súdwest-Fryslân', 870, 1225],
    [7, 'Warkum', 'Súdwest-Fryslân', 4440, 1399],
    [8, 'Boalsert', 'Súdwest-Fryslân', 10120, 1455],
    [9, 'Harns', 'Harlingen', 14740, 1234],
    [10, 'Frjentsjer', 'Waadhoeke', 12760, 1374],
    [11, 'Dokkum', 'Noardeast-Fryslân', 12675, 1298],
]
# The TEST_DATA set that we'll use in most tests is limited to 3 rows for convenience.
TEST_DATA_CITIES = TEST_DATA_CITIES_FULL[:3]
CITIES_COLUMNS = ['skating_order', 'city', 'municipality', 'inhabitants', 'founding']
# The default dataframe has skating_order as index, so that column will be prepended before the actual
# data in the query results.
CITIES_INDEX_AND_COLUMNS = ['_index_skating_order'] + CITIES_COLUMNS

TEST_DATA_FOOD = [
    [1, 'Sûkerbôlle', '2021-05-03 11:28:36.388', '2021-05-03'],
    [2, 'Dúmkes', '2021-05-04 23:28:36.388', '2021-05-04'],
    [4, 'Grutte Pier Bier', '2022-05-03 14:13:13.388', '2022-05-03']
]
FOOD_COLUMNS = ['skating_order', 'food', 'moment', 'date']
FOOD_INDEX_AND_COLUMNS = ['_index_skating_order'] + FOOD_COLUMNS

TEST_DATA_RAILWAYS = [
    [1, 'Drylts', 'IJlst', 1],
    [2, 'It Hearrenfean', 'Heerenveen', 1],
    [3, 'It Hearrenfean', 'Heerenveen IJsstadion', 2],
    [4, 'Ljouwert', 'Leeuwarden', 4],
    [5, 'Ljouwert', 'Camminghaburen', 1],
    [6, 'Snits', 'Sneek', 2],
    [7, 'Snits', 'Sneek Noord', 2],
]
RAILWAYS_COLUMNS = ['station_id', 'town', 'station', 'platforms']
RAILWAYS_INDEX_AND_COLUMNS = ['_index_station_id'] + RAILWAYS_COLUMNS

TEST_DATA_JSON = [
    [0,
     '{"a": "b"}',
     '[{"a": "b"}, {"c": "d"}]',
     '{"a": "b"}'
     ],
    [1,
     '{"_type": "SectionContext", "id": "home"}',
     '["a","b","c","d"]',
     '["a","b","c","d"]'
     ],
    [2,
     '{"a": "b", "c": {"a": "c"}}',
     '[{"_type": "a", "id": "b"},{"_type": "c", "id": "d"},{"_type": "e", "id": "f"}]',
     '{"a": "b", "c": {"a": "c"}}'
     ],
    [3,
     '{"a": "b", "e": [{"a": "b"}, {"c": "d"}]}',
     '[{"_type":"WebDocumentContext","id":"#document"},'
     ' {"_type":"SectionContext","id":"home"},'
     ' {"_type":"SectionContext","id":"top-10"},'
     ' {"_type":"ItemContext","id":"5o7Wv5Q5ZE"}]',
     '[{"_type":"WebDocumentContext","id":"#document"},'
     ' {"_type":"SectionContext","id":"home"},'
     ' {"_type":"SectionContext","id":"top-10"},'
     ' {"_type":"ItemContext","id":"5o7Wv5Q5ZE"}]'
     ]
]
JSON_COLUMNS = ['row', 'dict_column', 'list_column', 'mixed_column']
JSON_INDEX_AND_COLUMNS = ['_row_id'] + JSON_COLUMNS

# We cache all Bach DataFrames, that way we don't have to recreate and query tables each time.
_TABLE_DATAFRAME_CACHE: Dict[str, 'DataFrame'] = {}


def _get_bt(
        table: str,
        dataset: List[List[Any]],
        columns: List[str],
        convert_objects: bool
) -> DataFrame:
    # We'll just use the table as lookup key and ignore the other paramters, if we store different things
    # in the same table, then tests will be confused anyway
    lookup_key = table
    if lookup_key not in _TABLE_DATAFRAME_CACHE:
        import pandas as pd
        df = get_pandas_df(dataset, columns)
        _TABLE_DATAFRAME_CACHE[lookup_key] = get_from_df(table, df, convert_objects)
    # We don't even renew the 'engine', as creating the database connection takes a bit of time too. If
    # we ever do into trouble because of stale connection or something, then we can change it at that point
    # in time.
    return _TABLE_DATAFRAME_CACHE[lookup_key].copy_override()


def get_pandas_df(dataset: List[List[Any]], columns: List[str]) -> pandas.DataFrame:
    """ Convert the given dataset to a Pandas DataFrame """
    df = pandas.DataFrame.from_records(dataset, columns=columns)
    df.set_index(df.columns[0], drop=False, inplace=True)
    if 'moment' in df.columns:
        df['moment'] = df['moment'].astype('datetime64')
    if 'date' in df.columns:
        df['date'] = df['date'].astype('datetime64')
    return df


def get_from_df(table: str, df: pandas.DataFrame, convert_objects=True) -> DataFrame:
    """ Create a database table with the data from the data-frame. """
    engine = sqlalchemy.create_engine(DB_TEST_URL)

    print(DB_TEST_URL)
    buh_tuh = DataFrame.from_pandas(
        engine=engine,
        df=df,
        convert_objects=convert_objects,
        name=table,
        materialization='table',
        if_exists='replace'
    )
    return buh_tuh


def get_bt_with_test_data(full_data_set: bool = False) -> DataFrame:
    if full_data_set:
        return _get_bt('test_table_full', TEST_DATA_CITIES_FULL, CITIES_COLUMNS, True)
    return _get_bt('test_table_partial', TEST_DATA_CITIES, CITIES_COLUMNS, True)


def get_bt_with_food_data() -> DataFrame:
    return _get_bt('test_merge_table_1', TEST_DATA_FOOD, FOOD_COLUMNS, True)


def get_bt_with_railway_data() -> DataFrame:
    return _get_bt('test_merge_table_2', TEST_DATA_RAILWAYS, RAILWAYS_COLUMNS, True)


def get_bt_with_json_data(as_json=True) -> DataFrame:
    bt = _get_bt('test_json_table', TEST_DATA_JSON, JSON_COLUMNS, True)
    if as_json:
        bt['dict_column'] = bt.dict_column.astype('jsonb')
        bt['list_column'] = bt.list_column.astype('jsonb')
        bt['mixed_column'] = bt.mixed_column.astype('jsonb')
    return bt


def run_query(engine: sqlalchemy.engine, sql: str) -> ResultProxy:
    # escape sql, as conn.execute will think that '%' indicates a parameter
    sql = sql.replace('%', '%%')
    with engine.connect() as conn:
        res = conn.execute(sql)
        return res


def df_to_list(df):
    data_list = df.reset_index().to_numpy().tolist()
    return(data_list)


def assert_equals_data(
        bt: Union[DataFrame, Series],
        expected_columns: List[str],
        expected_data: List[list],
        order_by: Union[str, List[str]] = None,
        use_to_pandas: bool = False,
) -> List[List[Any]]:
    """
    Execute the sql of ButTuhDataFrame/Series's view_sql(), with the given order_by, and make sure the
    result matches the expected columns and data.

    Note: By default this does not call `to_pandas()`, which we nowadays consider our 'normal' path,
    but directly executes the result from `view_sql()`. To test `to_pandas()` set use_to_pandas=True.
    :return: the values queried from the database
    """
    if len(expected_data) == 0:
        raise ValueError("Cannot check data if 0 rows are expected.")

    if isinstance(bt, Series):
        # Otherwise sorting does not work as expected
        bt = bt.to_frame()

    if order_by:
        bt = bt.sort_values(order_by)

    if not use_to_pandas:
        column_names, db_values = _get_view_sql_data(bt)
    else:
        column_names, db_values = _get_to_pandas_data(bt)

    assert len(db_values) == len(expected_data)
    assert column_names == expected_columns
    for i, df_row in enumerate(db_values):
        expected_row = expected_data[i]
        assert df_row == expected_row, f'row {i} is not equal: {expected_row} != {df_row}'
    return db_values


def _get_view_sql_data(df: DataFrame):
    sql = df.view_sql()
    db_rows = run_query(df.engine, sql)
    column_names = list(db_rows.keys())
    db_values = [list(row) for row in db_rows]
    print(db_values)
    return column_names, db_values


def _get_to_pandas_data(df: DataFrame):
    pdf = df.to_pandas()
    # Convert pdf to the same format as _get_view_sql_data gives
    column_names = list(pdf.index.names) + list(pdf.columns)
    pdf.reset_index()
    db_values = []
    for index_row, value_row in zip(pdf.index.values.tolist(), pdf.values.tolist()):
        if isinstance(index_row, tuple):
            index_row = list(index_row)
        elif not isinstance(index_row, list):
            index_row = [index_row]
        db_values.append(index_row + value_row)
    print(db_values)
    return column_names, db_values


def assert_db_type(
        series: Series,
        expected_db_type: str,
        expected_series_type: Type[Series]
):
    """
    Check that the given Series has the expected data type in the database, and that it has the
    expected Series type after being read back from the database.
    :param series: Series object to check the type of
    :param expected_db_type: one of the types listed on https://www.postgresql.org/docs/current/datatype.html
    :param expected_series_type: Subclass of Series
    """
    sql = series.to_frame().view_sql()
    sql = f'with check_type as ({sql}) select pg_typeof("{series.name}") from check_type limit 1'
    db_rows = run_query(sqlalchemy.create_engine(DB_TEST_URL), sql)
    db_values = [list(row) for row in db_rows]
    db_type = db_values[0][0]
    if expected_db_type:
        assert db_type == expected_db_type
    series_type = get_series_type_from_db_dtype(db_type)
    assert series_type == expected_series_type
