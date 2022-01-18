"""
Copyright 2021 Objectiv B.V.
"""
import datetime
from abc import ABC
from typing import Union, cast

import numpy

from bach.series import Series, SeriesString, SeriesBoolean
from bach.expression import Expression
from bach.series.series import WrappedPartition


class DateTimeOperation:
    def __init__(self, series: 'SeriesAbstractDateTime'):
        self._series = series

    def sql_format(self, format_str: str) -> SeriesString:
        """
        Allow formatting of this Series (to a string type).

        :param format_str: The format to apply to the date/time column.
            Currently, this uses Postgres' data format string syntax:
            https://www.postgresql.org/docs/14/functions-formatting.html

        .. code-block:: python

            df['year'] = df.some_date_series.dt.sql_format('YYYY')  # return year
            df['date'] = df.some_date_series.dt.sql_format('YYYYMMDD')  # return date

        :returns: a SeriesString containing the formatted date.
        """
        expression = Expression.construct('to_char({}, {})',
                                          self._series, Expression.string_value(format_str))
        return self._series.copy_override(dtype='string', expression=expression)


class SeriesAbstractDateTime(Series, ABC):
    """
    A Series that represents the generic date/time type and its specific operations. Selected arithmetic
    operations are accepted using the usual operators.

    **Date/Time Operations**

    On any of the subtypes, you can access date operations through the `dt` accessor.
    """
    @property
    def dt(self) -> DateTimeOperation:
        """
        Get access to date operations.

        .. autoclass:: bach.series.series_datetime.DateTimeOperation
            :members:

        """
        return DateTimeOperation(self)

    def _comparator_operation(self, other, comparator,
                              other_dtypes=('timestamp', 'date', 'time', 'string')) -> 'SeriesBoolean':
        return super()._comparator_operation(other, comparator, other_dtypes)

    @classmethod
    def _cast_to_date_if_dtype_date(cls, series: 'Series') -> 'Series':
        # PG returns timestamp in all cases were we expect date
        # Make sure we cast properly, and round similar to python datetime
        if series.dtype == 'date':
            return series.copy_override(
                expression=Expression.construct("cast({} + '12h'::interval as date)", series)
            )
        else:
            return series


