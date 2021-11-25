"""
Copyright 2021 Objectiv B.V.
"""
import re

from sql_models.model import Materialization
from sql_models.sql_generator import to_sql, to_sql_materialized_nodes
from tests.unit.sql_models.test_graph_operations import get_simple_test_graph
from tests.unit.sql_models.util import ValueModel, RefModel, JoinModel, assert_roughly_equal_sql


def test_simple_to_sql():
    # simple test that a simple graph compiles, and gets the expected sql with both
    # to_sql and to_sql_materialized_nodes
    graph = get_simple_test_graph()
    graph_view = graph.copy_set_materialization(Materialization.VIEW)
    graph_table = graph.copy_set_materialization(Materialization.TABLE)
    graph_temp_table = graph.copy_set_materialization(Materialization.TEMP_TABLE_DROP_ON_COMMIT)
    sql_view = to_sql(graph_view)
    sql_table = to_sql(graph_table)
    sql_temp_table = to_sql(graph_temp_table)

    # assert that output of to_sql_materialized_nodes() matched to_sql()
    assert [sql_view] == to_sql_materialized_nodes(graph_view)
    assert [sql_table] == to_sql_materialized_nodes(graph_table)
    assert [sql_temp_table] == to_sql_materialized_nodes(graph_temp_table)

    # assert that the sql generate for the table is correct
    expected_sql_table = '''
        create table "JoinModel___3ebde1f01590e5fe5fa072c173787704"
        as with "ValueModel___b7d73a5c6c1314049eed420498e93743" as (
            select 'a' as key, 1 as value
        ), "RefModel___f29f638f5e9d8d5c1901935f09f9cb6d" as (
            select * from "ValueModel___b7d73a5c6c1314049eed420498e93743"
        ), "ValueModel___f77eb4c4b41a3be5688a7a57f2c02f2b" as (
            select 'a' as key, 2 as value
        )
        select l.key, l.value + r.value as value
        from "RefModel___f29f638f5e9d8d5c1901935f09f9cb6d" as l
        inner join "ValueModel___f77eb4c4b41a3be5688a7a57f2c02f2b" as r on l.key=r.key
    '''
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


def test_edge_node_materialization():
    # test simple case: only edge nodes are materialized
    # Graph:
    #   vm2* <--\
    #           +-- graph
    #   vm1* <--/
    #
    vm1 = ValueModel().set_materialization(Materialization.VIEW).set_values(key='a', val=1).instantiate()
    vm2 = ValueModel().set_materialization(Materialization.TABLE).set_values(key='a', val=2).instantiate()
    graph = JoinModel.build(ref_left=vm1, ref_right=vm2)
    result = to_sql_materialized_nodes(graph)
    assert len(result) == 3
    expected_query = '''
        select l.key, l.value + r.value as value
        from "ValueModel___0ac9d97fdf6130a764a7a146da92cc9f" as l
        inner join "ValueModel___f9701cfe7e35725fa2fb60810e38a002" as r on l.key=r.key
    '''

    # TODO: the naming of these views and tables is something we need to improve
    assert result[0] == 'create table "ValueModel___f9701cfe7e35725fa2fb60810e38a002" as select \'a\' as key, 2 as value'
    assert result[1] == 'create view "ValueModel___0ac9d97fdf6130a764a7a146da92cc9f" as select \'a\' as key, 1 as value'
    assert_roughly_equal_sql(result[2], expected_query)


def test_non_edge_node_materialization():
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
    result = to_sql_materialized_nodes(graph)
    assert len(result) == 2
    # TODO: the naming of these views and tables in the generated sql is something we need to improve
    jm_expected_sql = '''
        create view "JoinModel___c10609d2c42f594bc65fe2f27ef15612" as
        with "ValueModel___b7d73a5c6c1314049eed420498e93743" as (
            select 'a' as key, 1 as value
        ), "ValueModel___f77eb4c4b41a3be5688a7a57f2c02f2b" as (
            select 'a' as key, 2 as value
        )
        select l.key, l.value + r.value as value
        from "ValueModel___b7d73a5c6c1314049eed420498e93743" as l
        inner join "ValueModel___f77eb4c4b41a3be5688a7a57f2c02f2b" as r on l.key=r.key
    '''
    graph_expected_sql = 'select * from "JoinModel___c10609d2c42f594bc65fe2f27ef15612"'
    assert_roughly_equal_sql(result[0], jm_expected_sql)
    assert_roughly_equal_sql(result[1], graph_expected_sql)
