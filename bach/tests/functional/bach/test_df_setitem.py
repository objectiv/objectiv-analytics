"""
Copyright 2021 Objectiv B.V.
"""
import datetime
from typing import Type, Any, List

import pandas
import pytest
import numpy as np
from pandas.core.indexes.numeric import Int64Index

from bach import SeriesInt64, SeriesString, SeriesFloat64, SeriesDate, SeriesTimestamp, \
    SeriesTime, SeriesTimedelta, Series, SeriesJson, SeriesBoolean
from sql_models.util import is_bigquery
from tests.functional.bach.test_data_and_utils import assert_postgres_type, assert_equals_data, \
    CITIES_INDEX_AND_COLUMNS,  get_df_with_test_data, get_df_with_railway_data


def check_set_const(engine, constants: List[Any], expected_series: Type[Series], expected_pg_db_type: str):
    bt = get_df_with_test_data(engine)
    column_names = []
    for i, constant in enumerate(constants):
        column_name = f'new_columns_{i}'
        column_names.append(column_name)
        bt[column_name] = constant

    for column_name in column_names:
        # we don't have an easy way to get the database type in BigQuery, so only support that check for PG
        assert_postgres_type(bt[column_name], expected_pg_db_type, expected_series)

    assert_equals_data(
        bt,
        use_to_pandas=True,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding',  # original columns
        ] + column_names,
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285] + constants,
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456] + constants,
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268] + constants
        ]
    )


def test_set_const_int(engine):
    constants = [
        np.int64(4),
        5,
        2147483647,
        2147483648
    ]
    check_set_const(engine, constants, SeriesInt64, 'bigint')


def test_set_const_float(engine):
    constants = [
        5.1,
        -5.1
    ]
    check_set_const(engine, constants, SeriesFloat64, 'double precision')
    # See also tests.functional.bach.test_series_float.test_from_value(), which tests some interesting
    # special cases.


def test_set_const_bool(engine):
    constants = [
        True,
        False
    ]
    check_set_const(engine, constants, SeriesBoolean, 'boolean')


def test_set_const_str(engine):
    constants = [
        'keatsen'
    ]
    check_set_const(engine, constants, SeriesString, 'text')


def test_set_const_date(engine):
    constants = [
        datetime.date(2019, 1, 5)
    ]
    check_set_const(engine, constants, SeriesDate, 'date')


def test_set_const_datetime(engine):
    constants = [
        datetime.datetime.now(),
        datetime.datetime(1999, 1, 15, 13, 37, 1, 23),
        np.datetime64('2022-01-01 12:34:56.7800'),
    ]
    check_set_const(engine, constants, SeriesTimestamp, 'timestamp without time zone')


def test_set_const_time(engine):
    constants = [
        datetime.time.fromisoformat('00:05:23.283')
    ]
    check_set_const(engine, constants, SeriesTime, 'time without time zone')


def test_set_const_timedelta(engine):
    constants = [
        np.datetime64('2005-02-25T03:30') - np.datetime64('2005-01-25T03:30'),
        datetime.datetime.now() - datetime.datetime(2015, 4, 6),
    ]
    check_set_const(engine, constants, SeriesTimedelta, 'interval')


def test_set_const_json(engine):
    constants = [
        ['a', 'b', 'c'],
        {'a': 'b', 'c': 'd'},
    ]
    check_set_const(engine, constants, SeriesJson, expected_pg_db_type='jsonb')


def test_set_const_int_from_series(engine):
    bt = get_df_with_test_data(engine)[['founding']]
    max_df = bt.groupby()[['founding']].sum()
    max_series = max_df['founding_sum']
    max_value = max_series.value
    bt['max_founding'] = max_value
    assert_postgres_type(bt['max_founding'], 'bigint', SeriesInt64, )

    assert_equals_data(
        bt,
        expected_columns=[
            '_index_skating_order',  # index
            'founding',  # original columns
            'max_founding'  # new
        ],
        expected_data=[
            [1, 1285, 4009], [2, 1456, 4009], [3, 1268, 4009]
        ]
    )
    assert bt.max_founding == bt['max_founding']


