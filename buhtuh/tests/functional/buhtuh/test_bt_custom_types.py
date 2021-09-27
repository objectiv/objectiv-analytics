"""
Copyright 2021 Objectiv B.V.
"""
import pytest

from buhtuh import BuhTuhSeries
from buhtuh.types import register_dtype, get_series_type_from_dtype, arg_to_type
from tests.functional.buhtuh.data_and_utils import get_bt_with_test_data, assert_equals_data


def test_astype_dtypes():
    # case 1: cast all columns to a type
    bt = get_bt_with_test_data()
    bt_int = bt[['inhabitants', 'founding']]
    bt_float = bt_int.astype('float64')
    assert bt_int.dtypes == {'founding': 'Int64', 'inhabitants': 'Int64'}
    assert bt_float.dtypes == {'founding': 'Float64', 'inhabitants': 'Float64'}

    # case 2: cast specific columns to a type
    # pre-test check
    assert bt.dtypes == {
        'city': 'string',
        'founding': 'Int64',
        'inhabitants': 'Int64',
        'municipality': 'string',
        'skating_order': 'Int64'
    }
    # 2.1: no columns specified
    bt_none_changed = bt.astype({})
    assert bt_none_changed.dtypes == bt.dtypes
    # 2.1: one column specified
    bt_astype1 = bt.astype({
        'inhabitants': 'float64'
    })
    assert bt_astype1.dtypes == {
        'city': 'string',
        'founding': 'Int64',
        'inhabitants': 'Float64',   # changed
        'municipality': 'string',
        'skating_order': 'Int64'
    }

    # 2.2: Multiple columns specified
    bt_astype2 = bt.astype({
        'founding': 'float64',
        'inhabitants': 'string',
        'city': 'string',  # not changed,
        'skating_order': 'string'
    })
    assert bt_astype2.dtypes == {
        'city': 'string',
        'founding': 'Float64',
        'inhabitants': 'string',
        'municipality': 'string',
        'skating_order': 'string'
    }
    assert bt.data['city'] is bt_astype2.data['city']
    assert bt.data['founding'] is not bt_astype2.data['founding']
    assert bt.data['inhabitants'] is not bt_astype2.data['inhabitants']
    assert bt.data['municipality'] is bt_astype2.data['municipality']
    assert bt.data['skating_order'] is not bt_astype2.data['skating_order']


def test_astype_to_int():
    bt = get_bt_with_test_data()
    bt = bt[['inhabitants']]
    bt['inhabitants'] = bt['inhabitants'] / 1000
    bt_int = bt.astype('int64')
    assert bt.dtypes == {'inhabitants': 'Float64'}
    assert bt_int.dtypes == {'inhabitants': 'Int64'}
    assert_equals_data(
        bt,
        expected_columns=['_index_skating_order', 'inhabitants'],
        expected_data=[
            [1, 93.485],
            [2, 33.520],
            [3, 3.055]
        ]
    )
    # When converted to ints, data will be rounded to nearest integer.
    assert_equals_data(
        bt_int,
        expected_columns=['_index_skating_order', 'inhabitants'],
        expected_data=[
            [1, 93],
            [2, 34],
            [3, 3]
        ]
    )

# todo: move above functions to other module?


def test_custom_type_register():
    class TestStringType(BuhTuhSeries):
        """ Test class for custom types. """
        dtype = 'test_type'

    # make sure to reset type-registry, as we might manipulate that in multiple tests.
    #  todo: use some pytest paradigm to reset registry?
    from buhtuh.types import _registry
    # todo: reset nicer
    _registry.dtype_series = {}
    _registry.value_type_dtype = []
    # 'test_type' should not yet exist as dtype
    # and 'string' should be the dtype for a string value
    with pytest.raises(Exception):
        get_series_type_from_dtype('test_type')
    assert arg_to_type('a string') == 'string'

    # now recreate TestStringType, but with registration decorator
    @register_dtype()
    class TestStringType(BuhTuhSeries):
        """ Test class for custom types. """
        dtype = 'test_type'

    assert get_series_type_from_dtype('test_type') is TestStringType
    assert arg_to_type('a string') == 'string'
    # todo: reset nicer
    _registry.dtype_series = {}
    _registry.value_type_dtype = []

    # now recreate TestStringType, and with registration decorator as default type for strings, and ints
    @register_dtype([str, int])
    class TestStringType(BuhTuhSeries):
        """ Test class for custom types. """
        dtype = 'test_type'
    assert get_series_type_from_dtype('test_type') is TestStringType
    assert arg_to_type('a string') == 'test_type'
    assert arg_to_type(123) == 'test_type'
    assert arg_to_type(123.45) == 'float64'

    # todo: reset nicer
    _registry.dtype_series = {}
    _registry.value_type_dtype = []


class ReversedStringType(BuhTuhSeries):
    """ Test class for custom types. """
    dtype = 'reversed_string'

    @staticmethod
    def constant_to_sql(value: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f'value should be str, actual type: {type(value)}')
        # TODO: fix sql injection!
        return f"'{reversed(value)}'"

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: str) -> str:
        if source_dtype == 'reversed_string':
            return expression
        elif source_dtype == 'String':
            return f'reverse({expression})'
        else:
            return f'reverse(({expression})::varchar)'


def test_custom_type():
    bt = get_bt_with_test_data()
    bt_city = bt[['city']]
    with pytest.raises(Exception):
        # 'reversed_string' has not be registerd yet
        bt_city.astype('reversed_string')

    #
    from buhtuh.types import _registry
    _registry.register_dtype_series('reversed_string', ReversedStringType, [])
    bt_city_special = bt_city.astype('reversed_string')

    assert bt_city.dtypes == {'city': 'string'}
    assert bt_city_special.dtypes == {'city': 'reversed_string'}

    assert_equals_data(
        bt_city,
        expected_columns=['_index_skating_order', 'city'],
        expected_data=[
            [1, 'Ljouwert'],
            [2, 'Snits'],
            [3, 'Drylts']
        ]
    )
    assert_equals_data(
        bt_city_special,
        expected_columns=['_index_skating_order', 'city'],
        expected_data=[
            [1, 'trewuojL'],
            [2, 'stinS'],
            [3, 'stlyrD']
        ]
    )
    # todo: reset nicer
    _registry.dtype_series = {}
    _registry.value_type_dtype = []
