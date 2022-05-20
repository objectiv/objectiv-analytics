"""
Copyright 2022 Objectiv B.V.
"""
import pytest

from bach.series import SeriesList
from tests.functional.bach.test_data_and_utils import get_df_with_test_data, assert_equals_data


pytestmark = [pytest.mark.skip_postgres]  # SeriesList is not (yet) supported on Postgres.


def test_basic_value_to_expression(engine):
    df = get_df_with_test_data(engine)[['skating_order']]
    df = df.sort_index()[:1].materialize()
    df['int_list'] = SeriesList.from_value(base=df, value=[1, 2, 3], name='int_list', dtype=['int64'])
    df['str_list'] = SeriesList.from_value(base=df, value=['a', 'b', 'c'], name='str_list', dtype=['string'])
    assert_equals_data(
        df,
        expected_columns=['_index_skating_order', 'skating_order', 'int_list', 'str_list'],
        expected_data=[[1, 1, [1, 2, 3], ['a', 'b', 'c']]]
    )


def test_series_to_list(engine):
    df = get_df_with_test_data(engine)[['skating_order']]
    df['int_list'] = SeriesList.from_value(
        base=df,
        value=[
            df.skating_order,
            df.skating_order * 2,
            df.skating_order * 3],
        name='int_list',
        dtype=['int64']
    )
    df['str_list'] = SeriesList.from_value(
        base=df,
        value=['a', 'b', 'c'],
        name='str_list',
        dtype=['string']
    )
    assert_equals_data(
        df,
        expected_columns=['_index_skating_order', 'skating_order', 'int_list', 'str_list'],
        expected_data=[
            [1, 1, [1, 2, 3], ['a', 'b', 'c']],
            [2, 2, [2, 4, 6], ['a', 'b', 'c']],
            [3, 3, [3, 6, 9], ['a', 'b', 'c']]
        ]
    )


def test_getitem(engine):
    df = get_df_with_test_data(engine)[['skating_order']]
    df = df.sort_index()[:1].materialize()
    df['int_list'] = SeriesList.from_value(base=df, value=[1, 2, 3], name='int_list', dtype=['int64'])
    df['str_list'] = SeriesList.from_value(base=df, value=['a', 'b', 'c'], name='str_list', dtype=['string'])
    df['a'] = df['int_list'].elements[0]
    df['b'] = df['int_list'].elements[1]
    df['c'] = df['int_list'].elements[2]
    df['d'] = df['str_list'].elements[1]
    assert_equals_data(
        df,
        expected_columns=[
            '_index_skating_order', 'skating_order', 'int_list', 'str_list', 'a', 'b', 'c', 'd'
        ],
        expected_data=[[1, 1, [1, 2, 3], ['a', 'b', 'c'], 1, 2, 3, 'b']]
    )
    assert df.dtypes['a'] == 'int64'
    assert df.dtypes['b'] == 'int64'
    assert df.dtypes['c'] == 'int64'
    assert df.dtypes['d'] == 'string'


def test_len(engine):
    df = get_df_with_test_data(engine)[['skating_order']]
    df = df.sort_index()[:1].materialize()
    df['empty_list'] = SeriesList.from_value(base=df, value=[], name='empty_list', dtype=['int64'])
    df['int_list'] = SeriesList.from_value(base=df, value=[1, 2, 3, 4, 5, 6], name='int_list', dtype=['int64'])
    df['str_list'] = SeriesList.from_value(base=df, value=['a', 'b', 'c'], name='str_list', dtype=['string'])
    df['a'] = df['empty_list'].elements.len()
    df['b'] = df['int_list'].elements.len()
    df['c'] = df['str_list'].elements.len()
    print(df.dtypes)
    assert_equals_data(
        df,
        expected_columns=[
            '_index_skating_order', 'skating_order', 'empty_list', 'int_list', 'str_list', 'a', 'b', 'c'
        ],
        expected_data=[
            [1, 1, [], [1, 2, 3, 4, 5, 6], ['a', 'b', 'c'], 0, 6, 3]
        ]
    )
