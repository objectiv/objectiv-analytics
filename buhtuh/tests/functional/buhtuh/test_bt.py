"""
Copyright 2021 Objectiv B.V.

Tests for BuhTuhDataFrame using a very simple dataset.

"""
import os
from typing import List, Union

import pytest
import sqlalchemy
from sqlalchemy.engine import ResultProxy

from buhtuh import BuhTuhDataFrame, BuhTuhSeries, BuhTuhSeriesBoolean, BuhTuhSeriesString


DB_TEST_URL = os.environ.get('OBJ_DB_TEST_URL', 'postgresql://objectiv:@localhost:5432/objectiv')


FULL_TEST_DATA = [
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
TEST_DATA = FULL_TEST_DATA[:3]
TEST_COLUMNS = ['skating_order', 'city', 'municipality', 'inhabitants', 'founding']
# The default dataframe has skating_order as index, so that column will be prepended before the actual
# data in the query results.
INDEX_AND_COLUMNS = ['_index_skating_order'] + TEST_COLUMNS

MERGE_TEST_DATA = [

    [1, 'Sûkerbôlle', '2021-05-03 11:28:36.388', '2021-05-03'],
    [2, 'Dúmkes', '2021-05-04 23:28:36.388', '2021-05-04'],
    [4, 'Grutte Pier Bier', '2022-05-03 14:13:13.388', '2022-05-03']
]
MERGE_COLUMNS = ['skating_order', 'food', 'moment', 'date']
MERGE_INDEX_AND_COLUMNS = ['_index_skating_order'] + MERGE_COLUMNS


def _get_bt(table, dataset, columns) -> BuhTuhDataFrame:
    print(os.environ)
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


def _get_bt_with_test_data(full_data_set: bool = False) -> BuhTuhDataFrame:
    if full_data_set:
        test_data = FULL_TEST_DATA
    else:
        test_data = TEST_DATA
    return _get_bt('test_table', test_data, TEST_COLUMNS)


def _get_bt_with_merge_data() -> BuhTuhDataFrame:
    return _get_bt('test_merge_table', MERGE_TEST_DATA, MERGE_COLUMNS)


def run_query(engine: sqlalchemy.engine, sql: str) -> ResultProxy:
    with engine.connect() as conn:
        res = conn.execute(sql)
        return res


def assert_equals_data(
        bt: Union[BuhTuhDataFrame, BuhTuhSeries],
        expected_columns: List[str],
        expected_data: List[list],
        order_by: str = None,
    ):
    """
    Execute sql of ButTuhDataFrame/Series, with the given order_by, and make sure the result matches
    the expected columns and data.
    """
    if len(expected_data) == 0:
        raise ValueError("Cannot check data if 0 rows are expected.")

    bt_sorted = bt.sort_values(order_by)
    sql = bt_sorted.view_sql()
    db_rows = run_query(bt_sorted.engine, sql)
    column_names = list(db_rows.keys())
    db_values = [list(row) for row in db_rows]
    print(db_values)

    assert len(db_values) == len(expected_data)
    assert column_names == expected_columns
    for i, df_row in enumerate(db_values):
        expected_row = expected_data[i]
        assert df_row == expected_row, f'row {i} is not equal: {expected_row} != {df_row}'


def test_get_item_single():
    bt = _get_bt_with_test_data()

    selection = bt[['city']]
    assert isinstance(selection, BuhTuhDataFrame)
    assert_equals_data(
        selection,
        expected_columns=['_index_skating_order', 'city'],
        expected_data=[
            [1, 'Ljouwert'],
            [2, 'Snits'],
            [3, 'Drylts'],
        ]
    )

    selection = bt[['inhabitants']]
    assert isinstance(selection, BuhTuhDataFrame)
    assert_equals_data(
        selection,
        expected_columns=['_index_skating_order', 'inhabitants'],
        expected_data=[
            [1, 93485],
            [2, 33520],
            [3, 3055],
        ]
    )

    selection = bt['city']
    assert isinstance(selection, BuhTuhSeries)
    assert_equals_data(
        selection,
        expected_columns=['_index_skating_order', 'city'],
        expected_data=[
            [1, 'Ljouwert'],
            [2, 'Snits'],
            [3, 'Drylts'],
        ]
    )
    # todo: pandas supports _a lot_ of way to select columns and/or rows

def test_get_series_single():
    bt = _get_bt_with_test_data()

    series = bt['city']
    assert isinstance(series, BuhTuhSeriesString)

    value = series[1]

    assert isinstance(value, str)
    assert value == 'Ljouwert'

def test_get_item_multiple():
    bt = _get_bt_with_test_data()
    selection = bt[['city', 'founding']]
    assert isinstance(selection, BuhTuhDataFrame)
    assert_equals_data(
        selection,
        expected_columns=['_index_skating_order', 'city', 'founding'],
        expected_data=[
            [1, 'Ljouwert', 1285],
            [2, 'Snits',  1456],
            [3, 'Drylts', 1268],
        ]
    )


def test_set_const_int():
    bt = _get_bt_with_test_data()
    bt['new_column'] = 5
    assert_equals_data(
        bt,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding',  # original columns
            'new_column'  # new
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 5],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 5],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 5]
        ]
    )


