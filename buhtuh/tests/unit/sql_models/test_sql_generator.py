"""
Copyright 2021 Objectiv B.V.
"""
import pytest

from sql_models.model import SqlModelBuilder, CustomSqlModel
from sql_models.sql_generator import to_sql, _escape_value
from tests.unit.sql_models.test_graph_operations import get_simple_test_graph
from tests.unit.sql_models.util import assert_roughly_equal_sql


def test_simple():
    # simple test that this compiles and doesn't crash
    graph = get_simple_test_graph()
    result = to_sql(graph)
    assert result


def assert_escape_compare_value(value):
    """ helper for test__escape_value. Assert that the escaped value, after formatting equals the original"""
    escaped = _escape_value(value)
    assert escaped.format() == value


def test__escape_value():
    assert_escape_compare_value('test')
    assert_escape_compare_value('te{s}t')
    assert_escape_compare_value('te{{s}}t')
    assert_escape_compare_value('te{st')
    assert_escape_compare_value('te{{s}t')
    assert_escape_compare_value('te{{st')
    full_string = '{test}' + _escape_value('{test}') + '{test}'
    assert full_string.format(test='x') == 'x{test}x'
    full_string = '{test}' + _escape_value('{{test}}') + '{test}'
    assert full_string.format(test='x') == 'x{{test}}x'


def test_format_injection():
    # Make sure that (parts of) format strings in the properties of a model don't mess up the sql generation.
    mb = CustomSqlModel('select {a} from x')
    result = to_sql(mb(a='y'))
    assert result == 'select y from x'
    result = to_sql(mb(a="'{y}'"))
    assert result == "select '{y}' from x"
    result = to_sql(mb(a="'{{y}}'"))
    assert result == "select '{{y}}' from x"
    result = to_sql(mb(a="'{{{y}}}'"))
    assert result == "select '{{{y}}}' from x"
    result = to_sql(mb(a="'{{{y}'"))
    assert result == "select '{{{y}' from x"

    model = mb(a="'{{y}}'")
    mb = CustomSqlModel('select {a} from {{x}}')
    result = to_sql(mb(a='y', x=model))
    expected = 'with CustomSqlModel___0eece243b7a88bc997419498b4cdb1a1 as (select \'{{y}}\' from x)\n' \
               'select y from CustomSqlModel___0eece243b7a88bc997419498b4cdb1a1'
    assert result == expected

    result = to_sql(mb(a="'{y}'", x=model))
    expected = 'with CustomSqlModel___0eece243b7a88bc997419498b4cdb1a1 as (select \'{{y}}\' from x)\n' \
               "select '{y}' from CustomSqlModel___0eece243b7a88bc997419498b4cdb1a1"
    assert result == expected

    result = to_sql(mb(a="'{{y}}'", x=model))
    expected = 'with CustomSqlModel___0eece243b7a88bc997419498b4cdb1a1 as (select \'{{y}}\' from x)\n' \
               "select '{{y}}' from CustomSqlModel___0eece243b7a88bc997419498b4cdb1a1"
    assert result == expected


# Below are more complex scenarios, first define SqlModels to use in the tests
# todo: code to generate test classes?

class SourceTable(SqlModelBuilder):
    @property
    def sql(self):
        return 'select 1 as val'


class Double(SqlModelBuilder):
    @property
    def sql(self):
        return 'select (val * 2) as val from {{source}}'


class Add(SqlModelBuilder):
    """ Adds val column of two source models """
    @property
    def sql(self):
        return '''
            select (one.val + two.val) as val
            from {{one}} as one
            cross join {{two}} as two
        '''


class MultiplierNoId(SqlModelBuilder):
    """
    Multiplies a value by a constant.
    Takes:
        * one parameter: multiplier
        * one reference: source, expects the field value
    """
    @property
    def sql(self):
        return '''
            with multiplier_cte as (
                select {multiplier} as multiplier
            )
            select (src.val * multiplier_cte.multiplier) as val
            from {{source}} as src
            join multiplier_cte
        '''


class MultiplierWithId(SqlModelBuilder):
    """ Same as MultiplierNoId, but uses {{id}} in cte-name """
    @property
    def sql(self):
        return '''
            with multiplier_cte_{{id}} as (
                select {multiplier} as multiplier
            )
            select (src.val * multiplier_cte.multiplier) as val
            from {{source}} as src
            join multiplier_cte
        '''


