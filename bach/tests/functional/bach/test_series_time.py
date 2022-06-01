"""
Copyright 2021 Objectiv B.V.
"""
import datetime

from tests.functional.bach.test_data_and_utils import get_df_with_test_data
from tests.functional.bach.test_series_timestamp import types_plus_min


def test_time_arithmetic(engine):
    data = [
        ['d', datetime.date(2020, 3, 11), 'date', (None, None)],
        ['t', datetime.time(23, 11, 5), 'time', (None, None)],
        ['td', datetime.timedelta(days=321, seconds=9877), 'timedelta', (None, None)],
        ['dt', datetime.datetime(2021, 5, 3, 11, 28, 36, 388000), 'timestamp', (None, None)]
    ]
    types_plus_min(engine, data, datetime.time(13, 11, 5), 'time')


def test_to_pandas(engine):
    bt = get_df_with_test_data(engine)
    bt['t'] = datetime.time(23, 11, 5)
    bt[['t']].to_pandas()
    assert bt[['t']].to_numpy()[0] == [datetime.time(23, 11, 5)]
