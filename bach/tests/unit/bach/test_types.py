"""
Copyright 2022 Objectiv B.V.
"""
import pytest

from typing import Any
from bach.types import get_dtype_from_db_dtype, get_series_type_from_dtype, validate_dtype_value, \
    validate_is_dtype
from bach.series import SeriesList, SeriesBoolean, SeriesString
from sql_models.constants import DBDialect
from sql_models.util import is_postgres, is_bigquery


@pytest.mark.db_independent
def test_get_series_type_from_dtype():
    assert get_series_type_from_dtype('bool') is SeriesBoolean
    assert get_series_type_from_dtype('string') is SeriesString
    assert get_series_type_from_dtype(['int64']) is SeriesList


def test_get_dtype_from_db_dtype(dialect):
    # maybe get_dtype_from_db_dtype should take a dialect instead of a DBDialect?
    db_dialect = DBDialect.from_dialect(dialect)
    if is_postgres(dialect):
        assert get_dtype_from_db_dtype(db_dialect=db_dialect, db_dtype='double precision') == 'float64'
        assert get_dtype_from_db_dtype(db_dialect=db_dialect, db_dtype='bigint') == 'int64'
    if is_bigquery(dialect):
        assert get_dtype_from_db_dtype(db_dialect=db_dialect, db_dtype='FLOAT64') == 'float64'
        assert get_dtype_from_db_dtype(db_dialect=db_dialect, db_dtype='INT64') == 'int64'
        assert get_dtype_from_db_dtype(db_dialect=db_dialect, db_dtype='ARRAY<INT64>') == ['int64']


@pytest.mark.db_independent
def test_validate_is_dtype_ok():
    validate_is_dtype('bool')
    validate_is_dtype('int64')
    validate_is_dtype(['int64'])
    validate_is_dtype({'a': 'int64'})
    validate_is_dtype({'a': 'bool'})
    validate_is_dtype({'a': ['float64'], 'b': 'timestamp', 'c': {'ca': 'float64', 'cb': [{'cba': 'int64'}]}})
    validate_is_dtype(['date'])
    validate_is_dtype([['date']])
    validate_is_dtype([{'a': 'bool'}])


@pytest.mark.db_independent
def test_validate_is_dtype_non_happy():
    _test_validate_is_dtype_false('')
    _test_validate_is_dtype_false(None)
    _test_validate_is_dtype_false('test')
    _test_validate_is_dtype_false(['test'])
    _test_validate_is_dtype_false(['int64', 'int64'])
    _test_validate_is_dtype_false({123: 'int64'})
    _test_validate_is_dtype_false({'x': 'not_a_type'})


def _test_validate_is_dtype_false(dtype: Any, matches=None):
    with pytest.raises(ValueError, match=matches):
        validate_is_dtype(dtype)


def test_validate_dtype_value():
    validate_dtype_value(static_dtype='bool', instance_dtype='bool', value=True)
    validate_dtype_value(static_dtype='bool', instance_dtype='bool', value=False)
    _test_validate_dtype_value_false(static_dtype='bool', instance_dtype='bool', value='False')
    _test_validate_dtype_value_false(static_dtype='bool', instance_dtype='int64', value=False)

    validate_dtype_value(static_dtype='int64', instance_dtype='int64', value=123)
    _test_validate_dtype_value_false(static_dtype='int64', instance_dtype='in64', value=123.0)

    validate_dtype_value(static_dtype='dict', instance_dtype={'a': 'string'}, value={'a': 'test'})
    _test_validate_dtype_value_false(static_dtype='dict', instance_dtype='dict', value={'a': 'test'})
    validate_dtype_value(static_dtype='dict', instance_dtype={'a': ['int64']}, value={'a': [1, 2, 3]})
    _test_validate_dtype_value_false(static_dtype='dict', instance_dtype={'a': ['int64']},
                                     value={'a': [1, 2, 3.0, 4]})  # one float in there


def _test_validate_dtype_value_false(
        static_dtype: 'Dtype',
        instance_dtype: 'StructeredDtype',
        value: Any,
        matches=None
):
    with pytest.raises(ValueError, match=matches):
        validate_dtype_value(static_dtype=static_dtype, instance_dtype=instance_dtype, value=value)
