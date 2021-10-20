"""
Copyright 2021 Objectiv B.V.
"""
import uuid
from unittest.mock import ANY

import pytest
from psycopg2 import DataError

from buhtuh import BuhTuhSeriesUuid
from tests.functional.buhtuh.test_data_and_utils import get_bt_with_test_data, assert_equals_data, run_query


def test_uuid_value_to_sql():
    bt = get_bt_with_test_data()[['city']]
    bt['x'] = uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264')
    bt['y'] = '0022c7dd-074b-4a44-a7cb-b7716b668264'
    bt['yy'] = bt.y.astype('uuid')
    bt['z'] = bt.x == bt.y
    bt['zz'] = bt.x != '0022c7da-074b-4a44-a7cb-b7716b668263'
    bt['zzz'] = bt.x == bt.yy

    assert_equals_data(
        bt,
        expected_columns=['_index_skating_order', 'city', 'x', 'y', 'yy', 'z', 'zz', 'zzz'],
        expected_data=[
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
    )


def test_uuid_from_dtype_to_sql():
    bt = get_bt_with_test_data()[['city']]
    bt['x'] = uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264')
    bt['y'] = '0022c7dd-074b-4a44-a7cb-b7716b668264'
    bt['z'] = 123456
    assert_equals_data(
        bt,
        expected_columns=['_index_skating_order', 'city', 'x', 'y', 'z'],
        expected_data=[
            [1, 'Ljouwert', uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'), '0022c7dd-074b-4a44-a7cb-b7716b668264', 123456],
            [2, 'Snits', uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'), '0022c7dd-074b-4a44-a7cb-b7716b668264', 123456],
            [3, 'Drylts', uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'), '0022c7dd-074b-4a44-a7cb-b7716b668264', 123456],
        ]
    )
    bt = bt.astype({'x': 'uuid'})
    bt = bt.astype({'y': 'uuid'})
    with pytest.raises(Exception):
        bt = bt.astype({'z': 'uuid'})
    assert_equals_data(
        bt,
        expected_columns=['_index_skating_order', 'city', 'x', 'y', 'z'],
        expected_data=[
            [1, 'Ljouwert', uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'), uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'), 123456],
            [2, 'Snits', uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'), uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'), 123456],
            [3, 'Drylts', uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'), uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264'), 123456],
        ]
    )


def test_uuid_generate_random_uuid():
    bt = get_bt_with_test_data()[['city']]
    bt['x'] = BuhTuhSeriesUuid.sql_gen_random_uuid(base=bt)
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
    assert all(isinstance(val, uuid.UUID) for val in uuid_values)
    assert len(set(uuid_values)) == 3


def test_uuid_compare():
    bt = get_bt_with_test_data()[['city', 'founding']]
    bt['a'] = uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264')
    bt['b'] = uuid.UUID('0022c7dd-074b-4a44-a7cb-b7716b668264')
    bt['c'] = BuhTuhSeriesUuid.sql_gen_random_uuid(bt)
    # this is a bit funky, here we copy the 'gen_random_uuid()' expression instead of the result of the
    # expression. As a result bt['d'] != bt['c']. This is something that we might want to change in the
    # future (e.g. by having a flag indicating that we need to create a new node in the DAG if we copy this
    # column to force evaluation.) For now we include this in the test to 'document' it to future developers
    bt['d'] = bt['c']

    bt['w'] = bt['a'] == bt['b']
    bt['x'] = bt['b'] == bt['c']
    bt['y'] = bt['b'] != bt['c']
    bt['z'] = bt['c'] != bt['d']  # see comment above

    # non-happy path: compare with a different type, but it's a string so we can only detect failure
    # on query time. As city will not convert to uuid, this will raise hell
    with pytest.raises(Exception):
        dies = bt['b'] == bt['city']
        dies.head()

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

