"""
Copyright 2022 Objectiv B.V.
"""
import pytest

from bach import Series
from bach.types import TypeRegistry, get_series_type_from_dtype, value_to_dtype, register_dtype
from sql_models.constants import DBDialect


@pytest.mark.db_independent
def test_custom_type_register(monkeypatch):
    # make sure monkeypatch the type-registry, as it should be restored after this test finishes.
    monkeypatch.setattr('bach.types._registry', TypeRegistry())

    class TestStringType(Series):
        """ Test class for custom types. """
        dtype = 'test_type'
        dtype_aliases = ('test_type_1337', )
        supported_db_dtype = {DBDialect.POSTGRES: 'test_type'}
        supported_value_types = (str, int)

    # 'test_type' should not yet exist as dtype
    # and 'string' should be the dtype for a string value
    with pytest.raises(Exception):
        get_series_type_from_dtype('test_type')
    assert value_to_dtype('a string') == 'string'

    # now recreate TestStringType, but with registration decorator
    @register_dtype()
    class TestStringType(Series):
        """ Test class for custom types. """
        dtype = 'test_type'
        dtype_aliases = ('test_type_1337',)
        supported_db_dtype = {DBDialect.POSTGRES: 'test_type'}
        supported_value_types = (str, int)

    assert get_series_type_from_dtype('test_type') is TestStringType
    assert value_to_dtype('a string') == 'string'
    monkeypatch.setattr('bach.types._registry', TypeRegistry())

    # now recreate TestStringType, and with registration decorator as default type for strings, and ints
    @register_dtype([str, int], override_registered_types=True)
    class TestStringType(Series):
        """ Test class for custom types. """
        dtype = 'test_type'
        dtype_aliases = ('test_type_1337',)
        supported_db_dtype = {DBDialect.POSTGRES: 'test_type'}
        supported_value_types = (str, int)

    assert get_series_type_from_dtype('test_type') is TestStringType
    assert value_to_dtype('a string') == 'test_type'
    assert value_to_dtype(123) == 'test_type'
    assert value_to_dtype(123.45) == 'float64'
