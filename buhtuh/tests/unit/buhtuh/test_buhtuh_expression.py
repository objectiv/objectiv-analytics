from tests.unit.buhtuh.util import get_fake_df

from sql_models.expression import RawToken, ColumnReferenceToken, expression_to_sql
from buhtuh.expression import Expression


def test_construct_series():
    df = get_fake_df(['i'], ['a', 'b'])
    result = Expression.construct('cast({} as text)', df.a)
    assert result == Expression([
        RawToken('cast('),
        ColumnReferenceToken('a'),
        RawToken(' as text)')
    ])
    assert expression_to_sql(result.resolve_column_references()) == 'cast("a" as text)'

    result = Expression.construct('{}, {}, {}', df.a, Expression.raw('test'), df.b)
    assert expression_to_sql(result.resolve_column_references()) == '"a", test, "b"'


def test_combined():
    df = get_fake_df(['i'], ['duration', 'irrelevant'])
    expr1 = Expression.column_reference('year')
    expr2 = Expression.construct('cast({} as bigint)', df.duration)
    expr_sum = Expression.construct('{} + {}', expr1, expr2)
    expr_str = Expression.construct('"Finished in " || cast(({}) as text) || " or later."', expr_sum)
    assert expression_to_sql(expr_str.resolve_column_references()) == \
           '"Finished in " || cast(("year" + cast("duration" as bigint)) as text) || " or later."'
    assert expression_to_sql(expr_str.resolve_column_references('table_name')) == \
           '"Finished in " || cast(("table_name"."year" + cast("table_name"."duration" as bigint)) as text) || " or later."'