class SeriesTimestamp(SeriesAbstractDateTime):
    """
    A Series that represents the timestamp/datetime type and its specific operations


    Types in PG that we want to support: https://www.postgresql.org/docs/9.1/datatype-datetime.html
        timestamp without time zone
    """
    dtype = 'timestamp'
    dtype_aliases = ('datetime64', 'datetime64[ns]', numpy.datetime64)
    supported_db_dtype = 'timestamp without time zone'
    supported_value_types = (datetime.datetime, datetime.date, str)

    @classmethod
    def supported_literal_to_expression(cls, literal: Expression) -> Expression:
        return Expression.construct('cast({} as timestamp without time zone)', literal)

    @classmethod
    def supported_value_to_literal(cls, value: Union[str, datetime.datetime]) -> Expression:
        # TODO: check here already that the string has the correct format
        str_value = str(value)
        return Expression.string_value(str_value)

    @classmethod
    def dtype_to_expression(cls, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'timestamp':
            return expression
        else:
            if source_dtype not in ['string', 'date']:
                raise ValueError(f'cannot convert {source_dtype} to timestamp')
            return Expression.construct(f'cast({{}} as {cls.supported_db_dtype})', expression)

    def __add__(self, other) -> 'Series':
        return self._arithmetic_operation(other, 'add', '({}) + ({})', other_dtypes=tuple(['timedelta']))

    def __sub__(self, other) -> 'Series':
        type_mapping = {
            'timedelta': 'timestamp',
            'timestamp': 'timedelta'
        }
        return self._arithmetic_operation(other, 'sub', '({}) - ({})',
                                          other_dtypes=tuple(type_mapping.keys()),
                                          dtype=type_mapping)


class SeriesDate(SeriesAbstractDateTime):
    """
    A Series that represents the date type and its specific operations

    Types in PG that we want to support: https://www.postgresql.org/docs/9.1/datatype-datetime.html
        date
    """
    dtype = 'date'
    dtype_aliases = tuple()  # type: ignore
    supported_db_dtype = 'date'
    supported_value_types = (datetime.datetime, datetime.date, str)

    @classmethod
    def supported_literal_to_expression(cls, literal: Expression) -> Expression:
        return Expression.construct(f'cast({{}} as date)', literal)

    @classmethod
    def supported_value_to_literal(cls, value: Union[str, datetime.date]) -> Expression:
        if isinstance(value, datetime.date):
            value = str(value)
        # TODO: check here already that the string has the correct format
        return Expression.string_value(value)

    @classmethod
    def dtype_to_expression(cls, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'date':
            return expression
        else:
            if source_dtype not in ['string', 'timestamp']:
                raise ValueError(f'cannot convert {source_dtype} to date')
            return Expression.construct(f'cast({{}} as {cls.supported_db_dtype})', expression)

    def __add__(self, other) -> 'Series':
        type_mapping = {
            'timedelta': 'date'  # PG returns timestamp, needs explicit cast to date
        }
        return self._cast_to_date_if_dtype_date(
            self._arithmetic_operation(other, 'add', '({}) + ({})',
                                       other_dtypes=tuple(type_mapping.keys()),
                                       dtype=type_mapping)
        )

    def __sub__(self, other) -> 'Series':
        type_mapping = {
            'date': 'timedelta',
            'timedelta': 'date',  # PG returns timestamp, needs explicit cast to date
        }
        if other.dtype == 'date':
            # PG does unexpected things when doing date - date. Work around that.
            fmt_str = 'cast(cast({} as timestamp) - ({}) as interval)'
        else:
            fmt_str = '({}) - ({})'

        return self._cast_to_date_if_dtype_date(
            self._arithmetic_operation(other, 'sub', fmt_str,
                                       other_dtypes=tuple(type_mapping.keys()),
                                       dtype=type_mapping)
        )


class SeriesTime(SeriesAbstractDateTime):
    """
    A Series that represents the date time and its specific operations

    Types in PG that we want to support: https://www.postgresql.org/docs/9.1/datatype-datetime.html
        time without time zone
    """
    dtype = 'time'
    dtype_aliases = tuple()  # type: ignore
    supported_db_dtype = 'time without time zone'
    supported_value_types = (datetime.time, str)

    @classmethod
    def supported_literal_to_expression(cls, literal: Expression) -> Expression:
        return Expression.construct('cast({} as time without time zone)', literal)

    @classmethod
    def supported_value_to_literal(cls, value: Union[str, datetime.time]) -> Expression:
        value = str(value)
        # TODO: check here already that the string has the correct format
        return Expression.string_value(value)

    @classmethod
    def dtype_to_expression(cls, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'time':
            return expression
        else:
            if source_dtype not in ['string', 'timestamp']:
                raise ValueError(f'cannot convert {source_dtype} to time')
            return Expression.construct(f'cast ({{}} as {cls.supported_db_dtype})', expression)

    # python supports no arithmetic on Time


class SeriesTimedelta(SeriesAbstractDateTime):
    """
    A Series that represents the timedelta type and its specific operations
    """

    dtype = 'timedelta'
    dtype_aliases = ('interval',)
    supported_db_dtype = 'interval'
    supported_value_types = (datetime.timedelta, numpy.timedelta64, str)

    @classmethod
    def supported_literal_to_expression(cls, literal: Expression) -> Expression:
        return Expression.construct('cast({} as interval)', literal)

    @classmethod
    def supported_value_to_literal(
            cls,
            value: Union[str, numpy.timedelta64, datetime.timedelta]
    ) -> Expression:
        value = str(value)
        # TODO: check here already that the string has the correct format
        return Expression.string_value(value)

    @classmethod
    def dtype_to_expression(cls, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'timedelta':
            return expression
        else:
            if not source_dtype == 'string':
                raise ValueError(f'cannot convert {source_dtype} to timedelta')
            return Expression.construct('cast({} as interval)', expression)

    def _comparator_operation(self, other, comparator,
                              other_dtypes=('timedelta', 'string')) -> SeriesBoolean:
        return super()._comparator_operation(other, comparator, other_dtypes)

    def __add__(self, other) -> 'Series':
        type_mapping = {
            'date': 'date',  # PG makes this a timestamp
            'timedelta': 'timedelta',
            'timestamp': 'timestamp'
        }
        return self._cast_to_date_if_dtype_date(
            self._arithmetic_operation(other, 'add', '({}) + ({})',
                                       other_dtypes=tuple(type_mapping.keys()),
                                       dtype=type_mapping))

    def __sub__(self, other) -> 'Series':
        type_mapping = {
            'timedelta': 'timedelta',
        }
        return self._arithmetic_operation(other, 'sub', '({}) - ({})',
                                          other_dtypes=tuple(type_mapping.keys()),
                                          dtype=type_mapping)

    def __mul__(self, other) -> 'Series':
        return self._arithmetic_operation(other, 'mul', '({}) * ({})', other_dtypes=('int64', 'float64'))

    def __truediv__(self, other) -> 'Series':
        return self._arithmetic_operation(other, 'div', '({}) / ({})', other_dtypes=('int64', 'float64'))

    def sum(self, partition: WrappedPartition = None,
            skipna: bool = True, min_count: int = None) -> 'SeriesTimedelta':
        """
        :meta private:
        """
        result = self._derived_agg_func(
            partition=partition,
            expression='sum',
            skipna=skipna,
            min_count=min_count
        )
        return cast('SeriesTimedelta', result)

    def mean(self, partition: WrappedPartition = None, skipna: bool = True) -> 'SeriesTimedelta':
        """
        :meta private:
        """
        result = self._derived_agg_func(
            partition=partition,
            expression='avg',
            skipna=skipna
        )
        return cast('SeriesTimedelta', result)
