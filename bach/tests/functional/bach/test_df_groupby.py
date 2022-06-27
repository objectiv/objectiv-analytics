"""
Copyright 2021 Objectiv B.V.
"""
from decimal import Decimal

import numpy
import pandas as pd
import pytest
from psycopg2._range import NumericRange

from bach import Series, SeriesAbstractNumeric, SeriesNumericInterval
from bach.partitioning import GroupingList, GroupingSet, Rollup, Cube
from sql_models.util import is_postgres, is_bigquery
from tests.functional.bach.test_data_and_utils import assert_equals_data, get_df_with_test_data


def test_group_by_all(engine):
    bt = get_df_with_test_data(engine, full_data_set=True)
    btg = bt.groupby()
    result_bt = btg.nunique()

    assert result_bt.index == {}
    for d in result_bt.data.values():
        assert d.expression.is_single_value

    # no materialization has taken place yet.
    assert btg.base_node == bt.base_node
    assert result_bt.base_node == bt.base_node

    assert_equals_data(
        result_bt,
        expected_columns=['skating_order_nunique', 'city_nunique', 'municipality_nunique', 'inhabitants_nunique', 'founding_nunique'],
        order_by='skating_order_nunique',
        expected_data=[
            [11, 11, 6, 11, 11],
        ]
    )
    assert result_bt.dtypes == {
        'city_nunique': 'int64',
        'founding_nunique': 'int64',
        'inhabitants_nunique': 'int64',
        'municipality_nunique': 'int64',
        'skating_order_nunique': 'int64'
    }


def test_group_by_single_syntax(engine):
    bt = get_df_with_test_data(engine, full_data_set=True)
    result_bt_single_str = bt.groupby(['municipality']).count()
    result_bt_single_series = bt.groupby([bt.municipality]).count()

    for r in [result_bt_single_str, result_bt_single_series]:
        # no materialization has taken place yet.
        assert r.base_node == bt.base_node

        for d in r.data.values():
            assert not d.expression.is_single_value

        assert_equals_data(
            r,
            expected_columns=['municipality', 'skating_order_count', 'city_count', 'inhabitants_count', 'founding_count'],
            order_by=['skating_order_count', 'municipality'],
            expected_data=[
                ['De Friese Meren', 1, 1, 1, 1],
                ['Harlingen', 1, 1, 1, 1],
                ['Leeuwarden', 1, 1, 1, 1],
                ['Noardeast-Fryslân', 1, 1, 1, 1],
                ['Waadhoeke', 1, 1, 1, 1],
                ['Súdwest-Fryslân', 6, 6, 6, 6],
            ]
        )
        assert r.index_dtypes == {
            'municipality': 'string'
        }
        assert r.dtypes == {
            'city_count': 'int64',
            'founding_count': 'int64',
            'inhabitants_count': 'int64',
            'skating_order_count': 'int64'
        }


def test_group_by_multiple_syntax(engine):
    # Test whether multiple columns are accepted in different forms
    bt = get_df_with_test_data(engine, full_data_set=True)
    result_bt_list = bt.groupby(['municipality', 'city']).count()
    result_bt_list_series = bt.groupby([bt.municipality, bt.city]).count()
    result_bt_list_mixed1 = bt.groupby(['municipality', bt.city]).count()
    result_bt_list_mixed2 = bt.groupby([bt.municipality, 'city']).count()

    for r in [result_bt_list, result_bt_list_series, result_bt_list_series,
              result_bt_list_mixed1, result_bt_list_mixed2]:
        # no materialization has taken place yet.
        assert r.base_node == bt.base_node
        for d in r.data.values():
            assert not d.expression.is_single_value

        assert_equals_data(
            r,
            expected_columns=['municipality', 'city', 'skating_order_count', 'inhabitants_count', 'founding_count'],
            order_by=['skating_order_count', 'municipality', 'city'],
            expected_data=[
                ['De Friese Meren', 'Sleat', 1, 1, 1],
                ['Harlingen', 'Harns', 1, 1, 1],
                ['Leeuwarden', 'Ljouwert', 1, 1, 1],
                ['Noardeast-Fryslân', 'Dokkum', 1, 1, 1],
                ['Súdwest-Fryslân', 'Boalsert', 1, 1, 1],
                ['Súdwest-Fryslân', 'Drylts', 1, 1, 1],
                ['Súdwest-Fryslân', 'Hylpen', 1, 1, 1],
                ['Súdwest-Fryslân', 'Snits', 1, 1, 1],
                ['Súdwest-Fryslân', 'Starum', 1, 1, 1],
                ['Súdwest-Fryslân', 'Warkum', 1, 1, 1],
                ['Waadhoeke', 'Frjentsjer', 1, 1, 1]
            ]
        )
        assert r.index_dtypes == {
            'municipality': 'string',
            'city': 'string'
        }
        assert r.dtypes == {
            'founding_count': 'int64',
            'inhabitants_count': 'int64',
            'skating_order_count': 'int64'
        }


