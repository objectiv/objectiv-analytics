"""
Copyright 2021 Objectiv B.V.
"""
import numpy as np
import pandas as pd
import pytest

from bach import DataFrame, SeriesString, SeriesInt64
from bach.expression import Expression
from sql_models.util import is_postgres, is_bigquery
from tests.functional.bach.test_data_and_utils import (
    get_df_with_test_data, assert_equals_data, df_to_list,
    get_df_with_railway_data, get_df_with_food_data, get_bt_with_test_data, get_bt_with_food_data
)


def test_series__getitem__(engine):
    bt = get_df_with_test_data(engine, full_data_set=True)
    series = bt['city']
    assert isinstance(series, SeriesString)

    single_value_ref = series[1]
    assert isinstance(single_value_ref, SeriesString)
    value = single_value_ref.value
    assert isinstance(value, str)
    assert value == 'Ljouwert'

    single_value_ref = series[5]
    assert isinstance(single_value_ref, SeriesString)
    value = single_value_ref.value
    assert isinstance(value, str)
    assert value == 'Starum'

    l1 = bt.groupby('municipality').min()
    # selection on data of non-materialized groupby
    assert l1.inhabitants_min['Leeuwarden'].value == 93485

    non_existing_value_ref = l1.inhabitants_min['DoesNotExist']
    with pytest.raises(IndexError):
        non_existing_value_ref.value


def test_positional_slicing():
    bt = get_bt_with_test_data(full_data_set=True)['inhabitants'].sort_values()

    class ReturnSlice:
        def __getitem__(self, key):
            return key
    return_slice = ReturnSlice()

    # negative slices are not supported, so we will not test those.
    slice_list = [return_slice[:4],
                  return_slice[4:],
                  return_slice[4:7],
                  return_slice[:],
                  return_slice[4:5],
                  return_slice[:1]
                  ]

    pbt = bt.to_pandas()
    for s in slice_list:
        bt_slice = bt[s]

        assert isinstance(bt_slice, SeriesInt64)

        # if the slice length == 1, all Series need to have a single value expression
        assert (len('slice_me_now'.__getitem__(s)) == 1) == bt_slice.expression.is_single_value

        assert_equals_data(
            bt_slice,
            expected_columns=['_index_skating_order', 'inhabitants'],
            expected_data=df_to_list(pbt[s]),
            order_by=['inhabitants'],
        )


def test_series_value(engine):
    bt = get_df_with_test_data(engine, full_data_set=False)
    assert bt.city[1] == 'Ljouwert'
    assert bt.count().city_count.value == 3

    # make sure getitem works when multiple nodes are in play.
    l1 = bt.groupby('municipality').count()
    l2 = l1.groupby().city_count.sum()
    assert l2.value == 3


def test_series_sort_values(engine):
    bt = get_df_with_test_data(engine, full_data_set=True)
    bt_series = bt.city
    kwargs_list = [
        {'ascending': True},
        {'ascending': False},
        {},
    ]
    for kwargs in kwargs_list:
        assert_equals_data(
            bt_series.sort_values(**kwargs),
            expected_columns=['_index_skating_order', 'city'],
            expected_data=df_to_list(bt.to_pandas()['city'].sort_values(**kwargs))
        )


def test_series_sort_index_simple(engine):
    df = get_df_with_test_data(engine, full_data_set=False)
    s_city = df.set_index(['skating_order'])['city']
    assert_equals_data(
        s_city.sort_index(ascending=True),
        expected_columns=['skating_order', 'city'],
        expected_data=[[1, 'Ljouwert'], [2, 'Snits'], [3, 'Drylts']]
    )
    assert_equals_data(
        s_city.sort_index(ascending=[True]),
        expected_columns=['skating_order', 'city'],
        expected_data=[[1, 'Ljouwert'], [2, 'Snits'], [3, 'Drylts']]
    )
    assert_equals_data(
        s_city.sort_index(ascending=False),
        expected_columns=['skating_order', 'city'],
        expected_data=[[3, 'Drylts'], [2, 'Snits'], [1, 'Ljouwert']]
    )
    assert_equals_data(
        s_city.sort_index(ascending=[False]),
        expected_columns=['skating_order', 'city'],
        expected_data=[[3, 'Drylts'], [2, 'Snits'], [1, 'Ljouwert']]
    )


