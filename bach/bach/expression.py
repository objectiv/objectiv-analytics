"""
Copyright 2021 Objectiv B.V.
"""
import re
from dataclasses import dataclass
from typing import Optional, Union, TYPE_CHECKING, List, Dict, Tuple, Set, Sequence

from sqlalchemy.engine import Dialect

from sql_models.model import escape_raw_sql
from sql_models.util import quote_string, quote_identifier

if TYPE_CHECKING:
    from bach import Series
    from bach.sql_model import BachSqlModel


@dataclass(frozen=True)
class ExpressionToken:
    """ Abstract base class of ExpressionTokens"""

    def __post_init__(self):
        # Make sure that other code can rely on an ExpressionToken always being a subclass of this class.
        if self.__class__ == ExpressionToken:
            raise TypeError("Cannot instantiate ExpressionToken directly. Instantiate a subclass.")

    def to_sql(self, dialect: Dialect):
        """
        Must be implemented by subclasses. Generated SQL must be assumed to be used as raw sql in
        SqlModel.sql, therefore unknown/untrusted/etc. values should be properly escaped:
         * escape_format_string() twice, unless the value is a specific SqlModel placeholder or reference
         * other escaping/quoting as needed.
        """
        # Not abstract so we can stay a dataclass.
        raise NotImplementedError()


@dataclass(frozen=True)
class RawToken(ExpressionToken):
    raw: str

    def to_sql(self, dialect: Dialect) -> str:
        return escape_raw_sql(self.raw)


@dataclass(frozen=True)
class VariableToken(ExpressionToken):
    dtype: str
    name: str

    def to_sql(self, dialect: Dialect) -> str:
        return '{' + self.dtype_name_to_placeholder_name(self.dtype, self.name) + '}'

    @property
    def dtype_name(self):
        from bach.dataframe import DtypeNamePair
        return DtypeNamePair(dtype=self.dtype, name=self.name)

    @classmethod
    def dtype_name_to_placeholder_name(cls, dtype: str, name: str) -> str:
        return f'___bach_variable___{dtype}___{name}'

    @classmethod
    def placeholder_name_to_token(cls, placeholder_name: str) -> Optional['VariableToken']:
        """
        Reverse of dtype_name_to_placeholder_name().
        Will return None if the placeholder_name doesn't match the pattern
        """
        match = re.match('^___bach_variable___([a-zA-Z0-9)]+)___(.+)$', placeholder_name)
        if not match:
            return None
        return cls(match.group(1), match.group(2))


@dataclass(frozen=True)
class TableColumnReferenceToken(ExpressionToken):
    table_name: Optional[str]
    column_name: str

    def to_sql(self, dialect: Dialect):
        t = f'{quote_identifier(dialect, self.table_name)}.' if self.table_name else ''
        col_name = quote_identifier(dialect, self.column_name)
        return escape_raw_sql(f'{t}{col_name}')


@dataclass(frozen=True)
class ColumnReferenceToken(ExpressionToken):
    column_name: str

    def to_sql(self, dialect: Dialect):
        raise ValueError('ColumnReferenceTokens should be resolved first using '
                         'Expression.resolve_column_references')

    def resolve(self, table_name: Optional[str]) -> TableColumnReferenceToken:
        return TableColumnReferenceToken(table_name=table_name, column_name=self.column_name)


@dataclass(frozen=True)
class ModelReferenceToken(ExpressionToken):
    model: 'BachSqlModel'

    def refname(self) -> str:
        return f'reference{self.model.hash}'

    def to_sql(self, dialect: Dialect) -> str:
        return f'{{{{{self.refname()}}}}}'


@dataclass(frozen=True)
class StringValueToken(ExpressionToken):
    """ Wraps a string value. The value in this object is unescaped and unquoted. """
    value: str

    def to_sql(self, dialect: Dialect) -> str:
        return escape_raw_sql(quote_string(dialect, self.value))


@dataclass(frozen=True)
class IdentifierToken(ExpressionToken):
    name: str

    def to_sql(self, dialect: Dialect) -> str:
        return escape_raw_sql(quote_identifier(dialect, self.name))