def test_set_const_float():
    bt = _get_bt_with_test_data()
    bt['new_column'] = 5.1
    assert_equals_data(
        bt,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding',  # original columns
            'new_column'  # new
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 5.1],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 5.1],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 5.1]
        ]
    )


def test_set_const_str():
    bt = _get_bt_with_test_data()
    bt['alternative_sport'] = 'keatsen'
    assert_equals_data(
        bt,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding',  # original columns
            'alternative_sport'  # new
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285,  'keatsen'],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 'keatsen'],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 'keatsen']
        ]
    )

def test_set_const_int_from_series():
    bt = _get_bt_with_test_data()[['founding']]
    max = bt.groupby()['founding'].sum()
    max_series = max['founding_sum']
    max_value = max_series[1]
    bt['max_founding'] = max_value

    assert_equals_data(
        bt,
        expected_columns=[
            '_index_skating_order',  # index
            'founding',  # original columns
            'max_founding'  # new
        ],
        expected_data=[
            [1, 1285, 4009], [2, 1456, 4009], [3, 1268, 4009]
        ]
    )


def test_set_series_column():
    bt = _get_bt_with_test_data()
    bt['duplicated_column'] = bt['founding']
    assert_equals_data(
        bt,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding', 'duplicated_column'
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 1285],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 1456],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 1268],
        ]
    )

    bt['spaces in column'] = bt['founding']
    assert_equals_data(
        bt,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding', 'duplicated_column', 'spaces in column'
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 1285, 1285],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 1456, 1456],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 1268, 1268],
        ]
    )

    filtered_bt = bt[bt['city'] == 'Ljouwert']
    filtered_bt['town'] = filtered_bt['city']
    assert_equals_data(
        filtered_bt,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding', 'duplicated_column', 'spaces in column', 'town'
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 1285, 1285, 'Ljouwert']
        ]
    )


def test_set_multiple():
    bt = _get_bt_with_test_data()
    bt['duplicated_column'] = bt['founding']
    bt['alternative_sport'] = 'keatsen'
    bt['leet'] = 1337
    assert_equals_data(
        bt,
        expected_columns=INDEX_AND_COLUMNS + ['duplicated_column', 'alternative_sport', 'leet'],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 1285, 'keatsen', 1337],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 1456, 'keatsen', 1337],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 1268, 'keatsen', 1337]
        ]
    )


def test_set_existing():
    bt = _get_bt_with_test_data()
    bt['city'] = bt['founding']
    assert_equals_data(
        bt,
        expected_columns=INDEX_AND_COLUMNS,
        expected_data=[
            [1, 1, 1285, 'Leeuwarden', 93485, 1285],
            [2, 2, 1456, 'Súdwest-Fryslân', 33520, 1456],
            [3, 3, 1268, 'Súdwest-Fryslân', 3055, 1268]
        ]
    )


def test_set_existing_referencing_other_column_experience():
    bt = _get_bt_with_test_data()
    bt['city'] = bt['city'] + ' test'
    assert_equals_data(
        bt,
        expected_columns=INDEX_AND_COLUMNS,
        expected_data=[
            [1, 1, 'Ljouwert test', 'Leeuwarden', 93485, 1285],
            [2, 2, 'Snits test', 'Súdwest-Fryslân', 33520, 1456],
            [3, 3, 'Drylts test', 'Súdwest-Fryslân', 3055, 1268]
        ]
    )

    bt = _get_bt_with_test_data()
    a = bt['city'] + ' test1'
    b = bt['city'] + ' test2'
    c = bt['skating_order'] + bt['skating_order']
    bt['skating_order'] = 0
    bt['city'] = ''
    assert_equals_data(
        bt,
        expected_columns=INDEX_AND_COLUMNS,
        expected_data=[
            [1, 0, '', 'Leeuwarden', 93485, 1285],
            [2, 0, '', 'Súdwest-Fryslân', 33520, 1456],
            [3, 0, '', 'Súdwest-Fryslân', 3055, 1268]
        ]
    )
    bt['skating_order'] = c
    bt['city'] = a + ' - ' + b
    assert_equals_data(
        bt,
        expected_columns=INDEX_AND_COLUMNS,
        expected_data=[
            [1, 2, 'Ljouwert test1 - Ljouwert test2', 'Leeuwarden', 93485, 1285],
            [2, 4, 'Snits test1 - Snits test2', 'Súdwest-Fryslân', 33520, 1456],
            [3, 6, 'Drylts test1 - Drylts test2', 'Súdwest-Fryslân', 3055, 1268]
        ]
    )


