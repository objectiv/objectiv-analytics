"""
Copyright 2021 Objectiv B.V.
"""
import datetime

import pandas as pd
import pytest

from bach import SeriesDate
from sql_models.util import is_bigquery, is_postgres
from tests.functional.bach.test_data_and_utils import assert_equals_data, get_bt_with_food_data, \
    assert_postgres_type, get_df_with_test_data, get_df_with_food_data
from tests.functional.bach.test_series_timestamp import types_plus_min
from bach.series.utils.datetime_formats import _STANDARD_DATE_FORMAT_CODES

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


def test_date_format_timestamp(engine):
    mt = get_df_with_food_data(engine)[['moment']]

    assert mt['moment'].dtype == 'timestamp'
    assert mt['moment'].dt.sql_format('YYYY').dtype == 'string'

    if is_bigquery(engine):
        non_supported_codes = [
            'DAY_OF_MONTH_SUPPRESSED',
            'DAY_OF_YEAR_SUPPRESSED',
            'MONTH_NUMBER_SUPPRESSED',
            'HOUR24_SUPPRESSED',
            'HOUR12_SUPPRESSED',
            'MINUTE_SUPPRESSED',
            'SECOND_SUPPRESSED',
            'MICROSECOND',
        ]
    elif is_postgres(engine):
        non_supported_codes = [
            'WEEK_NUMBER_OF_YEAR_SUNDAY_FIRST',
            'WEEK_NUMBER_OF_YEAR_MONDAY_FIRST',
            'DAY_OF_MONTH_PRECEDED_BY_A_SPACE',
            'HOUR24_PRECEDED_BY_A_SPACE',
            'HOUR12_PRECEDED_BY_A_SPACE',
            'NEW_LINE',
            'TAB',
            'PERCENT_CHAR',
        ]
    else:
        raise Exception()

    # datetime.strftime does not support quarter but BQ and Postgres do
    # epoch might yield a different value for BQ due to UTC
    pandas_non_supported_codes = ['QUARTER', 'EPOCH', 'UTC_OFFSET', 'TIME_ZONE_NAME']
    pmt = mt.to_pandas()
    supported_codes = []
    for code_name, code in _STANDARD_DATE_FORMAT_CODES.items():
        pmt[code_name] = pmt['moment'].dt.strftime(code)
        mt[code_name] = mt['moment'].dt.sql_format(code)

        if code_name not in non_supported_codes and code_name not in pandas_non_supported_codes:
            supported_codes.append(code_name)

    result = mt.sort_index()
    expected = pmt[supported_codes].sort_index()

    if is_postgres(engine):
        # PG starts counting from 1
        expected['WEEKDAY_NUMBER'] = (expected['WEEKDAY_NUMBER'].astype(int) + 1).astype(str)
        expected['CENTURY'] = '21'  # datetime returns year / 100 and truncates integral part
    pd.testing.assert_frame_equal(expected, result[supported_codes].to_pandas())

    # testing non supported
    expected_columns = non_supported_codes + pandas_non_supported_codes
    if is_bigquery(engine):
        expected_data = [
            [1, '03', '123', '05', '11', '11', '28', '36', '%f', '2', '1620041316', '+0000', 'UTC'],
            [2, '04', '124', '05', '23', '11', '28', '36', '%f', '2', '1620170916', '+0000', 'UTC'],
            [4, '03', '123', '05', '14', '02', '13', '13', '%f', '2', '1651587193', '+0000', 'UTC'],
        ]
    else:
        expected_data = [
            [1, '%U', '%1', '%e', '%k', '%l', '%n', '%t', '%%', '2', '%s', '+00', ''],  # to_char(%W) is %1
            [2, '%U', '%1', '%e', '%k', '%l', '%n', '%t', '%%', '2', '%s', '+00', ''],
            [4, '%U', '%1', '%e', '%k', '%l', '%n', '%t', '%%', '2', '%s', '+00', ''],
        ]

    assert_equals_data(
        result[expected_columns],
        expected_columns=['_index_skating_order'] + expected_columns,
        expected_data=expected_data,
    )


def test_date_format_date(engine):
    mt = get_df_with_food_data(engine)[['date']]
    mt['date'] = mt['date'].astype('date')
    assert mt['date'].dtype == 'date'

    mt['date_f1'] = mt['date'].dt.sql_format('%Y-%m/%d')
    mt['date_f2'] = mt['date'].dt.sql_format('%Y-%m/%d', parse_format_str=False)
    mt['date_f3'] = mt['date'].dt.sql_format('YYYY-MM/DD', parse_format_str=False)

    if is_postgres(engine):
        expected_data = [
            [1, datetime.date(2021, 5, 3), '2021-05/03', '%1-%m/%2', '2021-05/03'],
            [2, datetime.date(2021, 5, 4), '2021-05/04', '%1-%m/%3', '2021-05/04'],
            [4, datetime.date(2022, 5, 3), '2022-05/03', '%2-%m/%3', '2022-05/03'],
        ]
    elif is_bigquery(engine):
        expected_data = [
            [1, datetime.date(2021, 5, 3), '2021-05/03', '2021-05/03', 'YYYY-MM/DD'],
            [2, datetime.date(2021, 5, 4), '2021-05/04', '2021-05/04', 'YYYY-MM/DD'],
            [4, datetime.date(2022, 5, 3), '2022-05/03', '2022-05/03', 'YYYY-MM/DD'],
        ]
    else:
        raise Exception()

    assert_equals_data(
        mt,
        expected_columns=['_index_skating_order', 'date', 'date_f1', 'date_f2', 'date_f3'],
        expected_data=expected_data,
    )


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
