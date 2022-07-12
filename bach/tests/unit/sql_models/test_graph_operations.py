"""
Copyright 2021 Objectiv B.V.
"""
from typing import List

import pytest

from sql_models.graph_operations import get_graph_nodes_info, get_node, get_node_info_selected_node, \
    find_nodes, find_node, FoundNode, get_all_placeholders, update_placeholders_in_graph
from sql_models.model import RefPath, SqlModel
from tests.unit.sql_models.util import ValueModel, RefModel, JoinModel, RefValueModel

pytestmark = [pytest.mark.db_independent]  # mark all tests here as database independent.


def get_simple_test_graph():
    """ Give a simple graph that consists of 4 model instances of 3 model types. """
    # Below we return the following graph, but written differently so it can be easier copy-pasted for
    # tests where want to access the component models
    # JoinModel.build(
    #     ref_left=RefModel(
    #         ref=ValueModel(key='a', val=1)
    #     ),
    #     ref_right=ValueModel(key='a', val=2)
    # )
    vm1 = ValueModel.build(key='a', val=1)
    vm2 = ValueModel.build(key='a', val=2)
    rm = RefModel.build(ref=vm1)
    model = JoinModel.build(ref_left=rm, ref_right=vm2)
    return model


def test_get_graph_nodes_info():
    graph = get_simple_test_graph()
    info = get_graph_nodes_info(graph)
    assert len(info) == 4

    # The last node_info should be about the queried node (i.e. the model that is `graph`)
    last_node_info = info[-1]
    assert last_node_info.reference_path == tuple()

    # Test that the graph structure is correctly represented
    assert len(last_node_info.in_edges) == 2
    # the two in-edges are referenced as ref_left and ref_right
    assert set(n.reference_path for n in last_node_info.in_edges) == {('ref_left',), ('ref_right',)}
    # the two in-edges both have the last node as out-edge
    assert [n.out_edges for n in last_node_info.in_edges] == [[last_node_info], [last_node_info]]

    # Get a specific node, and check the information about that node
    val_nodes = [node_info for node_info in info if node_info.reference_path == ('ref_left', 'ref')]
    assert len(val_nodes) == 1
    val_node = val_nodes[0]
    assert val_node.model.placeholders == {'key': 'a', 'val': 1}
    assert val_node.model.generic_name == 'ValueModel'
    assert val_node.in_edges == []
    assert len(val_node.out_edges) == 1
    assert val_node.out_edges[0].reference_path == ('ref_left', )
    assert val_node.out_edges[0].out_edges[0].reference_path == tuple()
    assert val_node.out_edges[0].out_edges[0].model is graph


def test_get_node():
    # Construct a simple test graph
    vm1 = ValueModel.build(key='a', val=1)
    vm2 = ValueModel.build(key='a', val=2)
    rm = RefModel.build(ref=vm1)
    graph = JoinModel.build(ref_left=rm, ref_right=vm2)

    assert get_node(graph, tuple()) == graph
    assert get_node(graph, ('ref_left', )) is rm
    assert get_node(graph, ('ref_right', )) is vm2
    assert get_node(graph, ('ref_left', 'ref')) is vm1

    with pytest.raises(ValueError, match='wrong_ref does not exist'):
        get_node(graph, ('wrong_ref', ))

    with pytest.raises(ValueError, match='wrong does not exist'):
        get_node(graph, ('ref_left', 'wrong', ))


def test_get_node_graph_with_duplicates():
    # Create a graph with two reference paths to the vm1 node
    vm1 = ValueModel.build(key='a', val=1)
    vm2 = ValueModel.build(key='a', val=2)
    rm = RefModel.build(ref=vm1)
    jm = JoinModel.build(ref_left=rm, ref_right=vm2)
    graph = JoinModel.build(ref_left=jm, ref_right=vm1)

    # vm1 appears in the graph twice, and has thus two reference paths. Check that both work
    assert vm1 is not vm2
    assert get_node(graph, ('ref_left', 'ref_left', 'ref')) is vm1
    assert get_node(graph, ('ref_right',)) is vm1
    assert get_node(graph, ('ref_left', 'ref_right')) is vm2
    # others
    assert get_node(graph, tuple()) == graph
    assert get_node(graph, ('ref_left', )) is jm