def test_set_series_expression():
    bt = _get_bt_with_test_data()
    bt['time_travel'] = bt['founding'] + 1000
    assert_equals_data(
        bt,
        expected_columns=INDEX_AND_COLUMNS + ['time_travel'],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 2285],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 2456],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 2268]
        ]
    )

def test_del_item():
    bt = _get_bt_with_test_data()

    del(bt['founding'])
    assert 'founding' not in bt.data.keys()

    # It will not choke un columns not there, is that okay?
    with pytest.raises(KeyError):
        del(bt['non existing column'])

    del(bt['city', 'municipality'])
    assert 'city' not in bt.data.keys()
    assert 'municipality' not in bt.data.keys()

    inh = bt['inhabitants']
    del(bt[inh])
    assert inh not in bt.data.values()

def test_add_int_constant():
    bt = _get_bt_with_test_data()
    bts = bt['founding'] + 200
    assert isinstance(bts, BuhTuhSeries)
    assert_equals_data(
        bts,
        expected_columns=['_index_skating_order', 'founding'],
        expected_data=[
            [1, 1485],
            [2, 1656],
            [3, 1468]
        ]
    )


def test_comparator_int_constant_boolean():
    bt = _get_bt_with_test_data()
    # [1, 1285],
    # [2, 1456],
    # [3, 1268]

    bts = bt['founding'] != 1285
    assert isinstance(bts, BuhTuhSeries)
    assert_equals_data(
        bts,
        expected_columns=['_index_skating_order', 'founding'],
        expected_data=[
            [1, False],
            [2, True],
            [3, True]
        ]
    )

    bts = bt['founding'] == 1285
    assert isinstance(bts, BuhTuhSeries)
    assert_equals_data(
        bts,
        expected_columns=['_index_skating_order', 'founding'],
        expected_data=[
            [1, True],
            [2, False],
            [3, False]
        ]
    )
    bts = bt['founding'] < 1285
    assert isinstance(bts, BuhTuhSeries)
    assert_equals_data(
        bts,
        expected_columns=['_index_skating_order', 'founding'],
        expected_data=[
            [1, False],
            [2, False],
            [3, True]
        ]
    )
    bts = bt['founding'] <= 1285
    assert isinstance(bts, BuhTuhSeries)
    assert_equals_data(
        bts,
        expected_columns=['_index_skating_order', 'founding'],
        expected_data=[
            [1, True],
            [2, False],
            [3, True]
        ]
    )
    bts = bt['founding'] >= 1285
    assert isinstance(bts, BuhTuhSeries)
    assert_equals_data(
        bts,
        expected_columns=['_index_skating_order', 'founding'],
        expected_data=[
            [1, True],
            [2, True],
            [3, False]
        ]
    )

    bts = bt['founding'] > 1285
    assert isinstance(bts, BuhTuhSeries)
    assert_equals_data(
        bts,
        expected_columns=['_index_skating_order', 'founding'],
        expected_data=[
            [1, False],
            [2, True],
            [3, False]
        ]
    )


def test_add_int_series():
    bt = _get_bt_with_test_data()
    # Add two integer columns
    bts = bt['founding'] + bt['inhabitants']
    assert isinstance(bts, BuhTuhSeries)
    assert_equals_data(
        bts,
        expected_columns=['_index_skating_order', 'founding'],
        expected_data=[
            [1, 94770],  # 93485 + 1285
            [2, 34976],  # 33520, 1456
            [3, 4323]    # 3055, 1268
        ]
    )
    # Add the same column three times
    bts = bt['inhabitants'] + bt['inhabitants'] + bt['inhabitants']
    assert isinstance(bts, BuhTuhSeries)
    assert_equals_data(
        bts,
        expected_columns=['_index_skating_order', 'inhabitants'],
        expected_data=[
            [1, 280455],  # 3 * 93485
            [2, 100560],  # 3 * 33520
            [3, 9165],    # 3 * 3055
        ]
    )


