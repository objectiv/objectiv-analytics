"""
Copyright 2021 Objectiv B.V.
"""
import pytest

from buhtuh import BuhTuhSeries, Expression
from buhtuh.expression import quote_string
from buhtuh.types import register_dtype, get_series_type_from_dtype, value_to_dtype, TypeRegistry
from tests.functional.buhtuh.test_data_and_utils import get_bt_with_test_data, assert_equals_data


def test_custom_type_register(monkeypatch):
    # make sure monkeypatch the type-registry, as it should be restored after this test finishes.
    monkeypatch.setattr('buhtuh.types._registry', TypeRegistry())

    class TestStringType(BuhTuhSeries):
        """ Test class for custom types. """
        dtype = 'test_type'
        dtype_aliases = ('test_type_1337', )
        supported_db_dtype = 'test_type'
        supported_value_types = (str, int)

    # 'test_type' should not yet exist as dtype
    # and 'string' should be the dtype for a string value
    with pytest.raises(Exception):
        get_series_type_from_dtype('test_type')
    assert value_to_dtype('a string') == 'string'

    # now recreate TestStringType, but with registration decorator
    @register_dtype()
    class TestStringType(BuhTuhSeries):
        """ Test class for custom types. """
        dtype = 'test_type'
        dtype_aliases = ('test_type_1337',)
        supported_db_dtype = 'test_type'
        supported_value_types = (str, int)

    assert get_series_type_from_dtype('test_type') is TestStringType
    assert value_to_dtype('a string') == 'string'
    monkeypatch.setattr('buhtuh.types._registry', TypeRegistry())

    # now recreate TestStringType, and with registration decorator as default type for strings, and ints
    @register_dtype([str, int], override_registered_types=True)
    class TestStringType(BuhTuhSeries):
        """ Test class for custom types. """
        dtype = 'test_type'
        dtype_aliases = ('test_type_1337',)
        supported_db_dtype = 'test_type'
        supported_value_types = (str, int)

    assert get_series_type_from_dtype('test_type') is TestStringType
    assert value_to_dtype('a string') == 'test_type'
    assert value_to_dtype(123) == 'test_type'
    assert value_to_dtype(123.45) == 'float64'


class ReversedStringType(BuhTuhSeries):
    """ Test class for custom types. """
    dtype = 'reversed_string'
    dtype_aliases = ('reversed_text', 'backwards_string')
    supported_db_dtype = 'text'
    supported_value_types = (str,)

    @classmethod
    def supported_value_to_expression(cls, value: str) -> Expression:
        return Expression.string_value(str(reversed(value)))

    @classmethod
    def from_dtype_to_sql(cls, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'reversed_string':
            return expression
        elif source_dtype == 'String':
            return Expression.construct('reverse({})', expression)
        else:
            return Expression.construct('reverse(cast({} as text))', expression)


def test_custom_type(monkeypatch):
    # make sure monkeypatch the type-registry, as it should be restored after this test finishes.
    monkeypatch.setattr('buhtuh.types._registry', TypeRegistry())
    # import after monkeypatching
    from buhtuh.types import _registry

    bt = get_bt_with_test_data()
    bt_city = bt[['city']]
    with pytest.raises(Exception):
        # 'reversed_string' has not be registerd yet
        bt_city.astype('reversed_string')

    # the db_dtype 'text' is already taken, so registering ReversedStringType should give an error
    with pytest.raises(Exception, match='db_dtype text, which is already assigned'):
        _registry.register_dtype_series(ReversedStringType, [], False)
    # with override_dtype=True, the error should disappear and 'reversed_string' should be registered
    _registry.register_dtype_series(ReversedStringType, [], override_registered_types=True)



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
