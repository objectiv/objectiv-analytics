"""
Copyright 2021 Objectiv B.V.
"""
from typing import List

import pytest

from bach import get_series_type_from_dtype, SortColumn
from bach.expression import Expression, AggregateFunctionExpression
from bach.partitioning import GroupBy
from bach.sql_model import BachSqlModel
from sql_models.constants import DBDialect
from sql_models.model import CustomSqlModelBuilder
from sql_models.util import DatabaseNotSupportedException
from tests.unit.bach.util import get_fake_df, FakeEngine, FakeSeries


def test_equals(dialect):
    def get_df(index_names: List[str], data_names: List[str]):
        return get_fake_df(dialect=dialect, index_names=index_names, data_names=data_names)

    left = get_df(['a'], ['b', 'c'])
    right = get_df(['a'], ['b', 'c'])

    result = left['b'].equals(left['b'])
    # assert result is a boolean (for e.g.  '==') this is not the case
    assert result is True
    assert left['b'].equals(left['b'])
    assert left['b'].equals(right['b'])
    assert not left['b'].equals(left['c'])
    assert not left['b'].equals(right['c'])

    left = get_df(['a', 'x'], ['b', 'c'])
    right = get_df(['a'], ['b', 'c'])
    assert left['b'].equals(left['b'])
    assert not left['b'].equals(right['b'])
    assert not left['b'].equals(left['c'])
    assert not left['b'].equals(right['c'])

    # different order in the index
    left = get_df(['a', 'b'], ['c'])
    right = get_df(['b', 'a'], ['c'])
    assert not left['c'].equals(right['c'])

    engine = left.engine
    engine_other = FakeEngine(dialect=engine.dialect, url='sql://some_other_string')

    int_type = get_series_type_from_dtype('int64')
    float_type = get_series_type_from_dtype('float64')

    expr_test = Expression.construct('test')
    expr_other = Expression.construct('test::text')

    sleft = int_type(engine=engine, base_node=None, index={}, name='test',
                     expression=expr_test, group_by=None, order_by=[],
                     instance_dtype='int64')
    sright = int_type(engine=engine, base_node=None, index={}, name='test',
                      expression=expr_test, group_by=None, order_by=[],
                      instance_dtype='int64')
    assert sleft.equals(sright)

    # different expression
    sright = int_type(engine=engine, base_node=None, index={}, name='test',
                      expression=expr_other, group_by=None, order_by=[],
                      instance_dtype='int64')
    assert not sleft.equals(sright)

    # different name
    sright = int_type(engine=engine, base_node=None, index={}, name='test_2',
                      expression=expr_test, group_by=None, order_by=[],
                      instance_dtype='int64')
    assert not sleft.equals(sright)

    # different base_node
    sright = int_type(engine=engine, base_node='test', index={}, name='test',
                      expression=expr_test, group_by=None, order_by=[],
                      instance_dtype='int64')
    assert not sleft.equals(sright)

    # different engine
    sright = int_type(engine=engine_other, base_node=None, index={}, name='test',
                      expression=expr_test, group_by=None, order_by=[],
                      instance_dtype='int64')
    assert not sleft.equals(sright)

    # different type
    sright = float_type(engine=engine, base_node=None, index={}, name='test',
                        expression=expr_test, group_by=None, order_by=[],
                        instance_dtype='float64')
    assert not sleft.equals(sright)

    # different group_by
    sright = int_type(engine=engine, base_node=None, index={}, name='test', expression=expr_test,
                      group_by=GroupBy(group_by_columns=[]), order_by=[],
                      instance_dtype='int64')
    assert not sleft.equals(sright)

    # different sorting
    sright = int_type(
        engine=engine, base_node=None, index={}, name='test', expression=expr_test,
        group_by=None, order_by=[SortColumn(expression=expr_test, asc=True)],
        instance_dtype='int64',
    )
    assert not sleft.equals(sright)
    sright = sright.copy_override(order_by=[])
    assert sleft.equals(sright)

    index_series = sleft
    sleft = int_type(engine=engine, base_node=None, index={'a': index_series}, name='test',
                     expression=expr_test, group_by=None, order_by=[],
                     instance_dtype='int64')
    sright = int_type(engine=engine, base_node=None, index={'a': index_series}, name='test',
                      expression=expr_test, group_by=None, order_by=[],
                      instance_dtype='int64')
    assert sleft.equals(sright)
    sright = sright.copy_override(order_by=[SortColumn(expression=expr_test, asc=True)])
    assert not sleft.equals(sright)


