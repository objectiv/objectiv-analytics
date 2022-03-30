"""
Copyright 2021 Objectiv B.V.
"""
import datetime
from typing import Type
import pytest

import numpy as np

from bach import SeriesInt64, SeriesString, SeriesFloat64, SeriesDate, SeriesTimestamp, \
    SeriesTime, SeriesTimedelta, Series, \
    SeriesJsonb, SeriesBoolean
from sql_models.util import is_postgres
from tests.conftest import get_postgres_engine_dialect
from tests.functional.bach.test_data_and_utils import get_bt_with_test_data, assert_db_type, \
    assert_equals_data, CITIES_INDEX_AND_COLUMNS, get_bt_with_railway_data, get_df_with_test_data


def check_set_const(engine, constant, expected_series: Type[Series], pg_db_type: str):
    bt = get_df_with_test_data(engine)
    bt['new_column'] = constant

    if is_postgres(engine):
        # we don't have an easy way to get the database type in BigQuery, so only support that check for PG
        assert_db_type(bt['new_column'], pg_db_type, expected_series)

    assert_equals_data(
        bt,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding',  # original columns
            'new_column'  # new
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, constant],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, constant],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, constant]
        ]
    )
    assert bt.new_column == bt['new_column']


def test_set_const_int(engine):
    check_set_const(engine, np.int64(4), SeriesInt64, 'bigint')
    check_set_const(engine, 5, SeriesInt64, 'bigint')
    check_set_const(engine, 2147483647, SeriesInt64, 'bigint')
    check_set_const(engine, 2147483648, SeriesInt64, 'bigint')


def test_set_const_float(engine):
    check_set_const(engine, 5.1, SeriesFloat64, 'double precision')


def test_set_const_bool(engine):
    check_set_const(engine, True, SeriesBoolean, 'boolean')


def test_set_const_str(engine):
    check_set_const(engine, 'keatsen', SeriesString, 'text')


def test_set_const_date(engine):
    check_set_const(engine, datetime.date(2019, 1, 5), SeriesDate, 'date')


def test_set_const_datetime(engine):
    check_set_const(engine, datetime.datetime.now(), SeriesTimestamp, 'timestamp without time zone')


def test_set_const_time(engine):
    check_set_const(
        engine,
        datetime.time.fromisoformat('00:05:23.283'),
        SeriesTime,
        'time without time zone'
    )


def test_set_const_timedelta():
    engine = get_postgres_engine_dialect().engine  # TODO: BigQuery
    check_set_const(
        engine,
        np.datetime64('2005-02-25T03:30') - np.datetime64('2005-01-25T03:30'),
        SeriesTimedelta,
        'interval'
    )
    check_set_const(
        engine,
        datetime.datetime.now() - datetime.datetime(2015, 4, 6),
        SeriesTimedelta,
        'interval'
    )


def test_set_const_json():
    engine = get_postgres_engine_dialect().engine  # TODO: BigQuery
    check_set_const(engine, ['a', 'b', 'c'], SeriesJsonb, 'jsonb')
    check_set_const(engine, {'a': 'b', 'c': 'd'}, SeriesJsonb, 'jsonb')


def test_set_const_int_from_series():
    bt = get_bt_with_test_data()[['founding']]
    max = bt.groupby()[['founding']].sum()
    max_series = max['founding_sum']
    max_value = max_series.value
    bt['max_founding'] = max_value
    assert_db_type(bt['max_founding'], 'bigint', SeriesInt64, )

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


def test_set_series_column():
    bt = get_bt_with_test_data()
    bt['duplicated_column'] = bt['founding']
    assert_db_type(bt['duplicated_column'], 'bigint', SeriesInt64)
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

    bt['spaces in column'] = bt['founding']
    assert_equals_data(
        bt,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding', 'duplicated_column', 'spaces in column'
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 1285, 1285],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 1456, 1456],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 1268, 1268],
        ]
    )

    filtered_bt = bt[bt['city'] == 'Ljouwert']
    filtered_bt['town'] = filtered_bt['city']
    assert_equals_data(
        filtered_bt,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding', 'duplicated_column', 'spaces in column', 'town'
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 1285, 1285, 'Ljouwert']
        ]
    )
    assert filtered_bt.town == filtered_bt['town']

def test_set_multiple():
    bt = get_bt_with_test_data()
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


def test_set_existing():
    bt = get_bt_with_test_data()
    bt['city'] = bt['founding']
    assert_db_type(bt['city'], 'bigint', SeriesInt64)
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


def test_set_different_base_node():
    # set different shape series / different index name
    bt = get_bt_with_test_data(full_data_set=True)
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
    bt = get_bt_with_test_data()
    mt = get_bt_with_railway_data()
    bt['skating_order'] = mt['station']
    assert_db_type(bt['skating_order'], 'text', SeriesString)
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
    bt = get_bt_with_test_data()
    mt = get_bt_with_railway_data()
    bt[['a','city']] = mt[['town','station']]
    assert_equals_data(
        bt,
        expected_columns=CITIES_INDEX_AND_COLUMNS + ['a'],
        expected_data=[
            [1, 1, 'IJlst', 'Leeuwarden', 93485, 1285, 'Drylts'],
            [2, 2, 'Heerenveen', 'Súdwest-Fryslân', 33520, 1456, 'It Hearrenfean'],
            [3, 3, 'Heerenveen IJsstadion', 'Súdwest-Fryslân', 3055, 1268, 'It Hearrenfean']
        ]
    )


def test_set_different_group_by():
    bt = get_bt_with_test_data(full_data_set=True)
    mt = get_bt_with_railway_data()
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


def test_set_existing_referencing_other_column_experience():
    bt = get_bt_with_test_data()
    bt['city'] = bt['city'] + ' test'
    assert_db_type(bt['city'], 'text', SeriesString)
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

    bt = get_bt_with_test_data()
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
    assert_db_type(bt['skating_order'], 'bigint', SeriesInt64)
    assert_db_type(bt['city'], 'text', SeriesString)
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


def test_set_series_expression():
    bt = get_bt_with_test_data()
    bt['time_travel'] = bt['founding'] + 1000
    assert_db_type(bt['time_travel'], 'bigint', SeriesInt64, )
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


def test_set_series_single_value():
    bt = get_bt_with_test_data()[['inhabitants']]
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


def test_set_pandas_series():
    bt = get_bt_with_test_data()
    pandas_series = bt['founding'].to_pandas()
    bt['duplicated_column'] = pandas_series
    assert_db_type(bt['duplicated_column'], 'bigint', SeriesInt64)
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


def test_set_pandas_series_different_shape():
    bt = get_bt_with_test_data()
    pandas_series = bt['founding'].to_pandas()[1:]
    bt['duplicated_column'] = pandas_series
    assert_db_type(bt['duplicated_column'], 'bigint', SeriesInt64)
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


def test_set_pandas_series_different_shape_and_name():
    bt = get_bt_with_test_data()
    bt2 = get_bt_with_railway_data()  # has more rows and different name index
    pandas_series = bt2['town'].to_pandas()
    bt['the_town'] = pandas_series
    assert_db_type(bt['the_town'], 'text', SeriesString)
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
