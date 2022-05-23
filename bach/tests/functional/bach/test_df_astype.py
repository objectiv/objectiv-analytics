"""
Copyright 2021 Objectiv B.V.
"""
from datetime import date, datetime, time

import pytest

from tests.functional.bach.test_data_and_utils import assert_equals_data, get_df_with_json_data, \
    CITIES_INDEX_AND_COLUMNS, get_df_with_test_data


def test_astype_dtypes(engine):
    # case 1: cast all columns to a type
    bt = get_df_with_test_data(engine)
    bt_int = bt[['inhabitants', 'founding']]
    bt_float = bt_int.astype('float64')
    assert bt_int.dtypes == {'founding': 'int64', 'inhabitants': 'int64'}
    assert bt_float.dtypes == {'founding': 'float64', 'inhabitants': 'float64'}

    # case 2: cast specific columns to a type
    # pre-test check
    assert bt.dtypes == {
        'city': 'string',
        'founding': 'int64',
        'inhabitants': 'int64',
        'municipality': 'string',
        'skating_order': 'int64'
    }
    # 2.1: no columns specified
    bt_none_changed = bt.astype({})
    assert bt_none_changed.dtypes == bt.dtypes
    # 2.1: one column specified
    bt_astype1 = bt.astype({
        'inhabitants': 'float64'
    })
    assert bt_astype1.dtypes == {
        'city': 'string',
        'founding': 'int64',
        'inhabitants': 'float64',   # changed
        'municipality': 'string',
        'skating_order': 'int64'
    }

    # 2.2: Multiple columns specified
    bt_astype2 = bt.astype({
        'founding': 'float64',
        'inhabitants': 'string',
        'city': 'string',  # not changed,
        'skating_order': 'string'
    })
    assert bt_astype2.dtypes == {
        'city': 'string',
        'founding': 'float64',
        'inhabitants': 'string',
        'municipality': 'string',
        'skating_order': 'string'
    }
    assert bt.data['city'] is bt_astype2.data['city']
    assert bt.data['founding'] is not bt_astype2.data['founding']
    assert bt.data['inhabitants'] is not bt_astype2.data['inhabitants']
    assert bt.data['municipality'] is bt_astype2.data['municipality']
    assert bt.data['skating_order'] is not bt_astype2.data['skating_order']
    assert_equals_data(
        bt_astype2,
        expected_columns=CITIES_INDEX_AND_COLUMNS,
        expected_data=[
            [1, '1', 'Ljouwert', 'Leeuwarden', '93485', 1285],
            [2, '2', 'Snits', 'Súdwest-Fryslân', '33520', 1456],
            [3, '3', 'Drylts', 'Súdwest-Fryslân', '3055', 1268]
        ]
    )


def test_astype_to_int(engine):
    bt = get_df_with_test_data(engine)
    bt = bt[['inhabitants']]
    bt['inhabitants'] = bt['inhabitants'] / 1000
    bt_int = bt.astype('int64')
    assert bt.dtypes == {'inhabitants': 'float64'}
    assert bt_int.dtypes == {'inhabitants': 'int64'}
    assert_equals_data(
        bt,
        expected_columns=['_index_skating_order', 'inhabitants'],
        expected_data=[
            [1, 93.485],
            [2, 33.520],
            [3, 3.055]
        ]
    )
    # When converted to ints, data will be rounded to nearest integer.
    assert_equals_data(
        bt_int,
        expected_columns=['_index_skating_order', 'inhabitants'],
        expected_data=[
            [1, 93],
            [2, 34],
            [3, 3]
        ]
    )


def test_astype_to_bool(engine):
    bt = get_df_with_test_data(engine)
    bt = bt[['skating_order']]
    bt['skating_order'] = bt['skating_order'] - 1
    bt['t'] = 'True'
    bt['f'] = 'False'
    bt = bt.astype('bool')
    assert_equals_data(
        bt,
        expected_columns=['_index_skating_order', 'skating_order', 't', 'f'],
        expected_data=[
            [1, False, True, False],
            [2, True, True, False ],
            [3, True, True, False ]
        ]
    )


