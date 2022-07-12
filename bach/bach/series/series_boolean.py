"""
Copyright 2021 Objectiv B.V.
"""
from abc import ABC
from typing import cast

from sqlalchemy.engine import Dialect

from bach.series import Series
from bach.expression import Expression
from bach.series.series import WrappedPartition
from bach.types import StructuredDtype
from sql_models.constants import DBDialect
from sql_models.util import is_postgres, is_bigquery, DatabaseNotSupportedException


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

    **Database support and types**

    * Postgres: utilizes the 'boolean' database type.
    * BigQuery: utilizes the 'BOOL' database type.
    """
    dtype = 'bool'
    dtype_aliases = ('boolean', '?', bool)
    supported_db_dtype = {
        DBDialect.POSTGRES: 'boolean',
        DBDialect.BIGQUERY: 'BOOL',
    }
    supported_value_types = (bool, )

    # Notes for supported_value_to_literal() and supported_literal_to_expression():
    # 'True' and 'False' are valid boolean literals in Postgres
    # See https://www.postgresql.org/docs/14/datatype-boolean.html

    @classmethod
    def supported_literal_to_expression(cls, dialect: Dialect, literal: Expression) -> Expression:
        return literal

    @classmethod
    def supported_value_to_literal(
        cls,
        dialect: Dialect,
        value: bool,
        dtype: StructuredDtype
    ) -> Expression:
        return Expression.raw(str(value))

    @classmethod
    def dtype_to_expression(cls, dialect: Dialect, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'bool':
            return expression
        if source_dtype not in ['int64', 'string']:
            raise ValueError(f'cannot convert {source_dtype} to bool')
        if is_postgres(dialect):
            # Postgres cannot directly cast a bigint to bool.
            # So we do a comparison against 0 (==False) instead
            if source_dtype == 'int64':
                return Expression.construct('{} != 0', expression)
        # Default case: do a regular cast
        return Expression.construct(f'cast({{}} as {cls.get_db_dtype(dialect)})', expression)

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

    def min(self, partition: WrappedPartition = None, skipna: bool = True):
        """
        Returns the minimum value in the partition, i.e. value will be True iff all values in the
        partition are True.

        :param partition: The partition or window to apply
        :param skipna: only ``skipna=True`` supported. This means NULL values are ignored.
        :returns: a new Series with the aggregation applied
        """
        if is_postgres(self.engine):
            return self._derived_agg_func(partition, 'bool_and', skipna=skipna)
        if is_bigquery(self.engine):
            return self._derived_agg_func(partition, 'logical_and', skipna=skipna)
        raise DatabaseNotSupportedException(self.engine)

    def max(self, partition: WrappedPartition = None, skipna: bool = True):
        """
        Returns the maximum value in the partition, i.e. value will be False iff all values in the
        partition are False.

        :param partition: The partition or window to apply
        :param skipna: only ``skipna=True`` supported. This means NULL values are ignored.
        :returns: a new Series with the aggregation applied
        """
        if is_postgres(self.engine):
            return self._derived_agg_func(partition, 'bool_or', skipna=skipna)
        if is_bigquery(self.engine):
            return self._derived_agg_func(partition, 'logical_or', skipna=skipna)
        raise DatabaseNotSupportedException(self.engine)