def test_string_slice():
    bt = _get_bt_with_test_data()

    # Now try some slices
    for s in [slice(0,3), slice(1,3), slice(3,3), slice(4,3), slice(-4,-2), slice(-2,-2), slice(-2,1)]:
        print(f'slice: {s}')
        bts = bt['city'].slice(s.start, s.stop)
        assert isinstance(bts, BuhTuhSeries)
        assert_equals_data(
            bts,
            expected_columns=['_index_skating_order', 'city'],
            expected_data=[
                [1, 'Ljouwert'.__getitem__(s)],
                [2, 'Snits'.__getitem__(s)],
                [3, 'Drylts'.__getitem__(s)]
            ]
        )

    # Some more with no beginnings or endings
    for s in [slice(None, 3), slice(3, None),slice(None, -3), slice(-3,None)]:
        print(f'slice: {s}')
        bts = bt['city'].slice(s.start, s.stop)
        assert isinstance(bts, BuhTuhSeries)
        assert_equals_data(
            bts,
            expected_columns=['_index_skating_order', 'city'],
            expected_data=[
                [1, 'Ljouwert'.__getitem__(s)],
                [2, 'Snits'.__getitem__(s)],
                [3, 'Drylts'.__getitem__(s)]
            ]
        )

def test_add_string_series():
    bt = _get_bt_with_test_data()
    bts = bt['city'] + ' is in the municipality ' + bt['municipality']
    assert isinstance(bts, BuhTuhSeries)
    assert_equals_data(
        bts,
        expected_columns=['_index_skating_order', 'city'],
        expected_data=[
            [1, 'Ljouwert is in the municipality Leeuwarden'],
            [2, 'Snits is in the municipality Súdwest-Fryslân'],
            [3, 'Drylts is in the municipality Súdwest-Fryslân']
        ]
    )


def test_divide_constant():
    bt = _get_bt_with_test_data()
    bts = bt['inhabitants'] / 1000
    assert isinstance(bts, BuhTuhSeries)
    assert_equals_data(
        bts,
        expected_columns=['_index_skating_order', 'inhabitants'],
        expected_data=[
            [1, 93.485],  # 93485 / 1000
            [2, 33.52],   # 33520 / 1000
            [3, 3.055],   #  3055 / 1000
        ]
    )


def test_integer_divide_constant():
    bt = _get_bt_with_test_data()
    bts = bt['inhabitants'] // 1000
    assert isinstance(bts, BuhTuhSeries)
    assert_equals_data(
        bts,
        expected_columns=['_index_skating_order', 'inhabitants'],
        expected_data=[
            [1, 93],  # 93485 // 1000
            [2, 33],  # 33520 // 1000
            [3, 3],   #  3055 // 1000
        ]
    )


def test_group_by_basics():
    bt = _get_bt_with_test_data(full_data_set=True)
    btg = bt.groupby('municipality')
    result_bt = btg.count()

    assert_equals_data(
        result_bt,
        expected_columns=['municipality', '_index_skating_order_count', 'skating_order_count', 'city_count', 'inhabitants_count', 'founding_count'],
        order_by='skating_order_count',
        expected_data=[
            ['Noardeast-Fryslân', 1, 1, 1, 1, 1],
            ['Leeuwarden', 1, 1, 1, 1, 1],
            ['Harlingen', 1, 1, 1, 1, 1],
            ['Waadhoeke', 1, 1, 1, 1, 1],
            ['De Friese Meren', 1, 1, 1, 1, 1],
            ['Súdwest-Fryslân', 6, 6, 6, 6, 6],
        ]
    )
    assert result_bt.index_dtypes == {
        'municipality': 'string'
    }
    assert result_bt.dtypes == {
        '_index_skating_order_count': 'Int64',
        'city_count': 'Int64',
        'founding_count': 'Int64',
        'inhabitants_count': 'Int64',
        'skating_order_count': 'Int64'
    }

    # now test multiple different aggregations
    result_bt = btg.aggregate({'_index_skating_order': 'nunique', 'skating_order': 'sum',
                               'city': 'count', 'inhabitants': 'min', 'founding': 'max'})
    assert_equals_data(
        result_bt,
        expected_columns=['municipality', '_index_skating_order_nunique', 'skating_order_sum', 'city_count', 'inhabitants_min', 'founding_max'],
        order_by='municipality',
        expected_data=[
            ['De Friese Meren', 1, 4, 1, 700, 1426],
            ['Harlingen', 1, 9, 1, 14740, 1234],
            ['Leeuwarden', 1, 1, 1, 93485, 1285],
            ['Noardeast-Fryslân', 1, 11, 1, 12675, 1298],
            ['Súdwest-Fryslân', 6, 31, 6, 870, 1456],
            ['Waadhoeke', 1, 10, 1, 12760, 1374]
        ]
    )
    assert result_bt.index_dtypes == {
        'municipality': 'string'
    }
    assert result_bt.dtypes == {
        '_index_skating_order_nunique': 'Int64',
        'city_count': 'Int64',
        'founding_max': 'Int64',
        'inhabitants_min': 'Int64',
        'skating_order_sum': 'Int64'
    }

