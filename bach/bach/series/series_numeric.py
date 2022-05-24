"""
Copyright 2021 Objectiv B.V.
"""
from abc import ABC
from typing import cast, Union, TYPE_CHECKING, Optional, List, Tuple

import numpy
from sqlalchemy.engine import Dialect

from bach.series import Series
from bach.expression import Expression, AggregateFunctionExpression
from bach.series.series import WrappedPartition
from bach.types import StructuredDtype
from sql_models.constants import DBDialect
from sql_models.util import is_postgres, is_bigquery, DatabaseNotSupportedException

if TYPE_CHECKING:
    from bach.series import SeriesBoolean


class SeriesAbstractNumeric(Series, ABC):
    """
    Abstract Series class that represents the base numeric types and its specific operations.

    **Operations**

    All common arithmetic operations are supported, as well as common aggregation functions, and statistical
    functions.

    Supported arithmetic operations:
    - add (+), subtract (-)
    - multiply (*), divide (/), floordiv (//), mod (%)
    - lshift (<<) and rshift(>>) for Integer types

    """
    def _arithmetic_operation(self, other, operation, fmt_str,
                              other_dtypes=('int64', 'float64'), dtype=None):
        return super()._arithmetic_operation(other, operation, fmt_str, other_dtypes, dtype)

    def _comparator_operation(self, other, comparator, other_dtypes=('int64', 'float64')) -> 'SeriesBoolean':
        return super()._comparator_operation(other, comparator, other_dtypes)

    def round(self, decimals: int = 0) -> 'SeriesAbstractNumeric':
        """
        Round the value of this series to the given amount of decimals.

        :param decimals: The amount of decimals to round to
        """
        return self.copy_override(
            expression=Expression.construct(f'round(cast({{}} as numeric), {decimals})', self)
        )

    def cut(self, bins: int, right: bool = True) -> 'SeriesAbstractNumeric':
        """
        Segments values into bins.

        :param bins: The amount of bins to segment data into
        :param right: If true (by default), each bin will include the rightmost edge. (e.g (x,y]).
        """
        from bach.operations.cut import CutOperation
        return CutOperation(series=self, bins=bins, right=right)()

    def qcut(self, q: Union[int, List[float]]) -> 'SeriesAbstractNumeric':
        """
        Segments values into equal-sized buckets based on rank or sample quantiles.

        :param q: Number of quantiles or list of quantiles to consider.

        :return: series containing each quantile range/interval per value. Original series is set as index.
        """
        from bach.operations.cut import QCutOperation
        return QCutOperation(series=self, q=q)()

    def _ddof_unsupported(self, ddof: Optional[int]):
        if ddof is not None and ddof != 1:
            raise NotImplementedError("ddof != 1 currently not implemented")

    # def kurt(self, partition: WrappedPartition = None, skipna: bool = True):
    #     return self.kurtosis(partition, skipna)
    #
    # def kurtosis(self, partition: WrappedPartition = None, skipna: bool = True):
    #     raise NotImplementedError("kurtosis currently not implemented")
    #
    # def mad(self, partition: WrappedPartition = None, skipna: bool = True):
    #     raise NotImplementedError("mad currently not implemented")
    #
    # def prod(self, partition: WrappedPartition = None, skipna: bool = True):
    #     return self.product(partition, skipna)
    #
    # def product(self, partition: WrappedPartition = None, skipna: bool = True):
    #     raise NotImplementedError("prod currently not implemented")
    #
    # def skew(self, partition: WrappedPartition = None, skipna: bool = True):
    #     raise NotImplementedError("skew currently not implemented")

    def sem(self, partition: WrappedPartition = None, skipna: bool = True, ddof: int = None, **kwargs):
        """
        Get the unbiased standard error of the mean.
        Normalized by N-1 by default.

        :param partition: The partition or window to apply
        :param skipna: Exclude NA/NULL values
        :param ddof: Delta degrees of freedom. he divisor used in calculations is N - ddof,
            where N represents the number of elements
        """
        self._ddof_unsupported(ddof)
        return self._derived_agg_func(
            partition,
            AggregateFunctionExpression.construct(f'{{}}/sqrt({{}})',
                                                  self.std(partition, skipna=skipna, ddof=ddof),
                                                  self.count(partition, skipna=skipna)),
            skipna=skipna
        )

    def std(self, partition: WrappedPartition = None, skipna: bool = True, ddof: int = None, **kwargs):
        """
        Get the standard deviation of the input values
        Normalized by N-1 by default.

        :param partition: The partition or window to apply
        :param skipna: Exclude NA/NULL values
        :param ddof: Delta degrees of freedom. The divisor used in calculations is N - ddof,
            where N represents the number of elements
        """
        if ddof is not None and ddof not in (0, 1):
            raise NotImplementedError(f"ddof == {ddof} currently not implemented")

        if ddof == 0:
            return self._derived_agg_func(partition, 'stddev_pop', skipna=skipna)
        return self._derived_agg_func(partition, 'stddev_samp', skipna=skipna)

    def sum(self, partition: WrappedPartition = None, skipna: bool = True, min_count: int = None, **kwargs):
        """
        Get the sum of the input values.

        :param partition: The partition or window to apply
        :param skipna: Exclude NA/NULL values
        :param min_count: This minimum amount of values (not NULL) to be present before returning a result.
        """
        return self._derived_agg_func(partition, 'sum', skipna=skipna, min_count=min_count)

    def mean(self, partition: WrappedPartition = None, skipna: bool = True, **kwargs) -> 'SeriesFloat64':
        """
        Get the mean/average of the input values.

        :param partition: The partition or window to apply
        :param skipna: Exclude NA/NULL values
        """
        return cast(
            'SeriesFloat64',  # for the mypies
            self._derived_agg_func(partition, 'avg', 'double precision', skipna=skipna),
        )

    def quantile(
        self, partition: WrappedPartition = None, q: Union[float, List[float]] = 0.5, **kwargs
    ) -> 'SeriesFloat64':
        """
        When q is a float or len(q) == 1, the resultant series index will remain
        In case multiple quantiles are calculated, the resultant series index will have all calculated
        quantiles as index values.

        :param partition: The partition or window to apply
        :param q: A quantile or list of quantiles to be calculated
        """
        from bach.quantile import calculate_quantiles
        result = calculate_quantiles(self, partition=partition, q=q)
        return cast('SeriesFloat64', result)

    def var(self, partition: WrappedPartition = None, skipna: bool = True, ddof: int = None, **kwargs):
        """
        Get the sample variance of the input values (square of the sample standard deviation)
        Normalized by N-1 by default.

        :param partition: The partition or window to apply
        :param skipna: Exclude NA/NULL values
        :param ddof: Delta degrees of freedom. he divisor used in calculations is N - ddof,
            where N represents the number of elements
        """
        self._ddof_unsupported(ddof)
        return self._derived_agg_func(partition, 'var_samp', skipna=skipna)

    def scale(self, with_mean: bool = True, with_std: bool = True) -> 'Series':
        """
        Standardizes series based on mean and population standard deviation.

        :param with_mean: if true, each value will be centered before scaling
        :param with_std: if true, each value will be scaled to unit variance

        :return: Series
        """
        return self.to_frame().scale(with_mean, with_std)[self.name]

    def minmax_scale(self, feature_range: Tuple[int, int] = (0, 1)) -> 'Series':
        """
        Scales series based on a given range.

        :param feature_range: ``tuple(min, max)`` desired range to use for scaling.
        :return: Series
        """
        return self.to_frame().minmax_scale(feature_range)[self.name]


