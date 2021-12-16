"""
Copyright 2021 Objectiv B.V.
"""
import re
from typing import List

import pytest

from sql_models.graph_operations import get_node, get_graph_nodes_info
from sql_models.model import SqlModel, RefPath, CustomSqlModelBuilder
from sql_models.sql_generator import to_sql
from tests.unit.sql_models.util import RefModel, ValueModel, JoinModel


def test_builder_cycles_raise_exception():
    rm1 = RefModel()
    rm2 = RefModel(ref=rm1)
    rm1.set_values(ref=rm2)

    # This should not loop endlessly, but error out because of the cycle between the SqlModelBuilder
    # classes.
    with pytest.raises(Exception):
        rm1.instantiate_recursively()
    with pytest.raises(Exception):
        rm2.instantiate_recursively()


def test_equality_base_cases():
    vm1 = ValueModel.build(key='X', val=1)
    vm2 = ValueModel.build(key='X', val=2)
    vm3 = ValueModel.build(key='X', val=1)
    assert vm1 != vm2
    assert vm1 == vm3
    assert vm2 != vm3

    rm = RefModel.build(ref=vm1)
    graph1 = JoinModel.build(ref_left=rm, ref_right=vm2)
    graph2 = JoinModel.build(ref_left=rm, ref_right=vm2)
    assert graph1 == graph2
    assert graph1 != vm1
    assert graph1 != vm2
    assert graph1 != vm3
    assert graph1 != rm


def test_equality_different_classes():
    vm1 = ValueModel.build(key='X', val=1)
    vm2 = ValueModel.build(key='X', val=2)
    csm1 = CustomSqlModelBuilder(
        sql="select '{key}' as key, {val} as value",
    )(key='X', val=2)
    # csm1 has the same sql, properties, references, and materialization as vm2, but not the same name
    # so generated sql will be different if it is part of a CTE, and thus the objects are not equal.
    assert vm1 != csm1
    assert vm2 != csm1

    # csm2 has the same attributes as vm2: sql, properties, references, materialization, generic name, and
    # the properties are formatted by the same function into sql. The fact that it is actually a different
    # sub-class of SqlModel doesn't matter for the sql generation nor for the equality check, cs2m == vm2
    csm2 = CustomSqlModelBuilder(
        sql="select '{key}' as key, {val} as value",
        name='ValueModel'
    )(key='X', val=2)
    assert vm1 != csm2
    assert vm2 == csm2


def test_equality_different_property_formatters():
    csm_builder = CustomSqlModelBuilder(sql='select {val} as value')
    csm_alt_builder = CustomSqlModelBuilder(sql='select {val} as value')
    csm_alt_builder.properties_to_sql = \
        lambda properties: {key: f'{val + 1}' for key, val in properties.items()}
    csm1 = csm_builder(val=2)
    csm2 = csm_builder(val=2)
    csm3 = csm_alt_builder(val=1)
    csm4 = csm_alt_builder(val=1)
    # csm1, csm2, csm3, csm4 all result in the same sql being generated and have the same
    # formatted properties. Their hashes are thus the same
    assert csm1.hash == csm2.hash
    assert csm1.hash == csm3.hash
    assert csm1.hash == csm4.hash
    # However, the objects are not all the same, as copies with changed properties might be different
    assert csm1 == csm2
    assert csm1 != csm3
    assert csm1 != csm4
    assert csm3 == csm4
    # The hash on copies expose why some objects are equal and others are not
    assert csm1.set(tuple(), val=3).hash == csm2.set(tuple(), val=3).hash
    assert csm1.set(tuple(), val=3).hash != csm3.set(tuple(), val=3).hash