def test_group_by_all():
    bt = _get_bt_with_test_data(full_data_set=True)
    btg = bt.groupby()
    result_bt = btg.nunique()

    assert_equals_data(
        result_bt,
        expected_columns=['index', '_index_skating_order_nunique', 'skating_order_nunique', 'city_nunique', 'municipality_nunique', 'inhabitants_nunique', 'founding_nunique'],
        order_by='skating_order_nunique',
        expected_data=[
            [1, 11, 11, 11, 6, 11, 11],
        ]
    )
    assert result_bt.index_dtypes == {
        'index': 'Int64'
    }
    assert result_bt.dtypes == {
        '_index_skating_order_nunique': 'Int64',
        'city_nunique': 'Int64',
        'founding_nunique': 'Int64',
        'inhabitants_nunique': 'Int64',
        'municipality_nunique': 'Int64',
        'skating_order_nunique': 'Int64'
    }

def test_group_by_expression():
    bt = _get_bt_with_test_data(full_data_set=True)
    btg = bt.groupby(bt['city'].slice(None,1))
    result_bt = btg.nunique()

    assert_equals_data(
        result_bt,
        expected_columns=['city', '_index_skating_order_nunique', 'skating_order_nunique', 'municipality_nunique', 'inhabitants_nunique', 'founding_nunique'],
        order_by='city',
        expected_data=[
            ['B', 1, 1, 1, 1, 1], ['D', 2, 2, 2, 2, 2], ['F', 1, 1, 1, 1, 1], ['H', 2, 2, 2, 2, 2],
            ['L', 1, 1, 1, 1, 1], ['S', 3, 3, 2, 3, 3], ['W', 1, 1, 1, 1, 1]
        ]
    )
    assert result_bt.index_dtypes == {
        'city': 'string'
    }
    assert result_bt.dtypes == {
        '_index_skating_order_nunique': 'Int64',
        'municipality_nunique': 'Int64',
        'founding_nunique': 'Int64',
        'inhabitants_nunique': 'Int64',
        'skating_order_nunique': 'Int64'
    }

def test_group_by_basics_series():
    bt = _get_bt_with_test_data(full_data_set=True)
    btg = bt.groupby('municipality')
    btg_series = btg['inhabitants']
    result_bt = btg_series.count()
    assert_equals_data(
        result_bt,
        order_by='municipality',
        expected_columns=['municipality', 'inhabitants_count'],
        expected_data=[
            ['De Friese Meren', 1],
            ['Harlingen', 1],
            ['Leeuwarden', 1],
            ['Noardeast-Fryslân', 1],
            ['Súdwest-Fryslân', 6],
            ['Waadhoeke', 1],
        ]
    )
    assert result_bt.index_dtypes == {
        'municipality': 'string'
    }
    assert result_bt.dtypes == {
        'inhabitants_count': 'Int64',
    }

    btg_series = btg['inhabitants','founding']
    result_bt = btg_series.count()
    assert_equals_data(
        result_bt,
        order_by='municipality',
        expected_columns=['municipality', 'inhabitants_count', 'founding_count'],
        expected_data=[
            ['De Friese Meren', 1, 1],
            ['Harlingen', 1, 1],
            ['Leeuwarden', 1, 1],
            ['Noardeast-Fryslân', 1, 1],
            ['Súdwest-Fryslân', 6, 6],
            ['Waadhoeke', 1, 1],
        ]
    )
    assert result_bt.index_dtypes == {
        'municipality': 'string'
    }
    assert result_bt.dtypes == {
        'inhabitants_count': 'Int64',
        'founding_count': 'Int64'
    }


def test_group_by_multiple_aggregations_on_same_series():
    bt = _get_bt_with_test_data(full_data_set=True)
    btg = bt.groupby('municipality')
    result_bt = btg.aggregate(['inhabitants', 'inhabitants'], ['min','max'])
    assert_equals_data(
        result_bt,
        order_by='municipality',
        expected_columns=['municipality', 'inhabitants_min', 'inhabitants_max'],
        expected_data=[
            ['De Friese Meren', 700, 700], ['Harlingen', 14740, 14740],
            ['Leeuwarden', 93485, 93485], ['Noardeast-Fryslân', 12675, 12675],
            ['Súdwest-Fryslân', 870, 33520], ['Waadhoeke', 12760, 12760]
        ]
    )
    assert result_bt.index_dtypes == {
        'municipality': 'string'
    }
    assert result_bt.dtypes == {
        'inhabitants_min': 'Int64',
        'inhabitants_max': 'Int64',
    }


def test_combined_operations1():
    bt = _get_bt_with_test_data(full_data_set=True)
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


def test_boolean_indexing_same_node():
    bt = _get_bt_with_test_data(full_data_set=True)
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


