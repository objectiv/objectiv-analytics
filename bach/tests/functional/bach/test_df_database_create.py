"""
Copyright 2022 Objectiv B.V.
"""
from random import randrange

import pytest

from tests.functional.bach.test_data_and_utils import get_df_with_test_data, assert_equals_data
from sql_models.sql_generator import to_sql
from sql_models.util import quote_identifier


def test_database_create_table(engine, unique_table_test_name: str):
    df = get_df_with_test_data(engine)

    # We add a random value to the dataframe, that way we can check that it was actually this test run
    # that wrote the table, and not some earlier run that happened to write the same data to the same table.
    random_value = randrange(1_000_000)
    df['x'] = random_value
    expected_columns = [
        '_index_skating_order', 'skating_order', 'city', 'municipality', 'inhabitants', 'founding', 'x'
    ]
    expected_data = [
        [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, random_value],
        [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, random_value],
        [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, random_value]
    ]

    table_name = unique_table_test_name

    # First test: write dataframe to table. We expect success
    df_from_table = df.database_create_table(
        table_name=table_name,
        if_exists='replace'
    )
    assert_equals_data(df_from_table, expected_columns=expected_columns, expected_data=expected_data)

    # check that df_from_table actually queries the table
    dialect = engine.dialect
    assert df_from_table.base_node != df.base_node
    assert len(df_from_table.base_node.references) == 0
    new_sql = to_sql(dialect=dialect, model=df_from_table.base_node)
    quoted_table_name = quote_identifier(dialect, table_name)
    expected_sql_fragment = f'FROM {quoted_table_name}'
    assert expected_sql_fragment in new_sql

    # Second test: try to write table, but with overwrite=False. We expect an error
    df['y'] = random_value
    # we get a database error, so the exact error is database dependent. Both Postgres and BigQuery should
    # raise an error containing the phrase 'already exists', but with different capitalization
    with pytest.raises(Exception, match='[aA]lready [eE]xists'):
        df_from_table = df.database_create_table(
            table_name=table_name,
            if_exists='fail'
        )
    # table should be unchanged after the last failed call
    assert_equals_data(df_from_table, expected_columns=expected_columns, expected_data=expected_data)

    # Third test: write table again, with overwrite=True. We expect the table now to have the y column too
    expected_columns = expected_columns + ['y']
    expected_data = [row + [random_value] for row in expected_data]
    df_from_table = df.database_create_table(
        table_name=table_name,
        if_exists='replace'
    )
    assert_equals_data(df_from_table, expected_columns=expected_columns, expected_data=expected_data)
