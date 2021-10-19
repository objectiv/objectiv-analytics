"""
Copyright 2021 Objectiv B.V.
"""
from buhtuh.partitioning import BuhTuhGroupingList, BuhTuhGroupingSet
from tests.functional.buhtuh.test_data_and_utils import get_bt_with_test_data, assert_equals_data


def test_group_by_basics():
    bt = get_bt_with_test_data(full_data_set=True)
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
        '_index_skating_order_count': 'int64',
        'city_count': 'int64',
        'founding_count': 'int64',
        'inhabitants_count': 'int64',
        'skating_order_count': 'int64'
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
        '_index_skating_order_nunique': 'int64',
        'city_count': 'int64',
        'founding_max': 'int64',
        'inhabitants_min': 'int64',
        'skating_order_sum': 'int64'
    }


def test_group_by_all():
    bt = get_bt_with_test_data(full_data_set=True)
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
        'index': 'int64'
    }
    assert result_bt.dtypes == {
        '_index_skating_order_nunique': 'int64',
        'city_nunique': 'int64',
        'founding_nunique': 'int64',
        'inhabitants_nunique': 'int64',
        'municipality_nunique': 'int64',
        'skating_order_nunique': 'int64'
    }


def test_group_by_expression():
    bt = get_bt_with_test_data(full_data_set=True)
    btg = bt.groupby(bt['city'].slice(None, 1))
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
        '_index_skating_order_nunique': 'int64',
        'municipality_nunique': 'int64',
        'founding_nunique': 'int64',
        'inhabitants_nunique': 'int64',
        'skating_order_nunique': 'int64'
    }


def test_group_by_basics_series():
    bt = get_bt_with_test_data(full_data_set=True)
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
        'inhabitants_count': 'int64',
    }

    btg_series = btg['inhabitants', 'founding']
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
        'inhabitants_count': 'int64',
        'founding_count': 'int64'
    }


def test_group_by_multiple_aggregations_on_same_series():
    bt = get_bt_with_test_data(full_data_set=True)
    btg = bt.groupby('municipality')
    result_bt = btg.aggregate(['inhabitants', 'inhabitants'], ['min', 'max'])
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
        'inhabitants_min': 'int64',
        'inhabitants_max': 'int64',
    }

def test_cube_basics():
    bt = get_bt_with_test_data(full_data_set=False)

    # instant stonks through variable naming
    btc = bt.groupby(['municipality','city']).cube()

    result_bt = btc['inhabitants'].sum()
    assert_equals_data(
        result_bt,
        order_by=['municipality','city'],
        expected_columns=['municipality', 'city', 'inhabitants_sum'],
        expected_data=[
            ['Leeuwarden', 'Ljouwert', 93485],
            ['Leeuwarden', None, 93485],
            ['Súdwest-Fryslân', 'Drylts', 3055],
            ['Súdwest-Fryslân', 'Snits', 33520],
            ['Súdwest-Fryslân', None, 36575],
            [None, 'Drylts', 3055],
            [None, 'Ljouwert', 93485],
            [None, 'Snits', 33520],
            [None, None, 130060]
        ]
    )

def test_rollup_basics():
    bt = get_bt_with_test_data(full_data_set=False)

    btc = bt.groupby(['municipality','city']).rollup()

    result_bt = btc['inhabitants'].sum()
    assert_equals_data(
        result_bt,
        order_by=['municipality','city'],
        expected_columns=['municipality', 'city', 'inhabitants_sum'],
        expected_data=[
            ['Leeuwarden', 'Ljouwert', 93485],
            ['Leeuwarden', None, 93485],
            ['Súdwest-Fryslân', 'Drylts', 3055],
            ['Súdwest-Fryslân', 'Snits', 33520],
            ['Súdwest-Fryslân', None, 36575],
            [None, None, 130060]
        ]
    )


def test_rollup_basics():
    bt = get_bt_with_test_data(full_data_set=False)

    btr = bt.groupby(['municipality','city']).rollup()

    result_bt = btr['inhabitants'].sum()
    assert_equals_data(
        result_bt,
        order_by=['municipality','city'],
        expected_columns=['municipality', 'city', 'inhabitants_sum'],
        expected_data=[
            ['Leeuwarden', 'Ljouwert', 93485],
            ['Leeuwarden', None, 93485],
            ['Súdwest-Fryslân', 'Drylts', 3055],
            ['Súdwest-Fryslân', 'Snits', 33520],
            ['Súdwest-Fryslân', None, 36575],
            [None, None, 130060]
        ]
    )

def test_grouping_list_basics():
    bt = get_bt_with_test_data(full_data_set=False)

    btm = bt.groupby(['municipality'])
    btc = bt.groupby(['city'])
    bts = BuhTuhGroupingList([btm,btc])

    result_bt = bts['inhabitants'].sum()
    assert_equals_data(
        result_bt,
        order_by=['municipality','city'],
        expected_columns=['municipality', 'city', 'inhabitants_sum'],
        expected_data=[
            ['Leeuwarden', 'Ljouwert', 93485], ['Súdwest-Fryslân', 'Drylts', 3055], ['Súdwest-Fryslân', 'Snits', 33520]
        ]
    )

def test_grouping_set_basics():
    bt = get_bt_with_test_data(full_data_set=False)

    btm = bt.groupby(['municipality'])
    btc = bt.groupby(['city'])
    bts = BuhTuhGroupingSet([btm, btc])

    result_bt = bts['inhabitants'].sum()
    assert_equals_data(
        result_bt,
        order_by=['municipality','city'],
        expected_columns=['municipality', 'city', 'inhabitants_sum'],
        expected_data=[
            ['Leeuwarden', None, 93485], ['Súdwest-Fryslân', None, 36575],
            [None, 'Drylts', 3055], [None, 'Ljouwert', 93485], [None, 'Snits', 33520]
        ]
    )