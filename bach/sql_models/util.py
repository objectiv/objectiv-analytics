"""
Copyright 2021 Objectiv B.V.
"""
import re
import string
from typing import Set, Union, Optional

from sqlalchemy.engine import Dialect, Engine

from sql_models.constants import DBDialect


def extract_format_fields(format_string: str, nested=1) -> Set[str]:
    """
    Given a python format string, return a set with all field names.

    If nested is set, it will do x rounds of:
        1. find field names in input string
        2. fill out values for field names. Use this as input string for step 1.

    Examples:
        extract_format_fields('{x} {{y}} {{{{z}}}} {a}', 1) == {'x', 'a'}
        extract_format_fields('{x} {{y}} {{{{z}}}} {a}', 2) == {'y'}
        extract_format_fields('{x} {{y}} {{{{z}}}} {a}', 3) == {'z'}
        extract_format_fields('{x} {{y}} {{{{z}}}}', 3)     == {'z'}
    """
    formatter = string.Formatter()
    fields = set()
    items = list(formatter.parse(format_string))
    for item in items:
        _literal_text, field_name, _format_spec, _conversion = item
        if field_name is not None:
            fields.add(field_name)
    if nested == 1:
        return fields
    dummy_values = {field_name: 'x' for field_name in fields}
    new_format_string = format_string.format(**dummy_values)
    return extract_format_fields(new_format_string, nested=nested-1)


def quote_identifier(dialect: Dialect, name: str) -> str:
    """
    Add quotes around an identifier (e.g. a table or column name), and escape special characters in the name.

    Note that the result of this function is not always a valid column name and/or table name. e.g. The
    following string can be quoted by this function to give a valid BigQuery identifier: '`te`st`'. However,
    that name is only valid as a table name, not as a column name as there are additional rules on what
    makes a valid column name.

    Examples
    >>> from sqlalchemy.dialects.postgresql.base import PGDialect
    >>> quote_identifier(PGDialect(), 'test')
    '"test"'
    >>> quote_identifier(PGDialect(), 'te"st')
    '"te""st"'
    >>> quote_identifier(PGDialect(), '"te""st"')
    '\"\"\"te\"\"\"\"st\"\"\"'
    """
    if is_postgres(dialect):
        # more 'logical' would be: dialect.preparer(dialect).quote_identifier(value=name)
        # But it seems that goes wrong in case there is a `%` in the value. Which sort of makes sense, as
        # sqlalchemy already escapes that for later on.

        # postgres spec: https://www.postgresql.org/docs/14/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS
        replaced_chars = name.replace('"', '""')
        return f'"{replaced_chars}"'

    if is_bigquery(dialect):
        # Spec: https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical#quoted_identifiers
        # For additional rules on column and table names (not enforced by this function!) See
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical#column_names
        # https://cloud.google.com/bigquery/docs/schemas#column_names
        # https://cloud.google.com/bigquery/docs/tables#table_naming
        replaced_chars = name.replace('\\', '\\\\')
        replaced_chars = replaced_chars.replace('`', '\\`')
        return f'`{replaced_chars}`'
    raise DatabaseNotSupportedException(dialect)


def quote_string(dialect_engine: Union[Dialect, Engine], value: str) -> str:
    """
    Quote and escape string value for the given database dialect.

    Examples:
    >>> from sqlalchemy.dialects.postgresql.base import PGDialect
    >>> quote_string(PGDialect(), "test")
    "'test'"
    >>> quote_string(PGDialect(), "te'st")
    "'te''st'"
    >>> quote_string(PGDialect(), "'te''st'")
    "'''te''''st'''"
    """

    if is_bigquery(dialect_engine):
        # Triple-quoted string, double-quotes are escaped in order to avoid conflicts
        # See https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical#string_and_bytes_literals
        replaced_chars = value.replace('\\', r'\\')
        replaced_chars = replaced_chars.replace('"', r'\"')
        return f'"""{replaced_chars}"""'

    replaced_chars = value.replace("'", "''")
    return f"'{replaced_chars}'"


def is_postgres(dialect_engine: Union[Dialect, Engine]) -> bool:
    return DBDialect.POSTGRES.is_dialect(dialect_engine)


def is_bigquery(dialect_engine: Union[Dialect, Engine]) -> bool:
    return DBDialect.BIGQUERY.is_dialect(dialect_engine)


class DatabaseNotSupportedException(Exception):
    def __init__(self, dialect_engine: Union[Dialect, Engine], message_override: Optional[str] = None):
        if message_override is not None:
            message = message_override
        else:
            message = f'This function is not supported for database dialect "{dialect_engine.name}".'
        super().__init__(message)
