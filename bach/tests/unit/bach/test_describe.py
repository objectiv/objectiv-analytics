"""
Copyright 2022 Objectiv B.V.
"""
import pytest

from bach.operations.describe import DescribeOperation
from tests.unit.bach.util import get_fake_df


def test_process_params_percentile_error(dialect) -> None:
    with pytest.raises(ValueError, match=r'percentiles should'):
        DescribeOperation(
            obj=get_fake_df(dialect, ['a'], ['b']),
            include=None,
            exclude=(),
            datetime_is_numeric=False,
            percentiles=[123],
        )


def test_process_params_empty_df(dialect) -> None:
    with pytest.raises(ValueError, match=r'Cannot describe a Dataframe'):
        DescribeOperation(
            obj=get_fake_df(dialect, [], []),
            include=(),
            exclude=(),
            datetime_is_numeric=False,
            percentiles=None,
        )


def test_include_exclude(dialect) -> None:
    df = get_fake_df(
        dialect=dialect,
        index_names=[],
        data_names=['a', 'b', 'c', 'd'],
        dtype={'a': 'string', 'b': 'int64', 'c': 'float64', 'd': 'timestamp'}
    )
    obj = DescribeOperation(
        obj=df,
        include='all',
        exclude=(),
        datetime_is_numeric=False,
        percentiles=None,
    )
    assert obj.series_to_describe == ['a', 'b', 'c', 'd']
    obj = DescribeOperation(
        obj=df,
        include=None,  # default to numeric
        exclude=(),
        datetime_is_numeric=False,
        percentiles=None,
    )
    assert obj.series_to_describe == ['b', 'c']
    obj = DescribeOperation(
        obj=df,
        include=['string', 'timestamp'],
        exclude=(),
        datetime_is_numeric=False,
        percentiles=None,
    )
    assert obj.series_to_describe == ['a', 'd']
    obj = DescribeOperation(
        obj=df,
        include='string',
        exclude=(),
        datetime_is_numeric=False,
        percentiles=None,
    )
    assert obj.series_to_describe == ['a']
    obj = DescribeOperation(
        obj=df,
        include=None,
        exclude=['float64'],
        datetime_is_numeric=False,
        percentiles=None,
    )
    assert obj.series_to_describe == ['b']
    obj = DescribeOperation(
        obj=df,
        include=None,
        exclude='float64',
        datetime_is_numeric=False,
        percentiles=None,
    )
    assert obj.series_to_describe == ['b']
    obj = DescribeOperation(
        obj=df,
        include=None,
        exclude=['double'],  # alias for float64
        datetime_is_numeric=False,
        percentiles=None,
    )
    assert obj.series_to_describe == ['b']

    with pytest.raises(ValueError, match='Include and exclude should not overlap'):
        DescribeOperation(
            obj=df,
            include='all',
            exclude=['float64'],
            datetime_is_numeric=False,
            percentiles=None,
        )

    with pytest.raises(ValueError, match='Unknown dtype'):
        DescribeOperation(
            obj=df,
            include=['not_a_dtype'],
            exclude=['not_a_dtype'],
            datetime_is_numeric=False,
            percentiles=None,
        )
