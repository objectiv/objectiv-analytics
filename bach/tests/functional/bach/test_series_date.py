"""
Copyright 2021 Objectiv B.V.
"""
import datetime

import pandas as pd
import pytest

from bach import SeriesDate, DataFrame
from sql_models.util import is_bigquery, is_postgres
from tests.functional.bach.test_data_and_utils import assert_equals_data, get_bt_with_food_data, \
    assert_postgres_type, get_df_with_test_data, get_df_with_food_data
from tests.functional.bach.test_series_timestamp import types_plus_min


@pytest.mark.parametrize("asstring", [True, False])
def test_date_comparator(asstring: bool, engine):
    mt = get_df_with_food_data(engine)[['date']]

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


def test_date_format(engine, recwarn):
    timestamp = datetime.datetime(2021, 5, 3, 11, 28, 36, 388000)
    date = datetime.date(2022, 1, 1)

    pdf = pd.DataFrame({'timestamp_series': [timestamp], 'date_series': [date]})
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True).reset_index(drop=True)

    same_result_formats = [
        '%Y', '%g%Y', '%Y-%m-%d', '%Y%m%d-%Y%m-%m%d-%d', '%Y%m-%d%d',  '%Y%Y%Y'
    ]
    edge_cases = [
        '%Y-%%%m-%d', '%s', 'abc %Y def%', '"abc" %Y "def"%', '%H:%M:%S %f', '%H:%M:%S MS', 'HH24:MI:SS MS',
    ]

    for idx, fmt in enumerate(same_result_formats + edge_cases):
        df[f'date_f{idx}'] = df['date_series'].dt.strftime(fmt)
        df[f'timestamp_f{idx}'] = df['timestamp_series'].dt.strftime(fmt)

    amount_of_srf_cols = (len(same_result_formats) + 1) * 2
    expected_columns = df.columns[2:amount_of_srf_cols]
    assert_equals_data(
        df[expected_columns],
        expected_columns=expected_columns,
        expected_data=[
            [
                '2022', '2021',
                '212022', '212021',
                '2022-01-01', '2021-05-03',
                '20220101-202201-0101-01', '20210503-202105-0503-03',
                '202201-0101', '202105-0303',
                '202220222022', '202120212021',
            ]
        ]
    )

    if is_postgres(engine):
        expected_data = [
            [
                '2022-%%01-01', '2021-%%05-03',
                '%s', '%s',  # there is no code for epoch
                'aad 2022 7ef%', 'aad 2021 2ef%',  # bc is era indicator, d is day of week in PG
                'abc 2022 def%', 'abc 2021 def%',  # skipping arbitrary text
                '00:00:00 000000', '11:28:36 388000',
                '00:00:00 000', '11:28:36 388',
                '00:00:00 000', '11:28:36 388',
            ]
        ]
    else:
        expected_data = [
            [
                '2022-%01-01', '2021-%05-03',
                '%s', '1620041316',
                'abc 2022 def%', 'abc 2021 def%',
                '"abc" 2022 "def"%', '"abc" 2021 "def"%',
                '%H:%M:%S %f', '11:28:36 %f',  # bq does not support microseconds format
                '%H:%M:%S MS', '11:28:36 MS',  # bq hour codes don't work for dates
                'HH24:MI:SS MS', 'HH24:MI:SS MS',
            ]
        ]

    expected_columns = df.columns[amount_of_srf_cols:]
    assert_equals_data(df[expected_columns], expected_columns=expected_columns, expected_data=expected_data)


def test_date_arithmetic(pg_engine):
    # TODO: BigQuery
    data = [
        ['d', datetime.date(2020, 3, 11), 'date', (None, 'timedelta')],
        ['t', datetime.time(23, 11, 5), 'time', (None, None)],
        ['td', datetime.timedelta(days=321, seconds=9877), 'timedelta', ('date', 'date')],
        ['dt', datetime.datetime(2021, 5, 3, 11, 28, 36, 388000), 'timestamp', (None, None)]
    ]
    types_plus_min(pg_engine, data, datetime.date(2021, 7, 23), 'date')


def test_to_pandas(engine):
    bt = get_df_with_test_data(engine)
    bt['d'] = datetime.date(2020, 3, 11)
    bt[['d']].to_pandas()
    assert bt[['d']].to_numpy()[0] == [datetime.date(2020, 3, 11)]
