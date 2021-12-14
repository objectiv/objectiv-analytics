"""
Copyright 2021 Objectiv B.V.
"""
import pytest

from bach.expression import RawToken, ColumnReferenceToken, StringValueToken, Expression, \
    ConstValueExpression, AggregateFunctionExpression, WindowFunctionExpression, SingleValueExpression, \
    NonAtomicExpression
from tests.unit.bach.util import get_fake_df


def test_construct():
    assert Expression.construct('') == Expression([])
    assert Expression.construct('test') == Expression([RawToken('test')])
    expr = Expression.construct('test')
    assert Expression.construct('test{}', expr) == \
           Expression([RawToken('test'), Expression([RawToken('test')])])
    assert Expression.construct('{}test', expr) == \
           Expression([Expression([RawToken('test')]), RawToken('test')])
    assert Expression.construct('te{}st', expr) == \
           Expression([RawToken('te'), Expression([RawToken('test')]), RawToken('st')])

    result = Expression.construct('cast({} as text)', Expression.construct('123'))
    assert result == Expression([
        RawToken('cast('),
        Expression([RawToken('123')]),
        RawToken(' as text)')
    ])
    assert result.to_sql() == 'cast(123 as text)'

    with pytest.raises(ValueError):
        Expression.construct('{}')

    with pytest.raises(ValueError):
        Expression.construct('{}', expr, expr)


def test_construct_series():
    df = get_fake_df(['i'], ['a', 'b'])
    result = Expression.construct('cast({} as text)', df.a)
    assert result == Expression([
        RawToken('cast('),
        Expression([ColumnReferenceToken('a')]),
        RawToken(' as text)')
    ])
    assert result.to_sql() == 'cast("a" as text)'

    result = Expression.construct('{}, {}, {}', df.a, Expression.raw('test'), df.b)
    assert result.to_sql() == '"a", test, "b"'


def test_column_reference():
    expr = Expression.column_reference('city')
    assert expr == Expression([ColumnReferenceToken('city')])
    assert expr.to_sql() == '"city"'
    assert expr.to_sql('') == '"city"'
    assert expr.to_sql('tab') == '"tab"."city"'


def test_string():
    expr = Expression.string_value('a string')
    assert expr == Expression([StringValueToken('a string')])
    assert expr.to_sql() == "'a string'"
    assert expr.to_sql('tab') == "'a string'"
    expr = Expression.string_value('a string \' with quotes\'\' in it')
    assert expr == Expression([StringValueToken('a string \' with quotes\'\' in it')])
    assert expr.to_sql() == "'a string '' with quotes'''' in it'"


def test_combined():
    df = get_fake_df(['i'], ['duration', 'irrelevant'])
    expr1 = Expression.column_reference('year')
    expr2 = Expression.construct('cast({} as bigint)', df.duration)
    expr_sum = Expression.construct('{} + {}', expr1, expr2)
    expr_str = Expression.construct('"Finished in " || cast(({}) as text) || " or later."', expr_sum)
    assert expr_str.to_sql() == \
           '"Finished in " || cast(("year" + cast("duration" as bigint)) as text) || " or later."'
    assert expr_str.to_sql('table_name') == \
           '"Finished in " || cast(("table_name"."year" + cast("table_name"."duration" as bigint)) as text) || " or later."'


def test_non_atomic():
    assert Expression.construct('') == Expression([])
    assert NonAtomicExpression.construct('') == NonAtomicExpression([])
    e1 = Expression.construct('a or ~c')
    e2 = Expression.construct('~a or b')
    assert e1 == Expression([RawToken('a or ~c')])
    assert e2 == Expression([RawToken('~a or b')])
    na1 = NonAtomicExpression.construct('a or ~c')
    na2 = NonAtomicExpression.construct('~a or b')
    assert na1 == NonAtomicExpression([RawToken('a or ~c')])
    assert na2 == NonAtomicExpression([RawToken('~a or b')])

    assert Expression.construct('{} & {}', e1, e2).to_sql() == 'a or ~c & ~a or b'
    assert NonAtomicExpression.construct('{} & {}', e1, e2).to_sql() == 'a or ~c & ~a or b'
    assert Expression.construct('{} & {}', na1, na2).to_sql() == '(a or ~c) & (~a or b)'
    assert NonAtomicExpression.construct('{} & {}', na1, na2).to_sql() == '(a or ~c) & (~a or b)'
    assert Expression.construct('{} & {}', e1, na2).to_sql() == 'a or ~c & (~a or b)'
    assert NonAtomicExpression.construct('{} & {}', e1, na2).to_sql() == 'a or ~c & (~a or b)'
    assert Expression.construct('{} & {}', na1, e2).to_sql() == '(a or ~c) & ~a or b'
    assert NonAtomicExpression.construct('{} & {}', na1, e2).to_sql() == '(a or ~c) & ~a or b'


