import pytest

from bach import DataFrame
from bach.merge import revert_merge
from tests.functional.bach.test_data_and_utils import (
    get_df_with_test_data, get_df_with_railway_data, get_df_with_food_data,
)


def test_revert_merge_basic(engine):
    bt = get_df_with_test_data(engine, full_data_set=False)[['skating_order', 'city']]
    mt = get_df_with_food_data(engine)[['skating_order', 'food']]
    merged = bt.merge(mt)

    result_bt, result_mt = revert_merge(merged)

    for expected, result in zip([bt, mt], [result_bt, result_mt]):
        _compare_source_with_replicate(expected, result)


def test_revert_merge_basic_on(engine):
    bt = get_df_with_test_data(engine, full_data_set=False)[['skating_order', 'city']]
    mt = get_df_with_food_data(engine)[['skating_order', 'food']]
    merged = bt.merge(mt, on='skating_order')

    result_bt, result_mt = revert_merge(merged)

    for expected, result in zip([bt, mt], [result_bt, result_mt]):
        _compare_source_with_replicate(expected, result)


def test_revert_merge_basic_left_on_right_on_same_column(engine):
    bt = get_df_with_test_data(engine, full_data_set=False)[['skating_order', 'city']]
    mt = get_df_with_food_data(engine)[['skating_order', 'food']]
    merged = bt.merge(mt, left_on='skating_order', right_on='skating_order')

    result_bt, result_mt = revert_merge(merged)
    for expected, result in zip([bt, mt], [result_bt, result_mt]):
        _compare_source_with_replicate(expected, result)


def test_revert_merge_basic_left_on_right_on_different_column(engine):
    bt = get_df_with_test_data(engine, full_data_set=False)[['skating_order', 'city']]
    mt = get_df_with_railway_data(engine)[['town', 'station']]
    merged = bt.merge(mt, left_on='city', right_on='town')

    result_bt, result_mt = revert_merge(merged)
    for expected, result in zip([bt, mt], [result_bt, result_mt]):
        _compare_source_with_replicate(expected, result)


def test_revert_merge_basic_on_indexes(engine):
    bt = get_df_with_test_data(engine, full_data_set=False)[['skating_order', 'city']]
    mt = get_df_with_food_data(engine)[['skating_order', 'food']]

    merged_1 = bt.merge(mt, left_index=True, right_on='skating_order')
    result_bt1, result_mt1 = revert_merge(merged_1)

    merged_2 = bt.merge(mt, left_on='skating_order', right_index=True)
    result_bt2, result_mt2 = revert_merge(merged_2)

    merged_3 = bt.merge(mt, left_index=True, right_index=True)
    result_bt3, result_mt3 = revert_merge(merged_3)

    frames_to_compare = zip([bt, mt] * 3, [result_bt1, result_mt1, result_bt2, result_mt2, result_bt3, result_mt3])
    for expected, result in frames_to_compare:
        _compare_source_with_replicate(expected, result)


def test_revert_merge_suffixes(engine):
    bt = get_df_with_test_data(engine, full_data_set=False)[['skating_order', 'city']]
    mt = get_df_with_food_data(engine)[['skating_order', 'food']]
    merged = bt.merge(mt, left_on='_index_skating_order', right_on='skating_order', suffixes=('_AA', '_BB'))
    result_bt, result_mt = revert_merge(merged)
    for expected, result in zip([bt, mt], [result_bt, result_mt]):
        _compare_source_with_replicate(expected, result)


def test_revert_merge_mixed_columns(engine):
    bt = get_df_with_test_data(engine, full_data_set=False)[['skating_order', 'city']]
    mt = get_df_with_railway_data(engine)[['station', 'platforms']]
    # join _index_skating_order on the 'platforms' column
    merged = bt.merge(mt, how='inner', left_on='skating_order', right_on='platforms')
    result_bt, result_mt = revert_merge(merged)
    for expected, result in zip([bt, mt], [result_bt, result_mt]):
        _compare_source_with_replicate(expected, result)


def test_revert_merge_self(engine):
    bt1 = get_df_with_test_data(engine, full_data_set=False)[['city']]
    bt2 = get_df_with_test_data(engine, full_data_set=False)[['inhabitants']]
    merged = bt1.merge(bt2, on='_index_skating_order')
    result_bt1, result_bt2 = revert_merge(merged)
    for expected, result in zip([bt1, bt2], [result_bt1, result_bt2]):
        _compare_source_with_replicate(expected, result)


def test_revert_merge_preselection(engine):
    bt = get_df_with_test_data(engine, full_data_set=False)[['skating_order', 'city', 'inhabitants']]
    mt = get_df_with_food_data(engine)[['skating_order', 'food']]

    preselected_bt = bt[bt['skating_order'] != 1]
    preselected_mt = mt[['food']]
    merged = preselected_bt.merge(preselected_mt, on='_index_skating_order')

    result_bt, result_mt = revert_merge(merged)

    assert bt.base_node != result_bt.base_node  # filtering generates a materialization
    assert mt.base_node == result_mt.base_node
    for expected, result in zip([preselected_bt, preselected_mt], [result_bt, result_mt]):
        _compare_source_with_replicate(expected, result)


def test_revert_merge_expression_columns(engine):
    bt = get_df_with_test_data(engine, full_data_set=False)[['skating_order', 'city', 'inhabitants']]
    mt = get_df_with_food_data(engine)[['skating_order', 'food']]
    bt['skating_order'] += 2
    bt['inhabitants'] = bt['inhabitants'] * 100 + bt['skating_order']
    mt['skating_order'] += 4

    merged = bt.merge(mt, on=['skating_order'])
    result_bt, result_mt = revert_merge(merged)
    for expected, result in zip([bt, mt], [result_bt, result_mt]):
        _compare_source_with_replicate(expected, result)


def test_revert_merge_w_constant(engine):
    bt = get_df_with_test_data(engine, full_data_set=False)[['skating_order', 'city', 'inhabitants']]
    mt = get_df_with_food_data(engine)[['skating_order', 'food']]
    bt['constant'] = 1

    merged = bt.merge(mt, on=['skating_order'])
    result_bt, result_mt = revert_merge(merged)
    _compare_source_with_replicate(bt, result_bt)

    assert 'constant' in result_mt.all_series
    _compare_source_with_replicate(mt, result_mt[['skating_order', 'food']])


def test_revert_merge_grouped(engine):
    bt1 = get_df_with_test_data(engine, full_data_set=False)[['city']]
    bt2 = get_df_with_test_data(engine, full_data_set=False)[['inhabitants']]
    merged = bt1.merge(bt2, on='_index_skating_order')
    merged = merged.groupby('city').sum()

    with pytest.raises(Exception, match=r'aggregated frame'):
        revert_merge(merged)


def _compare_source_with_replicate(original_source: DataFrame, replicate: DataFrame) -> None:
    assert original_source.base_node == replicate.base_node
    assert original_source.data_columns == replicate.data_columns
    assert original_source.index == replicate.index

    dialect = original_source.engine.dialect
    for series_name in original_source.all_series:
        expected_sql = original_source.all_series[series_name].expression.to_sql(dialect)
        result_sql = replicate.all_series[series_name].expression.to_sql(dialect)
        assert expected_sql == result_sql