def test_set_series_column(engine):
    bt = get_df_with_test_data(engine)
    bt['duplicated_column'] = bt['founding']
    assert_postgres_type(bt['duplicated_column'], 'bigint', SeriesInt64)
    assert_equals_data(
        bt,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding', 'duplicated_column'
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 1285],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 1456],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 1268],
        ]
    )
    assert bt.duplicated_column == bt['duplicated_column']

    filtered_bt = bt[bt['city'] == 'Ljouwert']
    filtered_bt['town'] = filtered_bt['city']
    assert_equals_data(
        filtered_bt,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding', 'duplicated_column', 'town'
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 1285, 'Ljouwert']
        ]
    )
    assert filtered_bt.town == filtered_bt['town']

@pytest.mark.skip_bigquery("Bigquery doesn't support spaces in column names")
def test_set_series_column_name_with_spaces(engine):
    bt = get_df_with_test_data(engine)
    bt['spaces in column'] = bt['founding']
    assert_equals_data(
        bt,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding', 'spaces in column'
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 1285],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 1456],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 1268],
        ]
    )


def test_set_multiple(engine):
    bt = get_df_with_test_data(engine)
    bt['duplicated_column'] = bt['founding']
    bt['alternative_sport'] = 'keatsen'
    bt['leet'] = 1337
    assert_equals_data(
        bt,
        expected_columns=CITIES_INDEX_AND_COLUMNS + ['duplicated_column', 'alternative_sport', 'leet'],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 1285, 'keatsen', 1337],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 1456, 'keatsen', 1337],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 1268, 'keatsen', 1337]
        ]
    )
    assert bt.duplicated_column == bt['duplicated_column']
    assert bt.alternative_sport == bt['alternative_sport']
    assert bt.leet == bt['leet']


def test_set_existing(engine):
    bt = get_df_with_test_data(engine)
    bt['city'] = bt['founding']
    assert_postgres_type(bt['city'], 'bigint', SeriesInt64)
    assert_equals_data(
        bt,
        expected_columns=CITIES_INDEX_AND_COLUMNS,
        expected_data=[
            [1, 1, 1285, 'Leeuwarden', 93485, 1285],
            [2, 2, 1456, 'Súdwest-Fryslân', 33520, 1456],
            [3, 3, 1268, 'Súdwest-Fryslân', 3055, 1268]
        ]
    )
    assert bt.city == bt['city']


def test_set_different_base_node(engine):
    # set different shape series / different index name
    bt = get_df_with_test_data(engine, full_data_set=True)
    bt = bt[bt.skating_order > 7]
    filtered_bt = bt[bt.skating_order < 9]

    bt['a'] = filtered_bt['city']

    assert_equals_data(
        bt,
        expected_columns=CITIES_INDEX_AND_COLUMNS + ['a'],
        expected_data=[
            [8, 8, 'Boalsert', 'Súdwest-Fryslân', 10120, 1455, 'Boalsert'],
            [9, 9, 'Harns', 'Harlingen', 14740, 1234, None],
            [10, 10, 'Frjentsjer', 'Waadhoeke', 12760, 1374, None],
            [11, 11, 'Dokkum', 'Noardeast-Fryslân', 12675, 1298, None]
        ]
    )

    # set existing column
    bt = get_df_with_test_data(engine)
    mt = get_df_with_railway_data(engine)
    bt['skating_order'] = mt['station']
    assert_postgres_type(bt['skating_order'], 'text', SeriesString)
    assert_equals_data(
        bt,
        expected_columns=CITIES_INDEX_AND_COLUMNS,
        expected_data=[
            [1, 'IJlst', 'Ljouwert', 'Leeuwarden', 93485, 1285],
            [2, 'Heerenveen', 'Snits', 'Súdwest-Fryslân', 33520, 1456],
            [3, 'Heerenveen IJsstadion', 'Drylts', 'Súdwest-Fryslân', 3055, 1268]
        ]
    )

    # set dataframe
    bt = get_df_with_test_data(engine)
    mt = get_df_with_railway_data(engine)
    bt[['a', 'city']] = mt[['town', 'station']]
    assert_equals_data(
        bt,
        expected_columns=CITIES_INDEX_AND_COLUMNS + ['a'],
        expected_data=[
            [1, 1, 'IJlst', 'Leeuwarden', 93485, 1285, 'Drylts'],
            [2, 2, 'Heerenveen', 'Súdwest-Fryslân', 33520, 1456, 'It Hearrenfean'],
            [3, 3, 'Heerenveen IJsstadion', 'Súdwest-Fryslân', 3055, 1268, 'It Hearrenfean']
        ]
    )


