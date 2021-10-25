"""
Copyright 2021 Objectiv B.V.
"""
from abc import ABC
from typing import cast, Union, TYPE_CHECKING, Optional

import numpy

from buhtuh.series import BuhTuhSeries, const_to_series
from buhtuh.expression import Expression

if TYPE_CHECKING:
    from buhtuh.partitioning import BuhTuhGroupBy


class BuhTuhSeriesAbstractNumeric(BuhTuhSeries, ABC):
    """
    Base class that defines shared logic between BuhTuhSeriesInt64 and BuhTuhSeriesFloat64
    """
    def __add__(self, other) -> 'BuhTuhSeries':
        other = const_to_series(base=self, value=other)
        self._check_supported('add', ['int64', 'float64'], other)
        expression = Expression.construct('({}) + ({})', self, other)
        new_dtype = 'float64' if 'float64' in (self.dtype, other.dtype) else 'int64'
        return self._get_derived_series(new_dtype, expression)

    def __sub__(self, other) -> 'BuhTuhSeries':
        other = const_to_series(base=self, value=other)
        self._check_supported('sub', ['int64', 'float64'], other)
        expression = Expression.construct('({}) - ({})', self, other)
        new_dtype = 'float64' if 'float64' in (self.dtype, other.dtype) else 'int64'
        return self._get_derived_series(new_dtype, expression)

    def _comparator_operator(self, other, comparator):
        other = const_to_series(base=self, value=other)
        self._check_supported(f"comparator '{comparator}'", ['int64', 'float64'], other)
        expression = Expression.construct(f'({{}}) {comparator} ({{}})', self, other)
        return self._get_derived_series('bool', expression)

    def __truediv__(self, other):
        other = const_to_series(base=self, value=other)
        self._check_supported('division', ['int64', 'float64'], other)
        expression = Expression.construct('cast({} as float) / ({})', self, other)
        return self._get_derived_series('float64', expression)

    def __floordiv__(self, other):
        other = const_to_series(base=self, value=other)
        self._check_supported('division', ['int64', 'float64'], other)
        expression = Expression.construct('cast({} as bigint) / ({})', self, other)
        return self._get_derived_series('int64', expression)

    def round(self, decimals: int = 0):
        return self._get_derived_series(
            self.dtype,
            # cast to numeric, as double precision values can not be rounded
            # if you round, you don't care about precision anyway ;)
            Expression.construct(f'round(cast({{}} as numeric), {decimals})', self)
        )

    def _ddof_unsupported(self, ddof: Optional[float]):
        if ddof is not None and ddof != 1:
            raise NotImplementedError("ddof != 1 currently not implemented")

    def kurt(self, partition: 'BuhTuhGroupBy' = None, skipna: bool = True):
        return self.kurtosis(partition, skipna)

    def kurtosis(self, partition: 'BuhTuhGroupBy' = None, skipna: bool = True):
        raise NotImplementedError("kurtosis currently not implemented")

    def mad(self, partition: 'BuhTuhGroupBy' = None, skipna: bool = True):
        raise NotImplementedError("mad currently not implemented")

    def prod(self, partition: 'BuhTuhGroupBy' = None, skipna: bool = True):
        return self.product(partition, skipna)

    def product(self, partition: 'BuhTuhGroupBy' = None, skipna: bool = True):
        self._skipna_unsupported(skipna)

        # https://stackoverflow.com/questions/13156055/product-aggregate-in-postgresql
        # horrible solution, but best we have until we support custom defined aggregates
        return self._window_or_agg_func(
            partition,
            Expression.construct(f'exp(sum(ln({{}})))', self)
        )

    def skew(self, partition: 'BuhTuhGroupBy' = None, skipna: bool = True):
        raise NotImplementedError("skew currently not implemented")

    def sem(self, partition: 'BuhTuhGroupBy' = None, skipna: bool = True, ddof: float = None):
        self._skipna_unsupported(skipna)
        self._ddof_unsupported(ddof)

        return self._window_or_agg_func(
            partition,
            Expression.construct(f'{{}}/sqrt({{}})',
                                 self.std(partition, skipna=skipna, ddof=ddof),
                                 self.count(partition, skipna=skipna))
        )

    def std(self, partition: 'BuhTuhGroupBy' = None, skipna: bool = True, ddof: float = None):
        # sample standard deviation of the input values
        self._ddof_unsupported(ddof)
        return self._derived_agg_func(partition, 'stddev_samp', skipna=skipna)

    def sum(self, partition: 'BuhTuhGroupBy' = None, skipna: bool = True, min_count: int = None):
        if min_count is not None:
            return self._window_or_agg_func(
                partition,
                Expression.construct(f'CASE WHEN {{}} >= {min_count} THEN {{}} ELSE NULL END',
                                     self.count(partition, skipna=skipna),
                                     self._derived_agg_func(partition, 'sum', skipna=skipna)))
        else:
            return self._derived_agg_func(partition, 'sum', skipna=skipna)

    def mean(self, partition: 'BuhTuhGroupBy' = None, skipna: bool = True) -> 'BuhTuhSeriesFloat64':
        return self._derived_agg_func(partition, 'avg', 'double precision', skipna=skipna)

    def var(self, partition: 'BuhTuhGroupBy' = None, skipna: bool = True, ddof: float = None):
        # sample variance of the input values (square of the sample standard deviation)
        self._ddof_unsupported(ddof)
        return self._derived_agg_func(partition, 'var_samp', skipna=skipna)