def test_is_constant():
    df = get_fake_df(['i'], ['duration', 'irrelevant'])
    notconst1 = Expression.column_reference('year')
    notconst2 = Expression.construct('cast({} as bigint)', df.duration)
    assert not notconst1.is_constant
    assert not notconst2.is_constant

    # all subexpression should be constant, but at least on should exist.
    assert not Expression.construct('no subexpressions, only a token').is_constant
    # a token-only ConstValueExpression is constant
    assert ConstValueExpression.construct('no idea what this is ').is_constant

    notconst3 = Expression.construct('{} + {}', notconst1, notconst2)
    notconst4 = Expression.construct('"Finished in " || cast(({}) as text) || " or later."', notconst3)
    assert not notconst3.is_constant
    assert not notconst4.is_constant

    const1 = ConstValueExpression([RawToken('5')])
    const2 = ConstValueExpression([RawToken('10')])
    assert const1.is_constant
    assert const2.is_constant

    const3 = Expression.construct('func({})', const1)
    const4 = Expression.construct('{} + {}', const1, const2)
    assert const3.is_constant
    assert const4.is_constant

    assert Expression.construct('{} + ({})', const3, const4).is_constant
    assert not Expression.construct('{} + ({})', notconst1, const4).is_constant
    assert not Expression.construct('{} + ({})', const1, notconst4).is_constant
    assert not Expression.construct('{} + ({})', notconst1, notconst4).is_constant

    # Aggregation functions are never constant
    assert not AggregateFunctionExpression.construct('agg({})', const1).is_constant
    assert not AggregateFunctionExpression.construct('agg({})', notconst1).is_constant
    assert not AggregateFunctionExpression.construct('agg({}, {}, {})', const1, const2, const3).is_constant

    # Window functions are never constant
    assert not WindowFunctionExpression.construct('agg({})', const1).is_constant
    assert not WindowFunctionExpression.construct('agg({})', notconst1).is_constant
    assert not WindowFunctionExpression.construct('agg({}, {}, {})', const1, const2, const3).is_constant


def test_is_single_value():
    df = get_fake_df(['i'], ['duration', 'irrelevant'])
    notsingle1 = Expression.column_reference('year')
    notsingle2 = Expression.construct('cast({} as bigint)', df.duration)
    assert not notsingle1.is_single_value
    assert not notsingle2.is_single_value

    # all subexpression should be single, but at least on should exist.
    assert not Expression.construct('no subexpressions, only a token').is_single_value
    # a token-only ConstValueExpression is constant
    assert SingleValueExpression.construct('no idea what this is ').is_single_value

    notsingle3 = Expression.construct('{} + {}', notsingle1, notsingle2)
    notsingle4 = Expression.construct('"Finished in " || cast(({}) as text) || " or later."', notsingle3)
    assert not notsingle3.is_single_value
    assert not notsingle4.is_single_value

    single1 = ConstValueExpression([RawToken('5')])
    single2 = ConstValueExpression([RawToken('10')])
    assert single1.is_single_value
    assert single2.is_single_value

    single3 = Expression.construct('func({})', single1)
    single4 = Expression.construct('{} + {}', single1, single2)
    assert single3.is_single_value
    assert single4.is_single_value

    # these examples aren't great, but let's test this anyway
    assert Expression.construct('{} + ({})', single3, single4).is_single_value
    assert not Expression.construct('{} + ({})', notsingle1, single4).is_single_value
    assert not Expression.construct('{} + ({})', single1, notsingle4).is_single_value
    assert not Expression.construct('{} + ({})', notsingle1, notsingle4).is_single_value

    # Aggregation single values remain single
    assert AggregateFunctionExpression.construct('agg({})', single1).is_single_value
    # Aggregated non-single values don't automatically become single.
    assert not AggregateFunctionExpression.construct('agg({})', notsingle1).is_single_value
    # multi single, still single
    assert AggregateFunctionExpression.construct('agg({}, {}, {})', single1, single2, single3).is_single_value
    # one not single, end of single
    assert not AggregateFunctionExpression.construct('agg({}, {}, {})',
                                                     notsingle1, single2, single3).is_single_value
    assert not AggregateFunctionExpression.construct('agg({}, {}, {})',
                                                     single1, notsingle2, single3).is_single_value
    assert not AggregateFunctionExpression.construct('agg({}, {}, {})',
                                                     single1, single2, notsingle3).is_single_value
    assert not AggregateFunctionExpression.construct('agg({}, {}, {})',
                                                     notsingle1, notsingle2, notsingle3).is_single_value