class Expression:
    """
    Immutable object representing a fragment of SQL as a sequence of sql-tokens or Expressions.

    Expressions can easily be converted to a string with actual sql using the to_sql() function. Storing a
    sql-expression using this class, rather than storing it directly as a string, makes it possible to
    for example substitute the table-name after constructing the expression.
    Additionally this move this burden of correctly quoting and escaping string literals to this class, if
    literals are expressed with the correct tokens at least.
    In the future we might add support for more literal types.

    This class does not offer full-tokenization of sql. There are only a limited number of tokens for the
    needed use-cases. Most sql is simply encoded as a 'raw' token.

    For special type Expressions, this class is subclassed to assign special properties to a subexpression.
    """

    def __init__(self, data: Union['Expression', Sequence[Union[ExpressionToken, 'Expression']]] = None):
        if not data:
            data = []
        if isinstance(data, Expression):
            # if we only got a base Expression, we absorb it.
            data = data.data if type(data) is Expression else [data]
        self._data: Tuple[Union[ExpressionToken, 'Expression'], ...] = tuple(data)

    @property
    def data(self) -> List[Union[ExpressionToken, 'Expression']]:
        return list(self._data)

    def __eq__(self, other):
        return isinstance(other, Expression) and self.data == other.data

    def __repr__(self):
        return f'{self.__class__}({repr(self.data)})'

    def __hash__(self):
        return hash(self._data)

    @classmethod
    def construct(cls, fmt: str, *args: Union['Expression', 'Series']) -> 'Expression':
        """
        Construct an Expression using a format string that can refer existing expressions.
        Every occurrence of `{}` in the fmt string will be replace with a provided expression (in order that
        they are given). All other parts of fmt will be converted to RawTokens.

        As a convenience, instead of Expressions it is also possible to give Series as args, in that
        case the series's expression is taken as Expression.

        :param fmt: format string
        :param args: 0 or more Expressions or Series. Number of args must exactly match number of `{}`
            occurrences in fmt.
        """

        sub_strs = fmt.split('{}')
        data: List[Union[ExpressionToken, Expression]] = []
        if len(args) != len(sub_strs) - 1:
            raise ValueError(f'For each {{}} in the fmt there should be an Expression provided. '
                             f'Found {{}}: {len(sub_strs) - 1}, provided expressions: {len(args)}')
        for i, sub_str in enumerate(sub_strs):
            if i > 0:
                arg = args[i - 1]
                if not isinstance(arg, Expression):  # arg is a Series
                    arg_expr = arg.expression
                else:
                    arg_expr = arg

                if isinstance(arg_expr, NonAtomicExpression):
                    data.extend([RawToken('('), arg_expr, RawToken(')')])
                else:
                    data.append(arg_expr)
            if sub_str != '':
                data.append(RawToken(raw=sub_str))
        return cls(data=data)

    @classmethod
    def construct_expr_as_name(cls, expr: 'Expression', name: str) -> 'Expression':
        """
        Construct an expression that represents the sql: {expr} as "name"
        """
        ident_expr = Expression.identifier(name)
        # TODO: enable this optimisation again
        # if expr.to_sql() == ident_expr.to_sql():
        #     # this is to prevent generating sql of the form `x as x`, we'll just return `x` in that case
        #     return expr
        return cls.construct('{} as {}', expr, ident_expr)

    @classmethod
    def raw(cls, raw: str) -> 'Expression':
        """ Return an expression that contains a single RawToken. """
        return cls([RawToken(raw)])

    @classmethod
    def variable(cls, dtype: str, name: str) -> 'Expression':
        """ Return an expression that contains a single RawToken. """
        return cls([VariableToken(dtype=dtype, name=name)])

    @classmethod
    def string_value(cls, value: str) -> 'Expression':
        """
        Return an expression that contains a single StringValueToken with the value.
        :param value: unquoted, unescaped string value.
        """
        return cls([StringValueToken(value)])

    @classmethod
    def identifier(cls, name: str) -> 'Expression':
        return cls([IdentifierToken(name=name)])

    @classmethod
    def column_reference(cls, field_name: str) -> 'Expression':
        """ Construct an expression for field-name, where field-name is a column in a table or CTE. """
        return cls([ColumnReferenceToken(field_name)])

    @classmethod
    def table_column_reference(cls, table_name: str, field_name: str) -> 'Expression':
        """ Construct an expression for table referenced field,
         where table_name is a reference of a table or CTE from which field_name is a column """
        return cls([TableColumnReferenceToken(table_name, field_name)])

    @classmethod
    def model_reference(cls, model: 'BachSqlModel') -> 'Expression':
        """ Construct an expression for model, where model is a reference to a model. """
        return cls([ModelReferenceToken(model)])

    @property
    def is_single_value(self):
        """
        Will this expression return just one value (at most)

        Any Expression made up out of Tokens and Expressions, where all Expressions are single values,
        are expected to also yield a single value. Leaves consisting only of Tokens are considered
        not single valued, so at least one SingleValueExpression need to be present for a branch to
        become single valued.
        """
        if isinstance(self, SingleValueExpression):
            return True
        all_single_value = [d.is_single_value for d in self._data if isinstance(d, Expression)]
        return len(all_single_value) and all(all_single_value)

    @property
    def is_constant(self):
        """
        Does this expression represent a constant value, or an expressions constructed of only constants

        Any Expression made up out of Tokens and Expressions, where all Expressions are constant
        is considered constant. Leaves consisting only of Tokens are considered not constant, so
        at least one ConstValueExpressions need to be present for a branch to become constant.
        """
        if isinstance(self, ConstValueExpression):
            return True
        all_constant = [d.is_constant for d in self._data if isinstance(d, Expression)]
        return len(all_constant) and all(all_constant)

    @property
    def is_independent_subquery(self):
        return isinstance(self, IndependentSubqueryExpression)

    @property
    def has_aggregate_function(self) -> bool:
        """
        True iff we are a AggregateFunctionExpression, or there is at least one in this Expression.
        """
        return isinstance(self, AggregateFunctionExpression) or any(
            d.has_aggregate_function for d in self.data if isinstance(d, Expression)
        )

    @property
    def has_windowed_aggregate_function(self) -> bool:
        """
        True iff we are a WindowFunctionExpression, or there is at least one in this Expression.
        """
        return isinstance(self, WindowFunctionExpression) or any(
            d.has_windowed_aggregate_function for d in self.data if isinstance(d, Expression)
        )

    @property
    def has_table_column_references(self) -> bool:
        """
        True iff we are a TableColumnReference, or there is at least one in this Expression.
        """
        return any(
            isinstance(token, TableColumnReferenceToken) for token in self.get_all_tokens()
        )

    @property
    def has_multi_level_expressions(self) -> bool:
        return isinstance(self, MultiLevelExpression) or any(
            d.has_multi_level_expressions for d in self.data if isinstance(d, Expression)
        )

    def resolve_column_references(self, dialect: Dialect, table_name: Optional[str]) -> 'Expression':
        """ resolve the table name aliases for all columns in this expression """
        result: List[Union[ExpressionToken, Expression]] = []
        for data_item in self.data:
            if isinstance(data_item, Expression):
                result.append(data_item.resolve_column_references(dialect, table_name))
            elif isinstance(data_item, ColumnReferenceToken):
                result.append(data_item.resolve(table_name))
            else:
                result.append(data_item)
        return self.__class__(result)

    def replace_column_references(self, old_column_name: str, new_column_name: str) -> 'Expression':
        """
        replaces all ColumnReferenceToken where old_column_name is present with another ColumnReferenceToken
        """
        replaced_tokens = []
        for token in self.get_all_tokens():
            if not isinstance(token, ColumnReferenceToken) or token.column_name != old_column_name:
                replaced_tokens.append(token)
                continue
            replaced_tokens.append(ColumnReferenceToken(new_column_name))
        return self.__class__(replaced_tokens)

    def remove_table_column_references(self) -> Tuple[str, str, 'Expression']:
        """
        removes all table references from this expression.
        Returns first table_name and column_name found and a new expression without table column references
        """
        table_name = ''
        column_name = ''
        if not self.has_table_column_references:
            return table_name, column_name, self

        new_tokens: List[Union[ExpressionToken, Expression]] = []
        for token in self.get_all_tokens():
            if not isinstance(token, TableColumnReferenceToken):
                new_tokens.append(token)
                continue

            if table_name and table_name != token.table_name:
                raise Exception('expressions with different table references are not allowed.')

            table_name = token.table_name if token.table_name and not table_name else table_name
            column_name = column_name or token.column_name
            new_tokens.extend(Expression.column_reference(token.column_name).data)

        return table_name, column_name, Expression(new_tokens)

    def get_references(self) -> Dict[str, 'BachSqlModel']:
        rv = {}
        for data_item in self.data:
            if isinstance(data_item, Expression):
                rv.update(data_item.get_references())
            elif isinstance(data_item, ModelReferenceToken):
                rv[data_item.refname()] = data_item.model
        return rv

    def get_all_tokens(self) -> List[ExpressionToken]:
        result = []
        for data_item in self.data:
            if isinstance(data_item, Expression):
                result.extend(data_item.get_all_tokens())
            else:
                result.append(data_item)
        return result

    def to_sql(self, dialect: Dialect, table_name: Optional[str] = None) -> str:
        """
        Compile the expression to a SQL fragment by calling to_sql() on every token or expression in data
        :param table_name: Optional table name, if set all column-references will be compiled as
            '"{table_name}"."{column_name}"' instead of just '"{column_name}"'.
        :return SQL representation of the expression.
        """
        resolved_tables_expression = self.resolve_column_references(dialect, table_name)
        return ''.join(
            d.to_sql(dialect=dialect) for d in resolved_tables_expression.data
        )


