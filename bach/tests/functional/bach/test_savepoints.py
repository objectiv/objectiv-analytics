"""
Copyright 2021 Objectiv B.V.
"""
import pytest
from sqlalchemy.future import Engine

from bach.savepoints import Savepoints
from sql_models.model import Materialization
from tests.functional.bach.test_data_and_utils import get_bt_with_test_data


def test_add_df():
    df = get_bt_with_test_data()
    sp = Savepoints()

    assert sp.views_created == []
    assert sp.tables_created == []

    # Basic test
    df = df.materialize()
    df.base_node.set_materialization(Materialization.QUERY).set_materialization_name('the_name')
    sp.add_df(df)
    assert sp.get_df('the_name') == df

    # Test error conditions
    # wrong materialization
    df = df.materialize()
    df.base_node.set_materialization(Materialization.CTE).set_materialization_name(None)

    with pytest.raises(ValueError, match='Materialization type not supported'):
        sp.add_df(df)

    # no name
    df = df.materialize()
    df.base_node.set_materialization(Materialization.QUERY).set_materialization_name(None)

    with pytest.raises(ValueError, match='Name must match'):
        sp.add_df(df)

    # wrong name
    df = df.materialize()
    df.base_node\
        .set_materialization(Materialization.QUERY)\
        .set_materialization_name('An invalid name (spaces)')
    with pytest.raises(ValueError, match='Name must match'):
        sp.add_df(df)

    # duplicate name
    df = df.materialize()
    df.base_node.set_materialization(Materialization.QUERY).set_materialization_name('the_name')
    with pytest.raises(ValueError, match='already exists'):
        sp.add_df(df)


def test_execute_query():
    df = get_bt_with_test_data()
    engine = df.engine
    sp = Savepoints()

    df = df.materialize()
    df.base_node\
        .set_materialization(Materialization.QUERY)\
        .set_materialization_name('the_name')

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
    df = df.materialize()
    df.base_node\
        .set_materialization(Materialization.QUERY)\
        .set_materialization_name('second_point')

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
    sps = Savepoints()

    df = df.materialize()
    df.base_node\
        .set_materialization(Materialization.TABLE)\
        .set_materialization_name('sp_first_point')

    sps.add_df(df)
    result = sps.execute(engine)
    assert result == {}


    # reduce df to one row and add savepoint
    df = df[df.skating_order == 1]
    df = df.materialize()
    df.base_node\
        .set_materialization(Materialization.TABLE)\
        .set_materialization_name('sp_second_point')

    sps.add_df(df)

    # Change columns in df and add savepoint
    df = df[['skating_order', 'city', 'founding']]
    df['x'] = 12345
    df = df.materialize()
    df.base_node\
        .set_materialization(Materialization.TABLE)\
        .set_materialization_name('sp_third_point')
    sps.add_df(df)

    # No changes, add query
    df = df.materialize()
    df.base_node\
        .set_materialization(Materialization.QUERY)\
        .set_materialization_name('sp_final_point')
    sps.add_df(df)

    expected_result = {
        'sp_final_point': [
            (1, 1, 'Ljouwert', 1285, 12345),
        ]
    }

    assert sps.tables_created == ['sp_first_point']
    result = sps.execute(engine)
    assert sps.tables_created == ['sp_first_point', 'sp_second_point', 'sp_third_point']
    assert result == expected_result
    assert sps.to_sql()['sp_final_point'] == \
           'select "_index_skating_order", "skating_order", "city", "founding", "x" from ' \
           '"sp_third_point"   limit all'

    # executing multiple times doesn't create tables multiple times or changes the result.
    result = sps.execute(engine)
    result = sps.execute(engine)
    assert result == expected_result

    # Test clean up:
    # TODO: make test clean-up robust to failures half-way
    remove_created_db_objects(sps, engine)


def remove_created_db_objects(sps: Savepoints, engine: Engine):
    """ Utility function: remove all tables and views that Savepoints has created. """
    with engine.connect() as conn:
        for name, materialization in reversed(sps.created):
            if materialization == Materialization.TABLE:
                conn.execute(f'drop table "{name}";')
            elif materialization == Materialization.VIEW:
                conn.execute(f'drop view "{name}";')
            else:
                raise Exception("unhandled case")
