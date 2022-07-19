"""
Copyright 2021 Objectiv B.V.
"""
from typing import Optional

import pytest

from sql_models.graph_operations import get_graph_nodes_info
from sql_models.util import is_bigquery, is_postgres
from tests.functional.bach.test_data_and_utils import assert_equals_data, get_df_with_test_data


def test_get_sample(engine, unique_table_test_name):
    # For reliable asserts (see below) we need more rows than the standard dataset of 11 rows has.
    # Therefore we append the dataset to itself two times to get 33 rows in total.
    df = get_df_with_test_data(engine, True)
    df = df.append([df, df])

    df_sample = df.get_sample(table_name=unique_table_test_name,
                              sample_percentage=50,
                              overwrite=True)
    # We cannot know the exact rows in df_sample, as that's random.
    # However, the columns should match, and additionally, since df has 33 rows, we can be _very_ sure
    # that df_sample has at least a row and less than 33.
    pdf_sample = df_sample.to_pandas()
    assert pdf_sample.index.name == '_index_skating_order'
    assert list(pdf_sample.columns) == ['skating_order', 'city', 'municipality', 'inhabitants', 'founding']
    assert len(pdf_sample) > 0
    assert len(pdf_sample) < 33

    # If overwrite is not set, we expect an error
    with pytest.raises(Exception, match='[aA]lready [eE]xists'):
        df_sample = df.get_sample(table_name=unique_table_test_name,
                                  sample_percentage=50)


@pytest.mark.skip_bigquery('We do not support the seed parameter for bigquery')
def test_get_sample_seed(engine, unique_table_test_name):
    bt = get_df_with_test_data(engine, True)
    bt_sample = bt.get_sample(table_name=unique_table_test_name,
                              sample_percentage=50,
                              seed=_get_seed(engine),
                              overwrite=True)

    assert_equals_data(
        bt_sample,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding',  # data columns
        ],
        expected_data=[
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268],
            [4, 4, 'Sleat', 'De Friese Meren', 700, 1426],
            [6, 6, 'Hylpen', 'Súdwest-Fryslân', 870, 1225]
        ]
    )


_EXPECTED_COLUMNS_OPERATIONS = [
    '_index_skating_order',  # index
    'skating_order', 'city', 'municipality', 'inhabitants', 'founding',
    'better_city', 'a', 'big_city', 'b', 'extra_ppl'
]
_EXPECTED_DATA_OPERATIONS = [
    [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 'Ljouwert_better', 'LjLe', 93495, 94770, 93490],
    [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 'Snits_better', 'SnSú', 33530, 34976, 33525],
    [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 'Drylts_better', 'DrSú', 3065, 4323, 3060],
    [4, 4, 'Sleat', 'De Friese Meren', 700, 1426, 'Sleat_better', 'SlDe', 710, 2126, 705],
    [5, 5, 'Starum', 'Súdwest-Fryslân', 960, 1061, 'Starum_better', 'StSú', 970, 2021, 965],
    [6, 6, 'Hylpen', 'Súdwest-Fryslân', 870, 1225, 'Hylpen_better', 'HySú', 880, 2095, 875],
    [7, 7, 'Warkum', 'Súdwest-Fryslân', 4440, 1399, 'Warkum_better', 'WaSú', 4450, 5839, 4445],
    [8, 8, 'Boalsert', 'Súdwest-Fryslân', 10120, 1455, 'Boalsert_better', 'BoSú', 10130, 11575, 10125],
    [9, 9, 'Harns', 'Harlingen', 14740, 1234, 'Harns_better', 'HaHa', 14750, 15974, 14745],
    [10, 10, 'Frjentsjer', 'Waadhoeke', 12760, 1374, 'Frjentsjer_better', 'FrWa', 12770, 14134, 12765],
    [11, 11, 'Dokkum', 'Noardeast-Fryslân', 12675, 1298, 'Dokkum_better', 'DoNo', 12685, 13973, 12680]
]


def test_sample_operations(engine, unique_table_test_name):
    bt = get_df_with_test_data(engine, True)
    seed = _get_seed(engine)
    bt_sample = bt.get_sample(table_name=unique_table_test_name,
                              sample_percentage=50,
                              seed=seed,
                              overwrite=True)

    bt_sample['better_city'] = bt_sample.city + '_better'
    bt_sample['a'] = bt_sample.city.str[:2] + bt_sample.municipality.str[:2]
    bt_sample['big_city'] = bt_sample.inhabitants + 10
    bt_sample['b'] = bt_sample.inhabitants + bt_sample.founding

    # If seed is set, we know what to expect from the 'random' values.
    # If seed is not set, then the database doesn't support it. We just skip the assert for those databases.
    if seed is not None:
        assert bt_sample.skating_order.nunique().value == 3

    all_data_bt = bt_sample.get_unsampled()
    all_data_bt['extra_ppl'] = all_data_bt.inhabitants + 5

    assert_equals_data(
        all_data_bt,
        expected_columns=_EXPECTED_COLUMNS_OPERATIONS,
        expected_data=_EXPECTED_DATA_OPERATIONS
    )


