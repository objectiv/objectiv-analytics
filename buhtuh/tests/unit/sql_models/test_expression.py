"""
Copyright 2021 Objectiv B.V.
"""
import pytest

from sql_models.expression import RawToken, ColumnReferenceToken, expression_to_sql, quote_string, \
    quote_identifier, StringValueToken, Expression
from buhtuh.expression import Expression as BTExpression

from tests.unit.buhtuh.util import get_fake_df


def test_construct():
    assert Expression.construct('') == Expression([])
    assert Expression.construct('test') == Expression([RawToken('test')])
    expr = Expression.construct('test')
    assert Expression.construct('test{}', expr) == Expression([RawToken('test'), RawToken('test')])
    assert Expression.construct('{}test', expr) == Expression([RawToken('test'), RawToken('test')])
    assert Expression.construct('te{}st', expr) == \
           Expression([RawToken('te'), RawToken('test'), RawToken('st')])

    result = Expression.construct('cast({} as text)', Expression.construct('123'))
    assert result == Expression([
        RawToken('cast('),
        RawToken('123'),
        RawToken(' as text)')
    ])
    assert expression_to_sql(result) == 'cast(123 as text)'

    with pytest.raises(ValueError):
        Expression.construct('{}')

    with pytest.raises(ValueError):
        Expression.construct('{}', expr, expr)


def test_construct_series():
    df = get_fake_df(['i'], ['a', 'b'])
    result = BTExpression.construct('cast({} as text)', df.a)
    assert result == BTExpression([
        RawToken('cast('),
        ColumnReferenceToken('a'),
        RawToken(' as text)')
    ])
    assert expression_to_sql(result.resolve_column_references()) == 'cast("a" as text)'

    result = BTExpression.construct('{}, {}, {}', df.a, BTExpression.raw('test'), df.b)
    assert expression_to_sql(result.resolve_column_references()) == '"a", test, "b"'


def test_column_reference():
    expr = Expression.column_reference('city')
    assert expr == Expression([ColumnReferenceToken('city')])
    assert expression_to_sql(expr.resolve_column_references()) == '"city"'
    assert expression_to_sql(expr.resolve_column_references('')) == '"city"'
    assert expression_to_sql(expr.resolve_column_references('tab')) == '"tab"."city"'


def test_string():
    expr = Expression.string_value('a string')
    assert expr == Expression([StringValueToken('a string')])
    assert expression_to_sql(expr.resolve_column_references()) == "'a string'"
    assert expression_to_sql(expr.resolve_column_references('tab')) == "'a string'"
    expr = Expression.string_value('a string \' with quotes\'\' in it')
    assert expr == Expression([StringValueToken('a string \' with quotes\'\' in it')])
    assert expression_to_sql(expr.resolve_column_references()) == "'a string '' with quotes'''' in it'"


def test_combined():
    df = get_fake_df(['i'], ['duration', 'irrelevant'])
    expr1 = Expression.column_reference('year')
    expr2 = BTExpression.construct('cast({} as bigint)', df.duration)
    expr_sum = Expression.construct('{} + {}', expr1, expr2)
    expr_str = Expression.construct('"Finished in " || cast(({}) as text) || " or later."', expr_sum)
    assert expression_to_sql(expr_str.resolve_column_references()) == \
           '"Finished in " || cast(("year" + cast("duration" as bigint)) as text) || " or later."'
    assert expression_to_sql(expr_str.resolve_column_references('table_name')) == \
           '"Finished in " || cast(("table_name"."year" + cast("table_name"."duration" as bigint)) as text) || " or later."'


def test_quote_string():
    assert quote_string("test") == "'test'"
    assert quote_string("te'st") == "'te''st'"
    assert quote_string("'te''st'") == "'''te''''st'''"


def test_quote_identifier():
    assert quote_identifier('test') == '"test"'
    assert quote_identifier('te"st') == '"te""st"'
    assert quote_identifier('"te""st"') == "\"\"\"te\"\"\"\"st\"\"\""