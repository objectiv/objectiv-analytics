"""
Copyright 2021 Objectiv B.V.
"""
import uuid
from typing import List, Any
from unittest.mock import ANY

import pytest
from sqlalchemy.engine import Engine

from bach import SeriesUuid
from sql_models.util import is_postgres, is_bigquery
from tests.functional.bach.test_data_and_utils import assert_equals_data, run_query, get_df_with_test_data


def test_uuid_value_to_expression(engine):
    bt = get_df_with_test_data(engine)[['city']]
    bt['x'] = uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264')
    bt['y'] = '0022c7dd-074b-4a44-a7cb-b7716b668264'
    bt['yy'] = bt.y.astype('uuid')
    bt['z'] = bt.x == bt.y
    bt['zz'] = bt.x != '0022c7da-074b-4a44-a7cb-b7716b668263'
    bt['zzz'] = bt.x == bt.yy

    with pytest.raises(ValueError):
        # not a valid uuid format
        bt['yyyy'] = SeriesUuid.from_value(
            base=bt, value='0022c7dd.074b.4a44.a7cb.b7716b668264', name='tmp')

    expected_data = [
        [1, 'Ljouwert', uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'),
         '0022c7dd-074b-4a44-a7cb-b7716b668264',
         uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'), True, True, True],
        [2, 'Snits', uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'),
         '0022c7dd-074b-4a44-a7cb-b7716b668264',
         uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'), True, True, True],
        [3, 'Drylts', uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'),
         '0022c7dd-074b-4a44-a7cb-b7716b668264',
         uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'), True, True, True],
    ]

    assert_equals_data(
        bt,
        expected_columns=['_index_skating_order', 'city', 'x', 'y', 'yy', 'z', 'zz', 'zzz'],
        expected_data=expected_data,
        convert_uuid=True,
    )


def test_uuid_from_dtype_to_sql(engine):
    bt = get_df_with_test_data(engine)[['city']]
    bt['x'] = uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264')
    bt['y'] = '0022c7dd-074b-4a44-a7cb-b7716b668264'
    bt['z'] = 123456

    expected_data = [
        [1, 'Ljouwert', uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'), '0022c7dd-074b-4a44-a7cb-b7716b668264', 123456],
        [2, 'Snits', uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'), '0022c7dd-074b-4a44-a7cb-b7716b668264', 123456],
        [3, 'Drylts', uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'), '0022c7dd-074b-4a44-a7cb-b7716b668264', 123456],
    ]
    assert_equals_data(
        bt,
        expected_columns=['_index_skating_order', 'city', 'x', 'y', 'z'],
        expected_data=expected_data,
        convert_uuid=True,
    )

    bt = bt.astype({'x': 'uuid'})
    bt = bt.astype({'y': 'uuid'})
    with pytest.raises(Exception):
        bt = bt.astype({'z': 'uuid'})
    expected_data = [
        [1, 'Ljouwert', uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'), uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'), 123456],
        [2, 'Snits', uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'), uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'), 123456],
        [3, 'Drylts', uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'), uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'), 123456],
    ]
    assert_equals_data(
        bt,
        expected_columns=['_index_skating_order', 'city', 'x', 'y', 'z'],
        expected_data=expected_data,
        convert_uuid=True,
    )


def test_uuid_random(engine):
    bt = get_df_with_test_data(engine)[['city']]
    bt['x'] = SeriesUuid.random(base=bt)
    assert_equals_data(
        bt,
        expected_columns=['_index_skating_order', 'city', 'x'],
        expected_data=[
            [1, 'Ljouwert', ANY],
            [2, 'Snits', ANY],
            [3, 'Drylts', ANY],
        ]
    )
    # Check that the ANY values are 1) uuids, and 2) distinct values
    sql = bt.view_sql()
    db_rows = run_query(bt.engine, sql)
    uuid_values = [row['x'] for row in db_rows]
    if is_postgres(engine):
        assert all(isinstance(val, uuid.UUID) for val in uuid_values)
    elif is_bigquery(engine):
        assert all(isinstance(val, str) for val in uuid_values)
    else:
        raise Exception()
    assert len(set(uuid_values)) == 3


def test_uuid_compare(engine):
    bt = get_df_with_test_data(engine)[['city', 'founding']]
    bt['a'] = uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264')
    bt['b'] = uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264')
    bt['c'] = SeriesUuid.random(bt)
    # this is a bit funky, here we copy the 'gen_random_uuid()' expression instead of the result of the
    # expression. As a result bt['d'] != bt['c']. This is something that we might want to change in the
    # future (e.g. by having a flag indicating that we need to create a new node in the DAG if we copy this
    # column to force evaluation.) For now we include this in the test to 'document' it to future developers
    bt['d'] = bt['c']

    bt['w'] = bt['a'] == bt['b']
    bt['x'] = bt['b'] == bt['c']
    bt['y'] = bt['b'] != bt['c']
    bt['z'] = bt['c'] != bt['d']  # see comment above

    # non-happy path: Compare with a different type, but it's a string so we can only detect failure
    # on query time on some database.. As city will not convert to uuid, this will raise hell on databases
    # with a dedicated uuid type. On databases where we use strings to represents uuids this will not raise
    # an error but rather the comparison will just fail.
    cmp_series = bt['b'] == bt['city']
    if is_postgres(engine):
        with pytest.raises(Exception):
            cmp_series.head()
    elif is_bigquery(engine):
        cmp_series.head()

    # if you really want False, you should
    bt['u'] = bt['b'].astype('string') == bt['city']

    # non-happy path: compare with a different type that not convertable to uuid
    with pytest.raises(TypeError):
        bt['v'] = bt['b'] == bt['founding']

    # clear long columns, and check results
    bt = bt[['city', 'w', 'x', 'y', 'z', 'u']]
    assert_equals_data(
        bt,
        expected_columns=['_index_skating_order', 'city', 'w', 'x', 'y', 'z', 'u'],
        expected_data=[
            [1, 'Ljouwert', True, False, True, True, False],
            [2, 'Snits', True, False, True, True, False],
            [3, 'Drylts', True, False, True, True, False],
        ]
    )


def test_to_pandas(engine):
    bt = get_df_with_test_data(engine)
    bt['a'] = uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264')
    bt['c'] = SeriesUuid.random(bt)
    result_pdf = bt[['a', 'c']].to_pandas()
    assert result_pdf[['a']].to_numpy()[0] == [uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264')]
    assert type(result_pdf[['a']].to_numpy()[0][0]) == type(uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'))
