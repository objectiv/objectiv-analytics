"""
Copyright 2022 Objectiv B.V.
"""
from datetime import timedelta
from numpy import timedelta64

from bach import SeriesTimedelta
from bach.expression import Expression


def test_supported_value_to_literal(dialect):
    def assert_call(value, expected_token_value: str):
        result = SeriesTimedelta.supported_value_to_literal(dialect=dialect, value=value, dtype='timedelta')
        assert result == Expression.string_value(expected_token_value)

    assert_call(timedelta(seconds=1234),                                'P0DT0H20M34S')
    assert_call(timedelta(seconds=1234, microseconds=1234),             'P0DT0H20M34.001234S')
    assert_call(timedelta(days=5, seconds=1234, microseconds=1234),     'P5DT0H20M34.001234S')
    assert_call(timedelta(days=-5, seconds=1234, microseconds=1234),    'P-5DT0H20M34.001234S')
    assert_call(timedelta(days=365, seconds=1234, microseconds=1234),   'P365DT0H20M34.001234S')
    assert_call(timedelta(days=50_000, seconds=123, microseconds=9),    'P50000DT0H2M3.000009S')

    assert_call(timedelta64(1234, 's'),                                                   'P0DT0H20M34S')
    assert_call(timedelta64(1234, 's') + timedelta64(1234, 'us'),                         'P0DT0H20M34.001234S')
    assert_call(timedelta64(5, 'D') + timedelta64(1234, 's') + timedelta64(1234, 'us'),   'P5DT0H20M34.001234S')
    assert_call(timedelta64(-5, 'D') + timedelta64(1234, 's') + timedelta64(1234, 'us'),  'P-5DT0H20M34.001234S')
    assert_call(timedelta64(365, 'D') + timedelta64(1234, 's') + timedelta64(1234, 'us'), 'P365DT0H20M34.001234S')
    assert_call(timedelta64(50_000, 'D') + timedelta64(123, 's') + timedelta64(9, 'us'),  'P50000DT0H2M3.000009S')

    # Special cases: Not-a-Time will be represented as NULL, and NULL itself
    nat = timedelta64('NaT')
    dtype = 'timedelta'
    assert SeriesTimedelta.supported_value_to_literal(dialect, nat, dtype) == Expression.construct('NULL')
    assert SeriesTimedelta.supported_value_to_literal(dialect, None, dtype) == Expression.construct('NULL')