class NonAtomicExpression(Expression):
    """
    An expression that needs '( .. )' around it when used together with other Expressions
    in Expression.construct(). This subclass is required, because not all Expressions need to be wrapped
    in parenthesis, e.g. `expression` `<` `ANY (subquery)` should probably have `expression` wrapped if it's
    a complex expression, but not the `ANY ...` part, since that would not be valid SQL.
    """
    pass


class IndependentSubqueryExpression(Expression):
    pass


class SingleValueExpression(Expression):
    """
    An Expression that is expected to return just one value.
    If wrapped around IndependentSubqueryExpression, this will still have is_independent_subquery == True
    """
    @property
    def is_independent_subquery(self) -> bool:
        # If this Expression is wrapped around a IndependentSubqueryExpression, most likely, there will be
        # just one in here, but let's make sure.
        all_isq = [d.is_independent_subquery for d in self._data if isinstance(d, Expression)]
        return len(all_isq) > 0 and all(all_isq)


class ConstValueExpression(SingleValueExpression):
    pass


class AggregateFunctionExpression(Expression):
    @property
    def is_constant(self) -> bool:
        # We don't consider an aggregate function constant even if all its subexpressions are,
        # because it requires materialization of the aggregation to actually be a constant value again.
        # Maybe we will revisit this some day. If that day comes, make sure to look at Series.count() as well.
        return False


