"""
Copyright 2021 Objectiv B.V.

Tests for BuhTuhDataFrame using a very simple dataset.

"""
import os
from typing import List, Union

import pytest
import sqlalchemy
from sqlalchemy.engine import ResultProxy

from buhtuh import BuhTuhDataFrame, BuhTuhSeries, BuhTuhSeriesBoolean


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


def _get_bt(table, dataset, columns) -> BuhTuhDataFrame:
    engine = sqlalchemy.create_engine(DB_TEST_URL)
    import pandas as pd
    df = pd.DataFrame.from_records(dataset, columns=columns)
    # by default the strings are marked as 'object' not as string type, fix that:
    df = df.convert_dtypes()

    df.set_index(columns[0], drop=False, inplace=True)
    # I'm not so sure about this one. Int64 columns as an index becomes 'Object' for which we have no decent Series type
    # let's restore it to what it whas when it was still a column.
    df.index = df.index.astype('int64')

    if 'moment' in df.columns:
        df['moment'] = df['moment'].astype('datetime64')

    if 'date' in df.columns:
        df['date'] = df['date'].astype('datetime64')

    buh_tuh = BuhTuhDataFrame.from_dataframe(df, table, engine, if_exists='replace')
    return buh_tuh


def get_bt_with_test_data(full_data_set: bool = False) -> BuhTuhDataFrame:
    if full_data_set:
        test_data = TEST_DATA_CITIES_FULL
    else:
        test_data = TEST_DATA_CITIES
    return _get_bt('test_table', test_data, CITIES_COLUMNS)


def get_bt_with_food_data() -> BuhTuhDataFrame:
    return _get_bt('test_merge_table_1', TEST_DATA_FOOD, FOOD_COLUMNS)


def get_bt_with_railway_data() -> BuhTuhDataFrame:
    return _get_bt('test_merge_table_2', TEST_DATA_RAILWAYS, RAILWAYS_COLUMNS)


def run_query(engine: sqlalchemy.engine, sql: str) -> ResultProxy:
    with engine.connect() as conn:
        res = conn.execute(sql)
        return res


def assert_equals_data(
        bt: Union[BuhTuhDataFrame, BuhTuhSeries],
        expected_columns: List[str],
        expected_data: List[list],
        order_by: Union[str, List[str]] = None
):
    """
    Execute sql of ButTuhDataFrame/Series, with the given order_by, and make sure the result matches
    the expected columns and data.
    """
    if len(expected_data) == 0:
        raise ValueError("Cannot check data if 0 rows are expected.")

    if order_by:
        bt = bt.sort_values(order_by)
    sql = bt.view_sql()
    db_rows = run_query(bt.engine, sql)
    column_names = list(db_rows.keys())
    db_values = [list(row) for row in db_rows]
    print(db_values)

    assert len(db_values) == len(expected_data)
    assert column_names == expected_columns
    for i, df_row in enumerate(db_values):
        expected_row = expected_data[i]
        assert df_row == expected_row, f'row {i} is not equal: {expected_row} != {df_row}'


def df_to_list(df):
    data_list = df.reset_index().to_numpy().tolist()
    return(data_list)


def test_del_item():
    bt = get_bt_with_test_data()

    del(bt['founding'])
    assert 'founding' not in bt.data.keys()
    with pytest.raises(KeyError):
        bt.founding

    with pytest.raises(KeyError):
        del(bt['non existing column'])


def test_sort_values():
    bt = get_bt_with_test_data(full_data_set=True)
    kwargs_list = [{'by': 'city'},
                   {'by': ['municipality', 'city']},
                   {'by': ['municipality', 'city'], 'ascending': False},
                   {'by': ['municipality', 'city'], 'ascending': [False, True]},
                   ]
    for kwargs in kwargs_list:
        assert_equals_data(
            bt.sort_values(**kwargs),
            expected_columns=['_index_skating_order', 'skating_order', 'city', 'municipality', 'inhabitants',
                              'founding'],
            expected_data=df_to_list(bt.to_df().sort_values(**kwargs))
        )


def test_combined_operations1():
    bt = get_bt_with_test_data(full_data_set=True)
    bt['x'] = bt['municipality'] + ' some string'
    bt['y'] = bt['skating_order'] + bt['skating_order']
    result_bt = bt.groupby('x')['y'].count()
    print(result_bt.view_sql())
    assert_equals_data(
        result_bt,
        order_by='x',
        expected_columns=['x', 'y_count'],
        expected_data=[
            ['De Friese Meren some string', 1],
            ['Harlingen some string', 1],
            ['Leeuwarden some string', 1],
            ['Noardeast-Fryslân some string', 1],
            ['Súdwest-Fryslân some string', 6],
            ['Waadhoeke some string', 1],
        ]
    )

    result_bt['z'] = result_bt['y_count'] + 10
    result_bt['y_count'] = result_bt['y_count'] + (-1)
    assert_equals_data(
        result_bt,
        order_by='x',
        expected_columns=['x', 'y_count', 'z'],
        expected_data=[
            ['De Friese Meren some string', 0, 11],
            ['Harlingen some string', 0, 11],
            ['Leeuwarden some string', 0, 11],
            ['Noardeast-Fryslân some string', 0, 11],
            ['Súdwest-Fryslân some string', 5, 16],
            ['Waadhoeke some string', 0, 11],
        ]
    )
    assert result_bt.y_count == result_bt['y_count']


def test_boolean_indexing_same_node():
    bt = get_bt_with_test_data(full_data_set=True)
    bti = bt['founding'] < 1300
    assert isinstance(bti, BuhTuhSeriesBoolean)
    result_bt = bt[bti]
    assert isinstance(result_bt, BuhTuhDataFrame)
    assert_equals_data(
        result_bt,
        expected_columns=['_index_skating_order', 'skating_order', 'city', 'municipality', 'inhabitants',
                          'founding'],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268],
            [5, 5, 'Starum', 'Súdwest-Fryslân', 960, 1061],
            [6, 6, 'Hylpen', 'Súdwest-Fryslân', 870, 1225],
            [9, 9, 'Harns', 'Harlingen', 14740, 1234],
            [11, 11, 'Dokkum', 'Noardeast-Fryslân', 12675, 1298]
        ]
    )

# TODO: more tests