def test_series_sort_index_multi_level(engine):
    df = get_df_with_railway_data(engine)
    s_station = df.set_index(['platforms', 'station_id'])['station']
    s_station = s_station.sort_values(ascending=True)  # sort_index should override this
    assert_equals_data(
        s_station.sort_index(ascending=True),
        expected_columns=['platforms', 'station_id', 'station'],
        expected_data=[
            [1, 1, 'IJlst'],
            [1, 2, 'Heerenveen'],
            [1, 5, 'Camminghaburen'],
            [2, 3, 'Heerenveen IJsstadion'],
            [2, 6, 'Sneek'],
            [2, 7, 'Sneek Noord'],
            [4, 4, 'Leeuwarden']
        ]
    )
    assert_equals_data(
        s_station.sort_index(ascending=[True, False]),
        expected_columns=['platforms', 'station_id', 'station'],
        expected_data=[
            [1, 5, 'Camminghaburen'],
            [1, 2, 'Heerenveen'],
            [1, 1, 'IJlst'],
            [2, 7, 'Sneek Noord'],
            [2, 6, 'Sneek'],
            [2, 3, 'Heerenveen IJsstadion'],
            [4, 4, 'Leeuwarden']
        ]
    )


def test_fillna(engine):
    # TODO test fillna with series instead of constants.
    values = [1, np.nan, 3, np.nan, 7]
    pdf = pd.DataFrame(data={'num': values})
    bt = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)

    def tf(x):
        bt_fill = bt['num'].fillna(x)
        assert bt_fill.expression.is_constant == bt['num'].expression.is_constant
        np.testing.assert_equal(pdf['num'].fillna(x).to_numpy(), bt_fill.to_numpy())

    assert(bt['num'].dtype == 'float64')
    tf(1.25)
    tf(float(99))
    tf(np.nan)

    # pandas allows this, but we can't
    for val in [int(99), 'nope']:
        with pytest.raises(TypeError):
            bt['num'].fillna(val)


def test_isnull(pg_engine):
    engine = pg_engine  # TODO BigQuery, fix sorting for nullable columns
    values = ['a', 'b', None]
    pdf = pd.DataFrame(data=values, columns=['text_with_null'])
    pdf.set_index('text_with_null', drop=False, inplace=True)
    bt = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    bt['const_not_null'] = 'not_null'
    bt['const_null'] = None
    bt['y'] = bt.text_with_null.isnull()
    bt['z'] = bt.text_with_null.notnull()
    assert bt.y.expression.is_constant == bt.text_with_null.expression.is_constant
    assert bt.z.expression.is_constant == bt.text_with_null.expression.is_constant
    assert bt.const_not_null.isnull().expression.is_constant
    assert bt.const_null.isnull().expression.is_constant
    assert bt.const_not_null.notnull().expression.is_constant
    assert bt.const_null.notnull().expression.is_constant
    assert_equals_data(
        bt,
        expected_columns=['_index_text_with_null', 'text_with_null', 'const_not_null', 'const_null', 'y', 'z'],
        expected_data=[['a', 'a', 'not_null', None, False, True],
                       ['b', 'b', 'not_null', None, False, True],
                       [None, None, 'not_null', None, True, False]]
    )


