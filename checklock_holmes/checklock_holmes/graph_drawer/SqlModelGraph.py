from copy import deepcopy
from functools import cached_property

from sql_models.model import SqlModel
from graphviz import Digraph


class SqlModelGraph:
    NODE_NAME_PROP_NAME = 'node_name'
    NODE_ORDER_PROP_NAME = 'node_creation_order'
    NODE_IS_MERGE_PROP_NAME = 'generated_by_merged'

    def __init__(self, node: SqlModel):
        self._last_node = node
        self._added_nodes = []
        self._initialize_graph()

    def draw(self) -> None:
        self._graph.render('doctest-output/round-table.gv').replace('\\', '/')

    @property
    def graph(self) -> Digraph:
        return self._graph

    @cached_property
    def root_node(self) -> SqlModel:
        current_node = deepcopy(self._last_node)
        while current_node.references:
            current_node = list(current_node.references.values())[0]

        return current_node

    def _initialize_graph(self) -> None:
        self._graph = Digraph()
        self._add_node_references(self._last_node)

    def _add_node_references(
        self, current_node: SqlModel,
    ) -> None:
        self._add_node_as_vertex(current_node)
        for ref in current_node.references.values():
            self._graph.edge(ref.hash, current_node.hash)

            if ref.hash not in self._added_nodes:
                self._add_node_references(ref)

    def _add_node_as_vertex(self, node: SqlModel) -> None:
        if node.hash in self._added_nodes:
            return
        self._graph.node(name=node.hash, label=f'{node.generic_name}_{node.hash}')
        self._added_nodes.append(node.hash)
