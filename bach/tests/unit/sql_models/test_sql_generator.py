"""
Copyright 2021 Objectiv B.V.
"""
import pytest
from sqlalchemy.dialects.postgresql.base import PGDialect

from sql_models.model import SqlModelBuilder, CustomSqlModelBuilder
from sql_models.sql_generator import to_sql
from sql_models.util import is_bigquery
from tests.unit.sql_models.test_graph_operations import get_simple_test_graph
from tests.unit.sql_models.util import assert_roughly_equal_sql


def test_simple(dialect):
    # simple test that this compiles and doesn't crash
    graph = get_simple_test_graph()
    result = to_sql(dialect=dialect, model=graph)
    assert result


def test_format_injection_single_model(dialect):
    # Make sure that (parts of) format strings in the properties of a model don't mess up the sql generation.
    mb = CustomSqlModelBuilder('select {a} from x')
    result = to_sql(dialect, mb(a='y'))
    assert result == 'select y from x'
    result = to_sql(dialect=dialect, model=mb(a="'{y}'"))
    assert result == "select '{y}' from x"
    result = to_sql(dialect=dialect, model=mb(a="'{{y}}'"))
    assert result == "select '{{y}}' from x"
    result = to_sql(dialect=dialect, model=mb(a="'{{{y}}}'"))
    assert result == "select '{{{y}}}' from x"
    result = to_sql(dialect=dialect, model=mb(a="'{{{y}'"))
    assert result == "select '{{{y}' from x"


def test_format_injection_composed_models(dialect):
    def dialect_expected(expected_sql: str) -> str:
        # replace the expected identifier quoatations if we are dealing with BigQuery dialect
        if is_bigquery(dialect):
            return expected_sql.replace('"', '`')
        return expected_sql

    # Make sure that (parts of) format strings in the properties of a model don't mess up the sql generation.
    mb = CustomSqlModelBuilder('select {a} from x')
    model = mb(a="'{{y}}'")
    mb = CustomSqlModelBuilder('select {a} from {{x}}')
    result = to_sql(dialect=dialect, model=mb(a='y', x=model))
    expected = 'with "CustomSqlModel___cdc8d7087835e90c219061949951b631" as (select \'{{y}}\' from x)\n' \
               'select y from "CustomSqlModel___cdc8d7087835e90c219061949951b631"'
    expected = dialect_expected(expected)
    assert result == expected

    result = to_sql(dialect=dialect, model=mb(a="'{y}'", x=model))
    expected = 'with "CustomSqlModel___cdc8d7087835e90c219061949951b631" as (select \'{{y}}\' from x)\n' \
               "select '{y}' from \"CustomSqlModel___cdc8d7087835e90c219061949951b631\""
    expected = dialect_expected(expected)
    assert result == expected

    result = to_sql(dialect=dialect, model=mb(a="'{{y}}'", x=model))
    expected = 'with "CustomSqlModel___cdc8d7087835e90c219061949951b631" as (select \'{{y}}\' from x)\n' \
               "select '{{y}}' from \"CustomSqlModel___cdc8d7087835e90c219061949951b631\""
    expected = dialect_expected(expected)
    assert result == expected


# Below are more complex scenarios, first define SqlModels to use in the tests
# todo: code to generate test classes?

class SourceTable(SqlModelBuilder):
    @property
    def sql(self):
        return 'select 1 as val'

    @property
    def generic_name(self):
        # Test that a name with special characters works too
        return 'Source "Table"'


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
    # TODO: bigquery
    dialect = PGDialect()
    model = Double.build(
        source=Double(
            source=Double(
                source=SourceTable()
            )
        )
    )
    result = to_sql(dialect=dialect, model=model)
    expected = '''
        with "Source ""Table""___8767445ba1af5136eeffd5341e01045d" as (
            select 1 as val
        ), "Double___f121c8a22ad316abde7720951c3289dc" as (
            select (val * 2) as val
            from "Source ""Table""___8767445ba1af5136eeffd5341e01045d"
        ), "Double___82474fb08efe26024ac77a358a288af8" as (
            select (val * 2) as val
            from "Double___f121c8a22ad316abde7720951c3289dc"
        )
        select (val * 2) as val
        from "Double___82474fb08efe26024ac77a358a288af8"
    '''
    assert_roughly_equal_sql(result, expected)


def test_model_duplicate_no_id(dialect):
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
    sql1 = to_sql(dialect=dialect, model=model)
    assert sql1
    # Now change the model, so that the 'multiplier' parameter is different for the different Multiplier
    # instances, and thus the 'multiplier_cte' has different sql.
    update_model = model.set((), multiplier=3)
    with pytest.raises(Exception,
                       match='CTE .multiplier_cte. multiple times, but with different definitions'):
        to_sql(dialect=dialect, model=update_model)


def test_model_duplicate_with_id(dialect):
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
    sql1 = to_sql(dialect=dialect, model=model)
    # Now change the model, so that the 'multiplier' parameter is different for the different Multiplier
    # instances, and thus the 'multiplier_cte_{{id}}' has different sql. This should still work, as the
    # CTE-names don't collide
    update_model = model.set((), multiplier=3)
    sql2 = to_sql(dialect=dialect, model=update_model)
    assert sql1 != sql2


def test_code_deduplication_multiple_reference(dialect):
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
    sql = to_sql(dialect=dialect, model=graph)
    assert sql
    assert sql.count('select 1 as val') == 1
    assert sql.count('one.val + two.val') == 2


def test_code_deduplication_multiple_instances(dialect):
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
    sql = to_sql(dialect=dialect, model=graph)
    assert sql
    assert sql.count('select 1 as val') == 1
    assert sql.count('one.val + two.val') == 2


# be explicit as this is also a performance test: max 1 sec runtime.
# But conftests.py should already define limit for all unittests.
@pytest.mark.timeout(1)
def test_code_deduplication_multiple_reference_many_paths(dialect):
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
    sql = to_sql(dialect=dialect, model=graph)
    assert sql
    assert sql.count('select 1 as val') == 1
    assert sql.count('one.val + two.val') == depth
    assert len(sql) < 6000  # If for any database we generate sql bigger than this, something might be wrong
