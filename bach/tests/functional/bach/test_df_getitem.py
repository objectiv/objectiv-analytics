"""
Copyright 2021 Objectiv B.V.
"""
import pytest

from bach import DataFrame, Series, SeriesDict
from sql_models.util import is_bigquery, is_postgres
from tests.functional.bach.test_data_and_utils import assert_equals_data, df_to_list, \
    get_df_with_test_data


def test_get_item_single(engine):
    bt = get_df_with_test_data(engine)

    selection = bt[['city']]
    assert isinstance(selection, DataFrame)
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
    assert isinstance(selection, DataFrame)
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
    assert isinstance(selection, Series)
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


def test_get_item_multiple(engine):
    bt = get_df_with_test_data(engine)
    selection = bt[['city', 'founding']]
    assert isinstance(selection, DataFrame)
    assert_equals_data(
        selection,
        expected_columns=['_index_skating_order', 'city', 'founding'],
        expected_data=[
            [1, 'Ljouwert', 1285],
            [2, 'Snits',  1456],
            [3, 'Drylts', 1268],
        ]
    )


def test_positional_slicing(pg_engine):
    # TODO: BigQuery
    bt = get_df_with_test_data(pg_engine, full_data_set=True)

    class ReturnSlice:
        def __getitem__(self, key):
            return key
    return_slice = ReturnSlice()

    with pytest.raises(NotImplementedError, match="index key lookups not supported, use slices instead."):
        bt[3]

    # negative slices are not supported, so we will not test those.
    slice_list = [return_slice[:4],
                  return_slice[4:],
                  return_slice[4:7],
                  return_slice[:],
                  return_slice[4:5],
                  return_slice[:1]
                  ]
    for s in slice_list:
        bt_slice = bt[s]

        # if the slice length == 1, all Series need to have a single value expression
        assert (len('slice_me_now'.__getitem__(s)) == 1) == all(s.expression.is_single_value
                                                                for s in bt_slice.all_series.values())

        assert_equals_data(
            bt[s],
            expected_columns=['_index_skating_order', 'skating_order', 'city', 'municipality', 'inhabitants',
                              'founding'],
            expected_data=df_to_list(bt.to_pandas()[s])
        )


def test_get_item_materialize(engine):
    bt = get_df_with_test_data(engine, full_data_set=True)[['municipality', 'inhabitants']]
    bt = bt.groupby('municipality')[['inhabitants']].sum()
    r = bt[bt.inhabitants_sum != 700] #  'Friese Meren' be gone!

    assert_equals_data(
        r,
        order_by='inhabitants_sum',
        expected_columns=['municipality', 'inhabitants_sum'],
        expected_data=[
            ['Noardeast-Fryslân', 12675], ['Waadhoeke', 12760],
            ['Harlingen', 14740], ['Súdwest-Fryslân', 52965],
            ['Leeuwarden', 93485]
        ]
    )


def test_get_item_mixed_groupby(engine):
    bt = get_df_with_test_data(engine, full_data_set=True)[['municipality', 'inhabitants', 'founding']]

    grouped = bt.groupby('municipality')
    grouped_sum = grouped.inhabitants.sum()
    grouped_all_sum = grouped.sum()

    with pytest.raises(ValueError, match="Can not apply aggregated BooleanSeries to a non-grouped df."):
        bt[grouped_sum > 50000]

    # Okay to apply same grouping filter
    assert_equals_data(
        grouped_all_sum[grouped_sum > 50000],
        order_by='inhabitants_sum',
        expected_columns=['municipality', 'inhabitants_sum', 'founding_sum'],
        expected_data=[
            ['Súdwest-Fryslân', 52965, 7864],
            ['Leeuwarden', 93485, 1285]
        ]
    )

    # Apply a filter on a column of the pre-aggregation df
    assert_equals_data(
        grouped_all_sum[bt.founding < 1300],
        order_by='inhabitants_sum',
        expected_columns=['municipality', 'inhabitants_sum', 'founding_sum'],
        expected_data=[
            ['Súdwest-Fryslân', 4885, 3554], ['Noardeast-Fryslân', 12675, 1298],
            ['Harlingen', 14740, 1234], ['Leeuwarden', 93485, 1285]
        ]
    )

    # Apply a filter on non-aggregated index column of the df
    assert_equals_data(
        grouped_all_sum[grouped_all_sum.index['municipality'] == 'Harlingen'],
        order_by='inhabitants_sum',
        expected_columns=['municipality', 'inhabitants_sum', 'founding_sum'],
        expected_data=[
            ['Harlingen', 14740, 1234]
        ]
    )

    grouped_other = bt.groupby(bt.municipality.str[:3])
    grouped_other_sum = grouped_other.inhabitants.sum()

    # This does not work because it has to materialize to filter, but no aggregations functions have been
    # applied yet, so we can't.
    with pytest.raises(ValueError, match="groupby set, but contains Series that have no aggregation func"):
        grouped[bt.founding < 1300]

    # check that it's illegal to mix different groupings in filters
    expected_message = "Can not apply aggregated BooleanSeries with non matching group_by"

    with pytest.raises(ValueError, match=expected_message):
            grouped[grouped_other_sum > 50000]

    # check the other way around for good measure
    with pytest.raises(ValueError, match=expected_message):
        grouped_other[grouped_sum > 50000]

    # or the combination of both, behold!
    with pytest.raises(ValueError, match="Cannot apply Boolean series with a different base_node to DataFrame"):
        # todo do internal merge, similar to setting with different base nodes
        grouped_other[grouped_sum > grouped_other_sum]


@pytest.mark.skip_postgres
def test_get_item_w_dict_series(engine):
    df = get_df_with_test_data(engine)[['city']]
    struct = {
        'a': 123,
        'b': 'test',
    }
    dtype = {'a': 'int64', 'b': 'string'}
    df['struct'] = SeriesDict.from_value(base=df, value=struct, name='struct', dtype=dtype)

    result = df[df['city'] == 'Drylts']
    assert_equals_data(
        result,
        expected_columns=['_index_skating_order', 'city', 'struct'],
        expected_data=[[3, 'Drylts', struct]],
    )
