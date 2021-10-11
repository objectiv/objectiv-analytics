"""
Copyright 2021 Objectiv B.V.
"""
import datetime
from typing import Union, TYPE_CHECKING

import numpy

from buhtuh import BuhTuhSeries, const_to_series


if TYPE_CHECKING:
    from buhtuh import BuhTuhSeriesString


class BuhTuhSeriesTimestamp(BuhTuhSeries):
    """
    Types in PG that we want to support: https://www.postgresql.org/docs/9.1/datatype-datetime.html
        timestamp without time zone
    """
    dtype = 'timestamp'
    dtype_aliases = ('datetime64', 'datetime64[ns]', numpy.datetime64)
    supported_db_dtype = 'timestamp without time zone'
    supported_value_types = (datetime.datetime, datetime.date, str)

    @classmethod
    def value_to_sql(cls, value: Union[str, datetime.datetime]) -> str:
        if isinstance(value, datetime.date):
            value = str(value)
        if not isinstance(value, str):
            raise TypeError(f'value should be str or datetime.datetime, actual type: {type(value)}')
        # TODO: fix sql injection!
        # Maybe we should do some checking on syntax here?
        return f"'{value}'::{BuhTuhSeriesTimestamp.supported_db_dtype}"

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: str) -> str:
        if source_dtype == 'timestamp':
            return expression
        else:
            if source_dtype not in ['string', 'date']:
                raise ValueError(f'cannot convert {source_dtype} to timestamp')
            return f'({expression}::{BuhTuhSeriesTimestamp.supported_db_dtype})'

    def _comparator_operator(self, other, comparator):
        other = const_to_series(base=self, value=other)
        self._check_supported(f"comparator '{comparator}'", ['timestamp', 'date', 'string'], other)
        expression = f'({self.expression}) {comparator} ({other.expression})'
        return self._get_derived_series('bool', expression)

    def format(self, format) -> 'BuhTuhSeriesString':
        """
        Allow standard PG formatting of this Series (to a string type)

        :param format: The format as defined in https://www.postgresql.org/docs/14/functions-formatting.html
        :return: a derived Series that accepts and returns formatted timestamp strings
        """
        expr = f"to_char({self.expression}, '{format}')"
        return self._get_derived_series('string', expr)

    def __sub__(self, other) -> 'BuhTuhSeriesTimestamp':
        other = const_to_series(base=self, value=other)
        self._check_supported('sub', ['timestamp', 'date', 'time'], other)
        expression = f'({self.expression}) - ({other.expression})'
        return self._get_derived_series('timedelta', expression)


class BuhTuhSeriesDate(BuhTuhSeriesTimestamp):
    """
    Types in PG that we want to support: https://www.postgresql.org/docs/9.1/datatype-datetime.html
        date
    """
    dtype = 'date'
    dtype_aliases = tuple()  # type: ignore
    supported_db_dtype = 'date'
    supported_value_types = (datetime.datetime, datetime.date, str)

    @classmethod
    def value_to_sql(cls, value: Union[str, datetime.date]) -> str:
        if isinstance(value, datetime.date):
            value = str(value)
        if not isinstance(value, str):
            raise TypeError(f'value should be str or datetime.date, actual type: {type(value)}')
        # TODO: fix sql injection!
        # Maybe we should do some checking on syntax here?
        return f"'{value}'::{BuhTuhSeriesDate.supported_db_dtype}"

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: str) -> str:
        if source_dtype == 'date':
            return expression
        else:
            if source_dtype not in ['string', 'timestamp']:
                raise ValueError(f'cannot convert {source_dtype} to date')
            return f'({expression}::{BuhTuhSeriesDate.supported_db_dtype})'