class WindowFunctionExpression(Expression):
    """
    A WindowFunctionExpression contains an aggregation- or window function, and a window clause:
    e.g. agg_func() OVER (...). The agg_func. It's not a subclass of AggregateFunctionExpression because
    a window expression makes sense without the main query having a GROUP BY clause, as the partitioning
    is contained within the expression.

    """
    @property
    def is_constant(self) -> bool:
        # We don't consider an window expression constant even if all its subexpressions are,
        # because it requires materialization to actually be a constant value again.
        # Maybe we will revisit this some day. If that day comes, make sure to look at Series.count() as well.
        return False

    @property
    def has_aggregate_function(self) -> bool:
        # If a window expression contains an aggregate function, it's not an aggregate expression
        return False


class MultiLevelExpression(Expression):
    """
    A MultiLevelExpression contains multiple expressions referencing to different columns.
    """
    def to_sql(self, dialect: Dialect, table_name: Optional[str] = None) -> str:
        # same as original function, we just need to join by a comma since parent expression is composed
        # by multiple column references
        resolved_tables_expression = self.resolve_column_references(dialect, table_name)
        return ','.join(
            d.to_sql(dialect=dialect) for d in resolved_tables_expression.data
        )


def join_expressions(expressions: Sequence[Expression], join_str: str = ', ') -> Expression:
    """
    Construct an expression consisting of the given list of expressions joined by the join_str.
    """
    fmt = join_str.join(['{}'] * len(expressions))
    return Expression.construct(fmt, *expressions)


def get_variable_tokens(expressions: List['Expression']) -> Set[VariableToken]:
    """
    Get the names of all VariableTokens in the list of expressions
    """
    found_tokens = set()
    for expression in expressions:
        for token in expression.get_all_tokens():
            if isinstance(token, VariableToken):
                found_tokens.add(token)
    return found_tokens
