"""
Copyright 2021 Objectiv B.V.
"""
from sql_models.graph_operations import get_graph_nodes_info, NodeInfo
from sql_models.model import SqlModel


def print_graph_info(model: SqlModel):
    for node_info in get_graph_nodes_info(model):
        print_node_info(node_info)


def print_node_info(node_info: NodeInfo):
    print('\n----------')
    print(f'name: {node_info.node_id}')
    print(f'hash: {node_info.model.hash}')
    print(f'reference_path: {node_info.reference_path}')
    print(f'properties: {node_info.model.properties}')
    print(f'materialization: {node_info.model.materialization}')
    print(f'materialization_name: {node_info.model.materialization_name}')
    print(f'inputs: {[in_node.node_id for in_node in node_info.in_edges]}')
    print(f'outputs: {[out_node.node_id for out_node in node_info.out_edges]}')
