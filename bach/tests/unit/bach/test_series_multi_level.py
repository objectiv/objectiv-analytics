import pytest

from bach import SeriesNumericInterval, SeriesFloat64, SeriesString, Series
from bach.expression import Expression, MultiLevelExpression
from sql_models.util import is_postgres, is_bigquery
from tests.unit.bach.util import get_fake_df_test_data


def test_series_numeric_interval_levels_dtypes() -> None:
    supported_dtypes = SeriesNumericInterval.get_supported_level_dtypes()
    assert 'lower' in supported_dtypes
    assert supported_dtypes['lower'] == ('float64', 'int64')

    assert 'upper' in supported_dtypes
    assert supported_dtypes['upper'] == ('float64', 'int64')

    assert 'bounds' in supported_dtypes
    assert supported_dtypes['bounds'] == ('string', )


def test_series_numeric_interval_get_instance(dialect) -> None:
    bt = get_fake_df_test_data(dialect)
    params = {
        'engine': bt.engine,
        'base_node': bt.base_node,
        'expression': Expression.construct(''),
        'group_by': None,
        'index': {},
        'order_by': [],
        'name': 'interval',
        'instance_dtype': 'numeric_interval'
    }
    with pytest.raises(ValueError, match=r'base node must include all referenced'):
        SeriesNumericInterval.get_class_instance(**params)

    bt['_interval_lower'] = bt['inhabitants']
    bt['_interval_upper'] = bt['inhabitants']
    bt['_interval_bounds'] = '[]'
    bt = bt.materialize()
    params['base_node'] = bt.base_node
    numeric_interval = SeriesNumericInterval.get_class_instance(**params)

    assert isinstance(numeric_interval.lower, SeriesFloat64)
    assert numeric_interval.lower.name == '_interval_lower'

    assert isinstance(numeric_interval.upper, SeriesFloat64)
    assert numeric_interval.upper.name == '_interval_upper'

    assert isinstance(numeric_interval.bounds, SeriesString)
    assert numeric_interval.bounds.name == '_interval_bounds'


def test_series_numeric_interval_from_value(dialect) -> None:
    bt = get_fake_df_test_data(dialect)

    with pytest.raises(ValueError, match=r'value should contain mapping'):
        SeriesNumericInterval.from_value(
            base=bt,
            value={'lower': 0},
            name='num_interval',
        )

    result = SeriesNumericInterval.from_value(
        base=bt,
        value={
            'lower': 0,
            'upper': 1,
            'bounds': '(]'
        },
        name='num_interval',
    )

    assert result.lower.name == f'_num_interval_lower'
    assert '0' in result.lower.expression.to_sql(dialect)

    assert result.upper.name == f'_num_interval_upper'
    assert '1' in result.upper.expression.to_sql(dialect)

    assert result.bounds.name == f'_num_interval_bounds'
    assert '(]' in result.bounds.expression.to_sql(dialect)


def test_series_numeric_interval_copy_override(dialect) -> None:
    bt = get_fake_df_test_data(dialect)[['inhabitants']].agg(['min', 'max'])
    bt = bt.materialize()

    numeric_interval = SeriesNumericInterval.from_value(
        base=bt,
        value={
            'lower': bt['inhabitants_min'],
            'upper': bt['inhabitants_max'],
            'bounds': '[]'
        },
        name='num_interval',
    )

    new_name = 'num_interval_copy'
    result = numeric_interval.copy_override(name='num_interval_copy', bounds='[)')
    assert result.lower.name == f'_{new_name}_lower'
    assert 'inhabitants_min' in result.lower.expression.to_sql(dialect)

    assert result.upper.name == f'_{new_name}_upper'
    assert 'inhabitants_max' in result.upper.expression.to_sql(dialect)

    assert result.bounds.name == f'_{new_name}_bounds'
    assert '[)' in result.bounds.expression.to_sql(dialect)


def test_series_numeric_interval_parse_level_value(dialect) -> None:
    bt = get_fake_df_test_data(dialect)
    numeric_interval = SeriesNumericInterval.from_value(
        base=bt,
        value={
            'lower': 0,
            'upper': 1,
            'bounds': '(]'
        },
        name='num_interval',
    )

    with pytest.raises(ValueError, match=r'is not a supported level'):
        numeric_interval._parse_level_value(level_name='random', value=1)

    with pytest.raises(ValueError, match=r'level should be any of'):
        numeric_interval._parse_level_value(level_name='upper', value='random')

    result = numeric_interval._parse_level_value(level_name='upper', value=bt['inhabitants'])
    assert result.name == '_num_interval_upper'
    assert 'inhabitants' in result.expression.to_sql(dialect)


def test_series_numeric_expression(dialect) -> None:
    inhabitants = get_fake_df_test_data(dialect)['inhabitants']
    numeric_interval = SeriesNumericInterval.from_value(
        base=inhabitants,
        value={
            'lower': inhabitants,
            'upper': inhabitants,
            'bounds': '[]'
        },
        name='num_interval',
    )
    assert isinstance(numeric_interval.expression, MultiLevelExpression)

    sql_result = numeric_interval.expression.to_sql(dialect, table_name='table')

    if is_postgres(dialect):
        assert sql_result == '"table"."inhabitants","table"."inhabitants",\'[]\''
    elif is_bigquery(dialect):
        assert sql_result == '`table`.`inhabitants`,`table`.`inhabitants`,"""[]"""'
    else:
        raise Exception()


