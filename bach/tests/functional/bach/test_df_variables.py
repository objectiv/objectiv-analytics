"""
Copyright 2021 Objectiv B.V.
"""
import pytest

from bach.dataframe import DtypeNamePair, DefinedVariable, DataFrame
from tests.functional.bach.test_data_and_utils import get_bt_with_test_data, assert_equals_data, \
    get_bt_with_food_data


def test_variable_happy_path():
    df = get_bt_with_test_data()[['city', 'founding']]
    assert_equals_data(
        df,
        expected_columns=['_index_skating_order', 'city', 'founding'],
        expected_data=[
            [1, 'Ljouwert', 1285],
            [2, 'Snits', 1456],
            [3, 'Drylts', 1268],
        ]
    )

    df, add_value = df.create_variable(name='add_value', value=1000)
    df, suffix = df.create_variable(name='suffix', value=' city')
    df, filter_value = df.create_variable(name='filter_value', value=2400)
    df['founding'] = df.founding + add_value
    df['city'] = df['city'] + suffix
    df = df[df.founding < filter_value]

    assert df.variables == {
        DtypeNamePair(dtype='int64', name='add_value'): 1000,
        DtypeNamePair(dtype='string', name='suffix'): ' city',
        DtypeNamePair(dtype='int64', name='filter_value'): 2400,
    }
    assert_equals_data(
        df,
        expected_columns=['_index_skating_order', 'city', 'founding'],
        expected_data=[
            [1, 'Ljouwert city', 2285],
            [3, 'Drylts city', 2268],
        ]
    )

    df = df.set_variable('add_value', 2000)
    df = df.set_variable('filter_value', 4400)
    assert df.variables == {
        DtypeNamePair(dtype='int64', name='add_value'): 2000,
        DtypeNamePair(dtype='string', name='suffix'): ' city',
        DtypeNamePair(dtype='int64', name='filter_value'): 4400,
    }
    assert_equals_data(
        df,
        expected_columns=['_index_skating_order', 'city', 'founding'],
        expected_data=[
            [1, 'Ljouwert city', 3285],
            [2, 'Snits city', 3456],
            [3, 'Drylts city', 3268],
        ]
    )

    df = df.materialize()
    df = df.set_variable('add_value', 3000)
    df = df.set_variable('suffix', ' sted')
    assert df.variables == {
        DtypeNamePair(dtype='int64', name='add_value'): 3000,
        DtypeNamePair(dtype='string', name='suffix'): ' sted',
        DtypeNamePair(dtype='int64', name='filter_value'): 4400,
    }
    assert_equals_data(
        df,
        expected_columns=['_index_skating_order', 'city', 'founding'],
        expected_data=[
            [1, 'Ljouwert sted', 4285],
            [3, 'Drylts sted', 4268],
        ]
    )


def test_set_variable_double_types():
    # It's possible to have two variables with the same name but different type.
    # This seems counter-intuitive, but removes a lot of the potential edge cases and problems around merging
    # DataFrames and Series with the same variable names.
    df = get_bt_with_test_data()[['city']]
    df, int_variable = df.create_variable('variable', 1000)
    df, str_variable = df.create_variable('variable', 'test')
    assert df.variables == {
        DtypeNamePair(dtype='int64', name='variable'): 1000,
        DtypeNamePair(dtype='string', name='variable'): 'test'
    }

    df['x'] = int_variable
    df['y'] = str_variable
    assert_equals_data(
        df,
        expected_columns=['_index_skating_order', 'city', 'x', 'y'],
        expected_data=[
            [1, 'Ljouwert', 1000, 'test'],
            [2, 'Snits', 1000, 'test'],
            [3, 'Drylts', 1000, 'test']
        ]
    )

    # We can be explicit about which dtype we want to set. If it doesn't match the value this will give an
    # error
    df.set_variable('variable', 1234, dtype='int64')
    df.set_variable('variable', '1234', dtype='string')
    with pytest.raises(ValueError,
                       match=r"Dtype of value \(int64\) and provided dtype \(string\) don't match"):
        df.set_variable('variable', 1234, dtype='string')
    with pytest.raises(ValueError,
                       match=r"Dtype of value \(string\) and provided dtype \(int64\) don't match"):
        df.set_variable('variable', '1234', dtype='int64')


def test_variable_missing():
    # test case where a variable is used in the series, but has no value assigned.
    df = get_bt_with_test_data()[['city', 'founding']]
    df, int_variable = df.create_variable('int_variable', 1000)
    assert df.variables == {DtypeNamePair(dtype='int64', name='int_variable'): 1000}
    df['x'] = int_variable
    # should work
    df.to_pandas()

    # without the variable set we expect an error
    df_without_variable = df.copy_override(variables={})
    assert df_without_variable.variables == {}
    with pytest.raises(Exception, match='Variable int_variable, with dtype int64 is used, but not set.'):
        df_without_variable.to_pandas()

    df.materialize(inplace=True)
    # Now that the variable is not used in the series anymore, only in base_node we should be able to unset
    # it.
    df_without_variable = df.copy_override(variables={})
    assert df_without_variable.variables == {}
    # now this should not raise an error
    df_without_variable.to_pandas()