def test_set():
    # Build a simple graph
    vm1 = ValueModel.build(key='X', val=1)
    vm2 = ValueModel.build(key='X', val=2)
    rm = RefModel.build(ref=vm1)
    graph = JoinModel.build(ref_left=rm, ref_right=vm2)

    # Get some base information about the constructed graph
    selected_model = get_node(graph, ('ref_right',))
    assert selected_model.properties == {'key': 'X', 'val': 2}
    sql = to_sql(graph)
    hash_original = graph.hash
    node_info = get_graph_nodes_info(graph)

    # Use set() to update node vm2 in the graph
    updated_graph = graph.set(('ref_right',), key='Y')

    # Assert that the original graph is unchanged
    assert selected_model.properties == {'key': 'X', 'val': 2}
    assert to_sql(graph) == sql
    assert graph.hash == hash_original
    reselected_original_selected_model = get_node(graph, ('ref_right',))
    assert reselected_original_selected_model.properties == {'key': 'X', 'val': 2}

    # Assert that the new graph has the requested change, and is otherwise the same
    # test: updated graph should have the same number of nodes
    assert len(get_graph_nodes_info(updated_graph)) == len(node_info)

    # test: the specific model should have the property set to 'Y' now
    updated_selected_model = get_node(updated_graph, ('ref_right',))
    assert updated_selected_model.properties == {'key': 'Y', 'val': 2}
    assert updated_graph.hash != hash_original
    # The generated sql should be different, but very similar.
    # 1. The length should be the same
    # 2. The md5 hashes used in the CTE-names should be different
    # 3. In one position 'X' should have changed in 'Y'
    updated_sql = to_sql(updated_graph)
    assert updated_sql != sql
    assert len(updated_sql) == len(sql)
    # Get a list with all characters that have changed in the updated_sql. But ignore all changes in the
    # range [0-9a-f] as we expect the md5 hashes to change.
    sql_diff = list((a, b) for a, b in zip(sql, updated_sql) if a != b)
    sql_diff_ignore_hash_changes = [(a, b) for a, b in sql_diff if not re.match('^[0-9a-f]$', a)]
    assert sql_diff_ignore_hash_changes == [('X', 'Y')]


def test_set_complex_graph():
    # Build a complex graph, and use set() to update a node
    #
    # Graph:
    # vm1 <--+-- rm <--------------+
    #        |                     |
    #        +-- jm1 <--+          +-- jm3 <-- graph
    #        |          |          |
    # vm2 <--+          +-- jm2 <--+
    #                   |
    # vm3 <-------------+
    #
    vm1 = ValueModel.build(key='a', val=1)
    vm2 = ValueModel.build(key='a', val=2)
    vm3 = ValueModel.build(key='a', val=3)
    rm = RefModel.build(ref=vm1)

    jm1 = JoinModel.build(ref_left=vm2, ref_right=vm1)
    jm2 = JoinModel.build(ref_left=vm3, ref_right=jm1)
    jm3 = JoinModel.build(ref_left=jm2, ref_right=rm)
    graph = RefModel.build(ref=jm3)

    paths = {
        'vm1': ('ref', 'ref_right', 'ref'),
        'vm1_alt': ('ref', 'ref_left', 'ref_right', 'ref_right'),
        'vm2': ('ref', 'ref_left', 'ref_right', 'ref_left'),
        'vm3': ('ref', 'ref_left', 'ref_left'),
        'rm': ('ref', 'ref_right'),
        'jm1': ('ref', 'ref_left', 'ref_right'),
        'jm2': ('ref', 'ref_left'),
        'jm3': ('ref',),
        'graph': tuple(),

    }

    # 'Simple' case: update vm3
    new_graph1 = graph.set(paths['vm3'], key='b')
    # Check that vm3 is updated as we except
    assert get_node(new_graph1, paths['vm3']).properties == {'key': 'b', 'val': 3}
    # Updating vm3 should give a new graph with the following nodes updated: vm3, jm2, jm3 and graph
    # amd the other nodes unchanged: vm2, vm1, rm, jm1
    same_paths = [paths[node_name] for node_name in ['vm1', 'vm1_alt', 'vm2', 'rm', 'jm1']]
    changed_paths = [paths[node_name] for node_name in ['vm3', 'jm2', 'jm3', 'graph']]
    _assert_graph_difference(graph, new_graph1, same_paths, changed_paths)

    # 'Complex' case: update vm1
    # There are two paths to vm1, changing vm1 through both paths should give different graph objects, but
    # with the same values
    new_graph2 = graph.set(paths['vm1'], key='c', val=100)
    new_graph3 = graph.set(paths['vm1_alt'], key='c', val=100)
    assert get_node(new_graph3, paths['vm1']).properties == {'key': 'c', 'val': 100}
    assert get_node(new_graph3, paths['vm1_alt']).properties == {'key': 'c', 'val': 100}

    # The two changed graphs should have the same semantic meaning:
    assert new_graph2.hash == new_graph3.hash
    assert graph.hash != new_graph2.hash
    assert graph.hash != new_graph3.hash

    # Check that vm1 is updated as we except
    assert get_node(new_graph2, paths['vm1']).properties == {'key': 'c', 'val': 100}
    assert get_node(new_graph3, paths['vm1']).properties == {'key': 'c', 'val': 100}
    assert get_node(new_graph2, paths['vm1_alt']).properties == {'key': 'c', 'val': 100}
    assert get_node(new_graph3, paths['vm1_alt']).properties == {'key': 'c', 'val': 100}

    # The following nodes should be updated: vm1, rm, jm3, graph, jm1, jm2
    # Nodes that should be unchanged: vm2, vm3
    changed_paths = [paths[node_name] for node_name in
                     ['vm1', 'vm1_alt', 'rm', 'jm3', 'graph', 'jm1', 'jm2']]
    same_paths = [paths[node_name] for node_name in ['vm2', 'vm3']]
    _assert_graph_difference(graph, new_graph2, same_paths, changed_paths)
    _assert_graph_difference(graph, new_graph3, same_paths, changed_paths)