def test_aggregation(engine):
    # Test aggregation on single series
    bt = get_df_with_test_data(engine, full_data_set=True)[['inhabitants']]
    s = bt['inhabitants']
    a1 = s.agg('sum')
    assert isinstance(a1, type(s))
    assert a1.expression.is_single_value
    assert a1.value == 187325

    a2 = s.sum()
    assert isinstance(a2, type(s))
    assert a1.expression.is_single_value
    assert a2.value == 187325

    df1 = s.agg(['sum', 'count'])
    assert isinstance(df1.inhabitants_sum, type(s))
    assert isinstance(df1.inhabitants_count, type(s))
    assert df1.inhabitants_sum.expression.is_single_value
    assert df1.inhabitants_count.expression.is_single_value

    # multiple series results return
    assert df1.inhabitants_sum.value == 187325
    assert df1.inhabitants_count.value == 11

    # duplicate result series should raise
    with pytest.raises(ValueError, match="duplicate"):
        s.agg(['sum','sum'])


def test_type_agnostic_aggregation_functions():
    bt = get_bt_with_test_data(full_data_set=True)
    btg = bt.groupby()

    # type agnostic aggregations
    aggregation_functions = ['count', 'max', 'min', 'nunique', 'mode', 'median']
    result_bt = btg[['municipality']].aggregate(aggregation_functions)

    result_series_dtypes = {
        'municipality_count': 'int64',
        'municipality_max': 'string',
        'municipality_min': 'string',
        'municipality_nunique': 'int64',
        'municipality_mode': 'string',
        'municipality_median': 'string'
    }

    assert_equals_data(
        result_bt,
        expected_columns=list(result_series_dtypes.keys()),
        expected_data=[
            [11, 'Waadhoeke', 'De Friese Meren', 6, 'Súdwest-Fryslân', 'Súdwest-Fryslân']
        ]
    )

    assert result_bt.dtypes == result_series_dtypes


def test_unique(engine):
    bt = get_df_with_test_data(engine, full_data_set=True)
    uq = bt.municipality.unique()
    assert not uq.expression.is_single_value

    muni_single = bt.municipality[:1]
    uq_single = muni_single.unique()
    assert uq_single.expression.is_single_value == muni_single.expression.is_single_value == True

    with pytest.raises(ValueError, match='dtypes of indexes should be the same'):
        # the uq series have an index with different dtypes
        bt['uq'] = uq

    assert_equals_data(
        uq,
        expected_columns=['municipality', 'municipality_unique'],
        expected_data=[
            ['De Friese Meren', 'De Friese Meren'],
            ['Harlingen', 'Harlingen'],
            ['Leeuwarden', 'Leeuwarden'],
            ['Noardeast-Fryslân', 'Noardeast-Fryslân'],
            ['Súdwest-Fryslân', 'Súdwest-Fryslân'],
            ['Waadhoeke', 'Waadhoeke'],
        ]
    )


def test_unique_subquery(engine):
    bt = get_df_with_test_data(engine, full_data_set=True)

    uq = bt.municipality.unique().sort_values()[:2]
    bt = bt[bt.municipality.isin(uq)]
    assert_equals_data(
        bt,
        expected_columns=['_index_skating_order', 'skating_order', 'city',
                          'municipality', 'inhabitants', 'founding'],
        expected_data=[
            [4, 4, 'Sleat', 'De Friese Meren', 700, 1426],
            [9, 9, 'Harns', 'Harlingen', 14740, 1234]
        ]
    )


def test_dataframe_agg_skipna_parameter(engine):
    # test full parameter traversal
    bt = get_df_with_test_data(engine, full_data_set=True)[['inhabitants']]

    series_agg = ['count', 'max', 'median', 'min', 'mode', 'nunique']
    for agg in series_agg:
        with pytest.raises(NotImplementedError):
            # currently not supported anywhere, so needs to raise
            bt.agg(agg, skipna=False)


def test_to_frame(engine):
    bt = get_df_with_test_data(engine, full_data_set=False)
    series = bt.inhabitants
    frame = series.to_frame()

    assert isinstance(frame, DataFrame)
    assert list(frame.index.keys()) == list(bt.inhabitants.index.keys())
    assert isinstance(series.to_pandas(), pd.Series)
    assert isinstance(frame.to_pandas(), pd.DataFrame)

    assert isinstance(frame, DataFrame)
    assert list(frame.index.keys()) == list(bt.inhabitants.index.keys())
    assert isinstance(series.head(), pd.Series)
    assert isinstance(frame.head(), pd.DataFrame)