def test_get_node_info_selected_node_simple():
    # Construct a simple test graph
    vm1 = ValueModel.build(key='a', val=1)
    vm2 = ValueModel.build(key='a', val=2)
    rm = RefModel.build(ref=vm1)
    graph = JoinModel.build(ref_left=rm, ref_right=vm2)

    assert get_node_info_selected_node(graph, tuple()).model == graph
    assert get_node_info_selected_node(graph, ('ref_left', )).model is rm
    assert get_node_info_selected_node(graph, ('ref_right', )).model is vm2
    assert get_node_info_selected_node(graph, ('ref_left', 'ref')).model is vm1

    node_info_vm1 = get_node_info_selected_node(graph, ('ref_left', 'ref'))
    assert node_info_vm1.reference_path == ('ref_left', 'ref')
    assert len(node_info_vm1.out_edges) == 1
    assert node_info_vm1.out_edges[0].model is rm
    assert node_info_vm1.in_edges == []


def test_get_node_info_selected_node_duplicate_paths():
    # Create a graph with two reference paths to the vm1 node
    vm1 = ValueModel.build(key='a', val=1)
    vm2 = ValueModel.build(key='a', val=2)
    rm = RefModel.build(ref=vm1)
    jm = JoinModel.build(ref_left=rm, ref_right=vm2)
    graph = JoinModel.build(ref_left=jm, ref_right=vm1)

    # vm1 appears in the graph twice, and has thus two reference paths. Check that both work
    node_info1 = get_node_info_selected_node(graph, ('ref_left', 'ref_left', 'ref'))
    node_info2 = get_node_info_selected_node(graph, ('ref_right',))
    # Both node_info1 and node_info2 are equal (but different objects), but they contain the same immutable
    # .model class that they describe
    assert node_info1.model is node_info2.model
    assert node_info1.model is vm1
    assert node_info2.model is vm1
    assert len(node_info1.out_edges) == 2
    assert len(node_info2.out_edges) == 2
    assert len(node_info1.in_edges) == 0
    assert len(node_info1.in_edges) == 0


def test_find_nodes():
    vm1 = ValueModel.build(key='a', val=1)
    vm2 = ValueModel.build(key='a', val=2)
    rm = RefModel.build(ref=vm1)
    jm = JoinModel.build(ref_left=rm, ref_right=vm2)
    graph = JoinModel.build(ref_left=jm, ref_right=vm1)

    # find none
    assert find_node(graph, lambda node: False) is None
    assert find_nodes(graph, lambda node: False) == []

    # find all
    assert find_node(graph, lambda node: True) == FoundNode(model=graph, reference_path=tuple())
    expected_result = [
        FoundNode(model=graph, reference_path=tuple()),
        FoundNode(model=jm, reference_path=('ref_left',)),
        FoundNode(model=vm1, reference_path=('ref_right',)),
        FoundNode(model=rm, reference_path=('ref_left', 'ref_left')),
        FoundNode(model=vm2, reference_path=('ref_left', 'ref_right'))
    ]
    assert find_nodes(graph, lambda node: True) == expected_result

    # find one
    assert find_node(graph, lambda node: node.generic_name == 'RefModel') == \
           FoundNode(model=rm, reference_path=('ref_left', 'ref_left'))
    assert find_nodes(graph, lambda node: node.generic_name == 'RefModel') == [
        FoundNode(model=rm, reference_path=('ref_left', 'ref_left'))
    ]

    # find some
    assert find_node(graph, lambda node: node.generic_name == 'ValueModel') == \
           FoundNode(model=vm1, reference_path=('ref_right',))
    assert find_nodes(graph, lambda node: node.generic_name == 'ValueModel') == [
        FoundNode(model=vm1, reference_path=('ref_right',)),
        FoundNode(model=vm2, reference_path=('ref_left', 'ref_right'))
    ]


