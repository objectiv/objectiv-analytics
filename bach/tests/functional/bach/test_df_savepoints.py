"""
Copyright 2021 Objectiv B.V.
"""
import pytest

from bach.savepoints import CreatedObject
from sql_models.model import Materialization
from tests.functional.bach.test_data_and_utils import get_bt_with_test_data, assert_equals_data
from tests.functional.bach.test_savepoints import remove_created_db_objects


@pytest.mark.xdist_group(name="db_writers")
def test_savepoint_materialization():
    df = get_bt_with_test_data()

    engine = df.engine
    df.set_savepoint("savepoint1")
    df['x'] = 'abcdef'
    df = df[['city', 'founding', 'x']]
    df.set_savepoint("savepoint2", 'view')

    df = df.savepoints.get_df('savepoint1')
    df = df[df.skating_order == 2]
    df = df[['city', 'municipality']]
    df.set_savepoint('savepoint3', Materialization.VIEW)

    expected_columns = ['_index_skating_order', 'city', 'municipality']
    expected_data = [[2, 'Snits', 'Súdwest-Fryslân']]
    assert_equals_data(df, expected_columns=expected_columns, expected_data=expected_data)

    df_mat = df.savepoints.get_materialized_df('savepoint3', engine)
    with pytest.raises(Exception, match='relation "savepoint3" does not exist'):
        # The df_mat DataFrame queries directly from the 'savepoint3' view in the database.
        # This will fail because that view has not been created yet.
        df_mat.to_pandas()

    # Create tables and views, then try again
    df.savepoints.set_materialization('savepoint1', 'table')
    created_result = df.savepoints.write_to_db()

    assert created_result == [
        CreatedObject('savepoint1', Materialization.TABLE),
        CreatedObject('savepoint3', Materialization.VIEW),
        CreatedObject('savepoint2', Materialization.VIEW),
    ]

    df_mat = df.savepoints.get_materialized_df('savepoint3', engine)
    assert_equals_data(df_mat, expected_columns=expected_columns, expected_data=expected_data)

    # Test clean up:
    # TODO: make test clean-up robust to failures half-way
    remove_created_db_objects(engine, created_result)
