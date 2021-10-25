"""
Copyright 2021 Objectiv B.V.
"""
from buhtuh import BuhTuhSeriesBoolean, BuhTuhSeriesInt64, BuhTuhSeriesString, \
    BuhTuhSeriesFloat64, BuhTuhSeriesTimestamp
from tests.functional.buhtuh.test_data_and_utils import _get_bt, assert_db_type

import datetime


def test_all_supported_types():
    TEST_DATA_SUPPORTED_TYPES = [
        [1.32, 4, datetime.datetime(2015, 12, 13, 9, 54, 45, 543), 'fierljeppen', True]
    ]
    bt = _get_bt('test_supported_types_table',
                 TEST_DATA_SUPPORTED_TYPES,
                 ['float', 'int', 'timestamp', 'string', 'bool'],
                 convert_objects=True)

    assert_db_type(bt['float'], 'double precision', BuhTuhSeriesFloat64)
    assert_db_type(bt['int'], 'bigint', BuhTuhSeriesInt64)
    assert_db_type(bt['timestamp'], 'timestamp without time zone', BuhTuhSeriesTimestamp)
    assert_db_type(bt['string'], 'text', BuhTuhSeriesString)
    assert_db_type(bt['bool'], 'boolean', BuhTuhSeriesBoolean)


def test_string_as_index():
    TEST_DATA_SUPPORTED_TYPES = [
        ['fierljeppen', 1.32, 4, datetime.datetime(2015, 12, 13, 9, 54, 45, 543), True]
    ]
    bt = _get_bt('test_supported_types_table',
                 TEST_DATA_SUPPORTED_TYPES,
                 ['string', 'float', 'int', 'timestamp', 'bool'],
                 convert_objects=True)

    assert_db_type(bt['float'], 'double precision', BuhTuhSeriesFloat64)
    assert_db_type(bt['int'], 'bigint', BuhTuhSeriesInt64)
    assert_db_type(bt['timestamp'], 'timestamp without time zone', BuhTuhSeriesTimestamp)
    assert_db_type(bt['string'], 'text', BuhTuhSeriesString)
    assert_db_type(bt['bool'], 'boolean', BuhTuhSeriesBoolean)


def test_load_df_without_conversion():
    TEST_DATA_SUPPORTED_TYPES = [
        [1.32, 4, datetime.datetime(2015, 12, 13, 9, 54, 45, 543), True]
    ]
    bt = _get_bt('test_supported_types_table',
                 TEST_DATA_SUPPORTED_TYPES,
                 ['float', 'int', 'timestamp', 'bool'],
                 convert_objects=False)

    assert_db_type(bt['float'], 'double precision', BuhTuhSeriesFloat64)
    assert_db_type(bt['int'], 'bigint', BuhTuhSeriesInt64)
    assert_db_type(bt['timestamp'], 'timestamp without time zone', BuhTuhSeriesTimestamp)
    assert_db_type(bt['bool'], 'boolean', BuhTuhSeriesBoolean)
