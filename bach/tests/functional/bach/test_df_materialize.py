"""
Copyright 2021 Objectiv B.V.
"""
from typing import Union
from unittest.mock import ANY

import pytest
from sqlalchemy.engine import Engine

from bach import SeriesUuid
from sql_models.graph_operations import get_graph_nodes_info
from sql_models.model import Materialization
from sql_models.util import is_bigquery, is_postgres
from tests.functional.bach.test_data_and_utils import assert_equals_data, get_df_with_test_data, \
    get_df_with_json_data


@pytest.mark.parametrize("inplace", [False, True])
@pytest.mark.parametrize("materialization", [Materialization.CTE, 'temp_table'])
def test_materialize(inplace: bool, materialization: Union[Materialization, str], engine: Engine):
    bt = get_df_with_test_data(engine)[['city', 'founding']]
    bt['city'] = bt['city'] + ' '
    bt['uuid'] = SeriesUuid.random(bt)
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

    if inplace:
        bt_materialized = bt.copy()
        bt_materialized.materialize(node_name='node', inplace=True, materialization=materialization)
    else:
        bt_materialized = bt.materialize(node_name='node', materialization=materialization)
    # The materialized DataFrame should result in the exact same data
    assert_equals_data(bt_materialized, expected_columns=expected_columns, expected_data=expected_data)

    assert bt_materialized.is_materialized
    # The original DataFrame has a 'complex' expression for all data columns. The materialized df should
    # have an expression that's simply the name of the column for all data columns, as the complex expression
    # has been moved to the new underlying base_node.
    for series_name in bt.data_columns:
        if is_postgres(engine):
            expected_to_sql = f'"{series_name}"'
        elif is_bigquery(engine):
            expected_to_sql = f'`{series_name}`'
        else:
            raise Exception('we need to expand this test')
        assert bt[series_name].expression.to_sql(engine.dialect) != expected_to_sql
        assert bt_materialized[series_name].expression.to_sql(engine.dialect) == expected_to_sql

    # The materialized graph should have one extra node
    # If the materialization was temp_table, then the node before that was changed too: its materialization
    # will be different
    node_info_orig = get_graph_nodes_info(bt.get_current_node('node'))
    node_info_mat = get_graph_nodes_info(bt_materialized.get_current_node('node'))
    assert len(node_info_orig) + 1 == len(node_info_mat)
    previous_node_mat = list(bt_materialized.get_current_node('node').references.values())[0]
    node_before_mat = bt.get_current_node('node')
    node_before_mat = node_before_mat.copy_set_materialization(Materialization.normalize(materialization))
    assert previous_node_mat == node_before_mat


@pytest.mark.parametrize("inplace", [False, True])
def test_materialize_with_non_aggregation_series(inplace: bool, engine):
    # A dataframe with a groupby set, but without all columns setup for aggregation should raise
    bt = get_df_with_test_data(engine)[['municipality', 'founding', 'inhabitants']]
    btg = bt.groupby('municipality')
    assert btg.group_by is not None
    with pytest.raises(ValueError, match="groupby set, but contains Series that have no aggregation func.*"
                                         "\\['founding', 'inhabitants'\\]"):
        btg.materialize(inplace=inplace)

    assert btg.base_node == bt.base_node

    # Add one that's aggregated, should still fail
    btg['founding'] = btg.founding.sum()
    with pytest.raises(ValueError, match="groupby set, but contains Series that have no aggregation func.*"
                                         "\\['inhabitants'\\]"):
        btg.materialize(inplace=inplace)
    assert btg.base_node == bt.base_node

    # Selecting the aggregated series in the df should work
    btg_founding_only = btg[['founding']]
    btg_founding_only_materialized = btg_founding_only.copy().materialize(inplace=inplace)
    assert btg_founding_only_materialized.base_node != bt.base_node

    # As should getting the series only and converting it back to a frame
    btg_founding_only = btg['founding'].to_frame()
    btg_founding_only_materialized = btg_founding_only.copy().materialize(inplace=inplace)
    assert btg_founding_only_materialized.base_node != bt.base_node

    # Fix the last one,
    btg['inhabitants'] = btg.inhabitants.sum()
    bt_materialized = btg.copy().materialize(inplace=inplace)
    assert bt_materialized.base_node != btg.base_node


@pytest.mark.parametrize("inplace", [False, True])
def test_materialize_non_deterministic_expressions(inplace: bool, engine):
    bt = get_df_with_test_data(engine)[['city']]
    bt['uuid1'] = SeriesUuid.random(bt)
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
    if inplace:
        bt.materialize(node_name='node', inplace=True)
    else:
        bt = bt.materialize(node_name='node')
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


def test_is_materialized(engine):
    df_original = get_df_with_test_data(engine)
    assert df_original.is_materialized
    df = df_original.copy()
    assert df.is_materialized

    # adding column
    df['x'] = 'test'
    assert not df.is_materialized
    del df['x']
    assert df.is_materialized

    # group by
    df = df.groupby('municipality')
    assert not df.is_materialized

    # sort_values
    df = df_original.copy()
    assert df.is_materialized
    df = df.sort_values('city')
    assert not df.is_materialized


    # switching columns
    df = df_original.copy()
    assert df.is_materialized
    df['x'] = df['municipality']
    df['municipality'] = df['city']
    df['city'] = df['x']
    del df['x']
    assert not df.is_materialized

    # removing columns
    df = df_original.copy()
    assert df.is_materialized
    del df['municipality']
    assert not df.is_materialized


def test_is_materialized_json(engine):
    # Note that we only test the 'json' type here, not the Postgres specific json_postgres, as there is a
    # known problem that is_materialized is always False if such a column is present.

    df = get_df_with_json_data(engine=engine, dtype='json')
    assert df.is_materialized


# TODO: we should probably have a test here for each dtype
