import re
from typing import NamedTuple, Dict, List, Set
from sqlalchemy.engine import Connection, Dialect

from bach.expression import Expression, ColumnReferenceToken
from bach.sql_model import BachSqlModel
from sql_models.util import is_postgres, DatabaseNotSupportedException, is_bigquery


class SortColumn(NamedTuple):
    expression: Expression
    asc: bool


class FeatureRange(NamedTuple):
    min: int
    max: int


class ResultSeries(NamedTuple):
    name: str
    expression: 'Expression'
    dtype: str


def get_result_series_dtype_mapping(result_series: List[ResultSeries]) -> Dict[str, str]:
    return {
        rs.name: rs.dtype
        for rs in result_series
    }


def get_merged_series_dtype(dtypes: Set[str]) -> str:
    """
    returns a final dtype when trying to combine series with different dtypes
    """
    from bach import get_series_type_from_dtype, SeriesAbstractNumeric
    if len(dtypes) == 1:
        return dtypes.pop()
    elif all(
        issubclass(get_series_type_from_dtype(dtype), SeriesAbstractNumeric)
        for dtype in dtypes
    ):
        return 'float64'

    # default casting will be as text, this way we avoid any SQL errors
    # when merging different db types into a column
    return 'string'


def escape_parameter_characters(conn: Connection, raw_sql: str) -> str:
    """
    Return a modified copy of the given sql with the query-parameter special characters escaped.
    e.g. if the connection uses '%' to mark a parameter, then all occurrences of '%' will be replaced by '%%'
    """
    # for now we'll just assume Postgres and assume the pyformat parameter style is used.
    # When we support more databases we'll need to do something smarter, see
    # https://www.python.org/dev/peps/pep-0249/#paramstyle
    return raw_sql.replace('%', '%%')


def is_valid_column_name(dialect: Dialect, name: str) -> bool:
    """
    Check that the given name is a valid column name in the SQL dialect.
    """
    if is_postgres(dialect):
        # Identifiers longer than 63 characters are not necessarily wrong, but they will be truncated which
        # could lead to identifier collisions, so we just disallow it.
        # source: https://www.postgresql.org/docs/14/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS
        return len(name) < 64
    if is_bigquery(dialect):
        # sources:
        #  https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical#column_names
        #  https://cloud.google.com/bigquery/docs/schemas#column_names
        regex = '^[a-zA-Z_][a-zA-Z0-9_]*$'
        reserved_prefixes = [
            '_TABLE_',
            '_FILE_',
            '_PARTITION',
            '_ROW_TIMESTAMP',
            '__ROOT__',
            '_COLIDENTIFIER'
        ]
        len_ok = len(name) <= 300
        pattern_ok = bool(re.match(pattern=regex, string=name))
        prefix_ok = not any(name.startswith(prefix) for prefix in reserved_prefixes)
        return len_ok and pattern_ok and prefix_ok
    raise DatabaseNotSupportedException(dialect)


def validate_node_column_references_in_sorting_expressions(
    node: BachSqlModel, order_by: List[SortColumn],
) -> None:
    """
    Validate that all ColumnReferenceTokens in order_by expressions refer columns that exist in node.
    """
    for ob in order_by:
        invalid_column_references = [
            token.column_name
            for token in ob.expression.get_all_tokens()
            if isinstance(token, ColumnReferenceToken) and token.column_name not in node.column_expressions
        ]
        if invalid_column_references:
            raise ValueError(
                (
                    'Sorting contains expressions referencing '
                    f'non-existent columns in current base node. {invalid_column_references}.'
                    ' Please call DataFrame.sort_values([]) or DataFrame.sort_index() for removing'
                    ' sorting and try again.'
                )
            )
