"""
Copyright 2021 Objectiv B.V.
"""
from typing import List

import pytest

from buhtuh import BuhTuhDataFrame, get_series_type_from_dtype
from buhtuh.merge import _determine_left_on_right_on, _determine_result_columns, ResultColumn, merge, How
from tests.unit.buhtuh.util import get_fake_df


def test__determine_left_on_right_on_simple_df_df_happy():
    left = get_fake_df(['a'], ['b', 'c'])
    right = get_fake_df(['a'], ['c', 'd'])
    assert call__determine_left_on_right_on(left, right) == (['c'], ['c'])


def test__determine_left_on_right_on_simple_df_df_non_happy():
    left = get_fake_df(['a'], ['b', 'c'])
    right = get_fake_df(['a'], ['d', 'e'])
    with pytest.raises(ValueError):
        # TODO: should we match on index in this case? That seems to make sense
        # there are no columns in left and right with the same name
        call__determine_left_on_right_on(left, right)


def test__determine_left_on_right_on_on_df_df_happy():
    left = get_fake_df(['a'], ['b', 'c'])
    right = get_fake_df(['a'], ['c', 'd'])
    assert call__determine_left_on_right_on(left, right, on='c') == (['c'], ['c'])
    assert call__determine_left_on_right_on(left, right, on=['c']) == (['c'], ['c'])
    assert call__determine_left_on_right_on(left, right, on='a') == (['a'], ['a'])
    assert call__determine_left_on_right_on(left, right, on=['a']) == (['a'], ['a'])
    assert call__determine_left_on_right_on(left, right, on=['a', 'c']) == (['a', 'c'], ['a', 'c'])


def test__determine_left_on_right_on_on_df_df_non_happy():
    left = get_fake_df(['a'], ['b', 'c'])
    right = get_fake_df(['a'], ['c', 'd'])
    with pytest.raises(ValueError):
        # 'x' does not exist in either of the dfs
        call__determine_left_on_right_on(left, right, on='x')
    with pytest.raises(ValueError):
        # 'b' does not exist in the right df
        call__determine_left_on_right_on(left, right, on='b')
    with pytest.raises(ValueError):
        # 'd' does not exist in the left df
        call__determine_left_on_right_on(left, right, on='d')
    with pytest.raises(ValueError, match='how'):
        # Cannot specify 'on' with how='cross'
        call__determine_left_on_right_on(left, right, How.cross, on='c')


def test__determine_left_on_right_on_left_on_right_on_df_df_happy():
    left = get_fake_df(['a'], ['b', 'c'])
    right = get_fake_df(['a'], ['c', 'd'])
    assert call__determine_left_on_right_on(left, right, left_on='c', right_on='c') == (['c'], ['c'])
    assert call__determine_left_on_right_on(left, right, left_on=['c'], right_on='c') == (['c'], ['c'])
    assert call__determine_left_on_right_on(left, right, left_on='c', right_on=['c']) == (['c'], ['c'])
    assert call__determine_left_on_right_on(left, right, left_on='a', right_on='a') == (['a'], ['a'])
    assert call__determine_left_on_right_on(left, right, left_on=['a'], right_on=['a']) == (['a'], ['a'])
    assert call__determine_left_on_right_on(left, right, left_on=['a', 'c'], right_on=['a', 'c']) \
           == (['a', 'c'], ['a', 'c'])
    assert call__determine_left_on_right_on(left, right, left_on=['a'], right_on=['c']) == (['a'], ['c'])
    assert call__determine_left_on_right_on(left, right, left_on=['a', 'b'], right_on=['a', 'd']) \
           == (['a', 'b'], ['a', 'd'])


def test__determine_left_on_right_on_left_on_right_on_df_df_non_happy():
    left = get_fake_df(['a'], ['b', 'c'])
    right = get_fake_df(['a'], ['c', 'd'])
    # Should always specify both left_on and right_on and not 'on' at the same time.
    with pytest.raises(ValueError):
        call__determine_left_on_right_on(left, right, left_on='c')
    with pytest.raises(ValueError):
        call__determine_left_on_right_on(left, right, right_on='c')
    with pytest.raises(ValueError):
        call__determine_left_on_right_on(left, right, on='c', left_on='c')
    with pytest.raises(ValueError):
        call__determine_left_on_right_on(left, right, on='c', right_on='c')
    with pytest.raises(ValueError):
        call__determine_left_on_right_on(left, right, on='c', left_on='c', right_on='c')
    # columns must exist
    with pytest.raises(ValueError):
        call__determine_left_on_right_on(left, right, left_on='a', right_on='x')
    with pytest.raises(ValueError):
        call__determine_left_on_right_on(left, right, left_on='x', right_on='a')
    with pytest.raises(ValueError):
        call__determine_left_on_right_on(left, right, left_on='x', right_on='x')
    # Cannot specify '*_on' with how='cross'
    with pytest.raises(ValueError, match='how'):
        call__determine_left_on_right_on(left, right, How.cross, left_on='c', right_on='c')


