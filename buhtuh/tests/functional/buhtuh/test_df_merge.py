"""
Copyright 2021 Objectiv B.V.
"""
from buhtuh import BuhTuhDataFrame
from tests.functional.buhtuh.data_and_utils import get_bt_with_test_data, get_bt_with_food_data, \
    assert_equals_data, get_bt_with_railway_data


def test_merge_basic():
    bt = get_bt_with_test_data(full_data_set=False)[['skating_order', 'city']]
    mt = get_bt_with_food_data()[['skating_order', 'food']]
    result = bt.merge(mt)
    assert isinstance(result, BuhTuhDataFrame)
    assert_equals_data(
        result,
        expected_columns=[
            '_index_skating_order_x',
            '_index_skating_order_y',
            'skating_order',  # skating_order is the 'on' column, so it is not duplicated
            'city',
            'food'
        ],
        expected_data=[
            [1, 1, 1, 'Ljouwert', 'Sûkerbôlle'],
            [2, 2, 2, 'Snits', 'Dúmkes'],
        ]
    )


def test_merge_basic_on():
    bt = get_bt_with_test_data(full_data_set=False)[['skating_order', 'city']]
    mt = get_bt_with_food_data()[['skating_order', 'food']]
    result = bt.merge(mt, on='skating_order')
    assert isinstance(result, BuhTuhDataFrame)
    assert_equals_data(
        result,
        expected_columns=[
            '_index_skating_order_x',
            '_index_skating_order_y',
            'skating_order',
            'city',
            'food'
        ],
        expected_data=[
            [1, 1, 1, 'Ljouwert', 'Sûkerbôlle'],
            [2, 2, 2, 'Snits', 'Dúmkes'],
        ]
    )


def test_merge_basic_on_series():
    bt = get_bt_with_test_data(full_data_set=False)[['skating_order', 'city']]
    mt = get_bt_with_food_data()['food']
    result = bt.merge(mt, on='_index_skating_order')
    assert isinstance(result, BuhTuhDataFrame)
    assert_equals_data(
        result,
        expected_columns=[
            '_index_skating_order',
            'skating_order',
            'city',
            'food'
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 'Sûkerbôlle'],
            [2, 2, 'Snits', 'Dúmkes'],
        ]
    )


def test_merge_basic_left_on_right_on_same_column():
    bt = get_bt_with_test_data(full_data_set=False)[['skating_order', 'city']]
    mt = get_bt_with_food_data()[['skating_order', 'food']]
    result = bt.merge(mt, left_on='skating_order', right_on='skating_order')
    assert isinstance(result, BuhTuhDataFrame)
    assert_equals_data(
        result,
        expected_columns=[
            '_index_skating_order_x',
            '_index_skating_order_y',
            'skating_order',
            'city',
            'food'
        ],
        expected_data=[
            [1, 1, 1, 'Ljouwert', 'Sûkerbôlle'],
            [2, 2, 2, 'Snits', 'Dúmkes'],
        ]
    )


def test_merge_basic_left_on_right_on_different_column():
    bt = get_bt_with_test_data(full_data_set=False)[['skating_order', 'city']]
    mt = get_bt_with_railway_data()[['town', 'station']]
    result = bt.merge(mt, left_on='city', right_on='town')
    assert isinstance(result, BuhTuhDataFrame)
    assert_equals_data(
        result,
        expected_columns=[
            '_index_skating_order',
            '_index_station_id',
            'skating_order',
            'city',
            'town',
            'station'
        ],
        expected_data=[
            [3, 1, 3, 'Drylts', 'Drylts', 'IJlst'],
            [1, 4, 1, 'Ljouwert', 'Ljouwert', 'Leeuwarden'],
            [1, 5, 1, 'Ljouwert', 'Ljouwert', 'Camminghaburen'],
            [2, 6, 2, 'Snits', 'Snits', 'Sneek'],
            [2, 7, 2, 'Snits', 'Snits', 'Sneek Noord'],
        ],
        order_by='_index_station_id'
    )


