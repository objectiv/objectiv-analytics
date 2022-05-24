"""
Copyright 2022 Objectiv B.V.
"""
import pytest
from bach.series import SeriesDict
from tests.functional.bach.test_data_and_utils import get_df_with_test_data, assert_equals_data


pytestmark = [pytest.mark.skip_postgres]  # SeriesDict is not supported on Postgres at all.


def test_basic_value_to_expression(engine):
    df = get_df_with_test_data(engine)[['skating_order']]
    df = df.sort_index()[:1].materialize()
    struct = {
        'a': 123,
        'b': 'test',
        'c': 123.456,
    }
    dtype = {'a': 'int64', 'b': 'string', 'c': 'float64'}
    df['struct'] = SeriesDict.from_value(base=df, value=struct, name='struct', dtype=dtype)
    assert_equals_data(
        df,
        expected_columns=['_index_skating_order', 'skating_order', 'struct'],
        expected_data=[[1, 1, {'a': 123, 'b': 'test', 'c': 123.456}]]
    )


def test_series_to_dict(engine):
    df = get_df_with_test_data(engine)[['skating_order']]
    df = df.sort_index()
    struct = {
        'a': 123,
        'b': df.skating_order.astype('string'),
        'c': df.skating_order * 5
    }
    dtype = {'a': 'int64', 'b': 'string', 'c': 'int64'}
    df['struct'] = SeriesDict.from_value(base=df, value=struct, name='struct', dtype=dtype)
    assert_equals_data(
        df,
        expected_columns=['_index_skating_order', 'skating_order', 'struct'],
        expected_data=[
            [1, 1, {'a': 123, 'b': '1', 'c': 5}],
            [2, 2, {'a': 123, 'b': '2', 'c': 10}],
            [3, 3, {'a': 123, 'b': '3', 'c': 15}]
        ]
    )


def test_getitem(engine):
    df = get_df_with_test_data(engine)[['skating_order']]
    df = df.sort_index()[:1].materialize()
    struct = {
        'a': 123,
        'b': 'test',
        'c': 123.456
    }
    dtype = {'a': 'int64', 'b': 'string', 'c': 'float64'}
    df['struct'] = SeriesDict.from_value(base=df, value=struct, name='struct', dtype=dtype)
    df['field_a'] = df['struct'].elements['a']
    df['field_b'] = df['struct'].elements['b']
    df['field_c'] = df['struct'].elements['c']
    assert_equals_data(
        df,
        expected_columns=[
            '_index_skating_order', 'skating_order', 'struct', 'field_a', 'field_b', 'field_c'
        ],
        expected_data=[[1, 1, {'a': 123, 'b': 'test', 'c': 123.456}, 123, 'test', 123.456]]
    )


def test_nested(engine):
    df = get_df_with_test_data(engine)[['skating_order']]
    df = df.sort_index()[:1].materialize()
    struct = {
        'x': 123,
        'y': {
            'a': 123,
            'b': 'test',
            'c': 123.456
        },
        'z': [
            {
                'a': 100,
                'b': 'z.b1',
                'c': 0.1
            }, {
                'a': 200,
                'b': 'z.b2',
                'c': 0.2
            },
        ]
    }
    simple_dtype={'a': 'int64', 'b': 'string', 'c': 'float64'}
    dtype = {
        'x': 'int64',
        'y': simple_dtype,
        'z': [simple_dtype],
    }
    df['struct'] = SeriesDict.from_value(base=df, value=struct, name='struct', dtype=dtype)
    df['field_x'] = df['struct'].elements['x']
    df['field_y'] = df['struct'].elements['y']
    df['field_z_0_a'] = df['struct'].elements['z'].elements[0].elements['a']
    df['field_z_1_b'] = df['struct'].elements['z'].elements[1].elements['b']
    assert_equals_data(
        df,
        expected_columns=[
            '_index_skating_order', 'skating_order',
            'struct',
            'field_x', 'field_y', 'field_z_0_a', 'field_z_1_b'
        ],
        expected_data=[
            [1, 1,
             struct,
             123,
             {'a': 123, 'b': 'test', 'c': 123.456}, 100, 'z.b2']]
    )
