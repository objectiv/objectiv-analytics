"""
Copyright 2021 Objectiv B.V.
"""
from bach import SortColumn
from bach.expression import Expression
from tests.unit.bach.util import get_fake_df


def test__eq__():
    assert get_fake_df(['a'], ['b', 'c']) != 123
    assert get_fake_df(['a'], ['b', 'c']) != 'a'
    assert get_fake_df(['a'], ['b', 'c']) != (['a'], ['b', 'c'])

    result = get_fake_df(['a'], ['b', 'c']) == get_fake_df(['a'], ['b', 'c'])
    # Assert that we get a boolean (e.g. for Series this is not the case since we overloaded __eq__ in a
    # different way)
    assert result is True

    assert get_fake_df(['a'], ['b', 'c']) == get_fake_df(['a'], ['b', 'c'])
    assert get_fake_df(['a', 'b'], ['c']) == get_fake_df(['a', 'b'], ['c'])
    # 'b' is index or data column
    assert get_fake_df(['a', 'b'], ['c']) != get_fake_df(['a'], ['b', 'c'])
    # switched order index columns
    assert get_fake_df(['b', 'a'], ['c']) != get_fake_df(['a', 'b'], ['c'])
    # switched order data columns
    assert get_fake_df(['a'], ['b', 'c']) != get_fake_df(['a'], ['c', 'b'])
    left = get_fake_df(['a'], ['b', 'c'])
    right = get_fake_df(['a'], ['b', 'c'])
    assert left == right
    # use fake value for engine and basenode to check that the values are tested
    left._engine = 'test'
    assert left != right
    right._engine = 'test'
    assert left == right
    right._base_node = 'test'
    assert left != right
    left._base_node = 'test'
    assert left == right
    right._order_by = [SortColumn(expression=Expression.column_reference('a'), asc=True)]
    assert left != right
    left._order_by = [SortColumn(expression=Expression.column_reference('a'), asc=False)]
    assert left != right
    left._order_by = [SortColumn(expression=Expression.column_reference('a'), asc=True)]
    assert left == right

    left = left.set_variable('a', 1234)
    right = right.set_variable('a', '1234')
    assert left != right
    left = left.set_variable('a', '1234')
    right = right.set_variable('a', 1234)
    assert left == right