def test_series_inherit_flag(engine):
    # TODO: change this so it checks the flag correctly
    bts = get_df_with_test_data(engine, full_data_set=False).groupby('municipality')['founding']
    bts_min = bts.min()
    assert not bts.expression.has_aggregate_function
    assert bts_min.expression.has_aggregate_function

    bts_min_materialized = bts_min.to_frame().materialize()['founding']
    assert not bts_min_materialized.expression.has_aggregate_function

    assert_equals_data(
        bts_min_materialized,
        expected_columns=['municipality', 'founding'],
        expected_data=[
            ['Leeuwarden', 1285],
            ['Súdwest-Fryslân', 1268]
        ]
    )

    bts_min_min = bts_min_materialized.min()
    assert_equals_data(bts_min_min, expected_columns=['founding'], expected_data=[[1268]])

    # bts_min_min has applied an aggregate function to a materialized view, so the aggregation flag should
    # be True again
    assert bts_min_min.expression.has_aggregate_function

    # Check that aggregation flag correctly gets inherited if multiple series are involved in a comparison
    # aggregation flag on left hand series
    bts_derived = bts_min_min - 5
    assert bts_derived.expression.has_aggregate_function

    # aggregation flag on right hand series, but it gets resolved when creating a single value subquery to
    # actually make this query executable.
    bts_derived = bts_min_materialized - bts_min_min
    assert not bts_derived.expression.has_aggregate_function


def test_series_independant_subquery_any_value_all_values():
    bt = get_bt_with_test_data(full_data_set=True)
    s = bt.inhabitants.max() // 4

    bt[bt.inhabitants > s.any_value()].head()
    result_bt = bt[bt.inhabitants > s.all_values()]

    assert_equals_data(
        result_bt[['city', 'inhabitants']],
        expected_columns=['_index_skating_order', 'city', 'inhabitants'],
        expected_data=[
            [1, 'Ljouwert', 93485], [2, 'Snits', 33520]
        ]
    )


def test_series_independant_subquery_sets(engine):
    bt = get_df_with_test_data(engine, full_data_set=True)
    # get 3 smallest cities
    s = bt.sort_values('inhabitants', True)[:3]
    result_bt = bt[bt.city.isin(s.city)]
    assert_equals_data(
        result_bt[['city', 'inhabitants']],
        expected_columns=['_index_skating_order', 'city', 'inhabitants'],
        expected_data=[
            [4, 'Sleat', 700], [5, 'Starum', 960], [6, 'Hylpen', 870]
        ]
    )

    result_bt = bt[~bt.city.isin(s.city)]
    assert_equals_data(
        result_bt[['city', 'inhabitants']],
        expected_columns=['_index_skating_order', 'city', 'inhabitants'],
        expected_data=[
            [1, 'Ljouwert', 93485], [2, 'Snits', 33520], [3, 'Drylts', 3055], [7, 'Warkum', 4440],
            [8, 'Boalsert', 10120], [9, 'Harns', 14740], [10, 'Frjentsjer', 12760], [11, 'Dokkum', 12675]
        ]
    )


def test_series_independant_subquery_single(engine):
    bt = get_df_with_test_data(engine, full_data_set=True)
    # get smallest city
    s = bt.sort_values('inhabitants', True)[:1]
    result_bt = bt[bt.city == s.city]
    assert_equals_data(
        result_bt[['city', 'inhabitants']],
        expected_columns=['_index_skating_order', 'city', 'inhabitants'],
        expected_data=[
            [4, 'Sleat', 700]
        ]
    )
    # and some math
    bt = get_df_with_test_data(engine, full_data_set=False)
    result_bt = bt.inhabitants + s.inhabitants
    assert_equals_data(
        result_bt,
        expected_columns=['_index_skating_order', 'inhabitants'],
        expected_data=[
            [1, 94185], [2, 34220], [3, 3755]
        ]
    )


