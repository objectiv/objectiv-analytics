"""
Copyright 2021 Objectiv B.V.
"""
from decimal import Decimal

import pytest

from bach import DataFrame
from tests.functional.bach.test_data_and_utils import get_bt_with_test_data, get_bt_with_food_data, \
    assert_equals_data, get_bt_with_railway_data


def test_merge_basic():
    bt = get_bt_with_test_data(full_data_set=False)[['skating_order', 'city']]
    mt = get_bt_with_food_data()[['skating_order', 'food']]
    result = bt.merge(mt)
    assert isinstance(result, DataFrame)
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
    assert isinstance(result, DataFrame)
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
    assert isinstance(result, DataFrame)
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
    assert isinstance(result, DataFrame)
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
    assert isinstance(result, DataFrame)
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

    # Note that the results here do not match exactly with Pandas. This is a known discrepancy, reproducing
    # Pandas logic is not trivial and perhaps not a 'better' solution. For now we'll just leave this as it
    # is.
    # Code to reproduce this test in pure pandas:
    #  bt = pd.DataFrame([(1, 1, 2), (2, 2, 3), (3, 3, 4)], columns=['_index_skating_order', 'skating_order', 'city'])
    #  bt.set_index(['_index_skating_order'], inplace=True)
    #  mt = pd.DataFrame([(1, 1, 2), (2, 2, 3), (4, 4, 4)], columns=['_index_skating_order', 'skating_order', 'food'])
    #  mt.set_index(['_index_skating_order'], inplace=True)
    #  bt.merge(mt, left_index=True, right_on='skating_order')

    result = bt.merge(mt, left_index=True, right_on='skating_order')
    assert isinstance(result, DataFrame)
    assert_equals_data(result, expected_columns=expected_columns, expected_data=expected_data)

    result = bt.merge(mt, left_on='skating_order', right_index=True)
    assert isinstance(result, DataFrame)
    assert_equals_data(result, expected_columns=expected_columns, expected_data=expected_data)

    result = bt.merge(mt, left_index=True, right_index=True)
    assert isinstance(result, DataFrame)
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

    # Test empty index behaviour.
    mtr = mt.reset_index()
    btr = bt.reset_index()
    with pytest.raises(
            ValueError,
            match="Len of left_on .* does not match that of right_on"):
        bt.merge(mtr, left_index=True, right_index=True)

    with pytest.raises(
            ValueError,
            match="Len of left_on .* does not match that of right_on"):
        btr.merge(mt, left_index=True, right_index=True)

    with pytest.raises(ValueError, match="No columns to perform merge on"):
        result = btr.merge(mtr, left_index=True, right_index=True)


def test_merge_suffixes():
    bt = get_bt_with_test_data(full_data_set=False)[['skating_order', 'city']]
    mt = get_bt_with_food_data()[['skating_order', 'food']]
    result = bt.merge(mt, left_on='_index_skating_order', right_on='skating_order', suffixes=('_AA', '_BB'))
    assert isinstance(result, DataFrame)
    assert_equals_data(
        result,
        expected_columns=[
            '_index_skating_order_AA',
            '_index_skating_order_BB',
            'skating_order_AA',
            'city',
            'skating_order_BB',
            'food'
        ],
        expected_data=[
            [1, 1, 1, 'Ljouwert', 1, 'Sûkerbôlle'],
            [2, 2, 2, 'Snits', 2, 'Dúmkes'],
        ]
    )


