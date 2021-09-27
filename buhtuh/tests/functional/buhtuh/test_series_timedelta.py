"""
Copyright 2021 Objectiv B.V.
"""
from tests.functional.buhtuh.data_and_utils import assert_equals_data, get_bt_with_food_data


def test_timedelta():
    mt = get_bt_with_food_data()[['skating_order', 'moment']]

    # import code has no means to distinguish between date and timestamp
    gb = mt.groupby([]).aggregate(['moment', 'moment'], ['min', 'max'])
    gb['delta'] = gb['moment_max'] - gb['moment_min']

    import datetime

    assert_equals_data(
        gb,
        expected_columns=['index', 'moment_min', 'moment_max', 'delta'],
        expected_data=[
            [1, datetime.datetime(2021, 5, 3, 11, 28, 36, 388000), datetime.datetime(2022, 5, 3, 14, 13, 13, 388000), datetime.timedelta(days=365, seconds=9877)]
        ]
    )

    r2 = gb.groupby([])['delta'].average()
    assert_equals_data(
        r2,
        expected_columns=['index', 'delta_average'],
        expected_data=[
            [1, datetime.timedelta(days=365, seconds=9877)]
        ]
    )

    r3 = r2['delta_average'] + datetime.timedelta()
    assert_equals_data(
        r3,
        expected_columns=['index', 'delta_average'],
        expected_data=[
            [1, datetime.timedelta(days=365, seconds=9877)]
        ]
    )
