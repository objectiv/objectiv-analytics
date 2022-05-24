"""
Copyright 2021 Objectiv B.V.
"""
import pytest

from sql_models.util import extract_format_fields, quote_identifier, quote_string, is_postgres,\
    is_bigquery


@pytest.mark.db_independent
def test_extract_format_fields():
    assert extract_format_fields('{test}') == {'test'}
    assert extract_format_fields('{test} more text {test}') == {'test'}
    assert extract_format_fields('text{test} more {{text}} {test2} te{x}t{test}') == {'test', 'test2', 'x'}


@pytest.mark.db_independent
def test_extract_format_fields_nested():
    # assert extract_format_fields('{test}', 2) == set()
    # assert extract_format_fields('{test} more text {test}', 2) == set()
    # assert extract_format_fields('text{test} more {{text}} {test2} te{x}t{test}', 2) == {'text'}
    assert extract_format_fields('{x} {{y}} {{{{z}}}} {a}', 1) == {'x', 'a'}
    assert extract_format_fields('{x} {{y}} {{{{z}}}} {a}', 2) == {'y'}
    assert extract_format_fields('{x} {{y}} {{{{z}}}} {a}', 3) == {'z'}
    assert extract_format_fields('{x} {{y}} {{{{z}}}}', 3) == {'z'}


def test_quote_identifier(dialect):
    if is_postgres(dialect):
        # https://www.postgresql.org/docs/14/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS
        assert quote_identifier(dialect, 'test') == '"test"'
        assert quote_identifier(dialect, 'te"st') == '"te""st"'
        assert quote_identifier(dialect, '"te""st"') == '"""te""""st"""'
        assert quote_identifier(dialect, '`te`st`') == '"`te`st`"'
        assert quote_identifier(dialect, 'te%st') == '"te%st"'
    elif is_bigquery(dialect):
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical#identifiers
        assert quote_identifier(dialect, 'test') == '`test`'
        assert quote_identifier(dialect, 'te"st') == '`te"st`'
        assert quote_identifier(dialect, '"te""st"') == r'`"te""st"`'
        assert quote_identifier(dialect, '`te`st`') == r'`\`te\`st\``'
        assert quote_identifier(dialect, 'te%st') == '`te%st`'
    else:
        # if we add more dialects, we should not forget to extend this test
        raise Exception()


def test_quote_string(dialect):
    if is_postgres(dialect):
        # https://www.postgresql.org/docs/14/sql-syntax-lexical.html#SQL-SYNTAX-CONSTANTS
        assert quote_string(dialect, "test") == "'test'"
        assert quote_string(dialect, "te'st") == "'te''st'"
        assert quote_string(dialect, "'te''st'") == "'''te''''st'''"

    elif is_bigquery(dialect):
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical#string_and_bytes_literals
        assert quote_string(dialect, "test") == '"""test"""'
        assert quote_string(dialect, "te'st") == '"""te\'st"""'
        assert quote_string(dialect, "'te''st'") == '"""\'te\'\'st\'"""'
    else:
        # if we add more dialects, we should not forget to extend this test
        raise Exception()