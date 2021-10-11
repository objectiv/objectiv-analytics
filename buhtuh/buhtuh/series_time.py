"""
Copyright 2021 Objectiv B.V.
"""
import datetime
from typing import Union

from buhtuh import BuhTuhSeries, const_to_series


class BuhTuhSeriesTime(BuhTuhSeries):
    """
    Types in PG that we want to support: https://www.postgresql.org/docs/9.1/datatype-datetime.html
        time without time zone
    """
    dtype = 'time'
    dtype_aliases = tuple()  # type: ignore
    supported_db_dtype = 'time without time zone'
    supported_value_types = (datetime.time, str)

    @classmethod
    def value_to_sql(cls, value: Union[str, datetime.time]) -> str:
        if isinstance(value, datetime.time):
            value = str(value)
        if not isinstance(value, str):
            raise TypeError(f'value should be str or datetime.time, actual type: {type(value)}')
        # TODO: fix sql injection!
        # Maybe we should do some checking on syntax here?
        return f"'{value}'::{BuhTuhSeriesTime.supported_db_dtype}"

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: str) -> str:
        if source_dtype == 'time':
            return expression
        else:
            if source_dtype not in ['string', 'timestamp']:
                raise ValueError(f'cannot convert {source_dtype} to time')
            return f'({expression}::{BuhTuhSeriesTime.supported_db_dtype})'

    def _comparator_operator(self, other, comparator):
        other = const_to_series(base=self, value=other)
        self._check_supported(f"comparator '{comparator}'", ['time', 'string'], other)
        expression = f'({self.expression}) {comparator} ({other.expression})'
        return self._get_derived_series('bool', expression)