def test_series_different_aggregations(engine):
    bt = get_df_with_test_data(engine, full_data_set=True)
    v = bt.groupby('municipality').skating_order.nunique() / bt.skating_order.nunique()
    assert_equals_data(
        v,
        expected_columns=['municipality', 'skating_order'],
        expected_data=[['De Friese Meren', 0.09090909090909091], ['Harlingen', 0.09090909090909091],
                       ['Leeuwarden', 0.09090909090909091], ['Noardeast-Fryslân', 0.09090909090909091],
                       ['Súdwest-Fryslân', 0.5454545454545454], ['Waadhoeke', 0.09090909090909091]]
    )

    with pytest.raises(Exception, match='both series must have at least one index level'):
        # todo give a better error: bt.skating_order.nunique() is a single value
        bt.skating_order.nunique() / bt.groupby('municipality').skating_order.nunique()


def test_series_different_base_nodes(engine):
    bt = get_df_with_test_data(engine)
    mt = get_df_with_railway_data(engine)
    bt_s = bt.skating_order + mt.platforms

    assert_equals_data(
        bt_s,
        expected_columns=['_index_skating_order', 'skating_order'],
        expected_data=[
            [1, 2],
            [2, 3],
            [3, 5],
            [4, None],
            [5, None],
            [6, None],
            [7, None]
        ]
    )


def test_series_append_same_dtype_different_index(engine) -> None:
    bt = get_df_with_test_data(engine, full_data_set=False)[['city', 'skating_order']]
    bt_other_index = bt.reset_index(drop=False)
    bt_other_index['_index_skating_order'] = bt_other_index['_index_skating_order'].astype('string')
    bt_other_index = bt_other_index.set_index('_index_skating_order')
    bt.skating_order = bt.skating_order.astype(str)

    with pytest.raises(ValueError, match='concatenation with different index dtypes is not supported yet.'):
        bt_other_index.city.append(bt.skating_order)


def test_series_dropna(engine) -> None:
    p_series = pd.Series(['a', None, 'c', 'd'], name='nan_series')
    bt = DataFrame.from_pandas(engine=engine, df=p_series.to_frame(), convert_objects=True).nan_series
    result = bt.dropna()
    pd.testing.assert_series_equal(
        p_series.dropna(),
        result.to_pandas(),
        check_names=False
    )


