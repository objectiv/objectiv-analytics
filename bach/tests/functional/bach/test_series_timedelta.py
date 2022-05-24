"""
Copyright 2021 Objectiv B.V.
"""
import datetime

import numpy as np
import pandas as pd

from bach import DataFrame
from tests.functional.bach.test_data_and_utils import get_bt_with_food_data, assert_equals_data, \
    get_bt_with_test_data
from tests.functional.bach.test_series_timestamp import types_plus_min


def test_timedelta_arithmetic(pg_engine):
    # TODO: BigQuery
    data = [
        ['d', datetime.date(2020, 3, 11), 'date', ('date', None)],
        ['t', datetime.time(23, 11, 5), 'time', (None, None)],
        ['td', datetime.timedelta(days=321, seconds=9877), 'timedelta', ('timedelta', 'timedelta')],
        ['dt', datetime.datetime(2021, 5, 3, 11, 28, 36, 388000), 'timestamp', ('timestamp', None)]
    ]
    types_plus_min(pg_engine, data, datetime.timedelta(days=123, seconds=5621), 'timedelta')


def test_timedelta_arithmetic2():
    bt = get_bt_with_test_data(full_data_set=True)[['inhabitants']]
    td = datetime.timedelta(days=365, seconds=9877)
    td2 = datetime.timedelta(days=23, seconds=12)

    bt['td'] = td
    bt['td2'] = td2
    expected = [td, td2]
    expected_types = ['timedelta', 'timedelta']

    # special timedelta ops only, rest is tested elsewhere
    bt['mul'] = bt.td * 5
    bt['div'] = bt.td / 5
    expected.extend([td * 5, td / 5])
    expected_types.extend(['timedelta', 'timedelta'])

    assert [s.dtype for s in list(bt.all_series.values())[2:]] == expected_types

    assert_equals_data(
        bt.sort_index()[:1],
        expected_columns=list(bt.all_series.keys()),
        expected_data=[
            [1, 93485, *expected],
        ]
    )


def test_timedelta():
    mt = get_bt_with_food_data()[['skating_order', 'moment']]

    # import code has no means to distinguish between date and timestamp
    gb = mt.groupby([]).aggregate({'moment': ['min', 'max']})
    gb['delta'] = gb['moment_max'] - gb['moment_min']

    assert_equals_data(
        gb,
        expected_columns=['moment_min', 'moment_max', 'delta'],
        expected_data=[
            [datetime.datetime(2021, 5, 3, 11, 28, 36, 388000), datetime.datetime(2022, 5, 3, 14, 13, 13, 388000), datetime.timedelta(days=365, seconds=9877)]
        ]
    )

    r2 = gb[['delta']].groupby().mean()
    assert_equals_data(
        r2,
        expected_columns=['delta_mean'],
        expected_data=[
            [datetime.timedelta(days=365, seconds=9877)]
        ]
    )

    r3 = r2['delta_mean'] + datetime.timedelta()
    assert_equals_data(
        r3,
        expected_columns=['delta_mean'],
        expected_data=[
            [datetime.timedelta(days=365, seconds=9877)]
        ]
    )


def test_to_pandas():
    bt = get_bt_with_test_data()
    bt['td'] = datetime.timedelta(days=321, seconds=9877)
    bt[['td']].to_pandas()
    # TODO, this is not great, but at least it does not error when imported into pandas,
    # and it looks good over there
    assert bt[['td']].to_numpy()[0] == [27744277000000000]


def test_timedelta_operations(pg_engine):
    pdf = pd.DataFrame(
        data={
            'start_date': [
                datetime.datetime(year=2022, month=1, day=d) for d in range(1, 17)
            ],
            'end_date': [
                datetime.datetime(year=2022, month=m, day=d) for m in range(2, 4) for d in range(1, 9)
            ]
        }
    )
    df = DataFrame.from_pandas(engine=pg_engine, df=pdf, convert_objects=True)

    pdf['diff'] = pdf['end_date'] - pdf['start_date']
    df['diff'] = df['end_date'] - df['start_date']

    result = df['diff'].quantile(q=[0.25, 0.5, .75])
    expected = pdf['diff'].quantile(q=[0.25, 0.5, .75])
    np.testing.assert_equal(expected.to_numpy(), result.sort_index().to_numpy())


def test_timedelta_dt_properties(pg_engine) -> None:
    pdf = pd.DataFrame(
        data={
            'start_date': [
                np.datetime64("2022-01-01 12:34:56.7800"),
                np.datetime64("2022-01-05 01:23:45.6700"),
                np.datetime64("2022-01-10 02:34:56.7800"),
            ],
            'end_date': [
                np.datetime64("2022-01-03"),
                np.datetime64("2022-01-06"),
                np.datetime64("2022-01-10"),
            ]
        }
    )
    df = DataFrame.from_pandas(engine=pg_engine, df=pdf, convert_objects=True)

    pdf['diff'] = pdf['end_date'] - pdf['start_date']
    df['diff'] = df['end_date'] - df['start_date']

    dt_properties = ['days', 'seconds', 'microseconds']
    properties_df = df.copy_override(
        series={
            p: getattr(df['diff'].dt, p)
            for p in dt_properties
        }
    )
    properties_pdf = pd.DataFrame(data={p: getattr(pdf['diff'].dt, p) for p in dt_properties})

    pd.testing.assert_frame_equal(
        properties_pdf,
        properties_df.sort_index().to_pandas(),
        check_dtype=False,
        check_names=False,
    )

    properties_df['total_seconds'] = df['diff'].dt.total_seconds

    expected_data = [
        [1., 41103., 220000., 127503.22],
        [0., 81374., 330000., 81374.33],
        [-1., 77103., 220000., -9296.78],
    ]
    np.testing.assert_equal(
        expected_data, properties_df.sort_index().to_numpy()
    )


def test_timedelta_dt_components(pg_engine) -> None:
    pdf = pd.DataFrame(
        data={
            'start_date': [
                np.datetime64("2022-01-01 12:34:56.7800"),
                np.datetime64("2022-01-05 01:23:45.6700"),
            ],
            'end_date': [
                np.datetime64("2022-01-03"),
                np.datetime64("2022-01-06"),
            ]
        }
    )
    df = DataFrame.from_pandas(engine=pg_engine, df=pdf, convert_objects=True)

    pdf['diff'] = pdf['end_date'] - pdf['start_date']
    df['diff'] = df['end_date'] - df['start_date']

    components = ['days', 'hours', 'minutes', 'seconds', 'milliseconds']
    result = df['diff'].dt.components.sort_index().to_pandas()[components]
    expected = pdf['diff'].dt.components[components]

    pd.testing.assert_frame_equal(expected, result, check_names=False)