def test_set_different_group_by(engine):
    bt = get_df_with_test_data(engine, full_data_set=True)
    mt = get_df_with_railway_data(engine)
    bt_g = bt.groupby('city')[['inhabitants', 'founding']]
    mt_g = mt.groupby('town').station_id.count()

    with pytest.raises(ValueError, match="Setting new columns to grouped DataFrame is only supported if the"
                                         " DataFrame has aggregated columns"):
        bt_g['a'] = mt_g

    bt_g = bt_g.max()
    bt_g['a'] = mt_g

    assert_equals_data(
        bt_g,
        expected_columns=['city', 'inhabitants_max', 'founding_max', 'a'],
        expected_data=[
            ['Boalsert', 10120, 1455, None],
            ['Dokkum', 12675, 1298, None],
            ['Drylts', 3055, 1268, 1],
            ['Frjentsjer', 12760, 1374, None],
            ['Harns', 14740, 1234, None],
            ['Hylpen', 870, 1225, None],
            ['Ljouwert', 93485, 1285, 2],
            ['Sleat', 700, 1426, None],
            ['Snits', 33520, 1456, 2],
            ['Starum', 960, 1061, None],
            ['Warkum', 4440, 1399, None],

        ]
    )


def test_set_existing_referencing_other_column_experience(engine):
    bt = get_df_with_test_data(engine)
    bt['city'] = bt['city'] + ' test'
    assert_postgres_type(bt['city'], 'text', SeriesString)
    assert_equals_data(
        bt,
        expected_columns=CITIES_INDEX_AND_COLUMNS,
        expected_data=[
            [1, 1, 'Ljouwert test', 'Leeuwarden', 93485, 1285],
            [2, 2, 'Snits test', 'Súdwest-Fryslân', 33520, 1456],
            [3, 3, 'Drylts test', 'Súdwest-Fryslân', 3055, 1268]
        ]
    )
    assert bt.city == bt['city']

    bt = get_df_with_test_data(engine)
    a = bt['city'] + ' test1'
    b = bt['city'] + ' test2'
    c = bt['skating_order'] + bt['skating_order']
    bt['skating_order'] = 0
    bt['city'] = ''
    assert_equals_data(
        bt,
        expected_columns=CITIES_INDEX_AND_COLUMNS,
        expected_data=[
            [1, 0, '', 'Leeuwarden', 93485, 1285],
            [2, 0, '', 'Súdwest-Fryslân', 33520, 1456],
            [3, 0, '', 'Súdwest-Fryslân', 3055, 1268]
        ]
    )
    bt['skating_order'] = c
    bt['city'] = a + ' - ' + b
    assert_postgres_type(bt['skating_order'], 'bigint', SeriesInt64)
    assert_postgres_type(bt['city'], 'text', SeriesString)
    assert_equals_data(
        bt,
        expected_columns=CITIES_INDEX_AND_COLUMNS,
        expected_data=[
            [1, 2, 'Ljouwert test1 - Ljouwert test2', 'Leeuwarden', 93485, 1285],
            [2, 4, 'Snits test1 - Snits test2', 'Súdwest-Fryslân', 33520, 1456],
            [3, 6, 'Drylts test1 - Drylts test2', 'Súdwest-Fryslân', 3055, 1268]
        ]
    )
    assert bt.skating_order == bt['skating_order']
    assert bt.city == bt['city']


def test_set_series_expression(engine):
    bt = get_df_with_test_data(engine)
    bt['time_travel'] = bt['founding'] + 1000
    assert_postgres_type(bt['time_travel'], 'bigint', SeriesInt64, )
    assert_equals_data(
        bt,
        expected_columns=CITIES_INDEX_AND_COLUMNS + ['time_travel'],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 2285],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 2456],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 2268]
        ]
    )
    assert bt.time_travel == bt['time_travel']


