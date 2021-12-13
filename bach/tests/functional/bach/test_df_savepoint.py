"""
Copyright 2021 Objectiv B.V.
"""
from bach.savepoints import Savepoints
from sql_models.model import Materialization
from tests.functional.bach.test_data_and_utils import get_bt_with_test_data, assert_equals_data, \
    get_pandas_df, TEST_DATA_CITIES, CITIES_COLUMNS
from tests.functional.bach.test_savepoints import remove_created_db_objects


def test_savepoint_simple():
    # setup
    df = get_bt_with_test_data()
    engine = df.engine
    sps = Savepoints()

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
    df.set_savepoint(sps, "savepoint1")

    result = sps.execute(engine)
    expected = {key: expected_results[key]for key in ['savepoint1']}
    assert result == expected

    df['x'] = 'abcdef'
    df = df[['city', 'founding', 'x']]
    df = df.materialize()
    df.set_savepoint(sps, "savepoint2")

    result = sps.execute(engine)
    expected = {key: expected_results[key] for key in ['savepoint1', 'savepoint2']}
    assert result == expected

    df = sps.get_df('savepoint1')
    df = df[df.skating_order == 2]
    df.materialize()
    df = df[['city', 'municipality']]
    # TODO: there is a bug in is_materialized. The df is marked as materialized because all columns are
    # unchanged, however the fact that some columns are missing (compared to the base_node) is not
    # accounted for. Therefore we'll have to do a manual materialize here
    df.materialize(inplace=True)
    df.set_savepoint(sps, 'savepoint3')

    result = sps.execute(engine)
    assert result == expected_results


def test_savepoint_tables():
    df = get_bt_with_test_data()

    engine = df.engine
    sps = Savepoints()
    df.set_savepoint(sps, "savepoint1", Materialization.TABLE)
    df['x'] = 'abcdef'
    df = df[['city', 'founding', 'x']]
    df = df.materialize()
    df.set_savepoint(sps, "savepoint2", Materialization.VIEW)

    df = sps.get_df('savepoint1')
    df = df[df.skating_order == 2]
    df.materialize()
    df = df[['city', 'municipality']]
    df.materialize(inplace=True)
    df.set_savepoint(sps, 'savepoint3', Materialization.VIEW)

    assert_equals_data(
        df,
        expected_columns=['_index_skating_order', 'city', 'municipality'],
        expected_data=[[2, 'Snits', 'Súdwest-Fryslân']]
    )

    # Test clean up:
    # TODO: make test clean-up robust to failures half-way
    remove_created_db_objects(sps, engine)
