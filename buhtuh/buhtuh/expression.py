"""
Copyright 2021 Objectiv B.V.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from buhtuh import BuhTuhSeries


@dataclass(frozen=True)
class ExpressionToken:
    """ Abstract base class of ExpressionTokens"""

    def __post_init__(self):
        # Make sure that other code can rely on an ExpressionToken always being a subclass of this class.
        if self.__class__ == ExpressionToken:
            raise TypeError("Cannot instantiate ExpressionToken directly. Instantiate a subclass.")


@dataclass(frozen=True)
class RawToken(ExpressionToken):
    raw: str


@dataclass(frozen=True)
class ColumnReferenceToken(ExpressionToken):
    column_name: str


@dataclass(frozen=True)
class StringValueToken(ExpressionToken):
    """ Wraps a string value. The value in this object is unescaped and unquoted. """
    value: str


@dataclass(frozen=True)
class Expression:
    """
    An Expression object represents a fragment of SQL as a series of sql-tokens.

    Expressions can easily be converted to a string with actual sql using the to_sql() function. Storing a
    sql-expression using this class, rather than storing it directly as a string, makes it possible to
    for example substitute the table-name after constructing the expression.
    Additionally this move this burden of correctly quoting and escaping string literals to this class, if
    literals are expressed with the correct tokens at least.
    In the future we might add support for more literal types.

    This class does not offer full-tokenization of sql. There are only a limited number of tokens for the
    needed use-cases. Most sql is simply encoded as a 'raw' token.
    """
    data: List[ExpressionToken] = field(default_factory=list)

    @classmethod
    def construct(cls, fmt: str, *args: Union['Expression', 'BuhTuhSeries']) -> 'Expression':
        """
        Construct an Expression using a format string that can refer existing expressions.
        Every occurrence of `{}` in the fmt string will be replace with a provided expression (in order that
        they are given). All other parts of fmt will be converted to RawTokens.

        As a convenience, instead of Expressions it is also possible to give BuhTuhSeries as args, in that
        case the series's expression is taken as Expression.

        :param fmt: format string
        :param args: 0 or more Expressions or BuhTuhSeries. Number of args must exactly match number of `{}`
            occurrences in fmt.
        """
        sub_strs = fmt.split('{}')
        data = []
        if len(args) != len(sub_strs) - 1:
            raise ValueError(f'For each {{}} in the fmt there should be an Expression provided. '
                             f'Found {{}}: {len(sub_strs) - 1}, provided expressions: {len(args)}')
        for i, sub_str in enumerate(sub_strs):
            if i > 0:
                arg = args[i - 1]
                if not isinstance(arg, Expression):  # arg is a BuhTuhSeries
                    arg_expr = arg.expression
                else:
                    arg_expr = arg
                data.extend(arg_expr.data)
            if sub_str != '':
                data.append(RawToken(raw=sub_str))
        return cls(data=data)

    @classmethod
    def raw(cls, raw: str) -> 'Expression':
        """ Return an expression that contains a single RawToken. """
        return cls([RawToken(raw)])

    @classmethod
    def string_value(cls, value: str) -> 'Expression':
        """
        Return an expression that contains a single StringValueToken with the value.
        :param value: unquoted, unescaped string value.
        """
        return Expression([StringValueToken(value)])

    @classmethod
    def column_reference(cls, field_name: str) -> 'Expression':
        """ Construct an expression for field-name, where field-name is a column in a table or CTE. """
        return Expression([ColumnReferenceToken(field_name)])

    def to_sql(self, table_name: Optional[str] = None) -> str:
        """ Short cut for expression_to_sql(self, table_name). """
        return expression_to_sql(self, table_name)


def expression_to_sql(expression: Expression, table_name: Optional[str] = None) -> str:
    """
    Compile the expression to a SQL fragment.
        * RawTokens will be represented by the raw string they embed.
        * StringValueTokens will be quoted and escaped
        * ColumnReferenceTokens will be quoted and escaped, and if table_name is provided preceded by the
            table name.
    :param expression: Expression
    :param table_name: Optional table name, if set all column-references will be compiled as
        '"{table_name}"."{column_name}"' instead of just '"{column_name}"'.
    :return SQL representation of the expression.
    """
    result: List[str] = []
    for data_item in expression.data:
        if isinstance(data_item, ColumnReferenceToken):
            if table_name:
                result.append(f'{quote_identifier(table_name)}.')
            result.append(quote_identifier(data_item.column_name))
        elif isinstance(data_item, RawToken):
            result.append(data_item.raw)
        elif isinstance(data_item, StringValueToken):
            result.append(quote_string(data_item.value))
        else:
            raise Exception("This should never happen. "
                            "expression_to_sql() doesn't cover all Expression subtypes.")
    return ''.join(result)


def quote_string(value: str) -> str:
    """
    Add single quotes around the value and escape any quotes in the value.

    This is in accordance with the Postgres string notation format, no guarantees for other databses.
    See https://www.postgresql.org/docs/14/sql-syntax-lexical.html#SQL-SYNTAX-CONSTANTS

    Examples:
    >>> quote_string("test")
    "'test'"
    >>> quote_string("te'st")
    "'te''st'"
    >>> quote_string("'te''st'")
    "'''te''''st'''"
    """
    replaced_chars = value.replace("'", "''")
    return f"'{replaced_chars}'"


def quote_identifier(name: str) -> str:
    """
    Add quotes around an identifier (e.g. a table or column name), and escape special characters in the name.

    This is in accordance with the Postgres string notation format, no guarantees for other databses.
    See https://www.postgresql.org/docs/14/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS

    Examples:
    >>> quote_identifier('test')
    '"test"'
    >>> quote_identifier('te"st')
    '"te""st"'
    >>> quote_identifier('"te""st"')
    "\"\"\"te\"\"\"\"st\"\"\""
    """
    replaced_chars = name.replace('"', '""')
    return f'"{replaced_chars}"'
