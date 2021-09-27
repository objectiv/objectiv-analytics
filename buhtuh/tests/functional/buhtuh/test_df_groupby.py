"""
Copyright 2021 Objectiv B.V.
"""
from tests.functional.buhtuh.data_and_utils import assert_equals_data, get_bt_with_test_data


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
        '_index_skating_order_nunique': 'Int64',
        'municipality_nunique': 'Int64',
        'founding_nunique': 'Int64',
        'inhabitants_nunique': 'Int64',
        'skating_order_nunique': 'Int64'
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
        'inhabitants_count': 'Int64',
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
        'inhabitants_count': 'Int64',
        'founding_count': 'Int64'
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
        'inhabitants_min': 'Int64',
        'inhabitants_max': 'Int64',
    }