def test_set_error():
    vm1 = ValueModel.build(key='a', val=1)
    with pytest.raises(ValueError, match='non-existing property'):
        vm1.set(tuple(), xyz=123)


def test_link():
    # Graph:
    # vm1 <--+-- rm <-----\
    #         \            +-- graph
    #          +-- jm1 <--/
    #         /
    # vm2 <--+
    #
    vm1 = ValueModel.build(key='a', val=1)
    vm2 = ValueModel.build(key='a', val=2)
    rm = RefModel.build(ref=vm1)
    jm1 = JoinModel.build(ref_left=vm2, ref_right=vm1)
    graph = JoinModel.build(ref_left=jm1, ref_right=rm)

    # baseline asserts:
    assert len(get_graph_nodes_info(graph)) == 5
    assert get_node(graph, ('ref_right', 'ref')) is vm1
    assert get_node(graph, ('ref_left', 'ref_right')) is vm1

    # Change 1: link rm to new node instead of vm1
    new_node = ValueModel.build(key='a', val=3)
    new_graph1 = graph.link(('ref_right',), ref=new_node)
    assert new_graph1.hash != graph.hash
    # ref path through rm should give new node
    assert get_node(new_graph1, ('ref_right', 'ref')) is new_node
    #  vm1 will still be referenced by jm1
    assert get_node(new_graph1, ('ref_left', 'ref_right')) is vm1

    # Change 2: link graph.ref_left to vm1
    new_graph2 = graph.link(tuple(), ref_left=vm1)
    assert new_graph2.hash != graph.hash
    assert get_node(new_graph2, ('ref_left', )) is vm1
    assert get_node(new_graph2, ('ref_right',)) is rm
    assert get_node(new_graph2, ('ref_right', 'ref')) is vm1

    # Change3: link graph.ref_left and graph.ref_right to graph
    new_graph3 = graph.link(tuple(), ref_left=graph, ref_right=graph)
    assert len(get_graph_nodes_info(new_graph3)) == 6
    assert get_node(new_graph3, ('ref_left', )) is graph
    assert get_node(new_graph3, ('ref_right',)) is graph


def test_set_materialization():
    pass
    # TODO


def _assert_graph_difference(graph: SqlModel,
                             new_graph: SqlModel,
                             same_paths: List[RefPath],
                             changed_paths: List[RefPath]):
    for path in same_paths:
        assert get_node(new_graph, path) is get_node(graph, path)
    for path in changed_paths:
        assert get_node(new_graph, path) is not get_node(graph, path)
        assert get_node(new_graph, path).hash != get_node(graph, path).hash