def test_merge_column():
    bt = _get_bt_with_test_data(full_data_set=False)[['skating_order','city']]
    mt = _get_bt_with_merge_data()[['skating_order','food']]

    result = bt.merge(mt, ['skating_order'])

    assert isinstance(result, BuhTuhDataFrame)
    assert_equals_data(
        result,
        # This is weak. Ordering is broken.
        expected_columns=['_index_skating_order', 'skating_order_left', 'skating_order_right', 'city', 'food'],
        expected_data=[
            [1, 1, 1, 'Ljouwert', 'Sûkerbôlle'],
            [2, 2, 2, 'Snits', 'Dúmkes'],
        ]
    )


def test_merge_index():
    bt = _get_bt_with_test_data(full_data_set=False)[['skating_order','city']]
    mt = _get_bt_with_merge_data()[['skating_order','food']]
    result = bt.merge(mt)

    assert isinstance(result, BuhTuhDataFrame)
    assert_equals_data(
        result,
        # This is weak. Ordering is broken.
        expected_columns=['_index_skating_order', 'skating_order_left', 'skating_order_right', 'city', 'food'],
        expected_data=[
            [1, 1, 1, 'Ljouwert', 'Sûkerbôlle'],
            [2, 2, 2, 'Snits', 'Dúmkes'],
        ]
    )


def test_merge_partial_columns():
    bt = _get_bt_with_test_data(full_data_set=False)
    mt = _get_bt_with_merge_data()[['skating_order','food']]
    result = bt[['city','inhabitants']].merge(mt[['food']])

    assert_equals_data(
        result,
        # This is weak. Ordering is broken.
        expected_columns=['_index_skating_order', 'city', 'inhabitants', 'food'],
        expected_data=[
            [1, 'Ljouwert', 93485, 'Sûkerbôlle'],
            [2, 'Snits', 33520, 'Dúmkes'],
        ]
    )


def test_merge_self():
    bt1 = _get_bt_with_test_data(full_data_set=False)[['city']]
    bt2 = _get_bt_with_test_data(full_data_set=False)[['inhabitants']]
    result = bt1.merge(bt2)
    assert_equals_data(
        result,
        expected_columns=['_index_skating_order', 'city', 'inhabitants'],
        expected_data=[
            [1, 'Ljouwert', 93485],
            [2, 'Snits', 33520],
            [3, 'Drylts', 3055]
        ]
    )


def test_merge_preselection():
    bt = _get_bt_with_test_data(full_data_set=False)[['skating_order', 'city', 'inhabitants']]
    mt = _get_bt_with_merge_data()[['skating_order', 'food']]
    result = bt[bt['skating_order'] != 1].merge(mt[['food']])
    assert_equals_data(
        result,
        # This is weak. Ordering is broken.
        expected_columns=['_index_skating_order', 'skating_order', 'city', 'inhabitants', 'food'],
        expected_data=[
            [2, 2, 'Snits', 33520, 'Dúmkes'],
        ]
    )


def test_merge_expression_columns():
    bt = _get_bt_with_test_data(full_data_set=False)[['skating_order','city','inhabitants']]
    mt = _get_bt_with_merge_data()[['skating_order','food']]
    bt['skating_order'] += 2
    mt['skating_order'] += 2

    result = bt.merge(mt, ['skating_order'])
    assert_equals_data(
        result,
        # This is weak. Ordering is broken.
        expected_columns=['_index_skating_order', 'skating_order_left', 'skating_order_right', 'city', 'inhabitants', 'food'],
        expected_data=[
            [1, 3, 3, 'Ljouwert', 93485, 'Sûkerbôlle'],
            [2, 4, 4, 'Snits', 33520, 'Dúmkes'],
        ]
    )

# This needs a better name
def test_merge_expression_columns_regression():
    bt = _get_bt_with_test_data(full_data_set=False)[['skating_order', 'city', 'inhabitants']]
    mt = _get_bt_with_merge_data()[['skating_order', 'food']]
    bt['x'] = bt['skating_order'] == 3
    bt['y'] = bt['skating_order'] == 3
    bt['z'] = bt['x'] & bt['y']
    result = bt.merge(mt, ['skating_order'])
    assert_equals_data(
        result,
        expected_columns=['_index_skating_order', 'skating_order_left', 'skating_order_right', 'city', 'inhabitants', 'x', 'y',
                          'z', 'food'],
        expected_data=[
            [1, 1, 1, 'Ljouwert', 93485, False, False, False, 'Sûkerbôlle'],
            [2, 2, 2, 'Snits', 33520, False, False, False, 'Dúmkes']
        ]
    )

