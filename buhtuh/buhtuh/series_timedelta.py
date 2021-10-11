"""
Copyright 2021 Objectiv B.V.
"""
import datetime
from typing import Union, TYPE_CHECKING

import numpy

from buhtuh import BuhTuhSeries, const_to_series

if TYPE_CHECKING:
    from buhtuh import BuhTuhSeriesString


class BuhTuhSeriesTimedelta(BuhTuhSeries):
    dtype = 'timedelta'
    dtype_aliases = ('interval',)
    supported_db_dtype = 'interval'
    supported_value_types = (datetime.timedelta, numpy.timedelta64, str)

    @classmethod
    def value_to_sql(cls, value: Union[str, numpy.timedelta64, datetime.timedelta]) -> str:
        if isinstance(value, (numpy.timedelta64, datetime.timedelta)):
            value = str(value)
        if not isinstance(value, str):
            raise TypeError(f'value should be str or (numpy.timedelta64, datetime.timedelta), '
                            f'actual type: {type(value)}')
        # TODO: fix sql injection!
        # Maybe we should do some checking on syntax here?
        return f"'{value}'::{BuhTuhSeriesTimedelta.supported_db_dtype}"

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: str) -> str:
        if source_dtype == 'timedelta':
            return expression
        else:
            if not source_dtype == 'string':
                raise ValueError(f'cannot convert {source_dtype} to timedelta')
            return f'({expression}::{BuhTuhSeriesTimedelta.supported_db_dtype})'

    def _comparator_operator(self, other, comparator):
        other = const_to_series(base=self, value=other)
        self._check_supported(f"comparator '{comparator}'", ['timedelta', 'date', 'time', 'string'], other)
        expression = f'({self.expression}) {comparator} ({other.expression})'
        return self._get_derived_series('bool', expression)

    def format(self, format) -> 'BuhTuhSeriesString':
        """
        Allow standard PG formatting of this Series (to a string type)

        :param format: The format as defined in https://www.postgresql.org/docs/9.1/functions-formatting.html
        :return: a derived Series that accepts and returns formatted timestamp strings
        """
        expr = f"to_char({self.expression}, '{format}')"
        return self._get_derived_series('string', expr)

    def __add__(self, other) -> 'BuhTuhSeriesTimedelta':
        other = const_to_series(base=self, value=other)
        self._check_supported('add', ['timedelta', 'timestamp', 'date', 'time'], other)
        expression = f'({self.expression}) + ({other.expression})'
        return self._get_derived_series('timedelta', expression)

    def __sub__(self, other) -> 'BuhTuhSeriesTimedelta':
        other = const_to_series(base=self, value=other)
        self._check_supported('sub', ['timedelta', 'timestamp', 'date', 'time'], other)
        expression = f'({self.expression}) - ({other.expression})'
        return self._get_derived_series('timedelta', expression)

    def sum(self) -> 'BuhTuhSeriesTimedelta':
        return self._get_derived_series('timedelta', f'sum({self.expression})')

    def average(self) -> 'BuhTuhSeriesTimedelta':
        return self._get_derived_series('timedelta', f'avg({self.expression})')