def test_merge_basic_on_indexes():
    bt = get_bt_with_test_data(full_data_set=False)[['skating_order', 'city']]
    mt = get_bt_with_food_data()[['skating_order', 'food']]

    expected_columns = [
        '_index_skating_order_x',
        '_index_skating_order_y',
        'skating_order_x',
        'city',
        'skating_order_y',
        'food'
    ]
    expected_data = [
        [1, 1, 1, 'Ljouwert', 1, 'Sûkerbôlle'],
        [2, 2, 2, 'Snits', 2, 'Dúmkes'],
    ]

    result = bt.merge(mt, left_index=True, right_on='skating_order')
    assert isinstance(result, BuhTuhDataFrame)
    assert_equals_data(result, expected_columns=expected_columns, expected_data=expected_data)

    result = bt.merge(mt, left_on='skating_order', right_index=True)
    assert isinstance(result, BuhTuhDataFrame)
    assert_equals_data(result, expected_columns=expected_columns, expected_data=expected_data)

    result = bt.merge(mt, left_index=True, right_index=True)
    assert isinstance(result, BuhTuhDataFrame)
    # `on` column is same for left and right, so it is not duplicated in this case
    assert_equals_data(
        result,
        expected_columns=[
            '_index_skating_order',
            'skating_order_x',
            'city',
            'skating_order_y',
            'food'
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 1, 'Sûkerbôlle'],
            [2, 2, 'Snits', 2, 'Dúmkes'],
        ]
    )


def test_merge_self():
    bt1 = get_bt_with_test_data(full_data_set=False)[['city']]
    bt2 = get_bt_with_test_data(full_data_set=False)[['inhabitants']]
    result = bt1.merge(bt2, on='_index_skating_order')
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
    bt = get_bt_with_test_data(full_data_set=False)[['skating_order', 'city', 'inhabitants']]
    mt = get_bt_with_food_data()[['skating_order', 'food']]
    result = bt[bt['skating_order'] != 1].merge(mt[['food']], on='_index_skating_order')
    assert_equals_data(
        result,
        # This is weak. Ordering is broken.
        expected_columns=['_index_skating_order', 'skating_order', 'city', 'inhabitants', 'food'],
        expected_data=[
            [2, 2, 'Snits', 33520, 'Dúmkes'],
        ]
    )


def test_merge_expression_columns():
    bt = get_bt_with_test_data(full_data_set=False)[['skating_order', 'city', 'inhabitants']]
    mt = get_bt_with_food_data()[['skating_order', 'food']]
    bt['skating_order'] += 2
    mt['skating_order'] += 2

    result = bt.merge(mt, on=['skating_order'])
    assert_equals_data(
        result,
        # This is weak. Ordering is broken.
        expected_columns=['_index_skating_order_x', '_index_skating_order_y', 'skating_order', 'city', 'inhabitants', 'food'],
        expected_data=[
            [1, 1, 3, 'Ljouwert', 93485, 'Sûkerbôlle'],
            [2, 2, 4, 'Snits', 33520, 'Dúmkes'],
        ]
    )


def test_merge_expression_columns_regression():
    bt = get_bt_with_test_data(full_data_set=False)[['skating_order', 'city', 'inhabitants']]
    mt = get_bt_with_food_data()[['skating_order', 'food']]
    bt['x'] = bt['skating_order'] == 3
    bt['y'] = bt['skating_order'] == 3
    bt['z'] = bt['x'] & bt['y']
    result = bt.merge(mt, on=['skating_order'])
    assert_equals_data(
        result,
        expected_columns=['_index_skating_order_x', '_index_skating_order_y', 'skating_order', 'city',
                          'inhabitants', 'x', 'y', 'z', 'food'],
        expected_data=[
            [1, 1, 1, 'Ljouwert', 93485, False, False, False, 'Sûkerbôlle'],
            [2, 2, 2, 'Snits', 33520, False, False, False, 'Dúmkes']
        ]
    )


def test_merge_mixed_columns():
    bt = get_bt_with_test_data(full_data_set=False)[['skating_order', 'city']]
    mt = get_bt_with_railway_data()[['station', 'platforms']]
    # join _index_skating_order on the 'platforms' column
    result = bt.merge(mt, how='inner', left_on='skating_order', right_on='platforms')
    assert isinstance(result, BuhTuhDataFrame)
    assert_equals_data(
        result,
        expected_columns=[
            '_index_skating_order',
            '_index_station_id',
            'skating_order',
            'city',
            'station',
            'platforms'
        ],
        expected_data=[
            [1, 1, 1, 'Ljouwert', 'IJlst', 1],
            [1, 2, 1, 'Ljouwert', 'Heerenveen', 1],
            [1, 5, 1, 'Ljouwert', 'Camminghaburen', 1],
            [2, 3, 2, 'Snits', 'Heerenveen IJsstadion', 2],
            [2, 6, 2, 'Snits', 'Sneek', 2],
            [2, 7, 2, 'Snits', 'Sneek Noord', 2],

        ],
        order_by=['_index_skating_order', '_index_station_id']
    )


