"""
Copyright 2021 Objectiv B.V.
"""
import pytest

from bach.expression import RawToken, ColumnReferenceToken, StringValueToken, Expression, \
    ConstValueExpression, AggregateFunctionExpression, WindowFunctionExpression, SingleValueExpression, \
    NonAtomicExpression, TableColumnReferenceToken
from sql_models.util import is_bigquery
from tests.unit.bach.util import get_fake_df


def test_construct(dialect):
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
    assert result.to_sql(dialect) == 'cast(123 as text)'

    with pytest.raises(ValueError):
        Expression.construct('{}')

    with pytest.raises(ValueError):
        Expression.construct('{}', expr, expr)


def test_construct_series(dialect):
    df = get_fake_df(dialect, ['i'], ['a', 'b'])
    result1 = Expression.construct('cast({} as text)', df.a)
    assert result1 == Expression([
        RawToken('cast('),
        Expression([ColumnReferenceToken('a')]),
        RawToken(' as text)')
    ])
    result2 = Expression.construct('{}, {}, {}', df.a, Expression.raw('test'), df.b)

    if not is_bigquery(dialect):  # 'normal' path
        assert result1.to_sql(dialect) == 'cast("a" as text)'
        assert result2.to_sql(dialect) == '"a", test, "b"'
    else:
        assert result1.to_sql(dialect) == 'cast(`a` as text)'
        assert result2.to_sql(dialect) == '`a`, test, `b`'


def test_column_reference(dialect):
    expr = Expression.column_reference('city')
    assert expr == Expression([ColumnReferenceToken('city')])
    if not is_bigquery(dialect):  # 'normal' path
        assert expr.to_sql(dialect) == '"city"'
        assert expr.to_sql(dialect, '') == '"city"'
        assert expr.to_sql(dialect, 'tab') == '"tab"."city"'
    else:
        assert expr.to_sql(dialect) == '`city`'
        assert expr.to_sql(dialect, '') == '`city`'
        assert expr.to_sql(dialect, 'tab') == '`tab`.`city`'


def test_string(dialect):
    expr = Expression.string_value('a string')
    assert expr == Expression([StringValueToken('a string')])

    if is_bigquery(dialect):
        assert expr.to_sql(dialect) == '"""a string"""'
        assert expr.to_sql(dialect, 'tab') == '"""a string"""'
    else:
        assert expr.to_sql(dialect) == "'a string'"
        assert expr.to_sql(dialect, 'tab') == "'a string'"

    expr = Expression.string_value('a string \' with quotes\'\' in it')
    assert expr == Expression([StringValueToken('a string \' with quotes\'\' in it')])

    if is_bigquery(dialect):
        assert expr.to_sql(dialect) == '"""a string \' with quotes\'\' in it"""'
    else:
        assert expr.to_sql(dialect) == "'a string '' with quotes'''' in it'"


def test_combined(dialect):
    df = get_fake_df(dialect, ['i'], ['duration', 'irrelevant'])
    expr1 = Expression.column_reference('year')
    expr2 = Expression.construct('cast({} as bigint)', df.duration)
    expr_sum = Expression.construct('{} + {}', expr1, expr2)
    expr_str = Expression.construct("'Finished in ' || cast(({}) as text) || ' or later.'", expr_sum)
    expected_sql = '\'Finished in \' || cast(("year" + cast("duration" as bigint)) as text) || \' or later.\''
    expected_sql_table = '\'Finished in \' || cast(("table_name"."year" + cast("table_name"."duration" as bigint)) as text) || \' or later.\''
    if is_bigquery(dialect):
        expected_sql = expected_sql.replace('"', '`')
        expected_sql_table = expected_sql_table.replace('"', '`')
    assert expr_str.to_sql(dialect) == expected_sql
    assert expr_str.to_sql(dialect, 'table_name') == expected_sql_table


def test_non_atomic(dialect):
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

    assert Expression.construct('{} & {}', e1, e2).to_sql(dialect) == 'a or ~c & ~a or b'
    assert NonAtomicExpression.construct('{} & {}', e1, e2).to_sql(dialect) == 'a or ~c & ~a or b'
    assert Expression.construct('{} & {}', na1, na2).to_sql(dialect) == '(a or ~c) & (~a or b)'
    assert NonAtomicExpression.construct('{} & {}', na1, na2).to_sql(dialect) == '(a or ~c) & (~a or b)'
    assert Expression.construct('{} & {}', e1, na2).to_sql(dialect) == 'a or ~c & (~a or b)'
    assert NonAtomicExpression.construct('{} & {}', e1, na2).to_sql(dialect) == 'a or ~c & (~a or b)'
    assert Expression.construct('{} & {}', na1, e2).to_sql(dialect) == '(a or ~c) & ~a or b'
    assert NonAtomicExpression.construct('{} & {}', na1, e2).to_sql(dialect) == '(a or ~c) & ~a or b'


def test_is_constant(dialect):
    df = get_fake_df(dialect, ['i'], ['duration', 'irrelevant'])
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


def test_is_single_value(dialect):
    df = get_fake_df(dialect, ['i'], ['duration', 'irrelevant'])
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


def test_table_column_reference(dialect) -> None:
    expr = Expression.table_column_reference('random', 'city')
    assert expr == Expression([TableColumnReferenceToken('random', 'city')])
    if not is_bigquery(dialect):  # 'normal' path
        assert expr.to_sql(dialect) == '"random"."city"'
        assert expr.to_sql(dialect, '') == '"random"."city"'
        assert expr.to_sql(dialect, 'tab') == '"random"."city"'
    else:
        assert expr.to_sql(dialect) == '`random`.`city`'
        assert expr.to_sql(dialect, '') == '`random`.`city`'
        assert expr.to_sql(dialect, 'tab') == '`random`.`city`'


@pytest.mark.db_independent
def test_remove_table_column_references() -> None:
    expr = Expression.table_column_reference('random', 'city')

    result_table_name, result_column_name, result_expr = expr.remove_table_column_references()
    assert result_table_name == 'random'
    assert result_column_name == 'city'
    assert result_expr == Expression.column_reference('city')

    expr2 = Expression.column_reference('city')
    result_table_name, result_column_name, result_expr = expr2.remove_table_column_references()
    assert result_table_name == ''
    assert result_column_name == ''
    assert result_expr == Expression.column_reference('city')


@pytest.mark.db_independent
def test_remove_table_column_references_error() -> None:
    expr = Expression(
        [Expression.table_column_reference('random', 'city'), Expression.table_column_reference('random2', 'city')],
    )

    with pytest.raises(Exception, match=r'different table references are not allowed.'):
        expr.remove_table_column_references()


@pytest.mark.db_independent
def test_has_table_column_reference() -> None:
    expr = Expression.table_column_reference('random', 'city')
    assert expr.has_table_column_references

    expr2 = Expression.column_reference('city')
    assert not expr2.has_table_column_references