def test_series_unstack():
    bt = get_bt_with_test_data(full_data_set=True)

    stacked_bt = bt.groupby(['city','municipality']).inhabitants.sum()
    unstacked_bt = stacked_bt.unstack()

    expected_columns = [
        'De Friese Meren', 'Harlingen', 'Leeuwarden', 'Noardeast-Fryslân', 'Súdwest-Fryslân', 'Waadhoeke',
    ]
    assert sorted(unstacked_bt.data_columns) == expected_columns
    unstacked_bt_sorted = unstacked_bt.copy_override(series={x: unstacked_bt[x] for x in expected_columns})

    assert_equals_data(
        unstacked_bt_sorted,
        expected_columns=['city'] + expected_columns,
        expected_data=[
            ['Boalsert', None, None, None, None, 10120, None],
            ['Dokkum', None, None, None, 12675, None, None], 
            ['Drylts', None, None, None, None, 3055, None],
            ['Frjentsjer', None, None, None, None, None, 12760],
            ['Harns', None, 14740, None, None, None, None],
            ['Hylpen', None, None, None, None, 870, None],
            ['Ljouwert', None, None, 93485, None, None, None],
            ['Sleat', 700, None, None, None, None, None],
            ['Snits', None, None, None, None, 33520, None],
            ['Starum', None, None, None, None, 960, None],
            ['Warkum', None, None, None, None, 4440, None]
        ],
        order_by='city'
    )

    stacked_bt = bt.groupby(['municipality', 'skating_order']).city.max()
    unstacked_bt = stacked_bt.unstack(fill_value='buh')

    expected_columns = ['1', '10', '11', '2', '3', '4', '5', '6', '7', '8', '9']
    assert sorted(unstacked_bt.data_columns) == expected_columns
    unstacked_bt_sorted = unstacked_bt.copy_override(series={x: unstacked_bt[x] for x in expected_columns})

    assert_equals_data(
        unstacked_bt_sorted,
        expected_columns=['municipality'] + expected_columns,
        expected_data=[
            ['De Friese Meren', 'buh', 'buh', 'buh', 'buh', 'buh', 'Sleat', 'buh', 'buh', 'buh', 'buh', 'buh'],
            ['Harlingen', 'buh', 'buh', 'buh', 'buh', 'buh', 'buh', 'buh', 'buh', 'buh', 'buh', 'Harns'],
            ['Leeuwarden', 'Ljouwert', 'buh', 'buh', 'buh', 'buh', 'buh', 'buh', 'buh', 'buh', 'buh', 'buh'],
            ['Noardeast-Fryslân', 'buh', 'buh', 'Dokkum', 'buh', 'buh', 'buh', 'buh', 'buh', 'buh', 'buh', 'buh'],
            ['Súdwest-Fryslân', 'buh', 'buh', 'buh', 'Snits', 'Drylts', 'buh', 'Starum', 'Hylpen', 'Warkum', 'Boalsert', 'buh'],
            ['Waadhoeke', 'buh', 'Frjentsjer', 'buh', 'buh', 'buh', 'buh', 'buh', 'buh', 'buh', 'buh', 'buh']
        ],
        order_by='municipality'
    )

    # test with column that references another column and grouping on that column
    bt = get_bt_with_test_data(full_data_set=False)
    bt['village'] = bt.city + ' village'
    unstacked_bt = bt.groupby(['skating_order', 'village']).inhabitants.sum().unstack()
    # unstacked_bt = bt.set_index(['skating_order', 'village']).inhabitants.unstack()

    expected_columns = ['Drylts village', 'Ljouwert village', 'Snits village']
    assert sorted(unstacked_bt.data_columns) == expected_columns
    unstacked_bt_sorted = unstacked_bt.copy_override(series={x: unstacked_bt[x] for x in expected_columns})

    assert_equals_data(
        unstacked_bt_sorted,
        expected_columns=['skating_order'] + expected_columns,
        expected_data=[
            [1, None, 93485., None],
            [2, None, None, 33520.],
            [3, 3055., None, None]
        ],
        order_by='skating_order'
    )


def test__set_item_with_merge_aggregated_series(engine) -> None:
    pdf1 = pd.DataFrame(data={'a': [1, 2, 3], 'b': [2, 2, 2], 'c': [3, 3, 3]}, )
    pdf2 = pd.DataFrame(
        data={'w': [1, 1, 1, 1], 'x': [1, 2, 3, 4], 'y': [2, 2, 4, 4], 'z': [1, 2, 3, 4]},
    )

    df1 = DataFrame.from_pandas(engine=engine, df=pdf1, convert_objects=True)
    df2 = DataFrame.from_pandas(engine=engine, df=pdf2, convert_objects=True)

    df1 = df1.set_index('a')
    df2 = df2.set_index('x')

    pdf1 = pdf1.set_index('a')
    pdf2 = pdf2.set_index('x')

    grouped_pdf2 = pdf2.groupby('y').sum()
    grouped_df2 = df2.groupby('y').sum()
    expected = pdf1.c + grouped_pdf2['z'] - grouped_pdf2['w']
    result = df1.c + grouped_df2['z_sum'] - grouped_df2['w_sum']

    pd.testing.assert_series_equal(
        expected,
        result.sort_index().to_pandas(),
        check_names=False,
    )

    # aggregated series are materialized, original references are not kept as leaves
    assert result.base_node.references['left_node'] != df1.base_node
    assert result.base_node.references['right_node'] != df2.base_node