class BuhTuhSeriesInt64(BuhTuhSeriesAbstractNumeric):
    dtype = 'int64'
    dtype_aliases = ('integer', 'bigint', 'i8', int, numpy.int64)
    supported_db_dtype = 'bigint'
    supported_value_types = (int, numpy.int64)

    @classmethod
    def supported_value_to_expression(cls, value: int) -> Expression:
        # A stringified integer is a valid integer or bigint literal, depending on the size. We want to
        # consistently get bigints, so always cast the result
        # See the section on numeric constants in the Postgres documentation
        # https://www.postgresql.org/docs/14/sql-syntax-lexical.html#SQL-SYNTAX-CONSTANTS
        return Expression.construct('cast({} as bigint)', Expression.raw(str(value)))

    @classmethod
    def dtype_to_expression(cls, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'int64':
            return expression
        if source_dtype not in ['float64', 'bool', 'string']:
            raise ValueError(f'cannot convert {source_dtype} to int64')
        return Expression.construct('cast({} as bigint)', expression)


class BuhTuhSeriesFloat64(BuhTuhSeriesAbstractNumeric):
    dtype = 'float64'
    dtype_aliases = ('float', 'double', 'f8', float, numpy.float64, 'double precision')
    supported_db_dtype = 'double precision'
    supported_value_types = (float, numpy.float64)

    @classmethod
    def supported_value_to_expression(cls, value: Union[float, numpy.float64]) -> Expression:
        # Postgres will automatically parse any number with a decimal point as a number of type `numeric`,
        # which could be casted to float. However we specify the value always as a string, as there are some
        # values that cannot be expressed as a numeric literal directly (NaN, infinity, and -infinity), and
        # a value that cannot be represented as numeric (-0.0).
        # See the sections on numeric constants, and on fLoating-point types in the Postgres documentation
        # https://www.postgresql.org/docs/14/sql-syntax-lexical.html#SQL-SYNTAX-CONSTANTS
        # https://www.postgresql.org/docs/14/datatype-numeric.html#DATATYPE-FLOAT
        str_value = str(value)
        return Expression.construct("cast({} as float)", Expression.string_value(str_value))

    @classmethod
    def dtype_to_expression(cls, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'float64':
            return expression
        if source_dtype not in ['int64', 'string']:
            raise ValueError(f'cannot convert {source_dtype} to float64')
        return Expression.construct('cast({} as float)', expression)
