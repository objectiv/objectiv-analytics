"""
Copyright 2021 Objectiv B.V.
"""
from buhtuh import BuhTuhSeries
from tests.functional.buhtuh.test_bt import assert_equals_data, get_bt_with_test_data


def test_add_int_constant():
    bt = get_bt_with_test_data()
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
    bt = get_bt_with_test_data()
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
    bt = get_bt_with_test_data()
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


def test_divide_constant():
    bt = get_bt_with_test_data()
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
    bt = get_bt_with_test_data()
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