def test_find_nodes_duplicates():
    vm1 = ValueModel.build(key='a', val=1)
    vm2 = ValueModel.build(key='a', val=1)
    graph = JoinModel.build(ref_left=vm1, ref_right=vm2)
    result = find_nodes(graph, lambda node: node.generic_name == 'ValueModel')
    assert len(result) == 2
    assert result == [
        FoundNode(model=vm1, reference_path=('ref_left',)),
        FoundNode(model=vm2, reference_path=('ref_right',))
    ]


def test_find_nodes_path_length():
    # Test for nodes that can be found through multiple paths.
    # The order of the returned nodes from find_nodes() depends on the length of the reference path. For
    # nodes with multiple paths either the longest or the shortest path is taken into account based on
    # the value of use_last_found_instance

    # Graph:

    #
    #                /--- rm1 <-+---------------------------\
    #               /            \                           +-- graph
    #   vm1 <------+              +-- jm2 <----\            /
    #               \            /              +-- jm4 <--/
    #                +-- jm1 <--+              /
    #               /            \            /
    #              /              +-- jm3 <--/
    #   vm2 <-----+              /
    #              \------------/

    vm1 = ValueModel.build(key='a', val=1)
    vm2 = ValueModel.build(key='a', val=2)
    rm1 = RefModel.build(ref=vm1)
    jm1 = JoinModel.build(ref_left=vm2, ref_right=vm1)
    jm2 = JoinModel.build(ref_left=jm1, ref_right=rm1)
    jm3 = JoinModel.build(ref_left=vm2, ref_right=jm1)
    jm4 = JoinModel.build(ref_left=jm3, ref_right=jm2)
    graph = JoinModel.build(ref_left=jm4, ref_right=rm1)

    # find vm1 from graph, both with longest and shortest path
    result = find_nodes(graph, function=lambda n: n is vm1, first_instance=True)
    assert result == [FoundNode(model=vm1, reference_path=('ref_right', 'ref'))]
    result = find_nodes(graph, function=lambda n: n is vm1, first_instance=False)
    assert result == [FoundNode(model=vm1, reference_path=('ref_left', 'ref_left', 'ref_right', 'ref_right'))]

    # find vm1 from jm4, both with longest and shortest path
    result = find_nodes(jm4, function=lambda n: n is vm1, first_instance=True)
    assert result == [FoundNode(model=vm1, reference_path=('ref_left', 'ref_right', 'ref_right'))]
    result = find_nodes(jm4, function=lambda n: n is vm1, first_instance=False)
    assert result == [FoundNode(model=vm1, reference_path=('ref_left', 'ref_right', 'ref_right'))]

    # find vm2 from graph, both with longest and shortest path
    result = find_nodes(graph, function=lambda n: n is vm2)
    assert result == [FoundNode(model=vm2, reference_path=('ref_left', 'ref_left', 'ref_left'))]
    result = find_nodes(graph, function=lambda n: n is vm2, first_instance=False)
    assert result == [FoundNode(model=vm2, reference_path=('ref_left', 'ref_left', 'ref_right', 'ref_left'))]


