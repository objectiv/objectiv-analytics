"""
Copyright 2022 Objectiv B.V.
"""
import pytest

from bach import SeriesDict
from bach.expression import Expression
from sql_models.util import DatabaseNotSupportedException, is_bigquery, is_postgres
from tests.unit.bach.util import get_fake_df_test_data


def test_db_not_supported_error_on_not_supported_db(dialect):
    df = get_fake_df_test_data(dialect=dialect)
    # Creating a SeriesDict should work on BigQuery, and should give a clear error on Postgres.
    # wrap call in function, so it's super clear we test the same statements for all dialects

    def call_to_init():
        # This is not the 'normal' way to create a Series for the end-user, but it should give a clear error
        # none the less.
        return SeriesDict(
            engine=df.engine,
            base_node=df.base_node,
            index=df.index,
            name='test',
            expression=Expression.construct('NULL'),
            group_by=None,
            order_by=[],
            instance_dtype={'a': 'int64'},
        )

    def call_from_value():
        # more 'normal' way to create a Series
        struct = {'a': 123, 'b': 'test'}
        dtype = {'a': 'int64', 'b': 'string'}
        return SeriesDict.from_value(base=df, value=struct, name='struct', dtype=dtype)

    def call_supported_value_to_literal():
        return SeriesDict.supported_value_to_literal(dialect, {'a': 123}, {'a': 'int64'})

    if is_bigquery(dialect):
        df['x'] = call_to_init()
        df['y'] = call_from_value()
        expr = call_supported_value_to_literal()
    if is_postgres(dialect):
        match = 'SeriesDict is not supported for database dialect postgresql'
        with pytest.raises(DatabaseNotSupportedException, match=match):
            df['x'] = call_to_init()
        with pytest.raises(DatabaseNotSupportedException, match=match):
            df['y'] = call_from_value()
        with pytest.raises(DatabaseNotSupportedException, match=match):
            expr = call_supported_value_to_literal()
