import re
import warnings

import numpy as np

from bach import DataFrameOrSeries
from bach.merge import MergeSqlModel
from sql_models.model import SqlModel

# default styling for bach graphs
DEFAULT_GRAPH_NODE_FORMAT = {
    'style': 'filled',
    'fontsize': '8',
    'scale': '0.5',
    'shape': 'plaintext',
    'fillcolor': 'white',
}


class SqlModelGraphDisplay:
    def __init__(
        self,
        obj: DataFrameOrSeries,
    ) -> None:
        try:
            from graphviz import Digraph
            self._graph = Digraph(node_attr=DEFAULT_GRAPH_NODE_FORMAT)
        except ModuleNotFoundError:
            warnings.warn(
                message='graphviz module is required for displaying SQLModel graphs.',
                category=UserWarning,
            )
            print(obj.view_sql())

        self._added_nodes = []

        # fill graph
        self._add_node_references(obj.base_node)

    def __call__(self) -> None:
        try:
            from IPython.display import display_svg
            display_svg(self._graph)
        except ModuleNotFoundError:
            warnings.warn(
                message='Please install IPython module for displaying the graph',
                category=UserWarning,
            )
            print(self._graph.source)

    def _add_node_references(self, current_node: SqlModel) -> None:
        # add current node to graph
        target = self._add_node_as_vertex(current_node)
        # add edges with ref nodes
        for ref_name, ref in current_node.references.items():
            node_target = target
            if isinstance(current_node, MergeSqlModel):
                # ref_name is left_node or right_node
                node_target = f'{target}:{ref_name}'

            self._graph.edge(ref.hash, node_target)

            if ref.hash not in self._added_nodes:
                self._add_node_references(ref)

    def _add_node_as_vertex(self, current_node: SqlModel) -> str:
        """
        Adds the node as a vertex into the graph using its hash as identifier.
        The vertex will be displayed based on default template:
        ____________________________________________________________
        |                                     | col1 | col2 | col3 |
        |            Node Name                |--------------------|
        |                                     | col4 | col5 | col6 |
        -----------------------------------------------------------
        Returns the id of the node to be referenced when adding a new edge.

        If base node is instance of MergeSqlModel, an extra node will be created for displaying
        merge information and its id will be returned instead.
        """
        # objectiv blue
        _SQL_NODE_COLOR = '#abe9fe'
        _NODE_LABEL_TEMPLATE = (
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">'
            '<TR>'
            f'<TD BGCOLOR="{_SQL_NODE_COLOR}" ROWSPAN="{{total_column_rows}}"><b>{{node_name}}</b></TD>'
            '</TR>'
            '{column_rows_tags}'
            '</TABLE>>'
        )

        column_name_rows = self._get_column_names_rows(current_node)
        node_name = f'{current_node.generic_name}_{current_node.hash}'
        label = _NODE_LABEL_TEMPLATE.format(
            total_column_rows=len(column_name_rows) + 1,
            node_name=node_name,
            column_rows_tags=''.join(column_name_rows)
        )

        # add current node to graph
        self._graph.node(name=current_node.hash, label=label)
        self._added_nodes.append(current_node.hash)

        # add a node for merge information
        # and make references create edges to merge info node instead
        if isinstance(current_node, MergeSqlModel):
            return self._add_merge_info_node(current_node)

        return current_node.hash

    @staticmethod
    def _get_column_names_rows(current_node: SqlModel):
        """
        Generates column labels for the node.
        """
        _COLUMNS_PER_ROW = 3
        _COLUMN_LABEL_COLOR = '#fef284'  # objectiv yellow
        _COLUMN_NAME_COLUMN_TEMPLATE = (
            f'<TD BGCOLOR="{_COLUMN_LABEL_COLOR}" COLSPAN="{{col_span}}">{{col}}</TD>'
        )

        col_names = list(current_node.column_expressions.keys())

        # split list of column names into equal-sized sub lists
        col_names_per_row = np.array_split(
            np.array(col_names), np.ceil(len(col_names)/_COLUMNS_PER_ROW)
        )

        row_tags = []
        for c_row in col_names_per_row:
            col_tags = []
            for pos, col in enumerate(c_row):
                col_span = 1

                # make the last col span bigger if the number of columns is less than the expected
                if len(c_row) < _COLUMNS_PER_ROW and pos == len(c_row) - 1:
                    col_span = _COLUMNS_PER_ROW - pos

                col_tag = _COLUMN_NAME_COLUMN_TEMPLATE.format(col=col, col_span=col_span)
                col_tags.append(col_tag)

            row_tags.append(f"<TR>{''.join(col_tags)}</TR>")

        return row_tags

    def _add_merge_info_node(self, merge_node: MergeSqlModel) -> str:
        """
        Adds a new vertex representing the merge information of the node.
        The vertex will be displayed with the following format:
            _____________________________
            |     <join_type> JOIN ON    |
            |----------------------------|
            |     left    |    right     |
            |------------ |--------------|
            |     col1    |     col1     |
            |     col2    |     col2     |
            -----------------------------
        """
        _MERGE_INFO_NODE_COLOR = '#fba99d'  # objectiv red
        self._graph.attr('node', fillcolor=_MERGE_INFO_NODE_COLOR, shape='record')
        join_regex = re.compile(
            r'.*(?P<join_type>left|right|outer|cross|inner).+join.*', re.S | re.I,
        )

        match = join_regex.match(merge_node.sql)
        if match:
            join_type = match.group('join_type')
        else:
            join_type = ''

        merge_node_name = f'{merge_node.hash}_merge'

        join_type_row = f'{join_type.upper()} JOIN ON'

        # <left_node> and <right_node> tags help graphviz know where to draw the edges from
        # each vertex of references from the node to the merge information node
        left_right_row = '{<left_node>left |<right_node>right}'

        left_on_column_labels = "|".join(merge_node.merge_on.left)
        right_on_column_labels = "|".join(merge_node.merge_on.right)
        on_column_rows = f'{left_on_column_labels}|{right_on_column_labels}'
        on_column_rows = f'{{{on_column_rows}}}'

        # rows are separated by pipes
        label = f'{join_type_row}|{left_right_row}|{on_column_rows}'
        label = f'{{{label}}}'
        self._graph.node(name=merge_node_name, label=label)

        # create edge to result merge
        self._graph.edge(f'{merge_node_name}', merge_node.hash)

        self._graph.attr('node', shape='plaintext', fillcolor='white')
        return merge_node_name


def display_sql_as_graph(obj: DataFrameOrSeries) -> None:
    """
    Displays a graph of all referenced nodes by :py:meth:`DataFrame.base_node` in the frontend (notebook)
    as an SVG.

    :param obj: DataFrame or Series from where to obtain the generated sql.

    .. note::
        Requires the graphviz package, if not installed the query will be print instead

    .. note::
        Requires the IPython package, if not installed the graph source will be print instead
    """
    SqlModelGraphDisplay(obj)()
