"""
Copyright 2021 Objectiv B.V.
"""
from collections import deque
from typing import NamedTuple, List, Dict, Set, Tuple, Optional, Callable, Deque

from sql_models.model import SqlModel, RefPath


class NodeInfo(NamedTuple):
    """
    Object that wraps an SqlModel and adds extra information that is not relevant for
    sql generation, but that can be relevant for visualizing and manipulating the graph.
    """
    node_id: str
    reference_path: RefPath
    model: SqlModel
    # Recursive types are not (yet) supported by MyPy, so we define in_edges and out_edges simply as
    # `list`, instead of their full types: List['NodeInfo']
    in_edges: list
    out_edges: list


class FoundNode(NamedTuple):
    model: SqlModel
    reference_path: RefPath


def get_graph_nodes_info(start_node: SqlModel) -> List[NodeInfo]:
    """
    Build a list of NodeInfo objects from the final node of the graph backwards.

    The NodeInfo objects contain a bit more information than the normal graph nodes. However this
    information is not kept in-sync with the actual graph (e.g. out-edges), or is dependent on the starting
    point in the graph (e.g. reference_path). Make sure to not use the return values of this function after
    the graph has been changed, or the context changed.

    :param start_node: final node of the graph. Start point for building the graph
    :return: List of NodeInfo objects.
    """
    nodes: Dict[int, NodeInfo] = {}
    # stack contains the models to process. Each entry contains two models:
    # 1) reference_path to the current model
    # 2) the model that referenced the current model
    # 3) the current model
    stack: List[Tuple[RefPath, Optional[SqlModel], SqlModel]] = \
        [(tuple(), None, start_node)]
    while stack:
        reference_path, referencing_model, current_model = stack.pop()
        current_id = id(current_model)
        if current_id not in nodes:
            # This model has not been processed yet
            # 1) create node
            # 2) schedule all referenced models to be processed too
            nodes[current_id] = NodeInfo(
                node_id=current_model.generic_name,  # use something more stable, but unique
                reference_path=reference_path,
                model=current_model,
                in_edges=[],
                out_edges=[]
            )
            for reference_name, reference in current_model.references.items():
                _next_reference_path = (*reference_path, reference_name)
                _next = (_next_reference_path, current_model, reference)
                stack.append(_next)
        current_node = nodes[current_id]
        if referencing_model is not None:
            referencing_id = id(referencing_model)
            referencing_node = nodes[referencing_id]
            _add_node_to_node_list(current_node.out_edges, referencing_node)
            _add_node_to_node_list(referencing_node.in_edges, current_node)
    return [node for node in nodes.values()][::-1]  # reverse list


def get_node_info_selected_node(start_node: SqlModel, reference_path: RefPath) -> NodeInfo:
    """
    Similar to get_graph_nodes_info, but only gets the NodeInfo for the node at the specified
    reference_path. This does build the complete graph, which is recursively available through the
    in_edges and out_edges of the returned NodeInfo
    :param start_node: start node
    :param reference_path: identifier of selected model
    :return: NodeInfo for the selected node
    :raise ValueError: if the selected node doesn't exist
    """
    node = get_node(start_node, reference_path)
    nodes_info = get_graph_nodes_info(start_node)
    selected_nodes = [ni for ni in nodes_info if ni.model is node]
    if len(selected_nodes) != 1:
        raise ValueError(f'Cannot find graph node identified by {reference_path} starting at {start_node}')
    selected_node = selected_nodes[0]
    return selected_node


def get_node(start_node: SqlModel, reference_path: RefPath) -> SqlModel:
    """
    Get a single node from the graph, by recursively traversing the references starting at start_node.
    :param start_node: start node
    :param reference_path: references to traverse to get to the node
    :return: found node
    """
    if not reference_path:
        return start_node
    first, rest = reference_path[0], reference_path[1:]
    if first not in start_node.references:
        raise ValueError(f'Reference {first} does not exist in model {start_node}')
    return get_node(start_node.references[first], rest)


def find_nodes(
        start_node: SqlModel,
        function: Callable[[SqlModel], bool],
        first_instance: bool = True
) -> List[FoundNode]:
    """
    Return all nodes for which function returns True, which can be found by recursively traversing the
    references starting at start_node.

    This function uses a breadth first approach, and the returned FoundNodes are in the order they were
    found. If a node is encountered multiple times, then only the first or last occurrence will be in the
    result depending on the value of use_last_found_instance.

    :param start_node: start node
    :param function: Function that should return either True or False for a given SqlModel
    :param first_instance: If set to true, if a node is encountered multiple times in the breadth first
        search then the first occurrence will be included in the result. If set to False then the last
        occurrence will be in the result.
    :return: A list of tuples. Each tuple contains the found SqlModel and a reference path to that model.
        The returned nodes are in the order in which they were encountered. As a result the reference_path
        of the returned tuples monotonically increases when iterating the list.
    """
    result_nodes: Dict[SqlModel, FoundNode] = {}
    queue: Deque[Tuple[SqlModel, RefPath]] = deque()
    queue.append((start_node, tuple()))
    while queue:
        node, path = queue.popleft()
        if function(node):
            if node not in result_nodes:
                result_nodes[node] = FoundNode(node, path)
            elif node in result_nodes and not first_instance:
                # we rely on the fact that python 3.7+ will keep the insertion order. So we'll have to
                # remove and reinsert the item to get it in the right position in the returned result.
                del result_nodes[node]
                result_nodes[node] = FoundNode(node, path)
        for next_path, next_node in node.references.items():
            next_tuple = (next_node, path + (next_path,))
            queue.append(next_tuple)
    return list(result_nodes.values())


