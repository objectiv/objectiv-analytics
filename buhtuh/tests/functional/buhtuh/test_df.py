"""
Copyright 2021 Objectiv B.V.
"""
from unittest.mock import ANY

import pytest
from buhtuh import BuhTuhDataFrame, BuhTuhSeriesBoolean, BuhTuhSeriesUuid
from sql_models.graph_operations import get_graph_nodes_info
from tests.functional.buhtuh.test_data_and_utils import get_bt_with_test_data, assert_equals_data


def test_del_item():
    bt = get_bt_with_test_data()

    del(bt['founding'])
    assert 'founding' not in bt.data.keys()
    with pytest.raises(KeyError):
        bt.founding

    with pytest.raises(KeyError):
        del(bt['non existing column'])


def test_drop_items():
    bt = get_bt_with_test_data()

    nbt = bt.drop(columns=['founding'])
    assert 'founding' not in nbt.data.keys()
    assert 'founding' in bt.data.keys()

    bt.founding
    with pytest.raises(KeyError):
        nbt.founding

    nbt = bt.drop(columns=['founding'], inplace=True)
    assert 'founding' not in nbt.data.keys()
    assert 'founding' not in bt.data.keys()

    bt.drop(columns=['inhabitants', 'city'], inplace=True)
    assert 'inhabitants' not in bt.data.keys()
    assert 'city' not in bt.data.keys()

    with pytest.raises(KeyError):
        bt.drop(columns=['non existing column'])

    bt.drop(columns=['non existing column'], errors='ignore')


def test_combined_operations1():
    bt = get_bt_with_test_data(full_data_set=True)
    bt['x'] = bt['municipality'] + ' some string'
    bt['y'] = bt['skating_order'] + bt['skating_order']
    result_bt = bt.groupby('x')['y'].count()
    print(result_bt.view_sql())
    assert_equals_data(
        result_bt,
        order_by='x',
        expected_columns=['x', 'y_count'],
        expected_data=[
            ['De Friese Meren some string', 1],
            ['Harlingen some string', 1],
            ['Leeuwarden some string', 1],
            ['Noardeast-Fryslân some string', 1],
            ['Súdwest-Fryslân some string', 6],
            ['Waadhoeke some string', 1],
        ]
    )

    result_bt['z'] = result_bt['y_count'] + 10
    result_bt['y_count'] = result_bt['y_count'] + (-1)
    assert_equals_data(
        result_bt,
        order_by='x',
        expected_columns=['x', 'y_count', 'z'],
        expected_data=[
            ['De Friese Meren some string', 0, 11],
            ['Harlingen some string', 0, 11],
            ['Leeuwarden some string', 0, 11],
            ['Noardeast-Fryslân some string', 0, 11],
            ['Súdwest-Fryslân some string', 5, 16],
            ['Waadhoeke some string', 0, 11],
        ]
    )
    assert result_bt.y_count == result_bt['y_count']


def test_boolean_indexing_same_node():
    bt = get_bt_with_test_data(full_data_set=True)
    bti = bt['founding'] < 1300
    assert isinstance(bti, BuhTuhSeriesBoolean)
    result_bt = bt[bti]
    assert isinstance(result_bt, BuhTuhDataFrame)
    assert_equals_data(
        result_bt,
        expected_columns=['_index_skating_order', 'skating_order', 'city', 'municipality', 'inhabitants',
                          'founding'],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268],
            [5, 5, 'Starum', 'Súdwest-Fryslân', 960, 1061],
            [6, 6, 'Hylpen', 'Súdwest-Fryslân', 870, 1225],
            [9, 9, 'Harns', 'Harlingen', 14740, 1234],
            [11, 11, 'Dokkum', 'Noardeast-Fryslân', 12675, 1298]
        ]
    )


def test_get_df_materialized_model():
    bt = get_bt_with_test_data()[['city', 'founding']]
    bt['city'] = bt['city'] + ' '
    bt['uuid'] = BuhTuhSeriesUuid.sql_gen_random_uuid(bt)
    bt['founding_str'] = bt['founding'].astype('string')
    bt['city_founding'] = bt['city'] + bt['founding_str']
    bt['founding'] = bt['founding'] + 200
    expected_columns = ['_index_skating_order', 'city', 'founding', 'uuid', 'founding_str', 'city_founding']
    expected_data = [
            [1, 'Ljouwert ', 1485, ANY, '1285', 'Ljouwert 1285'],
            [2, 'Snits ', 1656, ANY, '1456', 'Snits 1456'],
            [3, 'Drylts ', 1468, ANY, '1268', 'Drylts 1268'],
        ]

    assert_equals_data(bt, expected_columns=expected_columns, expected_data=expected_data)

    bt_materialized = bt.get_df_materialized_model()
    # The materialized DataFrame should result in the exact same data
    assert_equals_data(bt_materialized, expected_columns=expected_columns, expected_data=expected_data)

    # The original DataFrame has a 'complex' expression for all data columns. The materialized df should
    # have an expression that's simply the name of the column for all data columns, as the complex expression
    # has been moved to the new underlying base_node.
    for series in bt.data.values():
        assert series.get_expression() != f'"{series.name}"'
    for series in bt_materialized.data.values():
        assert series.get_expression() == f'"{series.name}"'

    # The materialized graph should have one extra node
    node_info_orig = get_graph_nodes_info(bt.get_current_node())
    node_info_mat = get_graph_nodes_info(bt_materialized.get_current_node())
    assert len(node_info_orig) + 1 == len(node_info_mat)
    previous_node_mat = list(bt_materialized.get_current_node().references.values())[0]
    assert previous_node_mat == bt.get_current_node()


def test_get_df_materialized_model_non_deterministic_expressions():
    bt = get_bt_with_test_data()[['city']]
    bt['uuid1'] = BuhTuhSeriesUuid.sql_gen_random_uuid(bt)
    # now bt['uuid1'] has not been evaluated, so copying the column should copy the unevaluated expression
    bt['uuid2'] = bt['uuid1']
    bt['eq'] = bt['uuid1'] == bt['uuid2']  # expect False
    expected_columns = ['_index_skating_order', 'city', 'uuid1', 'uuid2', 'eq']
    expected_data = [
            [1, 'Ljouwert', ANY, ANY, False],
            [2, 'Snits', ANY, ANY, False],
            [3, 'Drylts', ANY, ANY, False],
        ]
    assert_equals_data(bt, expected_columns=expected_columns, expected_data=expected_data)
    bt = bt.get_df_materialized_model()
    # Now bt['uuid1'] has been evaluated, so copying the column should copy the value not just the expression
    bt['uuid3'] = bt['uuid1']
    # Now a comparison should give True
    bt['eq2'] = bt['uuid1'] == bt['uuid3']
    expected_columns = ['_index_skating_order', 'city', 'uuid1', 'uuid2', 'eq', 'uuid3', 'eq2']
    expected_data = [
            [1, 'Ljouwert', ANY, ANY, False, ANY, True],
            [2, 'Snits', ANY, ANY, False, ANY, True],
            [3, 'Drylts', ANY, ANY, False, ANY, True],
        ]
    assert_equals_data(bt, expected_columns=expected_columns, expected_data=expected_data)
