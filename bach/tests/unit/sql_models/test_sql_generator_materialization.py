"""
Copyright 2021 Objectiv B.V.
"""
import re

from sql_models.model import Materialization
from sql_models.sql_generator import to_sql, to_sql_materialized_nodes, GeneratedSqlStatement
from sql_models.util import is_bigquery
from tests.unit.sql_models.test_graph_operations import get_simple_test_graph
from tests.unit.sql_models.util import ValueModel, RefModel, JoinModel, assert_roughly_equal_sql


def test_simple_to_sql(dialect):
    # simple test that a simple graph compiles, and gets the expected sql with both
    # to_sql and to_sql_materialized_nodes
    graph = get_simple_test_graph()
    graph_view = graph.copy_set_materialization(Materialization.VIEW)
    graph_table = graph.copy_set_materialization(Materialization.TABLE)
    graph_temp_table = graph.copy_set_materialization(Materialization.TEMP_TABLE)
    sql_view = to_sql(dialect=dialect, model=graph_view)
    sql_table = to_sql(dialect=dialect, model=graph_table)
    sql_temp_table = to_sql(dialect=dialect, model=graph_temp_table)

    # assert that output of to_sql_materialized_nodes() matched to_sql()
    expected_view = GeneratedSqlStatement(
        name='JoinModel___2c6ab23e2f26eec98c57470d04d05cbf',
        sql=sql_view,
        materialization=Materialization.VIEW
    )
    expected_table = GeneratedSqlStatement(
        name='JoinModel___9141afd6d19376e1c7d2025997f249b7',
        sql=sql_table,
        materialization=Materialization.TABLE
    )
    expected_temp_table = GeneratedSqlStatement(
        name='JoinModel___440ba69f7e973ec9a376255c3fd16edc',
        sql=sql_temp_table,
        materialization=Materialization.TEMP_TABLE
    )
    assert to_sql_materialized_nodes(dialect=dialect, start_node=graph_view) == [expected_view]
    assert to_sql_materialized_nodes(dialect=dialect, start_node=graph_table) == [expected_table]
    assert to_sql_materialized_nodes(dialect=dialect, start_node=graph_temp_table) == [expected_temp_table]

    # assert that the sql generate for the table is correct
    expected_sql_table = '''
        create table "JoinModel___9141afd6d19376e1c7d2025997f249b7"
        as with "ValueModel___02030afa3603fd134cde7518272d1076" as (
            select 'a' as key, 1 as value
        ), "RefModel___b24f07393e1432fcb37d0bc96d4eb407" as (
            select * from "ValueModel___02030afa3603fd134cde7518272d1076"
        ), "ValueModel___97e2f0126c5b60ef0a61a64cb166011e" as (
            select 'a' as key, 2 as value
        )
        select l.key, l.value + r.value as value
        from "RefModel___b24f07393e1432fcb37d0bc96d4eb407" as l
        inner join "ValueModel___97e2f0126c5b60ef0a61a64cb166011e" as r on l.key=r.key
    '''
    if is_bigquery(dialect):
        expected_sql_table = expected_sql_table.replace('"', '`')
    assert_roughly_equal_sql(expected_sql_table, sql_table)

    # assert that the generated sql for the other materializations only differs in the materialization and
    # the name of the final node (because the materialization influences the hash, which is part of the name)
    # TODO: don't make the hash part of the name? somehow
    sql_view_no_hash = re.sub(sql_view, 'JoinModel___[0-9a-f]*', 'JoinModel')
    sql_table_no_hash = re.sub(sql_table, 'JoinModel___[0-9a-f]*', 'JoinModel')
    sql_temp_table_no_hash = re.sub(sql_temp_table, 'JoinModel___[0-9a-f]*', 'JoinModel')
    assert sql_view_no_hash.replace('create view', 'create table') == sql_table_no_hash
    assert sql_temp_table_no_hash.replace('temporary ', '').replace(' on commit drop', '') == \
           sql_table_no_hash


def test_edge_node_materialization(dialect):
    # test simple case: only edge nodes are materialized
    # Graph:
    #   vm2* <--\
    #           +-- graph
    #   vm1* <--/
    #
    vm1 = ValueModel().set_materialization(Materialization.VIEW).set_values(key='a', val=1).instantiate()
    vm2 = ValueModel().set_materialization(Materialization.TABLE).set_values(key='a', val=2).instantiate()
    graph = JoinModel.build(ref_left=vm1, ref_right=vm2)
    result = to_sql_materialized_nodes(dialect=dialect, start_node=graph)
    assert len(result) == 3
    expected_query = '''
        select l.key, l.value + r.value as value
        from "ValueModel___130be867558e4620e86279b05dfbacd5" as l
        inner join "ValueModel___c51ebb544836be4d838c7e20080c3496" as r on l.key=r.key
    '''
    expected_table = 'create table "ValueModel___c51ebb544836be4d838c7e20080c3496" as select \'a\' as key, 2 as value'
    expected_view = 'create view "ValueModel___130be867558e4620e86279b05dfbacd5" as select \'a\' as key, 1 as value'
    if is_bigquery(dialect):
        expected_query = expected_query.replace('"', '`')
        expected_table = expected_table.replace('"', '`')
        expected_view = expected_view.replace('"', '`')
    assert result[0].sql == expected_table
    assert result[1].sql == expected_view
    assert_roughly_equal_sql(result[2].sql, expected_query)


def test_non_edge_node_materialization(dialect):
    # test simple case: only edge nodes are materialized
    # Graph:
    #   vm2 <--\
    #           +-- jm* <-- graph
    #   vm1 <--/
    #
    vm1 = ValueModel().set_values(key='a', val=1).instantiate()
    vm2 = ValueModel().set_values(key='a', val=2).instantiate()
    jm = JoinModel().set_materialization(Materialization.VIEW).\
        set_values(ref_left=vm1, ref_right=vm2).instantiate()
    graph = RefModel.build(ref=jm)
    result = to_sql_materialized_nodes(dialect=dialect, start_node=graph)
    assert len(result) == 2
    # TODO: the naming of these views and tables in the generated sql is something we need to improve
    jm_expected_sql = '''
        create view "JoinModel___325a4dbda493ad13c52f92cce0db2df4" as
        with "ValueModel___02030afa3603fd134cde7518272d1076" as (
            select 'a' as key, 1 as value
        ), "ValueModel___97e2f0126c5b60ef0a61a64cb166011e" as (
            select 'a' as key, 2 as value
        )
        select l.key, l.value + r.value as value
        from "ValueModel___02030afa3603fd134cde7518272d1076" as l
        inner join "ValueModel___97e2f0126c5b60ef0a61a64cb166011e" as r on l.key=r.key
    '''
    graph_expected_sql = 'select * from "JoinModel___325a4dbda493ad13c52f92cce0db2df4"'
    if is_bigquery(dialect):
        jm_expected_sql = jm_expected_sql.replace('"', '`')
        graph_expected_sql = graph_expected_sql.replace('"', '`')
    assert_roughly_equal_sql(result[0].sql, jm_expected_sql)
    assert_roughly_equal_sql(result[1].sql, graph_expected_sql)