def test_model_thrice_simple():
    model = Double.build(
        source=Double(
            source=Double(
                source=SourceTable()
            )
        )
    )
    result = to_sql(model)
    expected = '''
        with SourceTable___563606f14b78ab0a5ba36b3055e3d518 as (
            select 1 as val
        ), Double___95e1a5df04751be6eaa1eb40aa14d043 as (
            select (val * 2) as val
            from SourceTable___563606f14b78ab0a5ba36b3055e3d518
        ), Double___00ce2e48b4d54f24ca6d77cca5261107 as (
            select (val * 2) as val
            from Double___95e1a5df04751be6eaa1eb40aa14d043
        )
        select (val * 2) as val
        from Double___00ce2e48b4d54f24ca6d77cca5261107
    '''
    assert_roughly_equal_sql(result, expected)


def test_model_duplicate_no_id():
    # Test that the sql-generation correctly detects duplicate CTE-names with non-duplicate sql
    # In the future we might do some automagical rewriting, for  now we mainly expect an error to be raised

    model = MultiplierNoId.build(
        multiplier=2,
        source=MultiplierNoId(
            multiplier=2,
            source=SourceTable()
        )
    )
    # Multiplier has a CTE that is named 'multiplier_cte', for which the sql is influenced by the
    # 'multiplier' parameter. This is fine if it has the same value every time that the model is used.
    sql1 = to_sql(model)
    assert sql1
    # Now change the model, so that the 'multiplier' parameter is different for the different Multiplier
    # instances, and thus the 'multiplier_cte' has different sql.
    update_model = model.set((), multiplier=3)
    with pytest.raises(Exception,
                       match='CTE multiplier_cte multiple times, but with different definitions'):
        to_sql(update_model)


def test_model_duplicate_with_id():
    # Test that the sql-generation correctly generates unique CTE-names if the name contains {{id}}

    model = MultiplierWithId.build(
        multiplier=2,
        source=MultiplierWithId(
            multiplier=2,
            source=SourceTable()
        )
    )
    # Multiplier has a CTE that is named 'multiplier_cte_{{id}}', for which the sql is influenced by the
    # 'multiplier' parameter.
    sql1 = to_sql(model)
    # Now change the model, so that the 'multiplier' parameter is different for the different Multiplier
    # instances, and thus the 'multiplier_cte_{{id}}' has different sql. This should still work, as the
    # CTE-names don't collide
    update_model = model.set((), multiplier=3)
    sql2 = to_sql(update_model)
    assert sql1 != sql2


def test_code_deduplication_multiple_reference():
    source_model = SourceTable.build()
    add_model = Add.build(
        one=source_model,
        two=source_model
    )
    graph = Add.build(
        one=add_model,
        two=add_model
    )
    # graph contains two references to the same Add model instance, which each contain two references to
    # the same SourceTable model instance. That is the one SourceTable instance occurs four times in the
    # graph.
    # We don't want the sql for SourceTable to be duplicated four times.
    # Similarly the add_model appears in the graph three times, but two of those are the same instance. We
    # want those two to be deduplicated and only appear once. Plus the one other instance we expect the Add
    # sql twice
    sql = to_sql(graph)
    assert sql
    assert sql.count('select 1 as val') == 1
    assert sql.count('one.val + two.val') == 2


def test_code_deduplication_multiple_instances():
    # Similar to test_code_deduplication_multiple_reference above. But now the models are actually
    # duplicated, instead of just referenced multiple times. That is there really are four SourceTable
    # instances. We still want the same result tho
    graph = Add.build(
        one=Add.build(
            one=SourceTable.build(),
            two=SourceTable.build()
        ),
        two=Add.build(
            one=SourceTable.build(),
            two=SourceTable.build()
        )
    )
    sql = to_sql(graph)
    assert sql
    assert sql.count('select 1 as val') == 1
    assert sql.count('one.val + two.val') == 2


def test_code_deduplication_multiple_reference_many_paths():
    # Similar to test_code_deduplication_multiple_reference above, but with a generated graph with a lot
    # more possible references paths

    # The generated graph will have 2^depth possible reference paths. Our initial version produced sql for
    # 2^depth ctes. This test acts as a sort of performance test to see that this both performs well, and
    # that this doesn't generate a big sql output.
    depth = 20
    graph = SourceTable.build()
    for _ in range(depth):
        graph = Add.build(
            one=graph,
            two=graph
        )
    sql = to_sql(graph)
    assert sql
    assert sql.count('select 1 as val') == 1
    assert sql.count('one.val + two.val') == depth