def test_set_series_single_value(engine):
    bt = get_df_with_test_data(engine)[['inhabitants']]
    original_base_node = bt.base_node

    bt['const'] = 3
    bt['maxi'] = bt.inhabitants.max()
    bt['maxii'] = bt.inhabitants.max()
    assert bt.const.expression.is_single_value
    assert bt.maxi.expression.is_single_value
    # should recycle the same subquery
    assert bt.maxi.expression.get_references() == bt.maxii.expression.get_references()

    bt['moremax'] = bt.maxi + 5
    bt['constmoremax'] = bt.maxi + bt.const
    # should be reading from the same node and not create new ones
    assert bt.maxi.expression.get_references() \
           == bt.moremax.expression.get_references() \
           == bt.constmoremax.expression.get_references()
    assert bt.maxi.expression.is_single_value
    assert bt.moremax.expression.is_single_value
    assert bt.constmoremax.expression.is_single_value

    bt['moremax2'] = bt.inhabitants.max() + 6
    # a different reference, because + 6 gets added to the subquery here.
    assert bt.moremax2.expression.get_references() != bt.maxi.expression.get_references()
    assert bt.moremax2.expression.is_single_value

    bt['moremax3'] = bt.maxi + 7
    # The same reference, because + 7 gets added to the column expression
    assert bt.moremax3.expression.get_references() == bt.maxi.expression.get_references()
    assert bt.moremax3.expression.is_single_value

    # lots of subqueries added, but we were not materialized
    assert bt.base_node == original_base_node

    assert_equals_data(
        bt,
        expected_columns=['_index_skating_order', 'inhabitants', 'const', 'maxi', 'maxii',
                          'moremax', 'constmoremax',
                          'moremax2', 'moremax3'],
        expected_data=[
            [1, 93485, 3, 93485, 93485, 93490, 93488, 93491, 93492],
            [2, 33520, 3, 93485, 93485, 93490, 93488, 93491, 93492],
            [3, 3055, 3, 93485, 93485, 93490, 93488, 93491, 93492]
        ]
    )


def test_set_pandas_series(engine):
    bt = get_df_with_test_data(engine)
    pandas_series = bt['founding'].to_pandas()
    bt['duplicated_column'] = pandas_series
    assert_postgres_type(bt['duplicated_column'], 'bigint', SeriesInt64)
    assert_equals_data(
        bt,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding', 'duplicated_column'
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 1285],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 1456],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 1268],
        ]
    )


def test_set_pandas_series_different_shape(engine):
    bt = get_df_with_test_data(engine)
    pandas_series = bt['founding'].to_pandas()[1:]
    bt['duplicated_column'] = pandas_series
    assert_postgres_type(bt['duplicated_column'], 'bigint', SeriesInt64)
    assert_equals_data(
        bt,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding', 'duplicated_column'
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, None],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 1456],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 1268],
        ]
    )


def test_set_pandas_series_different_shape_and_name(engine):
    bt = get_df_with_test_data(engine)
    # Create a series with more rows and a differently named index.
    pandas_series = pandas.Series(
        data=['Drylts', 'It Hearrenfean', 'It Hearrenfean', 'Ljouwert', 'Ljouwert', 'Snits', 'Snits'],
        index=Int64Index([1, 2, 3, 4, 5, 6, 7], dtype='int64', name='_index_station_id')
    )
    bt['the_town'] = pandas_series
    assert_postgres_type(bt['the_town'], 'text', SeriesString)
    assert_equals_data(
        bt,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding', 'the_town'
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 'Drylts'],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 'It Hearrenfean'],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 'It Hearrenfean'],
        ]
    )


def test_set_pandas_series_uuid(engine):

    from tests.functional.bach.test_df_from_pandas import TYPES_DATA, TYPES_COLUMNS
    from uuid import UUID

    bt = get_df_with_test_data(engine)
    pdf = pandas.DataFrame.from_records(TYPES_DATA, columns=TYPES_COLUMNS).set_index('int_column')

    bt['u'] = pdf['uuid_column']
    assert_equals_data(
        bt,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding', 'u'
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, UUID('36ca4c0b-804d-48ff-809f-28cf9afd078a')],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, UUID('81a8ace2-273b-4b95-b6a6-0fba33858a22')],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, UUID('8a70b3d3-33ec-4300-859a-bb2efcf0b188')],
        ],
        convert_uuid=True,
    )