def test_merge_left_join():
    bt = get_bt_with_test_data(full_data_set=False)[['skating_order', 'city']]
    mt = get_bt_with_railway_data()[['station', 'platforms']]
    # join _index_skating_order on the 'platforms' column
    result = bt.merge(mt, how='left', left_on='skating_order', right_on='platforms')
    assert isinstance(result, BuhTuhDataFrame)
    assert_equals_data(
        result,
        expected_columns=[
            '_index_skating_order',
            '_index_station_id',
            'skating_order',
            'city',
            'station',
            'platforms'
        ],
        expected_data=[
            [1, 1, 1, 'Ljouwert', 'IJlst', 1],
            [1, 2, 1, 'Ljouwert', 'Heerenveen', 1],
            [1, 5, 1, 'Ljouwert', 'Camminghaburen', 1],
            [2, 3, 2, 'Snits', 'Heerenveen IJsstadion', 2],
            [2, 6, 2, 'Snits', 'Sneek', 2],
            [2, 7, 2, 'Snits', 'Sneek Noord', 2],
            [3, None, 3, 'Drylts', None, None],
        ],
        order_by=['_index_skating_order', '_index_station_id']
    )


def test_merge_right_join():
    bt = get_bt_with_test_data(full_data_set=False)[['skating_order', 'city']]
    mt = get_bt_with_railway_data()[['station', 'platforms']]
    result = bt.merge(mt, how='right', left_on='skating_order', right_on='platforms')
    assert isinstance(result, BuhTuhDataFrame)
    assert_equals_data(
        result,
        expected_columns=[
            '_index_skating_order',
            '_index_station_id',
            'skating_order',
            'city',
            'station',
            'platforms'
        ],
        expected_data=[
            [1, 1, 1, 'Ljouwert', 'IJlst', 1],
            [1, 2, 1, 'Ljouwert', 'Heerenveen', 1],
            [2, 3, 2, 'Snits', 'Heerenveen IJsstadion', 2],
            [None, 4, None, None, 'Leeuwarden', 4],
            [1, 5, 1, 'Ljouwert', 'Camminghaburen', 1],
            [2, 6, 2, 'Snits', 'Sneek', 2],
            [2, 7, 2, 'Snits', 'Sneek Noord', 2],
        ],
        order_by=['_index_station_id']
    )


def test_merge_outer_join():
    bt = get_bt_with_test_data(full_data_set=False)[['skating_order', 'city']]
    mt = get_bt_with_railway_data()[['station', 'platforms']]
    result = bt.merge(mt, how='outer', left_on='skating_order', right_on='platforms')
    assert isinstance(result, BuhTuhDataFrame)
    assert_equals_data(
        result,
        expected_columns=[
            '_index_skating_order',
            '_index_station_id',
            'skating_order',
            'city',
            'station',
            'platforms'
        ],
        # in bt there is no row with skating_order == 4, so for the station with 4 platforms we
        # expect to join None values.
        expected_data=[
            [1, 1, 1, 'Ljouwert', 'IJlst', 1],
            [1, 2, 1, 'Ljouwert', 'Heerenveen', 1],
            [2, 3, 2, 'Snits', 'Heerenveen IJsstadion', 2],
            [None, 4, None, None, 'Leeuwarden', 4],
            [1, 5, 1, 'Ljouwert', 'Camminghaburen', 1],
            [2, 6, 2, 'Snits', 'Sneek', 2],
            [2, 7, 2, 'Snits', 'Sneek Noord', 2],
            [3, None, 3, 'Drylts', None, None],
        ],
        order_by=['_index_station_id']
    )


def test_merge_cross_join():
    bt = get_bt_with_test_data(full_data_set=False)[['city']]
    mt = get_bt_with_food_data()[['food']]
    result = bt.merge(mt, how='cross')
    assert isinstance(result, BuhTuhDataFrame)
    assert_equals_data(
        result,
        expected_columns=[
            '_index_skating_order_x',
            '_index_skating_order_y',
            'city',
            'food'
        ],
        # in bt there is no row with skating_order == 4, so for the station with 4 platforms we
        # expect to join None values.
        expected_data=[
            [1, 1, 'Ljouwert', 'Sûkerbôlle'],
            [1, 2, 'Ljouwert', 'Dúmkes'],
            [1, 4, 'Ljouwert', 'Grutte Pier Bier'],
            [2, 1, 'Snits', 'Sûkerbôlle'],
            [2, 2, 'Snits', 'Dúmkes'],
            [2, 4, 'Snits', 'Grutte Pier Bier'],
            [3, 1, 'Drylts', 'Sûkerbôlle'],
            [3, 2, 'Drylts', 'Dúmkes'],
            [3, 4, 'Drylts', 'Grutte Pier Bier'],
        ],
        order_by=['_index_skating_order_x', '_index_skating_order_y']
    )
