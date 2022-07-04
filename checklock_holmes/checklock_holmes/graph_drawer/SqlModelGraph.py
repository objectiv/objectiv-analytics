from copy import deepcopy
from functools import cached_property

import graph_tool as gt
from bach.merge import MergeSqlModel
from graph_tool.draw import graph_draw, planar_layout
from sql_models.model import SqlModel


class SqlModelGraph:
    NODE_NAME_PROP_NAME = 'node_name'
    NODE_ORDER_PROP_NAME = 'node_creation_order'
    NODE_IS_MERGE_PROP_NAME = 'generated_by_merged'

    def __init__(self, node: SqlModel):
        self._last_node = node
        self._node_name_x_vertex_id = {}
        self._initialize_graph()

    def draw(self) -> None:
        pos = planar_layout(self._graph)
        graph_draw(
            self._graph,
            pos=pos,
            vertex_text=self._graph.vp[self.NODE_NAME_PROP_NAME],
            #edge_text=self._graph.ep[self.NODE_IS_MERGE_PROP_NAME],
            vprops={
                'size': 10,
                'text_position': 'centered'
            },
            output_size=(1000, 1000),
            output="sql_model_graph.pdf",
        )

    @property
    def graph(self) -> gt.Graph:
        return self._graph

    @cached_property
    def root_node(self) -> SqlModel:
        current_node = deepcopy(self._last_node)
        while current_node.references:
            current_node = list(current_node.references.values())[0]

        return current_node

    def _initialize_graph(self) -> None:
        self._graph = gt.Graph()
        self._graph.vp[self.NODE_NAME_PROP_NAME] = self._graph.new_vp('string')
        self._graph.vp[self.NODE_ORDER_PROP_NAME] = self._graph.new_vp('int')
        self._graph.ep[self.NODE_IS_MERGE_PROP_NAME] = self._graph.new_ep('string')

        # add first node
        ln_vertex = self._add_node_as_vertex(self._last_node)
        self._add_node_references(self._last_node, ln_vertex)

        self._assign_order_creation_property()

    def _add_node_references(
        self, current_node: SqlModel, current_vertex_id: int,
    ) -> None:
        for ref in current_node.references.values():
            ref_vertex_id = self._add_node_as_vertex(ref)
            # don't add the edge if it already exist
            if self._graph.edge(ref_vertex_id, current_vertex_id):
                continue

            e_id = self._graph.add_edge(source=ref_vertex_id, target=current_vertex_id)
            if isinstance(current_node, MergeSqlModel):
                self._graph.ep[self.NODE_IS_MERGE_PROP_NAME][e_id] = 'merge'

            if ref.references:
                self._add_node_references(
                    current_node=ref, current_vertex_id=ref_vertex_id,
                )

    def _add_node_as_vertex(self, node: SqlModel) -> int:

        node_name = f'{node.generic_name}_{node.hash}'
        if node_name in self._node_name_x_vertex_id:
            return self._node_name_x_vertex_id[node_name]

        vertex_id = self._graph.add_vertex()
        self._node_name_x_vertex_id[node_name] = vertex_id

        short_node_name = f'{node.generic_name}_{node.hash[0:3]}...{node.hash[-3:]}'
        self._graph.vp[self.NODE_NAME_PROP_NAME][vertex_id] = short_node_name

        return vertex_id

    def _assign_order_creation_property(self) -> None:
        for creation_index, v_index in enumerate(reversed(self._graph.get_vertices())):
            self._graph.vp[self.NODE_ORDER_PROP_NAME][v_index] = creation_index