def test_merge_happy_path():
    bt = get_bt_with_test_data(full_data_set=False)[['skating_order', 'city']]
    mt = get_bt_with_food_data()[['skating_order', 'food']]

    bt, shared = bt.create_variable(name='shared', value=' first')
    bt, variable1 = bt.create_variable(name='variable1', value=' city')
    bt['city'] = bt['city'] + variable1 + shared
    mt, shared = mt.create_variable(name='shared', value=' second')
    mt, variable2 = mt.create_variable(name='variable2', value=' food')
    mt['food'] = mt['food'] + variable2 + shared

    assert bt.variables == {
        DtypeNamePair(dtype='string', name='shared'): ' first',
        DtypeNamePair(dtype='string', name='variable1'): ' city'
    }
    assert mt.variables == {
        DtypeNamePair(dtype='string', name='shared'): ' second',
        DtypeNamePair(dtype='string', name='variable2'): ' food'
    }

    result = bt.merge(mt)
    # The 'shared' variable is in both DataFrames. The value from the left df will override the right
    assert result.variables == {
        DtypeNamePair(dtype='string', name='shared'): ' first',
        DtypeNamePair(dtype='string', name='variable1'): ' city',
        DtypeNamePair(dtype='string', name='variable2'): ' food'
    }

    assert_equals_data(
        result,
        expected_columns=['_index_skating_order_x', '_index_skating_order_y',
                          'skating_order', 'city', 'food'],
        expected_data=[
            [1, 1, 1, 'Ljouwert city first', 'Sûkerbôlle food first'],
            [2, 2, 2, 'Snits city first', 'Dúmkes food first'],
        ]
    )


def test_merge_variable_different_types():
    bt = get_bt_with_test_data(full_data_set=False)[['skating_order', 'inhabitants']]
    mt = get_bt_with_food_data()[['skating_order', 'food']]
    bt, bt_variable = bt.create_variable(name='shared', value=12345)
    bt['inhabitants'] = bt['inhabitants'] + bt_variable
    mt, mt_variable = mt.create_variable(name='shared', value=' string value')
    mt['food'] = mt['food'] + mt_variable

    result = bt.merge(mt)
    assert_equals_data(
        result,
        expected_columns=['_index_skating_order_x', '_index_skating_order_y',
                          'skating_order', 'inhabitants', 'food'],
        expected_data=[
            [1, 1, 1, 105830, 'Sûkerbôlle string value'],
            [2, 2, 2, 45865, 'Dúmkes string value']
        ]
    )


def test_get_all_variable_usage():
    df1 = get_bt_with_test_data(full_data_set=False)[['skating_order', 'inhabitants']]
    assert df1.get_all_variable_usage() == []

    df1, first = df1.create_variable(name='first', value=1234)
    # variable is not yet used
    assert df1.get_all_variable_usage() == []

    df1['inhabitants'] = df1.inhabitants + first
    assert df1.get_all_variable_usage() == [('first', 'int64', 1234, None, None)]

    df1.materialize(inplace=True)
    # materialize will migrate the usage of the variable from the self.series to self.base_node
    assert df1.get_all_variable_usage() == [('first', 'int64', 1234, tuple(), '1234')]

    df1, second = df1.create_variable(name='second', value='test')
    df1['x'] = second
    assert df1.get_all_variable_usage() == [
        DefinedVariable(name='second', dtype='string', value='test', ref_path=None, old_value=None),
        DefinedVariable(name='first', dtype='int64', value=1234, ref_path=(), old_value='1234')
    ]

    df1.materialize(inplace=True)
    # materialize will change the ref_paths, and migrate the 'second' variable to the base_node
    assert df1.get_all_variable_usage() == [
        DefinedVariable(name='second', dtype='string', value='test', ref_path=(), old_value="'test'"),
        DefinedVariable(name='first', dtype='int64', value=1234, ref_path=('prev',), old_value='1234')
    ]

    df2 = DataFrame.from_model(engine=df1.engine, model=df1.base_node, index=list(df1.index.keys()))
    # df2 a base_node that has one SqlModel after the df1.base_node.
    # df2 has the same variables in the base_node as df1, but it doesn't actually have the values defined.
    assert df2.get_all_variable_usage() == [
        DefinedVariable(name='second', dtype='string', value=None, ref_path=('model',), old_value="'test'"),
        DefinedVariable(name='first', dtype='int64', value=None, ref_path=('model', 'prev'), old_value='1234')
    ]


def test_variable_escaping():
    df = get_bt_with_test_data()[['city']]
    df = df[df['city'] == 'Ljouwert']

    weird_value = ' %(test)s %%  ? {test} {{test2}} {{{test3}}} {{}"test"{}\'test\'\'"'
    normal_value = 'test'
    df, str_variable1 = df.create_variable(name='str_variable1', value=weird_value)
    df, str_variable2 = df.create_variable(name='str_variable2', value=normal_value)
    df['x'] = str_variable1
    df['y'] = str_variable2

    assert_equals_data(
        df,
        expected_columns=['_index_skating_order', 'city', 'x', 'y'],
        expected_data=[[1, 'Ljouwert', weird_value, normal_value]]
    )

    df.materialize()
    df, str_variable3 = df.create_variable(name='str_variable3', value=normal_value)
    df['z'] = str_variable3
    df = df.set_variable('str_variable2', weird_value)
    assert_equals_data(
        df,
        expected_columns=['_index_skating_order', 'city', 'x', 'y', 'z'],
        expected_data=[[1, 'Ljouwert', weird_value, weird_value, normal_value]]
    )