def test_group_by_expression(engine):
    bt = get_df_with_test_data(engine, full_data_set=True)
    btg = bt.groupby(bt['city'].str[:1])
    result_bt = btg.nunique()
    assert result_bt.base_node == bt.base_node

    for d in result_bt.data.values():
        assert not d.expression.is_single_value

    assert_equals_data(
        result_bt,
        expected_columns=['city', 'skating_order_nunique',
                          'municipality_nunique', 'inhabitants_nunique', 'founding_nunique'],
        order_by='city',
        expected_data=[
            ['B', 1, 1, 1, 1], ['D', 2, 2, 2, 2], ['F', 1, 1, 1, 1], ['H', 2, 2, 2, 2],
            ['L', 1, 1, 1, 1], ['S', 3, 2, 3, 3], ['W', 1, 1, 1, 1]
        ]
    )
    assert result_bt.index_dtypes == {
        'city': 'string'
    }
    assert result_bt.dtypes == {
        'municipality_nunique': 'int64',
        'founding_nunique': 'int64',
        'inhabitants_nunique': 'int64',
        'skating_order_nunique': 'int64'
    }


def test_group_by_series_selection(engine):
    # Test selection of series from an aggregated dataframe
    bt = get_df_with_test_data(engine, full_data_set=True)
    btg = bt.groupby('municipality')
    btg_single_series_frame = btg[['inhabitants']]
    result_bt = btg_single_series_frame.count()

    # no materialization has taken place yet.
    assert result_bt.base_node == bt.base_node

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

    btg_double_series_frame = btg[['inhabitants', 'founding']]
    result_bt = btg_double_series_frame.count()
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


def test_dataframe_agg_all(engine):
    # test agg syntax for single function on a Dataframe that has no group_by set, e.g. on all rows.
    bt = get_df_with_test_data(engine, full_data_set=True)[['municipality', 'inhabitants']]

    result_bt = bt.nunique()
    result_bt_str = bt.agg('nunique')
    result_bt_list_str = bt.agg(['nunique'])
    result_bt_func_bounded = bt.agg(bt.municipality.nunique)
    result_bt_func_unbounded = bt.agg(Series.nunique)

    for result_bt in [result_bt, result_bt_str, result_bt_str, result_bt_list_str,
                      result_bt_func_bounded, result_bt_func_unbounded]:
        # no materialization has taken place yet.
        assert result_bt.base_node == bt.base_node

        assert result_bt.municipality_nunique.expression.is_single_value
        assert result_bt.inhabitants_nunique.expression.is_single_value

        assert_equals_data(
            result_bt,
            expected_columns=['municipality_nunique', 'inhabitants_nunique'],
            expected_data=[
                [6, 11]
            ]
        )
        assert result_bt.index == {}
        assert result_bt.dtypes == {
            'municipality_nunique': 'int64',
            'inhabitants_nunique': 'int64'
        }


def test_groupby_dataframe_agg(engine):
    # test agg syntax for single function on a Dataframe that has group_by set
    bt = get_df_with_test_data(engine, full_data_set=True)[['municipality', 'inhabitants']]
    btg = bt.groupby('municipality')
    result_bt = btg.nunique()
    result_bt_str = btg.agg('nunique')
    result_bt_list_str = btg.agg(['nunique'])
    result_bt_func_bounded = btg.agg(bt.municipality.nunique)
    result_bt_func_unbounded = btg.agg(Series.nunique)

    for result_bt in [result_bt, result_bt_str, result_bt_str, result_bt_list_str,
                      result_bt_func_bounded, result_bt_func_unbounded]:
        # no materialization has taken place yet.
        assert result_bt.base_node == bt.base_node

        assert_equals_data(
            result_bt,
            order_by=['municipality'],
            expected_columns=['municipality', 'inhabitants_nunique'],
            expected_data=[
                ['De Friese Meren', 1], ['Harlingen', 1], ['Leeuwarden', 1],
                ['Noardeast-Fryslân', 1], ['Súdwest-Fryslân', 6], ['Waadhoeke', 1]
            ]
        )
        assert result_bt.index_dtypes == {
            'municipality': 'string'
        }
        assert result_bt.dtypes == {
            'inhabitants_nunique': 'int64'
        }