def test_series_numeric_interval_get_column_expression(dialect) -> None:
    bt = get_fake_df_test_data(dialect)
    numeric_interval = SeriesNumericInterval.from_value(
        base=bt,
        value={
            'lower': 0,
            'upper': 1,
            'bounds': '(]'
        },
        name='num_interval',
    )

    result = numeric_interval.get_column_expression().to_sql(dialect)
    if is_postgres(dialect):
        assert result == (
            'CASE WHEN (((((cast(0 as bigint) is not null)) AND ((cast(1 as bigint) is not null)))) '
            'AND ((\'(]\' is not null))) THEN numrange(cast(cast(0 as bigint) as numeric), '
            'cast(cast(1 as bigint) as numeric), \'(]\') ELSE NULL END as "num_interval"'
        )
    elif is_bigquery(dialect):
        assert result == (
            'CASE WHEN (((((0 is not null)) AND ((1 is not null)))) AND (("""(]""" is not null))) '
            'THEN struct(0 as lower, 1 as upper, """(]""" as bounds) ELSE NULL END as `num_interval`'
        )
    else:
        raise Exception()


def test_series_numeric_interval_as_index_unstack(dialect) -> None:
    bt = get_fake_df_test_data(dialect)
    bt['num_interval'] = SeriesNumericInterval.from_value(
        base=bt,
        value={
            'lower': 0,
            'upper': 1,
            'bounds': '(]'
        },
        name='num_interval',
    )

    bt = bt.set_index('num_interval', append=True)
    with pytest.raises(IndexError, match=r'cannot be unstacked, since it is a MultiLevel series'):
        bt['inhabitants'].unstack()


def test_series_numeric_interval_arithmetic_operations(dialect) -> None:
    bt = get_fake_df_test_data(dialect)
    bt['num_interval'] = SeriesNumericInterval.from_value(
        base=bt,
        value={
            'lower': 0,
            'upper': 1,
            'bounds': '(]'
        },
        name='num_interval',
    )

    with pytest.raises(TypeError, match=r'not supported'):
        bt['num_interval'] + 1

    with pytest.raises(TypeError, match=r'not supported'):
        bt['num_interval'] + bt['num_interval']


def test_series_numeric_interval_as_independent_subquery(dialect) -> None:
    bt = get_fake_df_test_data(dialect)
    bt['num_interval'] = SeriesNumericInterval.from_value(
        base=bt,
        value={
            'lower': 0,
            'upper': 1,
            'bounds': '(]'
        },
        name='num_interval',
    )
    with pytest.raises(NotImplementedError, match=r'cannot be used as independent subquery'):
        Series.as_independent_subquery(bt['num_interval'])

    with pytest.raises(NotImplementedError, match=r'cannot be used as independent subquery'):
        bt['num_interval'].exists()

    with pytest.raises(NotImplementedError, match=r'cannot be used as independent subquery'):
        bt['num_interval'].any_value()

    with pytest.raises(NotImplementedError, match=r'cannot be used as independent subquery'):
        bt['num_interval'].all_values()

    with pytest.raises(NotImplementedError, match=r'cannot be used as independent subquery'):
        bt['inhabitants'].isin(bt['num_interval'])


def test_series_numeric_interval_equals(dialect) -> None:
    bt = get_fake_df_test_data(dialect)
    bt['num_interval'] = SeriesNumericInterval.from_value(
        base=bt,
        value={
            'lower': 0,
            'upper': 1,
            'bounds': '(]'
        },
        name='num_interval',
    )
    bt['num_interval_2'] = SeriesNumericInterval.from_value(
        base=bt,
        value={
            'lower': 0,
            'upper': 3,
            'bounds': '(]'
        },
        name='num_interval_2',
    )

    assert bt['num_interval'].equals(bt['num_interval'])
    assert not bt['num_interval'].equals(bt['num_interval_2'])
    assert not bt['num_interval'].equals(bt['inhabitants'])


def test_series_numeric_interval_isnull(dialect) -> None:
    bt = get_fake_df_test_data(dialect)
    bt['num_interval'] = SeriesNumericInterval.from_value(
        base=bt,
        value={
            'lower': 0,
            'upper': 1,
            'bounds': '(]'
        },
        name='num_interval',
    )
    expected = (
        bt['num_interval'].lower.isnull() & bt['num_interval'].upper.isnull() & bt['num_interval'].bounds.isnull()
    )
    result = bt['num_interval'].isnull()
    assert result.equals(expected)


def test_series_numeric_interval_notnull(dialect) -> None:
    bt = get_fake_df_test_data(dialect)
    bt['num_interval'] = SeriesNumericInterval.from_value(
        base=bt,
        value={
            'lower': 0,
            'upper': 1,
            'bounds': '(]'
        },
        name='num_interval',
    )
    expected = (
        bt['num_interval'].lower.notnull() & bt['num_interval'].upper.notnull() & bt['num_interval'].bounds.notnull()
    )
    result = bt['num_interval'].notnull()
    assert result.equals(expected)


def test_series_numeric_interval_fillna(dialect) -> None:
    bt = get_fake_df_test_data(dialect)[['inhabitants']]
    bt['num_interval'] = SeriesNumericInterval.from_value(
        base=bt,
        value={
            'lower': bt['inhabitants'],
            'upper': bt['inhabitants'],
            'bounds': '(]'
        },
        name='num_interval',
    )

    expected = bt['num_interval'].lower.fillna(0)
    result = bt['num_interval'].fillna({'lower': 0})
    assert result.lower.equals(expected)