def test_merge_mixed_columns():
    bt = get_bt_with_test_data(full_data_set=False)[['skating_order', 'city']]
    mt = get_bt_with_railway_data()[['station', 'platforms']]
    # join _index_skating_order on the 'platforms' column
    result = bt.merge(mt, how='inner', left_on='skating_order', right_on='platforms')
    assert isinstance(result, DataFrame)
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
    assert isinstance(result, DataFrame)
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
    assert isinstance(result, DataFrame)
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
    assert isinstance(result, DataFrame)
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

    # outer join on index
    mt2 = get_bt_with_test_data(full_data_set=True)
    result_merge = bt.merge(mt2, how='outer', left_index=True, right_index=True)

    assert_equals_data(
        result_merge,
        expected_columns=[
            '_index_skating_order',
            'skating_order_x', 'city_x', 'skating_order_y', 'city_y', 'municipality', 'inhabitants', 'founding'
        ],
        # in bt there is no row with _index_skating_order >= 4, in mt2 there is. expect to show the union of
        # indexes.
        expected_data=[
            [1, 1.0, 'Ljouwert', 1, 'Ljouwert', 'Leeuwarden', 93485, 1285],
            [2, 2.0, 'Snits', 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456],
            [3, 3.0, 'Drylts', 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268],
            [4, None, None, 4, 'Sleat', 'De Friese Meren', 700, 1426],
            [5, None, None, 5, 'Starum', 'Súdwest-Fryslân', 960, 1061],
            [6, None, None, 6, 'Hylpen', 'Súdwest-Fryslân', 870, 1225],
            [7, None, None, 7, 'Warkum', 'Súdwest-Fryslân', 4440, 1399],
            [8, None, None, 8, 'Boalsert', 'Súdwest-Fryslân', 10120, 1455],
            [9, None, None, 9, 'Harns', 'Harlingen', 14740, 1234],
            [10, None, None, 10, 'Frjentsjer', 'Waadhoeke', 12760, 1374],
            [11, None, None, 11, 'Dokkum', 'Noardeast-Fryslân', 12675, 1298]
        ]
    )


def test_merge_cross_join():
    bt = get_bt_with_test_data(full_data_set=False)[['city']]
    mt = get_bt_with_food_data()[['food']]
    result = bt.merge(mt, how='cross')
    assert isinstance(result, DataFrame)

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

    # empty index cross merge also supported
    btr = bt.reset_index()
    mtr = mt.reset_index()
    result2 = btr.merge(mtr, how='cross')
    assert isinstance(result, DataFrame)

    # series order is different though
    assert_equals_data(
        result2,
        expected_columns=[
            '_index_skating_order_x', 'city', '_index_skating_order_y', 'food'
        ],
        # in bt there is no row with skating_order == 4, so for the station with 4 platforms we
        # expect to join None values.
        expected_data=[
            [1, 'Ljouwert', 1, 'Sûkerbôlle'], [1, 'Ljouwert', 2, 'Dúmkes'],
            [1, 'Ljouwert', 4, 'Grutte Pier Bier'], [2, 'Snits', 1, 'Sûkerbôlle'], [2, 'Snits', 2, 'Dúmkes'],
            [2, 'Snits', 4, 'Grutte Pier Bier'], [3, 'Drylts', 1, 'Sûkerbôlle'], [3, 'Drylts', 2, 'Dúmkes'],
            [3, 'Drylts', 4, 'Grutte Pier Bier']],
        order_by=['_index_skating_order_x', '_index_skating_order_y']
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
        expected_columns=['_index_skating_order_x', '_index_skating_order_y', 'skating_order', 'city',
                          'inhabitants', 'food'],
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


def test_merge_non_materialized():
    bt = get_bt_with_test_data(full_data_set=False)[['municipality', 'inhabitants']]
    mt1 = bt.groupby('municipality')[['inhabitants']].sum()
    mt2 = bt.groupby('municipality')[['inhabitants']].mean()

    # check that merge properly materializes if required
    r1 = mt1.materialize().merge(mt2.materialize(), on='municipality')
    r2 = mt1.merge(mt2, on='municipality')
    r3 = mt1.materialize().merge(mt2, on='municipality')
    r4 = mt1.merge(mt2.materialize(), on='municipality')

    for r in [r1, r2, r3, r4]:
        assert_equals_data(
            r,
            expected_columns=['municipality', 'inhabitants_sum', 'inhabitants_mean'],
            expected_data=[
                ['Leeuwarden', Decimal('93485'), Decimal('93485.000000000000')],
                ['Súdwest-Fryslân', Decimal('36575'), Decimal('18287.500000000000')]
            ]
        )