def test_groupby_dataframe_agg_per_series_syntax(engine):
    bt = get_df_with_test_data(engine, full_data_set=True)[['municipality', 'inhabitants', 'founding']]
    btg = bt.groupby('municipality')
    result_bt_str = btg.agg({'inhabitants': 'min', 'founding': 'max'})
    result_bt_func_bound = btg.agg({'inhabitants': bt.inhabitants.min, 'founding': bt.founding.max})
    result_bt_list_mixed1_bound = btg.agg({'inhabitants': 'min', 'founding': bt.founding.max})
    result_bt_list_mixed2_bound = btg.agg({'inhabitants': bt.inhabitants.min, 'founding': 'max'})
    result_bt_list_unbound = btg.agg({'inhabitants': SeriesAbstractNumeric.min,
                                      'founding': SeriesAbstractNumeric.max})

    for result_bt in [result_bt_str, result_bt_func_bound, result_bt_list_mixed1_bound,
                      result_bt_list_mixed2_bound, result_bt_list_unbound]:
        # no materialization has taken place yet.
        assert result_bt.base_node == bt.base_node

        assert_equals_data(
            result_bt,
            order_by='municipality',
            expected_columns=['municipality', 'inhabitants_min', 'founding_max'],
            expected_data=[
                ['De Friese Meren', 700, 1426], ['Harlingen', 14740, 1234], ['Leeuwarden', 93485, 1285],
                ['Noardeast-Fryslân', 12675, 1298], ['Súdwest-Fryslân', 870, 1456],
                ['Waadhoeke', 12760, 1374]
            ]
        )
        assert result_bt.index_dtypes == {
            'municipality': 'string'
        }
        assert result_bt.dtypes == {
            'inhabitants_min': 'int64',
            'founding_max': 'int64',
        }


def test_groupby_agg_func_order(engine) -> None:
    bt = get_df_with_test_data(engine, full_data_set=True)[['municipality', 'inhabitants', 'founding']]
    btg = bt.groupby('municipality')
    result_bt = btg.agg({'founding': ['max', 'min'], 'inhabitants': 'min'})
    assert_equals_data(
        result_bt,
        order_by='municipality',
        expected_columns=['municipality', 'founding_max', 'founding_min', 'inhabitants_min'],
        expected_data=[
            ['De Friese Meren', 1426, 1426, 700],
            ['Harlingen', 1234, 1234, 14740],
            ['Leeuwarden', 1285, 1285, 93485],
            ['Noardeast-Fryslân', 1298, 1298, 12675],
            ['Súdwest-Fryslân', 1456, 1061, 870],
            ['Waadhoeke', 1374, 1374, 12760],
        ],
    )


def test_groupby_dataframe_agg_multiple_per_series_syntax(engine):
    bt = get_df_with_test_data(engine, full_data_set=True)
    btg = bt.groupby('municipality')
    result_bt_list_str = btg.aggregate({'inhabitants': ['min', 'max']})
    result_bt_list_func_bound = btg.aggregate({'inhabitants': [bt.inhabitants.min, bt.inhabitants.max]})
    result_bt_list_mixed_bound = btg.aggregate({'inhabitants': [bt.inhabitants.min, 'max']})
    result_bt_list_func_unbound = btg.aggregate(
        {'inhabitants': [SeriesAbstractNumeric.min, SeriesAbstractNumeric.max]})
    result_bt_list_mixed_unbound = btg.aggregate({'inhabitants': ['min', SeriesAbstractNumeric.max]})

    for result_bt in [result_bt_list_str, result_bt_list_func_bound, result_bt_list_mixed_bound,
                      result_bt_list_func_unbound, result_bt_list_mixed_unbound]:
        # no materialization has taken place yet.
        assert result_bt.base_node == bt.base_node

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


def test_dataframe_agg_numeric_only(engine):
    bt = get_df_with_test_data(engine, full_data_set=True)[['municipality', 'inhabitants']]
    with pytest.raises(AttributeError):
        # contains non-numeric series that don't have 'min' implemented
        bt.agg('sum')
    result_bt_str = bt.agg('sum', numeric_only=True)
    result_bt_func = bt.agg(SeriesAbstractNumeric.sum, numeric_only=True)
    for result_bt in [result_bt_str, result_bt_func]:
        # no materialization has taken place yet.
        assert result_bt.base_node == bt.base_node

        assert result_bt.inhabitants_sum.expression.is_single_value
        assert result_bt.inhabitants_sum.value == 187325
        assert result_bt.dtypes == {
            # infers that municipality was dropped because not numeric
            'inhabitants_sum': 'int64'
        }


