"""
Copyright 2021 Objectiv B.V.
"""
from abc import ABC
from typing import cast

from bach.series import Series, const_to_series
from bach.expression import Expression


class SeriesBoolean(Series, ABC):
    """
    A Series that represents the Boolean type and its specific operations

    Boolean Series can be used to create complex truth expressions like:
    `~(a & b ^ c)`, or in more human readable form `not(a and b xor c)`.

    .. code-block:: python

        ~a     not a (invert a)
        a & b  a and b
        a | b  a or b
        a ^ b  a xor b

    **Type Conversions**

    Boolean Series can be created from int and string values. Not all conversions errors will be caught on
    conversion time. Some will lead to database errors later.
    """
    dtype = 'bool'
    dtype_aliases = ('boolean', '?', bool)
    supported_db_dtype = 'boolean'
    supported_value_types = (bool, )

    # Notes for supported_value_to_literal() and supported_literal_to_expression():
    # 'True' and 'False' are valid boolean literals in Postgres
    # See https://www.postgresql.org/docs/14/datatype-boolean.html

    @classmethod
    def supported_literal_to_expression(cls, literal: Expression) -> Expression:
        return literal

    @classmethod
    def supported_value_to_literal(cls, value: bool) -> Expression:
        return Expression.raw(str(value))

    @classmethod
    def dtype_to_expression(cls, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'bool':
            return expression
        if source_dtype not in ['int64', 'string']:
            raise ValueError(f'cannot convert {source_dtype} to bool')
        return Expression.construct('cast({} as bool)', expression)

    def _comparator_operation(self, other, comparator, other_dtypes=tuple(['bool'])) -> 'SeriesBoolean':
        return super()._comparator_operation(other, comparator, other_dtypes)

    def _boolean_operator(self, other, operator: str, other_dtypes=tuple(['bool'])) -> 'SeriesBoolean':
        fmt_str = f'({{}}) {operator} ({{}})'
        if other.dtype != 'bool':
            # this is not currently used, as both bigint and float can not be cast to bool in PG
            fmt_str = f'({{}}) {operator} cast({{}} as bool)'
        return cast(
            'SeriesBoolean', self._binary_operation(
                other=other, operation=f"boolean operator '{operator}'",
                fmt_str=fmt_str, other_dtypes=other_dtypes, dtype='bool'
            )
        )

    def __invert__(self) -> 'SeriesBoolean':
        expression = Expression.construct('NOT ({})', self)
        return self.copy_override(expression=expression)

    def __and__(self, other) -> 'SeriesBoolean':
        return self._boolean_operator(other, 'AND')

    def __or__(self, other) -> 'SeriesBoolean':
        return self._boolean_operator(other, 'OR')

    def __xor__(self, other) -> 'SeriesBoolean':
        # This only works if both type are 'bool' in PG, but if the rhs is not, it will be cast
        # explicitly in _boolean_operator()
        return self._boolean_operator(other, '!=')
