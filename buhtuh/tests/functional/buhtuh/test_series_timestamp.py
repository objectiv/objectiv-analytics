"""
Copyright 2021 Objectiv B.V.
"""
import pytest

from tests.functional.buhtuh.test_bt import get_bt_with_food_data, assert_equals_data


def test_timestamp_data():
    mt = get_bt_with_food_data()[['moment']]
    from datetime import datetime
    assert_equals_data(
        mt,
        expected_columns=['_index_skating_order', 'moment'],
        expected_data=[
            [1, datetime(2021, 5, 3, 11, 28, 36, 388000)],
            [2, datetime(2021, 5, 4, 23, 28, 36, 388000)],
            [4, datetime(2022, 5, 3, 14, 13, 13, 388000)]
        ]
    )


@pytest.mark.parametrize("asstring", [True, False])
def test_timestamp_comparator(asstring: bool):
    mt = get_bt_with_food_data()[['moment']]
    from datetime import datetime
    dt = datetime(2021, 5, 3, 11, 28, 36, 388000)

    if asstring:
        dt = str(dt)

    result = mt[mt['moment'] == dt]
    assert_equals_data(
        result,
        expected_columns=['_index_skating_order', 'moment'],
        expected_data=[
            [1, datetime(2021, 5, 3, 11, 28, 36, 388000)]
        ]
    )

    assert_equals_data(
        mt[mt['moment'] >= dt],
        expected_columns=['_index_skating_order', 'moment'],
        expected_data=[
            [1, datetime(2021, 5, 3, 11, 28, 36, 388000)],
            [2, datetime(2021, 5, 4, 23, 28, 36, 388000)],
            [4, datetime(2022, 5, 3, 14, 13, 13, 388000)]
        ]
    )

    assert_equals_data(
        mt[mt['moment'] > dt],
        expected_columns=['_index_skating_order', 'moment'],
        expected_data=[
            [2, datetime(2021, 5, 4, 23, 28, 36, 388000)],
            [4, datetime(2022, 5, 3, 14, 13, 13, 388000)]
        ]
    )

    dt = datetime(2022, 5, 3, 14, 13, 13, 388000)
    if asstring:
        dt = str(dt)

    assert_equals_data(
        mt[mt['moment'] <= dt],
        expected_columns=['_index_skating_order', 'moment'],
        expected_data=[
            [1, datetime(2021, 5, 3, 11, 28, 36, 388000)],
            [2, datetime(2021, 5, 4, 23, 28, 36, 388000)],
            [4, datetime(2022, 5, 3, 14, 13, 13, 388000)]
        ]
    )

    assert_equals_data(
        mt[mt['moment'] < dt],
        expected_columns=['_index_skating_order', 'moment'],
        expected_data=[
            [1, datetime(2021, 5, 3, 11, 28, 36, 388000)],
            [2, datetime(2021, 5, 4, 23, 28, 36, 388000)]
        ]
    )


def test_date_format():
    mt = get_bt_with_food_data()[['moment', 'date']]

    mt['date'] = mt['date'].astype('date')

    assert mt['moment'].dtype == 'timestamp'
    assert mt['date'].dtype == 'date'

    assert mt['moment'].format('YYYY').dtype == 'string'

    mt['fyyyy'] = mt['moment'].format('YYYY')
    mt['fday'] = mt['date'].format('Day')

    assert_equals_data(
        mt[['fyyyy', 'fday']],
        expected_columns=['_index_skating_order', 'fyyyy', 'fday'],
        expected_data=[
            [1, '2021', 'Monday   '],
            [2, '2021', 'Tuesday  '],
            [4, '2022', 'Tuesday  ']
        ]
    )
