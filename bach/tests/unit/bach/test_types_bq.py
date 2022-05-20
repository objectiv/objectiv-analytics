"""
Copyright 2022 Objectiv B.V.
"""
import pytest

from bach.types_bq import bq_db_dtype_to_dtype

pytestmark = [pytest.mark.db_independent]
# mark all tests here as database independent. Obviously this code relates to BigQuery. But it does not
# require an Engine or Dialect. The tested code only converts strings to strings, dicts, lists, or tuples.


def test_basic_types():
    assert bq_db_dtype_to_dtype('STRING') == 'string'
    assert bq_db_dtype_to_dtype('INT64') == 'int64'
    assert bq_db_dtype_to_dtype('TIMESTAMP') == 'timestamp'
    assert bq_db_dtype_to_dtype('BOOL') == 'bool'


def test_struct_types():
    db_dtype = 'ARRAY<STRUCT<_type STRING, _types STRING, cookie_id STRING, event_id STRING, global_contexts STRING, location_stack STRING, time INT64>> '
    expected_dtype = [
        {
            '_type': 'string',
            '_types': 'string',
            'cookie_id': 'string',
            'event_id': 'string',
            'global_contexts': 'string',
            'location_stack': 'string',
            'time': 'int64'
        }
    ]
    assert bq_db_dtype_to_dtype(db_dtype) == expected_dtype


def test_nested_types():
    db_dtype = 'ARRAY<STRUCT<date DATE, winning_time_seconds INT64, persons ARRAY<STRUCT<name STRING, isWinner BOOL, times ARRAY<STRUCT<city STRING, seconds INT64>>, equipment STRUCT<skates STRUCT<manufacturer STRING, clap BOOL>, hat BOOL, layers INT64>>>>>'
    expected_dtype = [
        {
            'date': 'date',
            'winning_time_seconds': 'int64',
            'persons': [
                {
                    'name': 'string',
                    'isWinner': 'bool',
                    'times': [
                        {
                            'city': 'string',
                            'seconds': 'int64'
                        }
                    ],
                    'equipment': {
                        'hat': 'bool',
                        'layers': 'int64',
                        'skates': {
                            'clap': 'bool',
                            'manufacturer': 'string'
                        }
                    }
                }
            ]
        }
    ]
    assert bq_db_dtype_to_dtype(db_dtype) == expected_dtype


def test_non_happy_path():
    with pytest.raises(ValueError, match='found no token'):
        bq_db_dtype_to_dtype('')

    with pytest.raises(ValueError, match='Unexpected token'):
        bq_db_dtype_to_dtype('blabla')

    with pytest.raises(ValueError, match='Expected token "<"'):
        bq_db_dtype_to_dtype('STRUCT')

    with pytest.raises(ValueError, match='Expected token ">"'):
        bq_db_dtype_to_dtype('STRUCT<')

    with pytest.raises(ValueError, match='Expected token ">"'):
        bq_db_dtype_to_dtype('STRUCT<a INT64')

    with pytest.raises(ValueError, match='Unexpected tokens after last parsed tokens'):
        bq_db_dtype_to_dtype('STRUCT<a INT64>>')

    with pytest.raises(ValueError):
        bq_db_dtype_to_dtype('STRUCT<a INT64> bla bla bla')