class SeriesInt64(SeriesAbstractNumeric):
    """
    Series type for integer data.

    **Operations and Functions**

    All common arithmetic operations are supported, as well as common aggregation functions, and statistical
    functions.

    Supported arithmetic operations:
    - add (+), subtract (-)
    - multiply (*), divide (/), floordiv (//), mod (%)
    - lshift (<<) and rshift(>>)

    See the base class :class:`SeriesAbstractNumeric` for an overview of the supported aggregation and
    statistical functions.


    **Database support and types**

    * Postgres: utilizes the 'bigint' database type.
    * BigQuery: utilizes the 'INT64' database type.
    """
    dtype = 'int64'
    dtype_aliases = ('integer', 'bigint', 'i8', int, numpy.int64, 'int32')
    supported_db_dtype = {
        DBDialect.POSTGRES: 'bigint',
        DBDialect.BIGQUERY: 'INT64'
    }
    supported_value_types = (int, numpy.int64, numpy.int32)

    @classmethod
    def supported_literal_to_expression(cls, dialect: Dialect, literal: Expression) -> Expression:
        if is_postgres(dialect):
            # A stringified integer is a valid integer or bigint literal, depending on the size. We want to
            # consistently get bigints, so always cast the result
            # See the section on numeric constants in the Postgres documentation
            # https://www.postgresql.org/docs/14/sql-syntax-lexical.html#SQL-SYNTAX-CONSTANTS
            return Expression.construct(f'cast({{}} as {cls.get_db_dtype(dialect)})', literal)
        if is_bigquery(dialect):
            # BigQuery has only one integer type, so there is no confusion between 32-bit and 64-bit integers
            # https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types#integer_type
            # https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical#integer_literals
            return literal
        raise DatabaseNotSupportedException(dialect)

    @classmethod
    def supported_value_to_literal(
            cls,
            dialect: Dialect,
            value: int,
            dtype: StructuredDtype
    ) -> Expression:
        return Expression.raw(str(value))

    @classmethod
    def dtype_to_expression(cls, dialect: Dialect, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'int64':
            return expression
        if source_dtype not in ['float64', 'bool', 'string']:
            raise ValueError(f'cannot convert {source_dtype} to int64')
        return Expression.construct(f'cast({{}} as {cls.get_db_dtype(dialect)})', expression)

    def _arithmetic_operation(self, other, operation, fmt_str, other_dtypes=('int64', 'float64'), dtype=None):
        # Override this method, because we need to return a float if we interact with one.
        type_mapping = dtype if dtype else {
            'int64': 'int64',
            'float64': 'float64'
        }
        return super()._arithmetic_operation(other, operation, fmt_str, other_dtypes, type_mapping)

    def __truediv__(self, other) -> 'Series':
        return self.astype('float64') / other

    def __rshift__(self, other):
        if is_postgres(self.engine):
            # Postgres expects the argument to a bitshift to be a regular int, not bigint.
            return self._arithmetic_operation(other, 'rshift', '({}) >> cast({} as int)',
                                              other_dtypes=tuple(['int64']))
        return self._arithmetic_operation(other, 'rshift', '({}) >> ({})', other_dtypes=tuple(['int64']))

    def __lshift__(self, other):
        if is_postgres(self.engine):
            # Postgres expects the argument to a bitshift to be a regular int, not bigint.
            return self._arithmetic_operation(other, 'lshift', '({}) << cast({} as int)',
                                              other_dtypes=tuple(['int64']))
        return self._arithmetic_operation(other, 'lshift', '({}) << ({})', other_dtypes=tuple(['int64']))

    def sum(self, partition: WrappedPartition = None, skipna: bool = True, min_count: int = None, **kwargs):
        # sum() has the tendency to return float on bigint arguments. Cast it back.
        series = super().sum(partition, skipna, min_count)
        return series.copy_override(
            expression=Expression.construct('cast({} as bigint)', series.expression))

    def round(self, decimals: int = 0) -> 'SeriesAbstractNumeric':
        # round() should not affect int dtype series.
        return self


class SeriesFloat64(SeriesAbstractNumeric):
    """
    Series type for float data.

    **Operations and Functions**

    All common arithmetic operations are supported, as well as common aggregation functions, and statistical
    functions.

    Supported arithmetic operations:
    - add (+), subtract (-)
    - multiply (*), divide (/), floordiv (//), mod (%)

    See the base class :class:`SeriesAbstractNumeric` for an overview of the supported aggregation and
    statistical functions.

    **Database support and types**

    * Postgres: utilizes the 'double precision' database type.
    * BigQuery: utilizes the 'FLOAT64' database type.
    """
    dtype = 'float64'
    dtype_aliases = ('float', 'double', 'f8', float, numpy.float64, 'double precision')
    supported_db_dtype = {
        DBDialect.POSTGRES: 'double precision',
        DBDialect.BIGQUERY: 'FLOAT64'
    }
    supported_value_types = (float, numpy.float64)

    # Notes for supported_value_to_literal() and supported_literal_to_expression():
    #
    # ### Postgres ###
    # Postgres will automatically parse any number with a decimal point as a number of type `numeric`,
    # which could be casted to float. However we specify the value always as a string, as there are some
    # values that cannot be expressed as a numeric literal directly (NaN, infinity, and -infinity), and
    # a value that cannot be represented as numeric (-0.0).
    # See the sections on numeric constants, and on fLoating-point types in the Postgres documentation
    # https://www.postgresql.org/docs/14/sql-syntax-lexical.html#SQL-SYNTAX-CONSTANTS
    # https://www.postgresql.org/docs/14/datatype-numeric.html#DATATYPE-FLOAT
    #
    # ### BigQuery ###
    # BigQuery parses floating point literals as a float, no casts needed. However the special values (NaN,
    # infinity, and -infinity) can only be specified as strings that are then cast. For simplicity, we
    # always use a string literal that we then cast to float, just as we do for Postgres.
    # https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types#floating_point_types
    # https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical#floating_point_literals

    @classmethod
    def supported_literal_to_expression(cls, dialect: Dialect, literal: Expression) -> Expression:
        return Expression.construct(f'cast({{}} as {cls.get_db_dtype(dialect)})', literal)

    @classmethod
    def supported_value_to_literal(
        cls,
        dialect: Dialect,
        value: Union[float, numpy.float64],
        dtype: StructuredDtype
    ) -> Expression:
        return Expression.string_value(str(value))

    @classmethod
    def dtype_to_expression(cls, dialect: Dialect, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'float64':
            return expression
        if source_dtype not in ['int64', 'string']:
            raise ValueError(f'cannot convert {source_dtype} to float64')
        return Expression.construct(f'cast({{}} as {cls.get_db_dtype(dialect)})', expression)
