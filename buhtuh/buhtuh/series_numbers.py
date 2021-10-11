"""
Copyright 2021 Objectiv B.V.
"""
from abc import ABC
from typing import Union

import numpy

from buhtuh import const_to_series, BuhTuhSeries


class BuhTuhSeriesAbstractNumeric(BuhTuhSeries, ABC):
    """
    Base class that defines shared logic between BuhTuhSeriesInt64 and BuhTuhSeriesFloat64
    """
    def __add__(self, other) -> 'BuhTuhSeries':
        other = const_to_series(base=self, value=other)
        self._check_supported('add', ['int64', 'float64'], other)
        expression = f'({self.expression}) + ({other.expression})'
        new_dtype = 'float64' if 'float64' in (self.dtype, other.dtype) else 'int64'
        return self._get_derived_series(new_dtype, expression)

    def __sub__(self, other) -> 'BuhTuhSeries':
        other = const_to_series(base=self, value=other)
        self._check_supported('sub', ['int64', 'float64'], other)
        expression = f'({self.expression}) - ({other.expression})'
        new_dtype = 'float64' if 'float64' in (self.dtype, other.dtype) else 'int64'
        return self._get_derived_series(new_dtype, expression)

    def _comparator_operator(self, other, comparator):
        other = const_to_series(base=self, value=other)
        self._check_supported(f"comparator '{comparator}'", ['int64', 'float64'], other)
        expression = f'({self.expression}) {comparator} ({other.expression})'
        return self._get_derived_series('bool', expression)

    def __truediv__(self, other):
        other = const_to_series(base=self, value=other)
        self._check_supported('division', ['int64', 'float64'], other)
        expression = f'({self.expression})::float / ({other.expression})'
        return self._get_derived_series('float64', expression)

    def __floordiv__(self, other):
        other = const_to_series(base=self, value=other)
        self._check_supported('division', ['int64', 'float64'], other)
        expression = f'({self.expression})::int / ({other.expression})::int'
        return self._get_derived_series('int64', expression)

    def sum(self):
        # TODO: This cast here is rather nasty
        return self._get_derived_series('int64', f'sum({self.expression})::int')


class BuhTuhSeriesInt64(BuhTuhSeriesAbstractNumeric):
    dtype = 'int64'
    dtype_aliases = ('integer', 'bigint', 'i8', int, numpy.int64)
    supported_db_dtype = 'bigint'
    supported_value_types = (int, numpy.int64)

    @classmethod
    def value_to_sql(cls, value: int) -> str:
        if not isinstance(value, cls.supported_value_types):
            raise TypeError(f'value should be int, actual type: {type(value)}')
        return f'{value}::bigint'

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: str) -> str:
        if source_dtype == 'int64':
            return expression
        else:
            if source_dtype not in ['float64', 'bool', 'string']:
                raise ValueError(f'cannot convert {source_dtype} to int64')
            return f'({expression})::bigint'


class BuhTuhSeriesFloat64(BuhTuhSeriesAbstractNumeric):
    dtype = 'float64'
    dtype_aliases = ('float', 'double', 'f8', float, numpy.float64, 'double precision')
    supported_db_dtype = 'double precision'
    supported_value_types = (float, numpy.float64)

    @classmethod
    def value_to_sql(cls, value: Union[float, numpy.float64]) -> str:
        if not isinstance(value, cls.supported_value_types):
            raise TypeError(f'value should be float, actual type: {type(value)}')
        return f'{value}::float'

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: str) -> str:
        if source_dtype == 'float64':
            return expression
        else:
            if source_dtype not in ['int64', 'string']:
                raise ValueError(f'cannot convert {source_dtype} to float64')
            return f'({expression})::float'
