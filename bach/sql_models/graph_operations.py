"""
Copyright 2021 Objectiv B.V.
"""
from collections import deque
from typing import NamedTuple, List, Dict, Set, Tuple, Optional, Callable, Deque, Hashable, Mapping,\
    TypeVar,  Union

from sql_models.model import SqlModel, RefPath


TSqlModel = TypeVar('TSqlModel', bound='SqlModel')
T2SqlModel = TypeVar('T2SqlModel', bound='SqlModel')


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
    result depending on the value of use_last_found_instance. Note: this does not mean that the result cannot
    contain nodes that are equal to each other, but it does mean that the result will never contain the same
    object twice.

    :param start_node: start node
    :param function: Function that should return either True or False for a given SqlModel
    :param first_instance: If set to true, if a node is encountered multiple times in the breadth first
        search then the first occurrence will be included in the result. If set to False then the last
        occurrence will be in the result.
    :return: A list of tuples. Each tuple contains the found SqlModel and a reference path to that model.
        The returned nodes are in the order in which they were encountered. As a result the reference_path
        of the returned tuples monotonically increases when iterating the list.
    """
    # result_nodes maps the id of the found objects to a FoundNode object
    result_nodes: Dict[int, FoundNode] = {}
    # discovered maps the id of all models that are processed or are queued to be processed to the length of
    # the reference path to get to them. Depending on the value of first_instance, this is the length of the
    # longest or shortest reference path.
    discovered: Dict[int, int] = {}
    # queue contains the queue of items that have been discovered but not yet processed.
    queue: Deque[Tuple[SqlModel, RefPath]] = deque()

    discovered[id(start_node)] = 0
    queue.append((start_node, tuple()))
    while queue:
        node, path = queue.popleft()
        current_id = id(node)
        if function(node):
            if current_id not in result_nodes:
                result_nodes[current_id] = FoundNode(node, path)
            elif current_id in result_nodes and not first_instance:
                # We found a longer path to a node we already found earlier.
                # we rely on the fact that python 3.7+ will keep the insertion order. So we'll have to
                # remove and reinsert the item to get it in the right position in the returned result.
                del result_nodes[current_id]
                result_nodes[current_id] = FoundNode(node, path)
        for next_path_step, next_node in node.references.items():
            next_id = id(next_node)
            next_path = path + (next_path_step,)
            len_next_path = len(next_path)
            if next_id in discovered:
                # If there is already a path to next_node that's equally long or short (depending on
                # first_instance), then we don't add next_node to the queue.
                if first_instance and discovered[next_id] <= len_next_path:
                    continue
                if (not first_instance) and discovered[next_id] >= len_next_path:
                    continue
            discovered[next_id] = len_next_path
            next_tuple = (next_node, next_path)
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


def get_all_placeholders(start_node: SqlModel) -> Dict[str, Dict[RefPath, Hashable]]:
    """
    Get all placeholders in the graph.

    :return: Dict, keys: placeholder name, values: dictionary. The values sub-dictionary has as key the path
        to all nodes that use the placeholder, and as values the value in that node.
    """
    return _get_all_placeholders_recursive(start_node, tuple())


def _get_all_placeholders_recursive(start_node: SqlModel, path_so_far: RefPath):
    result = {name: {path_so_far: value} for name, value in start_node.placeholders.items()}
    for reference_name, reference in start_node.references.items():
        _next_reference_path = (*path_so_far, reference_name)
        result_ref = _get_all_placeholders_recursive(reference, _next_reference_path)
        for name, path_values in result_ref.items():
            result.setdefault(name, {}).update(path_values)
    return result


def update_placeholders_in_graph(
        start_node: TSqlModel,
        placeholder_values: Mapping[str, Hashable]
) -> TSqlModel:
    """
    Return a copy of the start_node with the given placeholder values updated throughout the tree.

    Will only update placeholder values of nodes that already have that placeholder and for which that
    placeholder has a different value. If a node doesn't have any of the placeholders in placeholder_values,
    or all the values match already, then nothing happens with that node.

    :param start_node: start node
    :param placeholder_values: Dictionary mapping placeholder names to new values.
    :return: Updated copy of the start_node. If nothing needs to be updated, then the start_node unchanged.
    """
    find_keys = set(placeholder_values.keys())

    def filter_function(node: SqlModel) -> bool:
        filter_node_keys = set(node.placeholders.keys())
        return bool(find_keys.intersection(filter_node_keys))

    found_nodes = find_nodes(start_node, function=filter_function)
    for found_node in found_nodes:
        node_keys = set(found_node.model.placeholders.keys())
        matching_keys = find_keys.intersection(node_keys)
        dict_to_update = {
            key: placeholder_values[key]
            for key in matching_keys if found_node.model.placeholders[key] != placeholder_values[key]
        }
        if not dict_to_update:
            continue
        new_dict = found_node.model.placeholders
        new_dict.update(dict_to_update)
        start_node = start_node.set(found_node.reference_path, **new_dict)
    return start_node


def replace_node_in_graph(
        start_node: TSqlModel,
        reference_path: RefPath,
        replacement_model: T2SqlModel) -> Union[TSqlModel, T2SqlModel]:
    """
    Create a (partial) copy of the graph that can be reached from start_node, with the referenced node
    replaced by replacement_model. All nodes along all reference paths to the referenced node will be
    replaced with copies of the original nodes that (indirectly) link to replacement_model.

    The original start node, and all nodes that it refers recursively are unchanged; the returned and
    modified SqlModel is a copy.
    :param start_node: start node
    :param reference_path: references to traverse to get to the node that has to be updated
    :param replacement_model: model instance that will replace the reference node
    :return: an updated copy of the start node, or the replacement_node if reference_path is empty
    """
    if reference_path == tuple():
        return replacement_model

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


def replace_non_start_node_in_graph(
        start_node: TSqlModel,
        reference_path: RefPath,
        replacement_model: SqlModel) -> TSqlModel:
    """
    Similar to :meth:`replace_node_in_graph()`, except in this case the reference_path cannot be empty, i.e.
    the node to replace cannot be the start_node.

    The limitation that reference_path cannot be empty has the advantage that this function guarantees to
    return a copy of the start_node, and never the replacement_model. This can be useful when one wants to
    be sure that the return type is the same as the type of start_node.

    The original start node, and all nodes that it refers recursively are unchanged.
    :param start_node: start node
    :param reference_path: references to traverse to get to the node that has to be updated. Cannot be empty
    :param replacement_model: model instance that will replace the reference node
    :return: an updated copy of the start node
    :raises ValueError: if reference_path is an empty tuple
    """
    if reference_path == tuple():
        raise ValueError(f'reference path cannot be empty, use replace_node_in_graph() instead.')
    selected_node = get_node_info_selected_node(start_node, reference_path)
    dependent_model_ids = _get_all_dependent_node_model_ids(selected_node)
    # See replace_node_in_graph() for more comments on the implementation
    return _replace_model_in_graph_recursively(
        current_node=start_node,
        model_to_replace=selected_node.model,
        replacement_node=replacement_model,
        dependent_model_ids=dependent_model_ids,
        replaced_models={}
    )


def _replace_model_in_graph_recursively(
        current_node: TSqlModel,
        model_to_replace: SqlModel,
        replacement_node: SqlModel,
        dependent_model_ids: Set[int],
        replaced_models: Dict[int, SqlModel]
) -> TSqlModel:
    """
    Return the a copy of current_node, with the recursively referenced nodes of the original replaced by
        copies too. The replacement_node is not replaced by a copy but by replacement_node.
    Only nodes in dependent_model_ids are copied/updated, for others the original nodes are linked.

    Effectively this can be used to replace a single node, and create a new graph that references that
    updated node.

    Important limitation: current_node cannot be the same as model_to_replace!

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
        # For a basic recursive function this would be the base case, and we'd return here. But as we want to
        # guarantee to return the same type as current_node, we disallow this and handle the base case below
        raise Exception('Function should only be used for the recursive case.')
    new_references = {}
    for ref_name, ref_node in current_node.references.items():
        node_id = id(ref_node)
        if node_id in dependent_model_ids:
            if node_id in replaced_models:
                # cached case
                new_references[ref_name] = replaced_models[node_id]
            elif ref_node is model_to_replace:
                # base case
                new_references[ref_name] = replacement_node
            else:
                # recursive case
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
