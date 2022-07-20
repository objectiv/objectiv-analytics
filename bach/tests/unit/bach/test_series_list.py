"""
Copyright 2022 Objectiv B.V.
"""
import pytest

from bach.expression import Expression
from bach.series import SeriesList
from sql_models.util import is_bigquery, is_postgres, DatabaseNotSupportedException
from tests.unit.bach.util import get_fake_df_test_data


@pytest.mark.skip_postgres
def test_supported_value_to_literal(dialect):

    result_empty = SeriesList.supported_value_to_literal(dialect, [], ['string'])
    result_int = SeriesList.supported_value_to_literal(dialect, [1, 2, 3], ['int64'])
    result_str = SeriesList.supported_value_to_literal(dialect, ['abc', 'def'], ['string'])
    if is_postgres(dialect):
        assert result_empty.to_sql(dialect) == 'ARRAY[]::text[]'
        assert result_int.to_sql(dialect) == 'ARRAY[cast(1 as bigint), cast(2 as bigint), cast(3 as bigint)]'
        assert result_str.to_sql(dialect) == "ARRAY['abc', 'def']"
    elif is_bigquery(dialect):
        assert result_empty.to_sql(dialect) == 'ARRAY<STRING>[]'
        assert result_int.to_sql(dialect) == '[1, 2, 3]'
        assert result_str.to_sql(dialect) == '["""abc""", """def"""]'
    else:
        raise Exception()

    with pytest.raises(ValueError, match='Dtype does not match value'):
        SeriesList.supported_value_to_literal(dialect, [1, '2'], ['int64'])


def test_db_not_supported_error_on_not_supported_db(dialect):
    df = get_fake_df_test_data(dialect=dialect)
    # Creating a SeriesList should work on BigQuery, and should give a clear error on Postgres.
    # wrap call in function, so it's super clear we test the same statements for all dialects

    def call_to_init():
        # This is not the 'normal' way to create a Series for the end-user, but it should give a clear error
        # none the less.
        return SeriesList(
            engine=df.engine,
            base_node=df.base_node,
            index=df.index,
            name='test',
            expression=Expression.construct('NULL'),
            group_by=None,
            order_by=[],
            instance_dtype=['int64'],
        )

    def call_from_value():
        # more 'normal' way to create a Series
        arr = [123, 456, 789]
        dtype = ['int64']
        return SeriesList.from_value(base=df, value=arr, name='struct', dtype=dtype)

    def call_supported_value_to_literal():
        return SeriesList.supported_value_to_literal(dialect, [], ['string'])

    if is_bigquery(dialect):
        df['x'] = call_to_init()
        df['y'] = call_from_value()
        expr = call_supported_value_to_literal()
    if is_postgres(dialect):
        match = 'SeriesList is not supported for database dialect postgresql'
        with pytest.raises(DatabaseNotSupportedException, match=match):
            df['x'] = call_to_init()
        with pytest.raises(DatabaseNotSupportedException, match=match):
            df['y'] = call_from_value()
        with pytest.raises(DatabaseNotSupportedException, match=match):
            expr = call_supported_value_to_literal()