def test_merge_differently_named_columns():
    bt = _get_bt_with_test_data(full_data_set=False)[['skating_order', 'city']]
    mt =  _get_bt_with_merge_data()[['skating_order', 'food']]

    # create a 'skating_order_min' column to merge on
    agg = mt.groupby('_index_skating_order')[['skating_order']].sum()
    result = bt.merge(agg, [('skating_order', 'skating_order_sum')])
    assert_equals_data(
        result,
        expected_columns=['_index_skating_order', 'skating_order', 'city', 'skating_order_sum'],
        expected_data=[
            [1, 1, 'Ljouwert', 1], [2, 2, 'Snits', 2]
        ]
    )

    with pytest.raises(KeyError):
        # swap left and right columns
        agg = mt.groupby('_index_skating_order')[['skating_order']].sum()
        bt.merge(agg, [('skating_order_sum', 'skating_order')]).head(1)

    # now do the same, but using the series
    agg = mt.groupby('_index_skating_order')[['skating_order']].sum()
    result = bt.merge(agg, [(bt['skating_order'], agg['skating_order_sum'])])
    assert_equals_data(
        result,
        expected_columns=['_index_skating_order', 'skating_order', 'city', 'skating_order_sum'],
        expected_data=[
            [1, 1, 'Ljouwert', 1], [2, 2, 'Snits', 2]
        ]
    )

    with pytest.raises(KeyError):
        # swap left and right columns
        agg = mt.groupby('_index_skating_order')[['skating_order']].sum()
        bt.merge(agg, [(agg['skating_order_sum']), bt['skating_order']]).head(1)

    # now do the same, but using the series with expression
    agg = mt.groupby('_index_skating_order')[['skating_order']].sum()
    result = bt.merge(agg, [(bt['skating_order']+1, agg['skating_order_sum']+1)])
    assert_equals_data(
        result,
        expected_columns=['_index_skating_order', 'skating_order', 'city', 'skating_order_sum'],
        expected_data=[
            [1, 1, 'Ljouwert', 1], [2, 2, 'Snits', 2]
        ]
    )

    # another one, but slightly more cool :)
    result = bt.merge(mt, [(bt['city'].slice(0,1), mt['food'].slice(0,1))])['city', 'food']
    assert_equals_data(
        result,
        expected_columns=['_index_skating_order', 'city', 'food'],
        expected_data=[
            [3, 'Drylts', 'Dúmkes'], [2, 'Snits', 'Sûkerbôlle']
        ]
    )

def test_merge_left_right():
    bt = _get_bt_with_test_data(full_data_set=False)[['skating_order', 'city']]
    mt =  _get_bt_with_merge_data()[['skating_order', 'food']]

    result = bt.merge(mt, how='left')
    assert_equals_data(
        result,
        expected_columns=['_index_skating_order', 'skating_order_left', 'skating_order_right', 'city', 'food'],
        expected_data=[
            [1, 1, 1, 'Ljouwert', 'Sûkerbôlle'], [2, 2, 2, 'Snits', 'Dúmkes'],  [3, 3, None, 'Drylts', None]
        ]
    )

    result = mt.merge(bt, how='right')
    assert_equals_data(
        result,
        expected_columns=['_index_skating_order', 'skating_order_left', 'skating_order_right', 'food', 'city'],
        expected_data=[
            [1, 1, 1, 'Sûkerbôlle', 'Ljouwert'], [2, 2, 2, 'Dúmkes', 'Snits'], [3, None, 3, None, 'Drylts']
        ]
    )

def test_timestamp_data():
    mt = _get_bt_with_merge_data()[['moment']]
    from datetime import datetime
    assert_equals_data(
        mt,
        expected_columns=['_index_skating_order', 'moment'],
        expected_data=[
            [1, datetime(2021, 5, 3, 11, 28, 36, 388000)],
            [2, datetime(2021, 5, 4, 23, 28, 36, 388000)],
            [4, datetime(2022, 5, 3, 14, 13, 13, 388000)]
        ]
    )

def test_timestamp_comparator(asstring = False):
    mt = _get_bt_with_merge_data()[['moment']]
    from datetime import datetime
    dt = datetime(2021, 5, 3, 11, 28, 36, 388000)

    if asstring:
        dt = str(dt)

    result = mt[mt['moment'] == dt]
    assert_equals_data(
        result,
        expected_columns=['_index_skating_order', 'moment'],
        expected_data=[
            [1, datetime(2021, 5, 3, 11, 28, 36, 388000)]
        ]
    )

    assert_equals_data(
        mt[mt['moment'] >= dt],
        expected_columns=['_index_skating_order', 'moment'],
        expected_data=[
            [1, datetime(2021, 5, 3, 11, 28, 36, 388000)],
            [2, datetime(2021, 5, 4, 23, 28, 36, 388000)],
            [4, datetime(2022, 5, 3, 14, 13, 13, 388000)]
        ]
    )

    assert_equals_data(
        mt[mt['moment'] > dt],
        expected_columns=['_index_skating_order', 'moment'],
        expected_data=[
            [2, datetime(2021, 5, 4, 23, 28, 36, 388000)],
            [4, datetime(2022, 5, 3, 14, 13, 13, 388000)]
        ]
    )

    dt = datetime(2022, 5, 3, 14, 13, 13, 388000)
    if asstring:
        dt = str(dt)

    assert_equals_data(
        mt[mt['moment'] <= dt],
        expected_columns=['_index_skating_order', 'moment'],
        expected_data=[
            [1, datetime(2021, 5, 3, 11, 28, 36, 388000)],
            [2, datetime(2021, 5, 4, 23, 28, 36, 388000)],
            [4, datetime(2022, 5, 3, 14, 13, 13, 388000)]
        ]
    )

    assert_equals_data(
        mt[mt['moment'] < dt],
        expected_columns=['_index_skating_order', 'moment'],
        expected_data=[
            [1, datetime(2021, 5, 3, 11, 28, 36, 388000)],
            [2, datetime(2021, 5, 4, 23, 28, 36, 388000)]
        ]
    )