def test__set_item_with_merge_index_data_column_name_conflict(engine) -> None:
    pdf1 = pd.DataFrame(data={'a': [1, 2, 3], 'c': [3, 3, 3]})
    pdf2 = pd.DataFrame(data={'x': [1, 2, 3, 4], 'a': [2, 2, 4, 4]})

    df1 = DataFrame.from_pandas(engine=engine, df=pdf1, convert_objects=True)
    df2 = DataFrame.from_pandas(engine=engine, df=pdf2, convert_objects=True)

    df1 = df1.set_index('a')
    df2 = df2.set_index('x')
    pdf1 = pdf1.set_index('a')
    pdf2 = pdf2.set_index('x')

    expected = pdf1['c'] + pdf2['a']
    result = df1['c'] + df2['a']
    pd.testing.assert_series_equal(
        expected,
        result.sort_index().to_pandas(),
        check_names=False,
    )


def test__set_item_with_merge_index_multi_level(engine) -> None:
    pdf1 = pd.DataFrame(data={'a': [1, 2, 3], 'b': [2, 2, 2], 'c': [3, 3, 3]}, )
    pdf2 = pd.DataFrame(data={'a': [1, 2, 3, 4], 'b': [2, 2, 4, 4], 'z': [1, 2, 3, 4]})

    df1 = DataFrame.from_pandas(engine=engine, df=pdf1, convert_objects=True)
    df2 = DataFrame.from_pandas(engine=engine, df=pdf2, convert_objects=True)

    df1 = df1.set_index(['a', 'b'])
    df2 = df2.set_index(['a', 'b'])

    pdf1 = pdf1.set_index(['a', 'b'])
    pdf2 = pdf2.set_index(['a', 'b'])

    expected = pdf1['c'] + pdf2['z']
    result = df1['c'] + df2['z']
    pd.testing.assert_series_equal(
        expected,
        result.sort_index().to_pandas(),
        check_names=False,
    )


def test__set_item_with_merge_index_uneven_multi_level(engine) -> None:
    pdf1 = pd.DataFrame(data={'a': [1, 2, 3], 'b': [2, 2, 2], 'c': [3, 3, 3]}, )
    pdf2 = pd.DataFrame(data={'x': [1, 2, 3, 4], 'a': [2, 2, 4, 4], 'z': [1, 2, 3, 4]})

    df1 = DataFrame.from_pandas(engine=engine, df=pdf1, convert_objects=True)
    df2 = DataFrame.from_pandas(engine=engine, df=pdf2, convert_objects=True)

    df1 = df1.set_index(['a', 'b'])
    df2 = df2.set_index(['x'])

    result = df1['c'] + df2['a'] + df2['z']
    assert_equals_data(
        result.sort_index(),
        expected_columns=['a', 'b', 'c'],
        expected_data=[
            [1, 2, 6],
            [2, 2, 7],
            [3, 2, 10],
            [4, None, None],
        ],
    )
    assert df1.base_node == result.base_node.references['left_node']
    assert df2.base_node == result.base_node.references['right_node']


