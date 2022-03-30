"""
Copyright 2021 Objectiv B.V.
"""
import datetime

import pytest

from bach import SeriesDate
from tests.functional.bach.test_data_and_utils import assert_equals_data, get_bt_with_food_data, \
    assert_postgres_type, get_bt_with_test_data
from tests.functional.bach.test_series_timestamp import types_plus_min


@pytest.mark.parametrize("asstring", [True, False])
def test_date_comparator(asstring: bool):
    mt = get_bt_with_food_data()[['date']]

    # import code has no means to distinguish between date and timestamp
    mt['date'] = mt['date'].astype('date')

    assert_postgres_type(mt['date'], 'date', SeriesDate)

    from datetime import date
    dt = date(2021, 5, 3)

    if asstring:
        dt = str(dt)

    result = mt[mt['date'] == dt]
    assert_equals_data(
        result,
        expected_columns=['_index_skating_order', 'date'],
        expected_data=[
            [1, date(2021, 5, 3)]
        ]
    )
    assert_equals_data(
        mt[mt['date'] >= dt],
        expected_columns=['_index_skating_order', 'date'],
        expected_data=[
            [1, date(2021, 5, 3)],
            [2, date(2021, 5, 4)],
            [4, date(2022, 5, 3)]
        ]
    )

    assert_equals_data(
        mt[mt['date'] > dt],
        expected_columns=['_index_skating_order', 'date'],
        expected_data=[
            [2, date(2021, 5, 4)],
            [4, date(2022, 5, 3)]
        ]
    )

    dt = date(2022, 5, 3)
    if asstring:
        dt = str(dt)

    assert_equals_data(
        mt[mt['date'] <= dt],
        expected_columns=['_index_skating_order', 'date'],
        expected_data=[
            [1, date(2021, 5, 3)],
            [2, date(2021, 5, 4,)],
            [4, date(2022, 5, 3)]
        ]
    )

    assert_equals_data(
        mt[mt['date'] < dt],
        expected_columns=['_index_skating_order', 'date'],
        expected_data=[
            [1, date(2021, 5, 3)],
            [2, date(2021, 5, 4)]
        ]
    )


def test_date_format():
    mt = get_bt_with_food_data()[['moment', 'date']]

    mt['date'] = mt['date'].astype('date')

    assert mt['moment'].dtype == 'timestamp'
    assert mt['date'].dtype == 'date'

    assert mt['moment'].dt.sql_format('YYYY').dtype == 'string'

    mt['fyyyy'] = mt['moment'].dt.sql_format('YYYY')
    mt['fday'] = mt['date'].dt.sql_format('Day')

    assert_equals_data(
        mt[['fyyyy', 'fday']],
        expected_columns=['_index_skating_order', 'fyyyy', 'fday'],
        expected_data=[
            [1, '2021', 'Monday   '],
            [2, '2021', 'Tuesday  '],
            [4, '2022', 'Tuesday  ']
        ]
    )


def test_date_arithmetic():
    data = [
        ['d', datetime.date(2020, 3, 11), 'date', (None, 'timedelta')],
        ['t', datetime.time(23, 11, 5), 'time', (None, None)],
        ['td', datetime.timedelta(days=321, seconds=9877), 'timedelta', ('date', 'date')],
        ['dt', datetime.datetime(2021, 5, 3, 11, 28, 36, 388000), 'timestamp', (None, None)]
    ]
    types_plus_min(data, datetime.date(2021, 7, 23), 'date')


def test_to_pandas():
    bt = get_bt_with_test_data()
    bt['d'] = datetime.date(2020, 3, 11)
    bt[['d']].to_pandas()
    assert bt[['d']].to_numpy()[0] == [datetime.date(2020, 3, 11)]