def test__determine_left_on_right_index_on_df_df_happy():
    left = get_fake_df(['a'], ['b', 'c'])
    right = get_fake_df(['a'], ['c', 'd'])
    assert call__determine_left_on_right_on(left, right, left_on='c', right_index=True) == (['c'], ['a'])
    assert call__determine_left_on_right_on(left, right, left_index=True, right_on='c') == (['a'], ['c'])
    assert call__determine_left_on_right_on(left, right, left_index=True, right_index=True) == (['a'], ['a'])


def test__determine_left_on_right_df_serie_happy():
    left = get_fake_df(['a'], ['b', 'c'])
    right = get_fake_df(['a'], ['c', 'd'])['c']
    assert call__determine_left_on_right_on(left, right) == (['c'], ['c'])
    assert call__determine_left_on_right_on(left, right, on='c') == (['c'], ['c'])
    assert call__determine_left_on_right_on(left, right, left_on='c', right_on='c') == (['c'], ['c'])
    assert call__determine_left_on_right_on(left, right, left_on='c', right_on='a') == (['c'], ['a'])
    assert call__determine_left_on_right_on(left, right, left_on='c', right_index=True) == (['c'], ['a'])
    assert call__determine_left_on_right_on(left, right, left_index=True, right_on='c') == (['a'], ['c'])
    assert call__determine_left_on_right_on(left, right, left_index=True, right_index=True) == (['a'], ['a'])


def test__determine_result_columns():
    left = get_fake_df(['a'], ['b', 'c'], 'int64')
    right = get_fake_df(['a'], ['c', 'd'], 'float64')
    result = _determine_result_columns(left, right, ['a'], ['a'], ('_x', '_y'))
    assert result == (
        [
            ResultColumn(name='a', expression='"l"."a"', dtype='int64'),
        ], [
            ResultColumn(name='b', expression='"l"."b"', dtype='int64'),
            ResultColumn(name='c_x', expression='"l"."c"', dtype='int64'),
            ResultColumn(name='c_y', expression='"r"."c"', dtype='float64'),
            ResultColumn(name='d', expression='"r"."d"', dtype='float64')
        ]
    )
    result = _determine_result_columns(left, right, ['c'], ['c'], ('_x', '_y'))
    assert result == (
        [
            ResultColumn(name='a_x', expression='"l"."a"', dtype='int64'),
            ResultColumn(name='a_y', expression='"r"."a"', dtype='float64'),
        ], [
            ResultColumn(name='b', expression='"l"."b"', dtype='int64'),
            ResultColumn(name='c', expression='"l"."c"', dtype='int64'),
            ResultColumn(name='d', expression='"r"."d"', dtype='float64')
        ]
    )
    result = _determine_result_columns(left, right, ['a', 'c'], ['a', 'c'], ('_x', '_y'))
    assert result == (
        [
            ResultColumn(name='a', expression='"l"."a"', dtype='int64'),
        ], [
            ResultColumn(name='b', expression='"l"."b"', dtype='int64'),
            ResultColumn(name='c', expression='"l"."c"', dtype='int64'),
            ResultColumn(name='d', expression='"r"."d"', dtype='float64')
        ]
    )


def test__determine_result_columns_non_happy_path():
    # With pandas the following works, there will just be two b_x and two b_y columns, but we cannot
    # generate sql that has the same column name multiple times, so we raise an error
    left = get_fake_df(['a'], ['b', 'b_x'], 'int64')
    right = get_fake_df(['a'], ['b', 'b_y'], 'float64')
    with pytest.raises(ValueError):
        _determine_result_columns(left, right, ['a'], ['a'], ('_x', '_y'))


def test_merge_non_happy_path_how():
    left = get_fake_df(['a'], ['b', 'b_x'], 'int64')
    right = get_fake_df(['a'], ['b', 'b_y'], 'float64')
    with pytest.raises(ValueError, match='how'):
        merge(left, right, 'wrong how',
              on=None, left_on=None, right_on=None, left_index=True, right_index=True,
              suffixes=('_x', '_y'))


def call__determine_left_on_right_on(
        left, right,
        how=How.inner, on=None, left_on=None, right_on=None, left_index=False, right_index=False):
    """ Wrapper around _determine_left_on_right_on that fills in the default arguments"""
    return _determine_left_on_right_on(
        left=left,
        right=right,
        how=how,
        on=on,
        left_on=left_on,
        right_on=right_on,
        left_index=left_index,
        right_index=right_index
    )
