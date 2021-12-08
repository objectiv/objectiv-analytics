"""
Copyright 2021 Objectiv B.V.
"""
import pytest

from bach.savepoints import Savepoints
from sql_models.model import Materialization
from tests.functional.bach.test_data_and_utils import get_bt_with_test_data


def test_add_df():
    df = get_bt_with_test_data()
    sp = Savepoints()

    assert sp.views_created == []
    assert sp.tables_created == []

    # Basic test
    df = df.materialize(
        node_name='manual_materialize',
        inplace=False,
        limit=None,
        materialization=Materialization.QUERY,
        savepoint_name='the_name'
    )
    sp.add_df(df)
    assert sp.get_df('the_name') == df

    # Test error conditions
    # wrong materialization
    df = df.materialize(
        node_name='manual_materialize',
        inplace=False,
        limit=None,
        materialization=Materialization.CTE,
        savepoint_name=None
    )
    with pytest.raises(ValueError, match='Materialization type not supported'):
        sp.add_df(df)

    # no name
    df = df.materialize(
        node_name='manual_materialize',
        inplace=False,
        limit=None,
        materialization=Materialization.QUERY,
        savepoint_name=None
    )
    with pytest.raises(ValueError, match='Name must match'):
        sp.add_df(df)

    # wrong name
    df = df.materialize(
        node_name='manual_materialize',
        inplace=False,
        limit=None,
        materialization=Materialization.QUERY,
        savepoint_name='A invalid name (spaces)'
    )
    with pytest.raises(ValueError, match='Name must match'):
        sp.add_df(df)

    # duplicate name
    df = df.materialize(
        node_name='manual_materialize',
        inplace=False,
        limit=None,
        materialization=Materialization.QUERY,
        savepoint_name='the_name'
    )
    with pytest.raises(ValueError, match='already exists'):
        sp.add_df(df)


def test_execute_query():
    df = get_bt_with_test_data()
    engine = df.engine
    sp = Savepoints()

    df = df.materialize(
        node_name='manual_materialize',
        inplace=False,
        limit=None,
        materialization=Materialization.QUERY,
        savepoint_name='the_name'
    )

    sp.add_df(df)
    result = sp.execute(engine)
    assert result == {
        'the_name': [
            (1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285),
            (2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456),
            (3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268)
        ]
    }

    df = df[df.skating_order < 3]
    df = df.materialize(
        node_name='manual_materialize',
        inplace=False,
        limit=None,
        materialization=Materialization.QUERY,
        savepoint_name='second_point'
    )
    sp.add_df(df)

    result = sp.execute(engine)
    assert result == {
        'the_name': [
            (1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285),
            (2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456),
            (3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268)
        ],
        'second_point': [
            (1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285),
            (2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456)
        ]
    }


def test_execute_table():
    df = get_bt_with_test_data()
    engine = df.engine
    sp = Savepoints()

    df = df.materialize(
        node_name='manual_materialize',
        inplace=False,
        limit=None,
        materialization=Materialization.TABLE,
        savepoint_name='sp_first_point'
    )

    sp.add_df(df)
    result = sp.execute(engine)
    assert result == {}


    # reduce df to one row and add savepoint
    df = df[df.skating_order == 1]
    df = df.materialize(
        node_name='manual_materialize',
        inplace=False,
        limit=None,
        materialization=Materialization.TABLE,
        savepoint_name='sp_second_point'
    )
    sp.add_df(df)

    # Change columns in df and add savepoint
    df = df[['skating_order', 'city', 'founding']]
    df['x'] = 12345
    df = df.materialize(
        node_name='manual_materialize',
        inplace=False,
        limit=None,
        materialization=Materialization.TABLE,
        savepoint_name='sp_third_point'
    )
    sp.add_df(df)

    # No changes, add query
    df = df.materialize(
        node_name='manual_materialize',
        inplace=False,
        limit=None,
        materialization=Materialization.QUERY,
        savepoint_name='sp_final_point'
    )
    sp.add_df(df)

    expected_result = {
        'sp_final_point': [
            (1, 1, 'Ljouwert', 1285, 12345),
        ]
    }

    assert sp.tables_created == ['sp_first_point']
    result = sp.execute(engine)
    assert sp.tables_created == ['sp_first_point', 'sp_second_point', 'sp_third_point']
    assert result == expected_result
    assert sp.to_sql()['sp_final_point'] == \
           'select "_index_skating_order", "skating_order", "city", "founding", "x" from ' \
           '"sp_third_point"   limit all'

    # executing multiple times doesn't create tables multiple times or changes the result.
    result = sp.execute(engine)
    result = sp.execute(engine)
    assert result == expected_result

    # Test clean up:
    # TODO: make test clean-up robust to failures half-way
    with engine.connect() as conn:
        for table in sp.tables_created:
            conn.execute(f'drop table "{table}";')


