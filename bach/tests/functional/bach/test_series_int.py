"""
Copyright 2021 Objectiv B.V.
"""
from bach import Series, SeriesInt64
from tests.functional.bach.test_data_and_utils import assert_equals_data, assert_postgres_type,\
    get_df_with_test_data
from tests.functional.bach.test_series_numeric import helper_test_simple_arithmetic


def test_add_int_constant(engine):
    bt = get_df_with_test_data(engine)
    bts = bt['founding'] + 200
    assert isinstance(bts, Series)
    assert_postgres_type(bt['founding'], 'bigint', SeriesInt64)
    assert_equals_data(
        bts,
        expected_columns=['_index_skating_order', 'founding'],
        expected_data=[
            [1, 1485],
            [2, 1656],
            [3, 1468]
        ]
    )


def test_create_big_int_constant(engine):
    bt = get_df_with_test_data(engine)
    bt = bt[['city']]
    # just under max size of a 4 byte integer
    bt['new'] = 2147483647
    # now over the max size of a 4 byte integer
    bt['new_big'] = 2147483648
    # Add 100 to new, now the number doesn't fit into 4 bytes anymore.
    bt['calc'] = bt['new'] + 100
    # Add something to new_big, the number still fits into 8 bytes.
    bt['calc_big'] = bt['new_big'] + 100000
    assert_postgres_type(bt['calc_big'], 'bigint', SeriesInt64)
    assert_equals_data(
        bt,
        expected_columns=['_index_skating_order', 'city', 'new', 'new_big', 'calc', 'calc_big'],
        expected_data=[
            [1, 'Ljouwert', 2147483647, 2147483648, 2147483747, 2147583648],
            [2, 'Snits', 2147483647, 2147483648, 2147483747, 2147583648],
            [3, 'Drylts', 2147483647, 2147483648, 2147483747, 2147583648],
        ]
    )


def test_comparator_int_constant_boolean(engine):
    bt = get_df_with_test_data(engine)
    # [1, 1285],
    # [2, 1456],
    # [3, 1268]

    bts = bt['founding'] != 1285
    assert isinstance(bts, Series)
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
    assert isinstance(bts, Series)
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
    assert isinstance(bts, Series)
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
    assert isinstance(bts, Series)
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
    assert isinstance(bts, Series)
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
    assert isinstance(bts, Series)
    assert_equals_data(
        bts,
        expected_columns=['_index_skating_order', 'founding'],
        expected_data=[
            [1, False],
            [2, True],
            [3, False]
        ]
    )


def test_add_int_series(engine):
    bt = get_df_with_test_data(engine)
    # Add two integer columns
    bts = bt['founding'] + bt['inhabitants']
    assert isinstance(bts, Series)
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
    assert isinstance(bts, Series)
    assert_equals_data(
        bts,
        expected_columns=['_index_skating_order', 'inhabitants'],
        expected_data=[
            [1, 280455],  # 3 * 93485
            [2, 100560],  # 3 * 33520
            [3, 9165],    # 3 * 3055
        ]
    )


def test_divide_constant(engine):
    bt = get_df_with_test_data(engine)
    bts = bt['inhabitants'] / 1000
    assert isinstance(bts, Series)
    assert_equals_data(
        bts,
        expected_columns=['_index_skating_order', 'inhabitants'],
        expected_data=[
            [1, 93.485],  # 93485 / 1000
            [2, 33.52],   # 33520 / 1000
            [3, 3.055],   #  3055 / 1000
        ]
    )


def test_integer_divide_constant(engine):
    bt = get_df_with_test_data(engine)
    bts = bt['inhabitants'] // 1000
    assert isinstance(bts, Series)
    assert_equals_data(
        bts,
        expected_columns=['_index_skating_order', 'inhabitants'],
        expected_data=[
            [1, 93],  # 93485 // 1000
            [2, 33],  # 33520 // 1000
            [3, 3],   #  3055 // 1000
        ]
    )


def test_int_int_arithmetic(engine):
    helper_test_simple_arithmetic(engine=engine, a=10, b=3)


def test_int_float_arithmetic(engine):
    helper_test_simple_arithmetic(engine=engine, a=10, b=2.25)


def test_int_shifts(engine):
    bt = get_df_with_test_data(engine, full_data_set=True)[['inhabitants']]
    bt['a'] = 8
    bt['b'] = 3
    bt['lshift'] = bt.a << bt.b
    bt['rshift'] = bt.a >> bt.b
    expected = [8, 3, 64, 1]

    bt = bt.sort_index()[:1]  # Only get the first row
    assert_equals_data(
        bt,
        expected_columns=list(bt.all_series.keys()),
        expected_data=[
            [1, 93485, *expected],
        ]
    )

# TODO test aggregation functions