def test_sample_operations_filter(engine, unique_table_test_name):
    bt = get_df_with_test_data(engine, True)
    bt_sample = bt.get_sample(table_name=unique_table_test_name,
                              filter=bt.skating_order % 2 == 0,
                              overwrite=True)

    bt_sample['better_city'] = bt_sample.city + '_better'
    bt_sample['a'] = bt_sample.city.str[:2] + bt_sample.municipality.str[:2]
    bt_sample['big_city'] = bt_sample.inhabitants + 10
    bt_sample['b'] = bt_sample.inhabitants + bt_sample.founding
    assert bt_sample.skating_order.nunique().value == 5

    all_data_bt = bt_sample.get_unsampled()
    all_data_bt['extra_ppl'] = all_data_bt.inhabitants + 5
    assert_equals_data(
        all_data_bt,
        expected_columns=_EXPECTED_COLUMNS_OPERATIONS,
        expected_data=_EXPECTED_DATA_OPERATIONS
    )


def test_combine_unsampled_with_before_data(engine, unique_table_test_name):
    # Test that the get_unsampled() df has a base_node and state that is compatible with the base_node and
    # state of the original df
    dff = get_df_with_test_data(engine, True)
    dff_s = dff[['municipality', 'city']].get_sample(
        unique_table_test_name, overwrite=True, sample_percentage=50
    )
    dff_s['e'] = dff_s.city + '_extended'
    new_dff = dff_s.get_unsampled()
    assert new_dff.all_series.keys() == dff_s.all_series.keys()
    dff['e'] = new_dff.e


def test_get_unsampled_multiple_nodes(engine, unique_table_test_name):
    # 1. Start with dataframe with multiple nodes in graph
    # 2. Create sampled dataframe
    # 3. Add node to sampled dataframe
    # 4. Go back to unsampled data
    bt = get_df_with_test_data(engine, False)
    num_start_nodes = len(get_graph_nodes_info(bt.base_node))
    bt = bt[['municipality', 'inhabitants', 'founding']]
    bt['inhabitants_more'] = bt['inhabitants'] + 1000
    bt = bt.materialize()
    bt['inhabitants_more'] = bt['inhabitants_more'] + 1000
    # assert graph contains multiple nodes
    assert len(get_graph_nodes_info(bt.base_node)) >= 2
    assert len(get_graph_nodes_info(bt.base_node)) == num_start_nodes + 1

    bt_sample = bt.get_sample(table_name=unique_table_test_name,
                              sample_percentage=50,
                              overwrite=True)
    # bt_sample is based on newly created table, so there will only be a single node in the graph
    assert len(get_graph_nodes_info(bt_sample.base_node)) == 1
    bt_sample = bt_sample[['municipality', 'inhabitants_more', 'founding']]
    bt_sample['inhabitants_plus_3000'] = bt_sample['inhabitants_more'] + 1000
    del bt_sample['inhabitants_more']
    bt_sample = bt_sample.groupby('municipality').sum(numeric_only=True)
    bt_sample['inhabitants_plus_3000_sum'] -= 3000

    bt2 = bt_sample.get_unsampled()
    bt2['extra_ppl'] = bt2.inhabitants_plus_3000_sum + 5

    with pytest.raises(ValueError, match='has not been sampled'):
        bt2.get_unsampled()

    assert_equals_data(
        bt2,
        expected_columns=[
            'municipality', 'founding_sum', 'inhabitants_plus_3000_sum',
            'extra_ppl'
        ],
        expected_data=[
            ['Leeuwarden', 1285, 93485, 93490],
            ['Súdwest-Fryslân', 2724, 39575, 39580]
        ]
    )


def test_sample_w_temp_tables(engine, unique_table_test_name):
    # Test to prevent regression: get_sample() should work after materialize(materialization='temp_table')
    df = get_df_with_test_data(engine, True)
    df = df.append([df, df])

    # materialize and add some operation
    df = df.materialize(node_name='first', materialization='temp_table')
    df['founding'] = df.founding + 1000
    df = df.materialize(node_name='second', materialization='temp_table')

    df_sample = df.get_sample(table_name=unique_table_test_name,
                              sample_percentage=50,
                              overwrite=True)
    pdf_sample = df_sample.to_pandas()
    assert pdf_sample.index.name == '_index_skating_order'
    assert list(pdf_sample.columns) == ['skating_order', 'city', 'municipality', 'inhabitants', 'founding']
    assert len(pdf_sample) > 0
    assert len(pdf_sample) < 33


