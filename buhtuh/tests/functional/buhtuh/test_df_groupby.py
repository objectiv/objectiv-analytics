"""
Copyright 2021 Objectiv B.V.
"""
from decimal import Decimal

import pytest

from buhtuh import BuhTuhSeries, BuhTuhSeriesAbstractNumeric
from buhtuh.partitioning import BuhTuhGroupingList, BuhTuhGroupingSet, BuhTuhRollup, BuhTuhCube
from tests.functional.buhtuh.test_data_and_utils import get_bt_with_test_data, assert_equals_data


def test_group_by_aggregate_syntax():
    bt = get_bt_with_test_data(full_data_set=True)
    btg = bt.groupby('municipality')
    result_bt = btg.count()
    result_bt_str = btg.aggregate('count')
    result_bt_list_str = btg.aggregate(['count'])
    result_bt_func_bounded = btg.aggregate(bt.municipality.count)
    result_bt_func_unbounded = btg.aggregate(BuhTuhSeries.count)

    for r in [result_bt, result_bt_str, result_bt_list_str, result_bt_func_bounded, result_bt_func_unbounded]:
        assert_equals_data(
            r,
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
    btg_series = btg[['inhabitants']]
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

    btg_series = btg[['inhabitants', 'founding']]
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
    result_bt_list_str = btg.aggregate({'inhabitants': ['min', 'max']})
    result_bt_list_func_bound = btg.aggregate({'inhabitants': [bt.inhabitants.min, bt.inhabitants.max]})
    result_bt_list_mixed_bound = btg.aggregate({'inhabitants': [bt.inhabitants.min, 'max']})
    result_bt_list_func_unbound = btg.aggregate(
        {'inhabitants': [BuhTuhSeriesAbstractNumeric.min, BuhTuhSeriesAbstractNumeric.max]})
    result_bt_list_mixed_unbound = btg.aggregate({'inhabitants': ['min', BuhTuhSeriesAbstractNumeric.max]})

    for result_bt in [result_bt_list_str, result_bt_list_func_bound, result_bt_list_mixed_bound,
                      result_bt_list_func_unbound, result_bt_list_mixed_unbound]:
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


def test_dataframe_agg():
    bt = get_bt_with_test_data(full_data_set=True)[['municipality', 'inhabitants']]

    result_bt_str = bt.agg('nunique')
    result_bt_func = bt.agg(BuhTuhSeries.nunique)

    for result_bt in [result_bt_str, result_bt_func]:
        assert_equals_data(
            result_bt,
            expected_columns=['index', 'municipality_nunique', 'inhabitants_nunique'],
            expected_data=[
                [1, 6, 11]
            ]
        )
        assert result_bt.dtypes == {
            'municipality_nunique': 'int64',
            'inhabitants_nunique': 'int64'
        }


def test_dataframe_agg_numeric_only():
    bt = get_bt_with_test_data(full_data_set=True)[['municipality', 'inhabitants']]
    with pytest.raises(AttributeError):
        # contains non-numeric series that don't have 'min' implemented
        bt.agg('sum')
    result_bt_str = bt.agg('sum', numeric_only=True)
    result_bt_func = bt.agg(BuhTuhSeriesAbstractNumeric.sum, numeric_only=True)

    for result_bt in [result_bt_str, result_bt_func]:

        assert_equals_data(
            result_bt,
            expected_columns=['index', 'inhabitants_sum'],
            expected_data=[
                [1, 187325]
            ]
        )
        assert result_bt.dtypes == {
            'inhabitants_sum': 'int64'
        }


def test_series_agg():
    bt = get_bt_with_test_data(full_data_set=True)
    s = bt['inhabitants']
    # single series results
    a1 = s.agg('sum')
    assert isinstance(a1, type(s))
    assert a1.head().iloc[0] == 187325

    a2 = s.sum()
    assert isinstance(a2, type(s))
    assert a2.head().iloc[0] == 187325

    df1 = s.agg(['sum', 'count'])
    assert isinstance(df1.inhabitants_sum, type(s))
    assert isinstance(df1.inhabitants_count, type(s))
    # multiple series results return
    assert df1.inhabitants_sum.head().iloc[0] == 187325
    assert df1.inhabitants_count.head().iloc[0] == 11

    # duplicate result series should raise
    with pytest.raises(ValueError, match="duplicate"):
        s.agg(['sum','sum'])


def test_cube_basics():
    bt = get_bt_with_test_data(full_data_set=False)

    # instant stonks through variable naming
    btc = bt.cube(['municipality','city'])

    assert(isinstance(btc.group_by, BuhTuhCube))
    assert(btc.group_by.get_group_by_columns_sql()
           == 'CUBE ("municipality", "city")')

    result_bt = btc[['inhabitants']].sum()
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

    btr = bt.rollup(['municipality','city'])
    assert(isinstance(btr.group_by, BuhTuhRollup))
    assert(btr.group_by.get_group_by_columns_sql()
           == 'ROLLUP ("municipality", "city")')

    result_bt = btr[['inhabitants']].sum()
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
    # This is not the greatest test, but at least it tests the interface.
    bt = get_bt_with_test_data(full_data_set=False)
    btl1 = bt.groupby([['municipality'], ['city']])
    btl2 = bt.groupby([['municipality'], 'city'])
    btl3 = bt.groupby(['municipality', ['city']])

    assert(btl1 == btl2)
    assert(btl1 == btl3)

    # This is not the greatest test, but at least it tests the interface.
    assert(isinstance(btl1.group_by, BuhTuhGroupingList))
    assert(btl1.group_by.get_group_by_columns_sql()
           == '("municipality"), ("city")')

    result_bt = btl1[['inhabitants']].sum()
    assert_equals_data(
        result_bt,
        order_by=['municipality', 'city'],
        expected_columns=['municipality', 'city', 'inhabitants_sum'],
        expected_data=[
            ['Leeuwarden', 'Ljouwert', Decimal('93485')],
            ['Súdwest-Fryslân', 'Drylts', Decimal('3055')],
            ['Súdwest-Fryslân', 'Snits', Decimal('33520')]
        ]
    )

def test_grouping_set_basics():
    # This is not the greatest test, but at least it tests the interface.
    bt = get_bt_with_test_data(full_data_set=False)
    bts1 = bt.groupby((('municipality'), ('city')))
    bts2 = bt.groupby((('municipality'), 'city'))
    bts3 = bt.groupby(('municipality', ('city')))

    assert(bts1 == bts2)
    assert(bts1 == bts3)

    assert(isinstance(bts1.group_by, BuhTuhGroupingSet))
    assert(bts1.group_by.get_group_by_columns_sql()
           == 'GROUPING SETS (("municipality"), ("city"))')

    result_bt = bts1[['inhabitants']].sum()

    # order of index is dynamic since it's a set. Make sure it's in the right order.
    # index_keys = list(result_bt.index.keys())
    # index_0 = index_keys.index(expected_columns[0])
    # index_1 = index_keys.index(expected_columns[1])
    # expected_data = [[r[index_0], r[index_1], r[2]] for r in expected_data]

    assert_equals_data(
        result_bt,
        order_by=['municipality', 'city'],
        expected_columns=['municipality', 'city', 'inhabitants_sum'],
        expected_data = [
            ['Leeuwarden', None, 93485], ['Súdwest-Fryslân', None, 36575],
            [None, 'Drylts', 3055], [None, 'Ljouwert', 93485], [None, 'Snits', 33520]
        ]
    )


def test_groupby_frame_split_series_aggregation():
    bt = get_bt_with_test_data(full_data_set=False)[['municipality', 'inhabitants', 'founding']]
    btg1 = bt.groupby(['municipality'])

    r1 = btg1['founding'].sum()
    r2 = bt.groupby(['municipality']).sum()['founding_sum']
    r3 = bt.groupby(['municipality'])[['founding']].sum()['founding_sum']
    assert (r1.head().values == r2.head().values).all()
    assert (r1.head().values == r3.head().values).all()

    # Does math work?
    r4 = btg1['inhabitants'].sum()
    r5 = btg1['founding'].sum() + btg1['inhabitants'].sum()
    assert ((r1.head().values + r4.head().values) == r5.head().values).all()

    # FIXME aggregation functions can not be nested without materialization in between
    r6 = r4.sum()  # This should raise
    with pytest.raises(Exception):
        r6.head() # this should not, but that's not how it currently works


def test_groupby_frame_split_recombine():
    bt = get_bt_with_test_data(full_data_set=False)[['municipality', 'inhabitants', 'founding']]
    btg1 = bt.groupby(['municipality'])[['inhabitants', 'founding']]
    btg1a = btg1[['inhabitants']]
    btg1b = btg1['founding']

    r0 = btg1.sum()

    assert btg1.group_by == btg1a.group_by
    assert btg1.group_by == btg1b.group_by

    # recombine from same parent
    btg1a['founding'] = btg1b
    r1 = btg1a.sum()
    assert btg1a == btg1

    # can not add columns from grouped df to ungrouped df
    with pytest.raises(ValueError, match="Index of assigned value does not match index of DataFrame"):
        bt2 = bt.drop(columns=['founding'])
        bt2['founding'] = btg1b

    # can not add columns from ungrouped df to grouped df
    with pytest.raises(ValueError, match="Index of assigned value does not match index of DataFrame"):
        bt2 = btg1.drop(columns=['founding'])
        bt2['founding'] = bt['founding']

    # create new grouping df, but with same grouping
    btg2 = bt.groupby(['municipality'])[['inhabitants', 'founding']]
    assert btg1.group_by == btg2.group_by
    assert btg1 == btg2

    # recombine from different parent with same grouping
    btg2.drop(columns=['founding'], inplace=True)
    btg2['founding'] = btg1b
    r2 = btg1a.sum()
    assert btg2 == btg1

    for r in [r0, r1, r2]:
        assert_equals_data(
            r,
            order_by=['municipality'],
            expected_columns=['municipality', 'inhabitants_sum', 'founding_sum'],

            expected_data=[
                ['Leeuwarden', 93485, 1285],
                ['Súdwest-Fryslân', 36575, 2724]
            ]
        )

def test_groupby_frame_split_recombine_aggregation_applied():
    bt = get_bt_with_test_data(full_data_set=False)[['municipality', 'inhabitants', 'founding']]
    group1 = bt.groupby('municipality')
    subgroup = group1[['founding', 'inhabitants']]
    inhabitants_sum = subgroup['inhabitants'].sum()
    founding_inhabitants_sum = group1[['founding', 'inhabitants']].sum()
    only_inhabitants = founding_inhabitants_sum[['inhabitants_sum']]
    founding_mean = group1['founding'].mean()

    # recombine
    founding_inhabitants_sum['founding_mean'] = founding_mean

    r1 = inhabitants_sum.to_frame()
    r1['founding_sum'] = group1['founding'].sum()
    r1['founding_mean'] = founding_mean
    r1.rename(columns={'inhabitants': 'inhabitants_sum'}, inplace=True)

    for r in [founding_inhabitants_sum, r1]:
        assert_equals_data(
            r,
            order_by=['municipality'],
            expected_columns=['municipality', 'inhabitants_sum', 'founding_sum', 'founding_mean'],

            expected_data=[
                ['Leeuwarden', 93485, 1285, 1285],
                ['Súdwest-Fryslân', 36575, 2724, 1362]
            ]
        )


def test_materialize_on_double_aggregation():
    # When we use a aggregation function twice, we need to materialize the node in between, because it's not
    # possible to nest the aggregate function calls. I.e. you cannot do `avg(sum(x))`
    # You cannot
    bt = get_bt_with_test_data(full_data_set=True)
    btg = bt.groupby('municipality')[['founding']]
    btg = btg.sum()
    with pytest.raises(ValueError, match='already aggregated'):
        btg.mean('founding_sum')
    # After manually materializing the frame everything is OK again.
    btg = btg.get_df_materialized_model()
    btg = btg.mean('founding_sum')
    assert_equals_data(btg, expected_columns=['index', 'founding_sum_mean'], expected_data=[[1,	2413.5]])