def test_timestamp_comparator_string():
    test_timestamp_comparator(asstring=True)


def test_date_comparator(asstring = False):
    mt = _get_bt_with_merge_data()[['date']]

    # import code has no means to distinguish between date and timestamp
    mt['date'] = mt['date'].astype('date')

    from datetime import date
    dt = date(2021, 5, 3)

    if asstring:
        dt = str(dt)

    result = mt[mt['date'] == dt]
    assert_equals_data(
        result,
        expected_columns=['_index_skating_order', 'date'],
        expected_data=[
            [1, date(2021, 5, 3)]
        ]
    )
    assert_equals_data(
        mt[mt['date'] >= dt],
        expected_columns=['_index_skating_order', 'date'],
        expected_data=[
            [1, date(2021, 5, 3)],
            [2, date(2021, 5, 4)],
            [4, date(2022, 5, 3)]
        ]
    )

    assert_equals_data(
        mt[mt['date'] > dt],
        expected_columns=['_index_skating_order', 'date'],
        expected_data=[
            [2, date(2021, 5, 4)],
            [4, date(2022, 5, 3)]
        ]
    )

    dt = date(2022, 5, 3)
    if asstring:
        dt = str(dt)

    assert_equals_data(
        mt[mt['date'] <= dt],
        expected_columns=['_index_skating_order', 'date'],
        expected_data=[
            [1, date(2021, 5, 3)],
            [2, date(2021, 5, 4,)],
            [4, date(2022, 5, 3)]
        ]
    )

    assert_equals_data(
        mt[mt['date'] < dt],
        expected_columns=['_index_skating_order', 'date'],
        expected_data=[
            [1, date(2021, 5, 3)],
            [2, date(2021, 5, 4)]
        ]
    )

def test_date_comparator_string():
    test_date_comparator(asstring=True)

# TODO test_time_* tests

def test_date_format():
    mt = _get_bt_with_merge_data()[['moment', 'date']]

    mt['date'] = mt['date'].astype('date')

    assert mt['moment'].dtype == 'timestamp'
    assert mt['date'].dtype == 'date'

    assert mt['moment'].format('YYYY').dtype == 'string'

    mt['fyyyy'] = mt['moment'].format('YYYY')
    mt['fday'] = mt['date'].format('Day')

    assert_equals_data(
        mt[['fyyyy','fday']],
        expected_columns=['_index_skating_order', 'fyyyy','fday'],
        expected_data=[
            [1, '2021', 'Monday   '],
            [2, '2021', 'Tuesday  '],
            [4, '2022', 'Tuesday  ']
        ]
    )

def test_timedelta():
    mt = _get_bt_with_merge_data()[['skating_order', 'moment']]

    # import code has no means to distinguish between date and timestamp
    gb = mt.groupby([]).aggregate(['moment','moment'],['min','max'])
    gb['delta'] = gb['moment_max'] - gb['moment_min']

    import datetime

    assert_equals_data(
        gb,
        expected_columns=['index', 'moment_min', 'moment_max', 'delta'],
        expected_data=[
            [1, datetime.datetime(2021, 5, 3, 11, 28, 36, 388000), datetime.datetime(2022, 5, 3, 14, 13, 13, 388000), datetime.timedelta(days=365, seconds=9877)]
        ]
    )

    r2 = gb.groupby([])['delta'].average()
    assert_equals_data(
        r2,
        expected_columns=['index', 'delta_average'],
        expected_data=[
            [1, datetime.timedelta(days=365, seconds=9877)]
        ]
    )

    r3 = r2['delta_average'] + datetime.timedelta()
    assert_equals_data(
        r3,
        expected_columns=['index', 'delta_average'],
        expected_data=[
            [1, datetime.timedelta(days=365, seconds=9877)]
        ]
    )

# TODO: more tests