def test__set_item_with_merge_w_conflict_names(engine) -> None:
    pdf1 = pd.DataFrame(data={'a': [1, 2, 3], 'b': [2, 2, 2], 'c': [3, 3, 3]})
    pdf2 = pd.DataFrame(data={'x': [1, 2, 3, 4], 'a': [2, 2, 4, 4], 'c': [1, 2, 3, 4]})

    df1 = DataFrame.from_pandas(engine=engine, df=pdf1, convert_objects=True)
    df2 = DataFrame.from_pandas(engine=engine, df=pdf2, convert_objects=True)

    df1 = df1.set_index('a')
    df2 = df2.set_index('x')
    dialect = df1.engine.dialect

    # data column name is in the resultant index
    result = df1['b'] - df2['a'] - df2['c']
    assert result.base_node.references['left_node'] == df1.base_node
    assert result.base_node.references['right_node'] == df2.base_node

    if is_postgres(dialect):
        assert '("b" - "a__data_column") - "c"' == result.expression.to_sql(dialect)
    elif is_bigquery(dialect):
        assert '(`b` - `a__data_column`) - `c`' == result.expression.to_sql(dialect)
    else:
        raise Exception()

    assert {'a', 'b', 'a__data_column', 'c'} == set(result.base_node.columns)
    assert Expression.table_column_reference('r', 'a') == result.base_node.column_expressions['a__data_column']

    # data column is already referenced on previous node
    result2 = (result + df1['c']) * df1['c'] - df2['c']
    assert result2.base_node.references['left_node'] == df1.base_node
    assert result2.base_node.references['right_node'] == df2.base_node
    if is_postgres(dialect):
        assert '(((("b" - "a__data_column") - "c__other") + "c") * "c") - "c__other"' == result2.expression.to_sql(
            dialect)
    elif is_bigquery(dialect):
        assert '((((`b` - `a__data_column`) - `c__other`) + `c`) * `c`) - `c__other`' == result2.expression.to_sql(
            dialect)
    else:
        raise Exception()

    assert {'a', 'b', 'a__data_column', 'c', 'c__other'} == set(result2.base_node.columns)

    assert Expression.table_column_reference('l', 'c') == result2.base_node.column_expressions['c']
    assert Expression.table_column_reference('r', 'c') == result2.base_node.column_expressions['c__other']


def test__set_item_with_merge_index_level_error(engine) -> None:
    bt = get_df_with_test_data(engine, full_data_set=False)
    bt2 = bt.groupby(bt.index_columns)['inhabitants'].sum().to_frame()

    bt = bt.reset_index(drop=True)
    bt2 = bt2.reset_index(drop=True)
    with pytest.raises(ValueError, match=r'both series must have at least one index level'):
        bt['inhabitants'] + bt2['inhabitants']


def test__set_item_with_merge_different_dtypes() -> None:
    bt = get_bt_with_test_data(full_data_set=False)

    bt2 = bt.copy()
    bt2._index[bt2.index_columns[0]] = bt2.index[bt2.index_columns[0]].astype(str)
    bt2 = bt2.groupby(bt2.index_columns)['inhabitants'].sum().to_frame()

    with pytest.raises(ValueError, match=r'dtypes of indexes to be merged'):
        bt['inhabitants'] + bt2['inhabitants']


def test__set_item_with_merge_w_group_shared_name() -> None:
    bt = get_bt_with_test_data(full_data_set=True)
    mt = get_bt_with_food_data()
    mt['inhabitants'] = mt.skating_order

    max_bt_inh = bt.groupby('skating_order').inhabitants.max()

    max_mt_inh = mt.groupby('skating_order').inhabitants.max()
    min_mt_inh = mt.groupby('skating_order').inhabitants.min()

    result1 = max_bt_inh / max_mt_inh
    assert_equals_data(
        result1,
        expected_columns=['skating_order', 'inhabitants'],
        expected_data=[
            [1, 93485.],
            [2, 16760.],
            [3, None],
            [4, 175.],
            [5, None],
            [6, None],
            [7, None],
            [8, None],
            [9, None],
            [10, None],
            [11, None],
        ],
    )
    result_expression = result1.expression.to_sql(result1.engine)
    assert 'inhabitants__other' in result_expression

    result2 = result1 - max_mt_inh
    result_expression2 = result2.expression.to_sql(result2.engine)
    assert_equals_data(
        result2,
        expected_columns=['skating_order', 'inhabitants'],
        expected_data=[
            [1, 93484.],
            [2, 16758.],
            [3, None],
            [4, 171.],
            [5, None],
            [6, None],
            [7, None],
            [8, None],
            [9, None],
            [10, None],
            [11, None],
        ],
    )
    assert 'inhabitants__other' in result_expression2

    grouped_df = mt.groupby('skating_order').agg(['min', 'max']).materialize()
    result3 = max_bt_inh / grouped_df['inhabitants_max'] - grouped_df['inhabitants_min']
    pd.testing.assert_series_equal(result2.sort_index().to_pandas(), result3.sort_index().to_pandas())
