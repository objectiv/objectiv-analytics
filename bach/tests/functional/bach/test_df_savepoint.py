"""
Copyright 2021 Objectiv B.V.
"""
from bach.savepoints import Savepoints
from sql_models.model import Materialization
from tests.functional.bach.test_data_and_utils import get_bt_with_test_data, assert_equals_data


def test_savepoint_simple():
    # setup
    df = get_bt_with_test_data()
    engine = df.engine
    sp = Savepoints()

    # all expected values
    expected_results = {
        'savepoint1': [
            (1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285),
            (2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456),
            (3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268)
        ],
        'savepoint2': [
            (1, 'Ljouwert', 1285, 'abcdef'),
            (2, 'Snits', 1456, 'abcdef'),
            (3, 'Drylts', 1268, 'abcdef')
        ],
        'savepoint3': [
            (2, 'Snits', 'Súdwest-Fryslân'),
        ]
    }

    # actual tests
    df.set_savepoint(sp, "savepoint1")

    result = sp.execute(engine)
    expected = {k: v for k, v in expected_results.items() if k in ('savepoint1')}
    assert result == expected

    df['x'] = 'abcdef'
    df = df[['city', 'founding', 'x']]
    df = df.materialize()
    df.set_savepoint(sp, "savepoint2")

    result = sp.execute(engine)
    expected = {k: v for k, v in expected_results.items() if k in ('savepoint1', 'savepoint2')}
    assert result == expected

    df = sp.get_df('savepoint1')
    df = df[df.skating_order == 2]
    df.materialize()
    df = df[['city', 'municipality']]
    # TODO: there is a bug in is_materialized. The df is marked as materialized because all columns are
    # unchanged, however the fact that some columns are missing (compared to the base_node) is not
    # accounted for. Therefore we'll have to do a manual materialize here
    df.materialize(inplace=True)
    df.set_savepoint(sp, 'savepoint3')

    result = sp.execute(engine)
    assert result == expected_results


def test_savepoint_tables():
    df = get_bt_with_test_data()
    engine = df.engine
    sp = Savepoints()
    df.set_savepoint(sp, "savepoint1", Materialization.TABLE)
    df['x'] = 'abcdef'
    df = df[['city', 'founding', 'x']]
    df = df.materialize()
    df.set_savepoint(sp, "savepoint2", Materialization.VIEW)

    df = sp.get_df('savepoint1')
    df = df[df.skating_order == 2]
    df.materialize()
    df = df[['city', 'municipality']]
    df.materialize(inplace=True)
    df.set_savepoint(sp, 'savepoint3', Materialization.VIEW)

    assert_equals_data(
        df,
        expected_columns=['_index_skating_order', 'city', 'municipality'],
        expected_data=[[2, 'Snits', 'Súdwest-Fryslân']]
    )

    # Test clean up:
    # TODO: make test clean-up robust to failures half-way
    with engine.connect() as conn:
        for name, materialization in sp.created:
            if materialization == Materialization.TABLE:
                conn.execute(f'drop table "{name}";')
            elif materialization == Materialization.VIEW:
                conn.execute(f'drop view "{name}";')
            else:
                raise Exception("unhandled case")