def find_node(
        start_node: SqlModel,
        function: Callable[[SqlModel], bool],
        first_instance: bool = True
) -> Optional[FoundNode]:
    """
    Similar to find_nodes, but will only return the first node in the result, or None if none are found.
    """
    result = find_nodes(start_node, function, first_instance)
    if not result:
        return None
    return result[0]


def replace_node_in_graph(start_node: SqlModel,
                          reference_path: RefPath,
                          replacement_model: SqlModel) -> SqlModel:
    """
    Create a (partial) copy of the graph that can be reached from start_node, with the referenced node
    replaced by replacement_model. All nodes along all reference paths to the referenced node will be
    replaced with copies of the original nodes that (indirectly) link to replacement_model.

    The original start node, and all nodes that it refers recursively are unchanged.
    :param start_node: start node
    :param reference_path: references to traverse to get to the node that has to be updated
    :param replacement_model: model instance that will replace the reference node
    :return: an updated copy of the start node
    """
    selected_node = get_node_info_selected_node(start_node, reference_path)
    dependent_model_ids = _get_all_dependent_node_model_ids(selected_node)
    # the dependent_model_ids are guaranteed to uniquely identify python objects as long as those objects
    # exist. We still have a reference to the start node here, so all objects that are being replaced are
    # guaranteed to still exist at the end of this function, ergo we can safely use dependent_model_ids to
    # identify python objects.
    return _replace_model_in_graph_recursively(
        current_node=start_node,
        model_to_replace=selected_node.model,
        replacement_node=replacement_model,
        dependent_model_ids=dependent_model_ids,
        replaced_models={}
    )


def _replace_model_in_graph_recursively(
        current_node: SqlModel,
        model_to_replace: SqlModel,
        replacement_node: SqlModel,
        dependent_model_ids: Set[int],
        replaced_models: Dict[int, SqlModel]
) -> SqlModel:
    """
    Return the a copy of current_node, with the recursively referenced nodes of the original replaced by
        copies too. The replacement_node is not replaced by a copy but by replacement_node.
    Only nodes in dependent_model_ids are copied/updated, for others the original nodes are linked.

    Effectively this can be used to replace a single node, and create a new graph that references that
    updated node.

    :param current_node: current node, copy of this node will be returned.
    :param model_to_replace: model that should be replaced.
    :param replacement_node: Replacement for the node that is identified by replacement_ref_path.
    :param dependent_model_ids: Set of id() of the python objects that should be updated.
    :param replaced_models: dictionary mapping the python instance id() of old nodes to the new version of
        already updated nodes. This is used to make sure we only create one replacement node for each node,
        even if that node is referenced multiple times. This dictionary will be updated by this function.
    :return: copy of current-node, with referred nodes copied and updated too.
    """
    if current_node is model_to_replace:
        return replacement_node
    new_references = {}
    for ref_name, ref_node in current_node.references.items():
        node_id = id(ref_node)
        if node_id in dependent_model_ids:
            if node_id in replaced_models:
                new_references[ref_name] = replaced_models[node_id]
            else:
                new_references[ref_name] = _replace_model_in_graph_recursively(
                    current_node=ref_node,
                    model_to_replace=model_to_replace,
                    replacement_node=replacement_node,
                    dependent_model_ids=dependent_model_ids,
                    replaced_models=replaced_models
                )
                replaced_models[node_id] = new_references[ref_name]
    return current_node.copy_link(new_references=new_references)


def _get_all_dependent_node_model_ids(node: NodeInfo) -> Set[int]:
    """
    Get all nodes that recursively refer the given node, and the given node itself.
    The returned nodes are identified by the id() of the their model.

    Python's id() uniquely identifies an object during it's lifetime [1]. So the results of this function
    can be used to identify dependent models in a graph, but only as long as all model instances in the
    graph still exist.

    [1] https://docs.python.org/3/library/functions.html#id
    """
    dependent_ids: Set[int] = {id(node.model)}
    out_edges: List[NodeInfo] = node.out_edges
    while out_edges:
        out_edge = out_edges.pop()
        model_id = id(out_edge.model)
        if model_id not in dependent_ids:
            dependent_ids.add(model_id)
            out_edges.extend(out_edge.out_edges)
    return dependent_ids


def _add_node_to_node_list(node_list: List[NodeInfo], node: NodeInfo):
    """ Add node to node_list, if there is no node yet with the same node-id. """
    if all(id(node) != id(list_entry) for list_entry in node_list):
        node_list.append(node)