def test_sample_grouped(engine, unique_table_test_name):
    bt = get_df_with_test_data(engine, True)
    seed = _get_seed(engine)
    bt = bt[['municipality', 'inhabitants', 'founding']]
    bt['founding_century'] = (bt['founding'] // 100) + 1
    btg = bt.groupby('municipality').sort_values('municipality')
    btg_min = btg.min()

    with pytest.raises(ValueError, match='contains Series that have no aggregation function yet'):
        btg_sample = btg.get_sample(table_name=unique_table_test_name,
                                    sample_percentage=50,
                                    seed=seed,
                                    overwrite=True)

    btg_max = btg.max()
    btg_sample_max = btg_max.get_sample(table_name=unique_table_test_name,
                                    sample_percentage=50,
                                    seed=seed,
                                    overwrite=True)
    btg_sample_max = btg_sample_max[['founding_century_max']]
    btg_sample_max['founding_century_max_plus_10'] = btg_sample_max['founding_century_max'] + 10
    del btg_sample_max['founding_century_max']

    btg_unsampled_max = btg_sample_max.get_unsampled()

    btg_unsampled_max['after_unsample_plus_20'] = btg_unsampled_max.founding_century_max_plus_10 + 10
    btg_unsampled_max['founding_century_min'] = btg_min['founding_century_min']

    with pytest.raises(ValueError, match='has not been sampled'):
        btg_unsampled_max.get_unsampled()

    # Assert sampled data first.
    # We expect less rows than in the unsampled data. Which rows are returned should be deterministic
    # given the seed and sample_percentage.
    # If seed is not set, then the database doesn't support it. We just skip the assert for those databases.
    if seed is not None:
        assert_equals_data(
            btg_sample_max,
            expected_columns=['municipality', 'founding_century_max_plus_10'],
            expected_data=[
                ['Leeuwarden', 23.0],
                ['Noardeast-Fryslân', 23.0],
                ['Waadhoeke', 24.0]
            ]
        )

    # Assert unsampled data.
    # Should have all rows, and a few more columns as we added those after unsampling.
    assert_equals_data(
        btg_unsampled_max,
        expected_columns=[
            'municipality', 'founding_century_max_plus_10', 'after_unsample_plus_20', 'founding_century_min'
        ],
        expected_data=[
            ['De Friese Meren', 25.0, 35.0, 15.0],
            ['Harlingen', 23.0, 33.0, 13.0],
            ['Leeuwarden', 23.0, 33.0, 13.0],
            ['Noardeast-Fryslân', 23.0, 33.0, 13.0],
            ['Súdwest-Fryslân', 25.0, 35.0, 11.0],
            ['Waadhoeke', 24.0, 34.0, 14.0]
        ]
    )


def test_sample_operations_variable(engine, unique_table_test_name):
    # Test to prevent regression: using variables and materializing them should not change the SqlModel type
    # and then break when calling `is_materialized` after unsample()
    bt = get_df_with_test_data(engine, True)
    seed = _get_seed(engine)
    bt_sample = bt.get_sample(table_name=unique_table_test_name,
                              sample_percentage=50,
                              seed=seed,
                              overwrite=True)

    bt_sample, var = bt_sample.create_variable('var', 10)
    bt_sample['better_city'] = bt_sample.city + '_better'
    bt_sample['a'] = bt_sample.city.str[:2] + bt_sample.municipality.str[:2]
    bt_sample['big_city'] = bt_sample.inhabitants + var
    bt_sample['b'] = bt_sample.inhabitants + bt_sample.founding
    bt_sample = bt_sample.materialize()
    # If seed is set, we know what to expect from the 'random' values.
    # If seed is not set, then the database doesn't support it. We just skip the assert for those databases.
    if seed is not None:
        assert bt_sample.skating_order.nunique().value == 3

    all_data_bt = bt_sample.get_unsampled()
    all_data_bt['extra_ppl'] = all_data_bt.inhabitants + 5

    assert_equals_data(
        all_data_bt,
        expected_columns=_EXPECTED_COLUMNS_OPERATIONS,
        expected_data=_EXPECTED_DATA_OPERATIONS
    )
    assert not all_data_bt.is_materialized  # this used to raise an exception
    all_data_bt = all_data_bt.materialize()
    assert all_data_bt.is_materialized


def _get_seed(engine) -> Optional[int]:
    """ Return 200 if the database supports seeding. """
    if is_bigquery(engine):
        return None
    if is_postgres(engine):
        return 200
    raise Exception()
