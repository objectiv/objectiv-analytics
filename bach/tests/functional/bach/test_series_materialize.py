"""
Copyright 2022 Objectiv B.V.
"""

import pytest

from bach.series import Series
from sql_models.graph_operations import get_graph_nodes_info
from sql_models.model import Materialization
from sql_models.util import is_bigquery, is_postgres
from tests.functional.bach.test_data_and_utils import assert_equals_data, get_df_with_test_data


@pytest.mark.parametrize("materialization", [Materialization.CTE, 'temp_table'])
def test_materialize(engine, materialization):
    bt = get_df_with_test_data(engine)['city'] + ' '
    assert isinstance(bt, Series)

    expected_columns = ['_index_skating_order', 'city']
    expected_data = [
            [1, 'Ljouwert '],
            [2, 'Snits '],
            [3, 'Drylts '],
        ]
    assert_equals_data(bt, expected_columns=expected_columns, expected_data=expected_data)

    bt_materialized = bt.materialize(node_name='node', materialization=materialization)
    # The materialized Series should result in the exact same data
    assert_equals_data(bt_materialized, expected_columns=expected_columns, expected_data=expected_data)

    assert bt_materialized.is_materialized
    # The materialized series should have an expression that's simply the name of the column,
    # the 'complex' expression has been moved to the new underlying base_node.
    series_name = bt.name
    if is_postgres(engine):
        expected_to_sql = f'"{series_name}"'
    elif is_bigquery(engine):
        expected_to_sql = f'`{series_name}`'
    else:
        raise Exception('we need to expand this test')
    assert bt.expression.to_sql(engine.dialect) != expected_to_sql
    assert bt_materialized.expression.to_sql(engine.dialect) == expected_to_sql

    # The materialized graph should have one extra node
    # If the materialization was temp_table, then the node before that was changed too: its materialization
    # will be different
    node_info_orig = get_graph_nodes_info(bt.to_frame().get_current_node('node'))
    node_info_mat = get_graph_nodes_info(bt_materialized.to_frame().get_current_node('node'))
    assert len(node_info_orig) + 1 == len(node_info_mat)
    previous_node_mat = list(bt_materialized.to_frame().get_current_node('node').references.values())[0]
    node_before_mat = bt.to_frame().get_current_node('node')
    node_before_mat = node_before_mat.copy_set_materialization(Materialization.normalize(materialization))
    assert previous_node_mat == node_before_mat


def test_materialize_with_non_aggregation_series(engine):
    bt = get_df_with_test_data(engine)[['municipality', 'founding']]
    btg = bt.groupby('municipality')['founding']
    assert isinstance(btg, Series)
    assert btg.group_by is not None
    with pytest.raises(ValueError, match="groupby set, but contains Series that have no aggregation func.*"
                                         "\\['founding'\\]"):
        btg = btg.materialize()
    assert btg.base_node == bt.base_node

    bt = bt['founding'].materialize()
    btc = bt.copy().materialize()
    assert btc.base_node != bt.base_node


def test_is_materialized(engine):
    df_original = get_df_with_test_data(engine)

    btg = df_original['city'].materialize()
    assert isinstance(btg, Series)
    assert btg.is_materialized

    # group by
    btg = df_original.groupby('municipality')['city']
    assert not btg.is_materialized

    with pytest.raises(ValueError, match="groupby set, but contains Series that have no aggregation func.*"
                                         "\\['city'\\]"):
        btg.materialize()

    # sort_values
    df = df_original['city'].copy()
    df = df.materialize()
    assert df.is_materialized
    df = df.sort_values()
    assert not df.is_materialized
