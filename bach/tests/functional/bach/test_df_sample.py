"""
Copyright 2021 Objectiv B.V.
"""
import pandas
import pytest

from bach import from_pandas
from sql_models.graph_operations import get_graph_nodes_info
from tests.functional.bach.test_data_and_utils import get_bt_with_test_data, assert_equals_data


def test_get_sample():
    bt = get_bt_with_test_data(True)
    bt_sample = bt.get_sample(table_name='test_data_sample',
                              sample_percentage=50,
                              seed=200,
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


def test_sample_operations():
    bt = get_bt_with_test_data(True)
    bt_sample = bt.get_sample(table_name='test_data_sample',
                              sample_percentage=50,
                              seed=200,
                              overwrite=True)

    bt_sample['better_city'] = bt_sample.city + '_better'
    bt_sample['a'] = bt_sample.city.str[:2] + bt_sample.municipality.str[:2]
    bt_sample['big_city'] = bt_sample.inhabitants + 10
    bt_sample['b'] = bt_sample.inhabitants + bt_sample.founding
    assert bt_sample.skating_order.nunique().value == 3

    all_data_bt = bt_sample.get_unsampled()
    all_data_bt['extra_ppl'] = all_data_bt.inhabitants + 5

    assert_equals_data(
        all_data_bt,
        expected_columns=_EXPECTED_COLUMNS_OPERATIONS,
        expected_data=_EXPECTED_DATA_OPERATIONS
    )


def test_sample_operations_filter():
    bt = get_bt_with_test_data(True)
    bt_sample = bt.get_sample(table_name='test_data_sample',
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


def test_combine_unsampled_with_before_data():
    # Test that the get_unsampled() df has a base_node and state that is compatible with the base_node and
    # state of the original df
    dff = get_bt_with_test_data(True)
    dff_s = dff[['municipality', 'city']].get_sample(
        'sample_example_table', overwrite=True, sample_percentage=50
    )
    dff_s['e'] = dff_s.city + '_extended'
    new_dff = dff_s.get_unsampled()
    dff['e'] = new_dff.e


def test_get_unsampled_multiple_nodes():
    # 1. Start with dataframe with multiple nodes in graph
    # 2. Create sampled dataframe
    # 3. Add node to sampled dataframe
    # 4. Go back to unsampled data
    bt = get_bt_with_test_data(False)
    assert len(get_graph_nodes_info(bt.base_node)) == 1
    bt = bt[['municipality', 'inhabitants', 'founding']]
    bt['inhabitants_more'] = bt['inhabitants'] + 1000
    bt = bt.materialize()
    bt['inhabitants_more'] = bt['inhabitants_more'] + 1000
    bt = bt.materialize()

    node_count_bt = len(get_graph_nodes_info(bt.base_node))
    assert node_count_bt == 3

    bt_sample = bt.get_sample(table_name='test_data_sample',
                              sample_percentage=50,
                              seed=200,
                              overwrite=True)
    # bt_sample is based on newly created table, so there will only be a single node in the graph
    assert len(get_graph_nodes_info(bt_sample.base_node)) == 1
    bt_sample = bt_sample[['municipality', 'inhabitants_more', 'founding']]
    bt_sample['inhabitants_plus_3000'] = bt_sample['inhabitants_more'] + 1000
    del bt_sample['inhabitants_more']
    bt_sample = bt_sample.materialize()
    bt_sample = bt_sample.groupby('municipality').sum(numeric_only=True)
    bt_sample['inhabitants_plus_3000_sum'] -= 3000

    node_count_bt_sample = len(get_graph_nodes_info(bt_sample.base_node))
    assert node_count_bt_sample == 2

    bt2 = bt_sample.get_unsampled()
    bt2['extra_ppl'] = bt2.inhabitants_plus_3000_sum + 5

    node_count_bt2 = len(get_graph_nodes_info(bt2.base_node))
    # since sample was grouped, it needs to materialize internally, we expect one more node
    assert node_count_bt2 == (node_count_bt + node_count_bt_sample) == 5

    with pytest.raises(ValueError, match='has not been sampled'):
        bt2.get_unsampled()

    assert_equals_data(
        bt2,
        expected_columns=[
            'municipality', '_index_skating_order_sum', 'founding_sum', 'inhabitants_plus_3000_sum',
            'extra_ppl'
        ],
        expected_data=[
            ['Leeuwarden', 1, 1285, 93485, 93490],
            ['Súdwest-Fryslân', 5, 2724, 39575, 39580]
        ]
    )
