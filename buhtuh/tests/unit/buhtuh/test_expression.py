"""
Copyright 2021 Objectiv B.V.
"""
import pytest

from buhtuh.expression import RawToken, ColumnReferenceToken, expression_to_sql, quote_string, \
    quote_identifier, StringValueToken, Expression
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
    result = Expression.construct('cast({} as text)', df.a)
    assert result == Expression([
        RawToken('cast('),
        ColumnReferenceToken('a'),
        RawToken(' as text)')
    ])
    assert expression_to_sql(result) == 'cast("a" as text)'

    result = Expression.construct('{}, {}, {}', df.a, Expression.raw('test'), df.b)
    assert expression_to_sql(result) == '"a", test, "b"'


def test_column_reference():
    expr = Expression.column_reference('city')
    assert expr == Expression([ColumnReferenceToken('city')])
    assert expression_to_sql(expr) == '"city"'
    assert expression_to_sql(expr, '') == '"city"'
    assert expression_to_sql(expr, 'tab') == '"tab"."city"'


def test_string():
    expr = Expression.string_value('a string')
    assert expr == Expression([StringValueToken('a string')])
    assert expression_to_sql(expr) == "'a string'"
    assert expression_to_sql(expr, 'tab') == "'a string'"
    expr = Expression.string_value('a string \' with quotes\'\' in it')
    assert expr == Expression([StringValueToken('a string \' with quotes\'\' in it')])
    assert expression_to_sql(expr) == "'a string '' with quotes'''' in it'"


def test_combined():
    df = get_fake_df(['i'], ['duration', 'irrelevant'])
    expr1 = Expression.column_reference('year')
    expr2 = Expression.construct('cast({} as bigint)', df.duration)
    expr_sum = Expression.construct('{} + {}', expr1, expr2)
    expr_str = Expression.construct('"Finished in " || cast(({}) as text) || " or later."', expr_sum)
    assert expression_to_sql(expr_str) == \
           '"Finished in " || cast(("year" + cast("duration" as bigint)) as text) || " or later."'
    assert expression_to_sql(expr_str, 'table_name') == \
           '"Finished in " || cast(("table_name"."year" + cast("table_name"."duration" as bigint)) as text) || " or later."'


def test_quote_string():
    assert quote_string("test") == "'test'"
    assert quote_string("te'st") == "'te''st'"
    assert quote_string("'te''st'") == "'''te''''st'''"


def test_quote_identifier():
    assert quote_identifier('test') == '"test"'
    assert quote_identifier('te"st') == '"te""st"'
    assert quote_identifier('"te""st"') == "\"\"\"te\"\"\"\"st\"\"\""
