"""
Copyright 2021 Objectiv B.V.
"""
from bach import SeriesBoolean, SeriesInt64, SeriesString, \
    SeriesFloat64, SeriesTimestamp
from tests.functional.bach.test_data_and_utils import get_bt, assert_postgres_type

import datetime


def test_all_supported_types():
    TEST_DATA_SUPPORTED_TYPES = [
        [1.32, 4, datetime.datetime(2015, 12, 13, 9, 54, 45, 543), 'fierljeppen', True]
    ]
    bt = get_bt('test_supported_types_table',
                TEST_DATA_SUPPORTED_TYPES,
                ['float', 'int', 'timestamp', 'string', 'bool'],
                convert_objects=True)

    assert_postgres_type(bt['float'], 'double precision', SeriesFloat64)
    assert_postgres_type(bt['int'], 'bigint', SeriesInt64)
    assert_postgres_type(bt['timestamp'], 'timestamp without time zone', SeriesTimestamp)
    assert_postgres_type(bt['string'], 'text', SeriesString)
    assert_postgres_type(bt['bool'], 'boolean', SeriesBoolean)


def test_string_as_index():
    TEST_DATA_SUPPORTED_TYPES = [
        ['fierljeppen', 1.32, 4, datetime.datetime(2015, 12, 13, 9, 54, 45, 543), True]
    ]
    bt = get_bt('test_supported_types_table',
                TEST_DATA_SUPPORTED_TYPES,
                ['string', 'float', 'int', 'timestamp', 'bool'],
                convert_objects=True)

    assert_postgres_type(bt['float'], 'double precision', SeriesFloat64)
    assert_postgres_type(bt['int'], 'bigint', SeriesInt64)
    assert_postgres_type(bt['timestamp'], 'timestamp without time zone', SeriesTimestamp)
    assert_postgres_type(bt['string'], 'text', SeriesString)
    assert_postgres_type(bt['bool'], 'boolean', SeriesBoolean)


def test_load_df_without_conversion():
    TEST_DATA_SUPPORTED_TYPES = [
        [1.32, 4, datetime.datetime(2015, 12, 13, 9, 54, 45, 543), True]
    ]
    bt = get_bt('test_supported_types_table',
                TEST_DATA_SUPPORTED_TYPES,
                ['float', 'int', 'timestamp', 'bool'],
                convert_objects=False)

    assert_postgres_type(bt['float'], 'double precision', SeriesFloat64)
    assert_postgres_type(bt['int'], 'bigint', SeriesInt64)
    assert_postgres_type(bt['timestamp'], 'timestamp without time zone', SeriesTimestamp)
    assert_postgres_type(bt['bool'], 'boolean', SeriesBoolean)
