"""
Copyright 2021 Objectiv B.V.
"""
import os
from typing import List, Any, Tuple

import sqlalchemy

from sql_models.graph_operations import find_node, replace_node_in_graph
from sql_models.model import Materialization
from sql_models.sql_generator import to_sql_materialized_nodes
from tests.unit.sql_models.util import ValueModel, RefModel, JoinModel, RefValueModel


DB_TEST_URL = os.environ.get('OBJ_DB_TEST_URL', 'postgresql://objectiv:@localhost:5432/objectiv')


def test_execute_multi_statement_sql_materialization():
    # Graph, with values calculated by the query shown above each node
    #
    #                                              16
    #    1       6             16      16     /-- rm2 <--\     40
    #   vm1 <-- rvm1 <--+--- rvm2 <-- rm1 <--+     24     +-- graph
    #                    \                    \-- jm2 <--/
    #                     \     8                 /
    #                      +-- jm1 <-------------/
    #              2      /
    #            vm2 <---/
    #

    # Create original graph, with all materializations as CTE
    vm1 = ValueModel.build(key='a', val=1)
    rvm1 = RefValueModel.build(ref=vm1, val=5)
    rvm2 = RefValueModel.build(ref=rvm1, val=10)
    rm1 = RefModel.build(ref=rvm2)
    rm2 = RefModel.build(ref=rm1)
    vm2 = ValueModel.build(key='a', val=2)
    jm1 = JoinModel.build(ref_left=vm2, ref_right=rvm1)
    jm2 = JoinModel.build(ref_left=jm1, ref_right=rm1)
    graph = JoinModel.build(ref_left=jm2, ref_right=rm2)

    # Expected output of the query
    expected_columns = ['key', 'value']
    expected_values = [['a', 40]]
    expected = expected_columns, expected_values
    # Verify that the model's query gives the expected output
    sql_statements = to_sql_materialized_nodes(graph)
    assert len(sql_statements) == 1
    result = run_queries(sql_statements)
    assert result == expected

    # Test: modify materialization of node 'jm2' in the graph
    reference_path = find_node(start_node=graph, function=lambda n: n is jm2).reference_path
    jm2_replacement = jm2.copy_set_materialization(Materialization.TEMP_TABLE_DROP_ON_COMMIT)
    graph = replace_node_in_graph(
        start_node=graph,
        reference_path=reference_path,
        replacement_model=jm2_replacement
    )
    # Verify that the model's query gives the expected output
    sql_statements = to_sql_materialized_nodes(graph)
    assert len(sql_statements) == 2
    result = run_queries(sql_statements)
    assert result == expected

    # Test: modify materialization of nodes 'jm1' and 'rvm2' in the graph
    graph = replace_node_in_graph(
        start_node=graph,
        reference_path=find_node(start_node=graph, function=lambda n: n is jm1).reference_path,
        replacement_model=jm1.copy_set_materialization(Materialization.VIEW)
    )
    graph = replace_node_in_graph(
        start_node=graph,
        reference_path=find_node(start_node=graph, function=lambda n: n is rvm2).reference_path,
        replacement_model=rvm2.copy_set_materialization(Materialization.TABLE)
    )
    # Verify that the model's query gives the expected output
    sql_statements = to_sql_materialized_nodes(graph)
    assert len(sql_statements) == 4
    result = run_queries(sql_statements)
    assert result == expected

    # Test: modify materialization of nodes 'rvm1' in the graph
    graph = replace_node_in_graph(
        start_node=graph,
        reference_path=find_node(start_node=graph, function=lambda n: n is rvm1).reference_path,
        replacement_model=rvm1.copy_set_materialization(Materialization.TEMP_TABLE_DROP_ON_COMMIT)
    )
    # Verify that the model's query gives the expected output
    sql_statements = to_sql_materialized_nodes(graph)
    assert len(sql_statements) == 5
    result = run_queries(sql_statements)
    assert result == expected


def test_materialized_shared_ctes():
    # Graph: jm1 and jm2 are materialized, vm2 is shared between the two
    #    1
    #   vm1 <---\     3
    #            +-- jm1* <--\
    #     2      /             \    8
    #   vm2 <--+               +-- graph
    #           \      5       /
    #     3       +-- jm2* <--/
    #   vm3 <---/


    # Create original graph, with all materializations as CTE
    vm1 = ValueModel.build(key='a', val=1)
    vm2 = ValueModel.build(key='a', val=2)
    vm3 = ValueModel.build(key='a', val=3)
    jm1 = JoinModel().set_materialization(Materialization.TEMP_TABLE_DROP_ON_COMMIT)\
        .set_values(ref_left=vm2, ref_right=vm1).instantiate()
    jm2 = JoinModel().set_materialization(Materialization.TEMP_TABLE_DROP_ON_COMMIT)\
        .set_values(ref_left=vm3, ref_right=vm2).instantiate()
    graph = JoinModel.build(ref_left=jm2, ref_right=jm1)

    # Verify that the model's query gives the expected output
    sql_statements = to_sql_materialized_nodes(graph)
    assert len(sql_statements) == 3
    columns, values = run_queries(sql_statements)
    assert columns == ['key', 'value']
    assert values == [['a', 8]]  # (1 + 2) + (2 + 3) = 3 + 5 = 8


def run_queries(sql_statements: List[str]) -> Tuple[List[str], List[List[Any]]]:
    """
    Execute all sql statements and return result of last one. The statements will be executed inside a
    transaction that will be rolled back, which will any table/view create statements.
    :param sql_statements: List of sql statements. Should not contain any transactions begin/commit/rollback
        statements.
    :return: tuple:
        1) List of column-names
        2) List of rows, with each row being a list of values
    """
    if not sql_statements:
        raise ValueError('Expected non-empty list')

    sql = ';'.join(sql_statement for sql_statement in sql_statements)
    print(f'\n\n{sql}\n\n')
    # escape sql, as conn.execute will think that '%' indicates a parameter
    sql = sql.replace('%', '%%')

    engine = sqlalchemy.create_engine(DB_TEST_URL)
    with engine.connect() as conn:
        with conn.begin() as transaction:
            res = conn.execute(sql)
            column_names = list(res.keys())
            db_values = [list(row) for row in res]
            # rollback. This will remove any tables or views that we might have created.
            transaction.rollback()
            return column_names, db_values