# be explicit as this is also a performance test: max 1 sec runtime.
# But conftests.py should already define limit for all unittests.
@pytest.mark.timeout(1)
def test_find_nodes_long_and_short_path_performance():
    # We'll build a graph with a simple structure but with a lot of paths. The number of joins is controlled
    # through the `depth` constant. Schematically the graph looks like this (all joins between 2 and N-1 are
    # omitted):
    #
    #               /------------------------------------------------------------------------------\
    #              /                                                                                +-- graph
    #   vm <------+                                                                                /
    #              \              /----\             /- ... -\                /----\              /
    #               +-- join1 <--+     +-- join2 <--+         +-- joinN-1 <--+      +-- joinN <--/
    #                             \----/             \- ... -/                \----/
    #
    # There are a lot of possible reference paths from the `graph` node to `vm` node: 2^depth + 1
    # For depth values above ~ 18 this used to get noticeably slow (> 1 second to run), for values larger
    # than 23 it was unbearable slow (> 1 minute to run) .
    #
    # If this test takes longer than a second to run, then that's a regression!
    #
    depth = 50
    vm = ValueModel.build(key='a', val=1)
    graph = vm
    for _ in range(depth):
        graph = JoinModel.build(ref_left=graph, ref_right=graph)
    graph = JoinModel.build(ref_left=graph, ref_right=vm)

    # shortest path: one step
    expected_path = ('ref_right',)
    result = find_nodes(graph, function=lambda n: n is vm, first_instance=True)
    assert result == [FoundNode(model=vm, reference_path=expected_path)]

    # longest path: depth + 1 steps
    expected_path = ('ref_left', ) * (depth + 1)
    result = find_nodes(graph, function=lambda n: n is vm, first_instance=False)
    assert result == [FoundNode(model=vm, reference_path=expected_path)]


def test_get_all_placeholders():
    graph = JoinModel.build(
        ref_left=RefValueModel(
            val=3,
            ref=ValueModel(key='a', val=1)
        ),
        ref_right=ValueModel(key='a', val=2)
    )
    result = get_all_placeholders(graph)
    assert result == {
        'key': {
            ('ref_right',): 'a',
            ('ref_left', 'ref'): 'a'
        }
        ,
        'val': {
            ('ref_left', ): 3,
            ('ref_right',): 2,
            ('ref_left', 'ref'): 1
        }
    }


def test_update_placeholders_in_graph():
    graph = JoinModel.build(
        ref_left=RefValueModel(
            val=3,
            ref=ValueModel(key='a', val=1)
        ),
        ref_right=ValueModel(key='a', val=2)
    )

    # Updating non existing placeholders doesn't do anything
    assert graph is update_placeholders_in_graph(graph, {'x': 'X'})

    # Assert current state
    assert get_node(graph, ('ref_left',)).placeholders == {'val': 3}
    assert get_node(graph, ('ref_right',)).placeholders == {'val': 2, 'key': 'a'}
    assert get_node(graph, ('ref_left', 'ref')).placeholders == {'val': 1, 'key': 'a'}

    # Update one property
    graph = update_placeholders_in_graph(graph, {'val': 5})
    assert get_node(graph, ('ref_left',)).placeholders == {'val': 5}
    assert get_node(graph, ('ref_right',)).placeholders == {'val': 5, 'key': 'a'}
    assert get_node(graph, ('ref_left', 'ref')).placeholders == {'val': 5, 'key': 'a'}

    # Update two placeholders
    graph = update_placeholders_in_graph(graph, {'val': 1234, 'key': 'b'})
    assert get_node(graph, ('ref_left',)).placeholders == {'val': 1234}
    assert get_node(graph, ('ref_right',)).placeholders == {'val': 1234, 'key': 'b'}
    assert get_node(graph, ('ref_left', 'ref')).placeholders == {'val': 1234, 'key': 'b'}

    # Update property to value it already has, nothing changes
    graph = update_placeholders_in_graph(graph, {'val': 1234})
    assert get_node(graph, ('ref_left',)).placeholders == {'val': 1234}
    assert get_node(graph, ('ref_right',)).placeholders == {'val': 1234, 'key': 'b'}
    assert get_node(graph, ('ref_left', 'ref')).placeholders == {'val': 1234, 'key': 'b'}


def _assert_graph_difference(graph: SqlModel,
                             new_graph: SqlModel,
                             same_paths: List[RefPath],
                             changed_paths: List[RefPath]):
    for path in same_paths:
        assert get_node(new_graph, path) is get_node(graph, path)
    for path in changed_paths:
        assert get_node(new_graph, path) is not get_node(graph, path)
        assert get_node(new_graph, path).hash != get_node(graph, path).hash
