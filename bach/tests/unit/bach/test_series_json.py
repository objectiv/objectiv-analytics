"""
Copyright 2022 Objectiv B.V.
"""
import pytest

from bach.series.series_json import JsonBigQueryAccessor
from tests.unit.bach.util import get_fake_df



@pytest.mark.skip_postgres
def test_bq_get_slice_partial_expr(dialect):
    # Here we test the _get_slice_partial_expr function of the BigQuery specific JsonBigQueryAccessor. So
    # skipping all other dialects
    df = get_fake_df(
        dialect=dialect,
        index_names=['i'],
        data_names=['a'],
        dtype='json'
    )
    jbqa = JsonBigQueryAccessor(df.a)
    assert jbqa._get_slice_partial_expr(None, True).to_sql(dialect) == '0'
    assert jbqa._get_slice_partial_expr(None, False).to_sql(dialect) == '9223372036854775807'
    assert jbqa._get_slice_partial_expr(5, False).to_sql(dialect) == '5'
    assert jbqa._get_slice_partial_expr(5, True).to_sql(dialect) == '5'
    assert jbqa._get_slice_partial_expr(-5, False).to_sql(dialect) == \
           '(ARRAY_LENGTH(JSON_QUERY_ARRAY(`a`)) -5)'
    assert jbqa._get_slice_partial_expr(-5, True).to_sql(dialect) == \
           '(ARRAY_LENGTH(JSON_QUERY_ARRAY(`a`)) -5)'