def test_astype_to_date(engine):
    bt = get_df_with_test_data(engine)
    bt = bt[[]]
    bt['d'] = '1999-12-31'
    bt = bt.astype('date')
    assert_equals_data(
        bt,
        expected_columns=['_index_skating_order', 'd'],
        expected_data=[[1, date(1999, 12, 31)], [2, date(1999, 12, 31)], [3, date(1999, 12, 31)]]
    )


def test_astype_to_timestamp(engine):
    bt = get_df_with_test_data(engine)
    bt = bt[[]]
    bt['d'] = date(2022, 3, 31)
    bt['s'] = '2022-02-15 13:37:00'
    bt = bt.astype('timestamp')
    assert_equals_data(
        bt,
        use_to_pandas=True,
        expected_columns=['_index_skating_order', 'd', 's'],
        expected_data=[
            [1, datetime(2022, 3, 31, 0, 0), datetime(2022, 2, 15, 13, 37)],
            [2, datetime(2022, 3, 31, 0, 0), datetime(2022, 2, 15, 13, 37)],
            [3, datetime(2022, 3, 31, 0, 0), datetime(2022, 2, 15, 13, 37)]
        ]
    )


def test_astype_to_time(engine):
    bt = get_df_with_test_data(engine)
    bt = bt[[]]
    bt['a'] = '03:04:00'
    bt['b'] = '23:25:59'
    bt = bt.astype('time')
    assert_equals_data(
        bt,
        expected_columns=['_index_skating_order', 'a', 'b'],
        expected_data=[
            [1, time(3, 4, 0), time(23, 25, 59)],
            [2, time(3, 4, 0), time(23, 25, 59)],
            [3, time(3, 4, 0), time(23, 25, 59)]
        ]
    )

@pytest.mark.parametrize('dtype', ('json', 'jsonb'))
def test_astype_to_json(pg_engine, dtype):
    # TODO: BigQuery
    bt = get_df_with_json_data(engine=pg_engine, dtype='string')
    assert bt.dict_column.dtype == 'string'
    bt_json_dict = bt.dict_column.astype(dtype)
    bt_json_list = bt.list_column.astype(dtype)
    bt_json_mixed = bt.mixed_column.astype(dtype)
    assert_equals_data(
        bt_json_dict,
        expected_columns=['_index_row', 'dict_column'],
        expected_data=[
            [0, {"a": "b"}],
            [1, {"_type": "SectionContext", "id": "home"}],
            [2, {"a": "b", "c": {"a": "c"}}],
            [3, {"a": "b", "e": [{"a": "b"}, {"c": "d"}]}]
        ]
    )
    assert_equals_data(
        bt_json_list,
        expected_columns=['_index_row', 'list_column'],
        expected_data=[
            [0, [{"a": "b"}, {"c": "d"}]],
            [1, ["a", "b", "c", "d"]],
            [2, [{"_type": "a", "id": "b"}, {"_type": "c", "id": "d"}, {"_type": "e", "id": "f"}]],
            [3, [{"_type": "WebDocumentContext", "id": "#document"}, {"_type": "SectionContext", "id": "home"}, {"_type": "SectionContext", "id": "top-10"}, {"_type": "ItemContext", "id": "5o7Wv5Q5ZE"}]]
        ]
    )
    assert_equals_data(
        bt_json_mixed,
        expected_columns=['_index_row', 'mixed_column'],
        expected_data=[
            [0, {"a": "b"}],
            [1, ["a", "b", "c", "d"]],
            [2, {"a": "b", "c": {"a": "c"}}],
            [3, [{"_type": "WebDocumentContext", "id": "#document"}, {"_type": "SectionContext", "id": "home"}, {"_type": "SectionContext", "id": "top-10"}, {"_type": "ItemContext", "id": "5o7Wv5Q5ZE"}]]
        ]
    )
