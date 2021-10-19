"""
Copyright 2021 Objectiv B.V.
"""
from buhtuh import Expression
from buhtuh.expression import TextToken, TableToken


def test_construct():
    assert Expression.construct('') == Expression([])
    assert Expression.construct('test') == Expression([TextToken('test')])

    result = Expression.construct('cast({} as text)', Expression.construct('123'))
    assert result == Expression([
        TextToken('cast('),
        TextToken('123'),
        TextToken(' as text)')
    ])
    assert result.to_string() == 'cast(123 as text)'


def test_table_field():
    expr = Expression.construct_table_field('city')
    assert expr == Expression([TableToken(), TextToken('"city"')])
    assert expr.to_string('') == '"city"'
    assert expr.to_string('tab') == '"tab"."city"'


def test_combined():
    expr1 = Expression.construct_table_field('year')
    expr2 = Expression.construct_table_field('duration')
    expr2 = Expression.construct('cast({} as bigint)', expr2)
    expr_sum = Expression.construct('{} + {}', expr1, expr2)
    expr_str = Expression.construct('"Finished in " || cast(({}) as text) || " or later."', expr_sum)
    assert expr_str.to_string() == \
           '"Finished in " || cast(("year" + cast("duration" as bigint)) as text) || " or later."'
    assert expr_str.to_string('table_name') == \
           '"Finished in " || cast(("table_name"."year" + cast("table_name"."duration" as bigint)) as text) || " or later."'