@pytest.mark.skip_postgres
def test_equals_instance_dtype(dialect):
    def get_df(index_names: List[str], data_names: List[str]):
        return get_fake_df(dialect=dialect, index_names=index_names, data_names=data_names)

    left = get_df(['a'], ['b', 'c'])
    engine = left.engine
    expr_test = Expression.construct('test')
    dict_type = get_series_type_from_dtype('dict')

    # Currently we only have bigquery types that actual use the instance_dtype. So skip postgres here.
    sleft = dict_type(engine=engine, base_node=None, index={}, name='test',
                      expression=expr_test, group_by=None, order_by=[],
                      instance_dtype={'a': 'int64', 'b': ['bool']})
    sright = sleft.copy_override()
    assert sleft.equals(sright)
    sright = sleft.copy_override(instance_dtype={'a': 'float64', 'b': ['bool']})
    assert not sleft.equals(sright)


def test_init_conditions(dialect, monkeypatch) -> None:
    engine = FakeEngine(dialect=dialect)
    base_node = BachSqlModel.from_sql_model(
        sql_model=CustomSqlModelBuilder('select * from x', name='base')(),
        column_expressions={'a': Expression.column_reference('a')},
    )
    base_params = {
        'engine': engine,
        'base_node': base_node,
        'index': {},
        'name': 'random',
        'expression': Expression.column_reference('a'),
        'group_by': None,
        'sorted_ascending': None,
        'index_sorting': [],
        'instance_dtype': 'int64'
    }

    # invalid dtype error
    with pytest.raises(NotImplementedError, match=r'Non-abstract Series subclasses must override `dtype`'):
        FakeSeries(**base_params)

    monkeypatch.setattr(FakeSeries, name='dtype', value='int64')

    # non-defined supported_db_dtype error
    with pytest.raises(
        NotImplementedError, match=r'Non-abstract Series subclasses must override `supported_db_dtype`'
    ):
        FakeSeries(**base_params)

    monkeypatch.setattr(FakeSeries, name='supported_db_dtype', value={'random': 'random'})
    # unsupported dialect
    with pytest.raises(
        DatabaseNotSupportedException, match=r'is not supported for database dialect'
    ):
        FakeSeries(**base_params)

    monkeypatch.setattr(
        FakeSeries, name='supported_db_dtype', value={DBDialect.from_dialect(dialect): 'random'}
    )
    df = get_fake_df(dialect, ['a'], ['b', 'c'])

    params_w_gb = base_params.copy()
    params_w_gb['group_by'] = GroupBy([df.b])
    # empty index and groupby with index
    with pytest.raises(
        ValueError, match=r'Index Series should be free of pending aggregation'
    ):
        FakeSeries(**params_w_gb)

    params_w_index_n_groupby = params_w_gb.copy()
    params_w_index_n_groupby['index'] = {
        'c': df['c']
    }

    # different index and groupby.index
    with pytest.raises(
        ValueError, match=r'Series and aggregation index do not match'
    ):
        FakeSeries(**params_w_index_n_groupby)

    # no groupby and is aggregated expression
    params_w_agg_expression_wo_gb = base_params.copy()
    params_w_agg_expression_wo_gb['expression'] = AggregateFunctionExpression.construct('random')
    with pytest.raises(
        ValueError, match=r'Expression has an aggregation function set'
    ):
        FakeSeries(**params_w_agg_expression_wo_gb)

    params_w_wrong_name = base_params.copy()
    params_w_wrong_name['name'] = '-' * 65
    # invalid names (both PG and BQ)
    with pytest.raises(ValueError, match=r'not valid for SQL dialect'):
        FakeSeries(**params_w_wrong_name)

    params_w_diff_base_node = base_params.copy()
    params_w_diff_base_node['index'] = {
        'c': df['c'].materialize()
    }
    # different base node for index and series
    with pytest.raises(ValueError, match=r'Base_node in `index` should match series'):
        FakeSeries(**params_w_diff_base_node)

    params_w_wrong_instance_dtype = base_params.copy()
    params_w_wrong_instance_dtype['instance_dtype'] = 'random'
    # wrong instance_dtype
    with pytest.raises(ValueError, match=r'instance_dtype: "random"'):
        FakeSeries(**params_w_wrong_instance_dtype)