def test_cube_basics(pg_engine):
    # TODO: BigQuery
    bt = get_df_with_test_data(pg_engine, full_data_set=False)
    engine = bt.engine

    # instant stonks through variable naming
    btc = bt.cube(['municipality', 'city'])

    assert(isinstance(btc.group_by, Cube))
    assert(btc.group_by.get_group_by_column_expression().to_sql(engine.dialect)
           == 'cube ("municipality", "city")')

    result_bt = btc[['inhabitants']].sum()
    # no materialization has taken place yet.
    assert result_bt.base_node == bt.base_node

    assert_equals_data(
        result_bt,
        order_by=['municipality', 'city'],
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


def test_rollup_basics(engine):
    bt = get_df_with_test_data(engine, full_data_set=False)

    btr = bt.rollup(['municipality', 'city'])
    assert(isinstance(btr.group_by, Rollup))

    result_expression = btr.group_by.get_group_by_column_expression().to_sql(engine.dialect)

    if is_postgres(engine):
        expected_expression = 'rollup ("municipality", "city")'
    elif is_bigquery(engine):
        expected_expression = 'rollup (`municipality`, `city`)'
    else:
        raise Exception()
    assert result_expression == expected_expression

    result_bt = btr[['inhabitants']].sum()
    # no materialization has taken place yet.
    assert result_bt.base_node == bt.base_node

    assert_equals_data(
        result_bt,
        order_by=['municipality', 'city'],
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


def test_grouping_list_basics(pg_engine):
    # TODO: BigQuery
    # This is not the greatest test, but at least it tests the interface.
    bt = get_df_with_test_data(pg_engine, full_data_set=False)
    engine = bt.engine
    btl1 = bt.groupby([['municipality'], ['city']])
    btl2 = bt.groupby([['municipality'], 'city'])
    btl3 = bt.groupby(['municipality', ['city']])

    assert(btl1 == btl2)
    assert(btl1 == btl3)

    # This is not the greatest test, but at least it tests the interface.
    assert(isinstance(btl1.group_by, GroupingList))
    assert(btl1.group_by.get_group_by_column_expression().to_sql(engine.dialect)
           == '("municipality"), ("city")')

    result_bt = btl1[['inhabitants']].sum()

    # no materialization has taken place yet.
    assert result_bt.base_node == bt.base_node

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


def test_grouping_set_basics(pg_engine):
    # TODO: BigQuery
    # This is not the greatest test, but at least it tests the interface.
    bt = get_df_with_test_data(pg_engine, full_data_set=False)
    engine = bt.engine
    bts1 = bt.groupby((('municipality'), ('city')))
    bts2 = bt.groupby((('municipality'), 'city'))
    bts3 = bt.groupby(('municipality', ('city')))

    assert(bts1 == bts2)
    assert(bts1 == bts3)

    assert(isinstance(bts1.group_by, GroupingSet))
    assert(bts1.group_by.get_group_by_column_expression().to_sql(engine.dialect)
           == 'grouping sets (("municipality"), ("city"))')

    result_bt = bts1[['inhabitants']].sum()

    # no materialization has taken place yet.
    assert result_bt.base_node == bt.base_node

    assert_equals_data(
        result_bt,
        order_by=['municipality', 'city'],
        expected_columns=['municipality', 'city', 'inhabitants_sum'],
        expected_data=[
            ['Leeuwarden', None, 93485], ['Súdwest-Fryslân', None, 36575],
            [None, 'Drylts', 3055], [None, 'Ljouwert', 93485], [None, 'Snits', 33520]
        ]
    )

    # test empty group in set
    bts1 = bt.groupby((('municipality'), ([])))
    bts2 = bt.groupby((('municipality'), []))
    bts3 = bt.groupby(('municipality', ([])))

    assert(bts1 == bts2)
    assert(bts1 == bts3)

    assert(isinstance(bts1.group_by, GroupingSet))
    assert(bts1.group_by.get_group_by_column_expression().to_sql(engine.dialect)
           == 'grouping sets (("municipality"), ())')

    result_bt = bts1[['inhabitants']].sum()

    assert_equals_data(
        result_bt,
        order_by=['municipality'],
        expected_columns=['municipality', 'inhabitants_sum'],
        expected_data=[
            ['Leeuwarden', 93485],
            ['Súdwest-Fryslân', 36575],
            [None, 130060]
        ]
    )


def test_groupby_frame_split_series_aggregation(engine):
    bt = get_df_with_test_data(engine, full_data_set=False)[['municipality', 'inhabitants', 'founding']]
    btg1 = bt.groupby(['municipality'])

    # Test whether all ways to get to a the same aggregated series yield the same result
    founding_sum = btg1['founding'].sum()
    df_sum_series = bt.groupby(['municipality']).sum()['founding_sum']
    df_df_sum_series = bt.groupby(['municipality'])[['founding']].sum()['founding_sum']

    # no materialization has taken place yet.
    assert founding_sum.base_node == bt.base_node
    assert df_sum_series.base_node == bt.base_node
    assert df_df_sum_series.base_node == bt.base_node

    assert (founding_sum.to_numpy() == df_sum_series.to_numpy()).all()
    assert (founding_sum.to_numpy() == df_df_sum_series.to_numpy()).all()

    # Does math work?
    inhabitants_sum = btg1['inhabitants'].sum()
    founding_sum = btg1['founding'].sum()
    add_series_sum = btg1['founding'].sum() + btg1['inhabitants'].sum()
    assert all(
        (founding_sum.to_numpy() + inhabitants_sum.to_numpy()) == add_series_sum.to_numpy()
    )
    # no materialization has taken place yet.
    assert inhabitants_sum.base_node == bt.base_node
    assert founding_sum.base_node == bt.base_node
    assert add_series_sum.base_node == bt.base_node

    with pytest.raises(ValueError, match='already aggregated'):
        founding_sum.sum()

    r6 = founding_sum.to_frame().materialize()
    assert r6.base_node != bt.base_node
    r6.to_pandas()  # still valid sql?


def test_groupby_frame_split_recombine(engine):
    bt = get_df_with_test_data(engine, full_data_set=False)[['municipality', 'inhabitants', 'founding']]
    btg1 = bt.groupby(['municipality'])[['inhabitants', 'founding']]
    btg1a = btg1[['inhabitants']]
    btg1b = btg1['founding']

    r0 = btg1.sum()

    assert btg1.group_by == btg1a.group_by
    assert btg1.group_by == btg1b.group_by

    # recombine from same parent
    btg1a['founding'] = btg1b
    r1 = btg1a.sum()
    assert btg1a == btg1  # inplies base_node and group_by are equal

    # can not add columns from grouped df to ungrouped df
    with pytest.raises(ValueError, match="Setting a grouped Series to a DataFrame is only supported if the"
                                         " Series is aggregated"):
        bt2 = bt.drop(columns=['founding'])
        bt2['founding'] = btg1b

    # can not add columns from ungrouped df to grouped df
    with pytest.raises(ValueError, match="Setting new columns to grouped DataFrame is only supported if the"
                                         " DataFrame has aggregated columns"):
        bt2 = btg1.drop(columns=['founding'])
        bt2['founding'] = bt['founding']

    # create new grouping df, but with same grouping
    btg2 = bt.groupby(['municipality'])[['inhabitants', 'founding']]
    assert btg1.group_by == btg2.group_by
    assert btg1 == btg2

    # recombine from different parent with same grouping
    btg2 = btg2.drop(columns=['founding'])
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


def test_groupby_frame_split_recombine_aggregation_applied(engine):
    bt = get_df_with_test_data(engine, full_data_set=False)[['municipality', 'inhabitants', 'founding']]
    group1 = bt.groupby('municipality')
    subgroup = group1[['founding', 'inhabitants']]
    inhabitants_sum = subgroup['inhabitants'].sum()
    founding_inhabitants_sum = group1[['founding', 'inhabitants']].sum()
    only_inhabitants = founding_inhabitants_sum[['inhabitants_sum']]
    founding_mean = group1['founding'].mean()

    # make sure no materialization has taken place
    assert founding_inhabitants_sum.base_node == only_inhabitants.base_node\
           == founding_mean.base_node == bt.base_node

    # recombine
    founding_inhabitants_sum['founding_mean'] = founding_mean
    assert founding_mean.base_node == bt.base_node

    r1 = inhabitants_sum.to_frame()
    r1['founding_sum'] = group1['founding'].sum()
    r1['founding_mean'] = founding_mean
    r1 = r1.rename(columns={'inhabitants': 'inhabitants_sum'})
    assert r1.base_node == bt.base_node

    expected_columns = ['inhabitants_sum', 'founding_sum', 'founding_mean']
    for r in [founding_inhabitants_sum, r1]:
        assert_equals_data(
            r[expected_columns],
            order_by=['municipality'],
            expected_columns=['municipality'] + expected_columns,

            expected_data=[
                ['Leeuwarden', 93485, 1285, 1285],
                ['Súdwest-Fryslân', 36575, 2724, 1362]
            ]
        )


def test_materialize_on_double_aggregation(engine):
    # When we use an aggregation function twice, we need to materialize the node in between, because it's not
    # possible to nest the aggregate function calls. I.e. you cannot do `avg(sum(x))`
    bt = get_df_with_test_data(engine, full_data_set=True)
    btg = bt.groupby('municipality')[['founding']]
    btg_sum = btg.sum()
    assert bt.base_node == btg.base_node == btg_sum.base_node

    with pytest.raises(ValueError, match='already aggregated'):
        btg_sum.founding_sum.mean()

    # After manually materializing the frame everything is OK again.
    btg_materialized = btg_sum.materialize()
    assert btg_materialized.base_node != btg_sum.base_node

    btg_materialized_mean = btg_materialized.founding_sum.mean()
    # did not get materialized again
    assert btg_materialized_mean.base_node == btg_materialized.base_node
    value = btg_materialized_mean.to_numpy()[0]
    # avg() of BigQuery gives a slightly different result than Postgres or python, so use assert_almost_equal
    numpy.testing.assert_almost_equal(value, 2413.5)


def test_groupby_w_multi_level_series(engine):
    bt = get_df_with_test_data(engine, full_data_set=True)
    bt['lower'] = 0

    bt.loc[bt['inhabitants'] > 900, 'lower'] = 1
    bt.loc[bt['inhabitants'] > 2000, 'lower'] = 2
    bt.loc[bt['inhabitants'] > 4000, 'lower'] = 3

    bt['upper'] = bt['lower'] * 2 + 1

    bt['range'] = SeriesNumericInterval.from_value(
        base=bt,
        value={'lower': bt['lower'], 'upper': bt['upper'], 'bounds': '[]'},
        name='range',
    )
    bt = bt[['range', 'municipality', 'inhabitants', 'skating_order']].reset_index(drop=True)

    with pytest.raises(ValueError, match=r'Level in multi-level series has a constant expression'):
        bt.groupby(by=['range', 'municipality'])
    bt = bt.materialize()

    expected = bt.to_pandas().groupby(by=['range', 'municipality']).sum()
    result = bt.groupby(by=['range', 'municipality']).sum(numeric_only=True).sort_index()

    result_pdf = result.rename(
        columns={'inhabitants_sum': 'inhabitants', 'skating_order_sum': 'skating_order'},
    ).to_pandas()
    pd.testing.assert_frame_equal(expected.sort_index(), result_pdf)

    if is_postgres(engine):
        range_1 = NumericRange(lower=Decimal('0.'), upper=Decimal('1.'), bounds='[]')
        range_2 = NumericRange(lower=Decimal('1.'), upper=Decimal('3.'), bounds='[]')
        range_3 = NumericRange(lower=Decimal('2.'), upper=Decimal('5.'), bounds='[]')
        range_4 = NumericRange(lower=Decimal('3.'), upper=Decimal('7.'), bounds='[]')
    elif is_bigquery(engine):
        range_1 = {'lower': 0., 'upper': 1., 'bounds': '[]'}
        range_2 = {'lower': 1., 'upper': 3., 'bounds': '[]'}
        range_3 = {'lower': 2., 'upper': 5., 'bounds': '[]'}
        range_4 = {'lower': 3., 'upper': 7., 'bounds': '[]'}
    else:
        raise Exception()

    assert_equals_data(
        result,
        expected_columns=['range', 'municipality', 'inhabitants_sum', 'skating_order_sum'],
        expected_data=[
            [range_1, 'De Friese Meren', 700, 4],
            [range_1, 'Súdwest-Fryslân', 870, 6],
            [range_2, 'Súdwest-Fryslân', 960, 5],
            [range_3, 'Súdwest-Fryslân', 3055, 3],
            [range_4, 'Harlingen', 14740, 9],
            [range_4, 'Leeuwarden', 93485, 1],
            [range_4, 'Noardeast-Fryslân', 12675, 11],
            [range_4, 'Súdwest-Fryslân', 48080, 17],
            [range_4, 'Waadhoeke', 12760, 10],
        ],
    )
