"""
Copyright 2021 Objectiv B.V.
"""
import datetime
import warnings
from abc import ABC
from enum import Enum
from typing import Union, cast, List, Tuple, Optional, Any

import numpy
import pandas
from sqlalchemy.engine import Dialect

from bach import DataFrame
from bach.series import Series, SeriesString, SeriesBoolean, SeriesFloat64, SeriesInt64
from bach.expression import Expression, join_expressions
from bach.series.series import WrappedPartition, ToPandasInfo
from bach.series.utils.datetime_formats import parse_c_standard_code_to_postgres_code, \
    parse_c_code_to_bigquery_code
from bach.types import DtypeOrAlias, StructuredDtype
from sql_models.constants import DBDialect
from sql_models.util import is_postgres, is_bigquery, DatabaseNotSupportedException


class DatePart(str, Enum):
    DAY = 'days'
    HOUR = 'hours'
    MINUTE = 'minutes'
    SECOND = 'seconds'
    MILLISECOND = 'milliseconds'
    MICROSECOND = 'microseconds'


# conversions for date parts to seconds
# when adjusting intervals, 30-day time periods are represented as months
# BigQuery seems to follow Postgres threshold
# https://www.postgresql.org/docs/current/functions-datetime.html#:~:text=justify_days%20(%20interval%20)%20%E2%86%92%20interval,mon%205%20days
# For example 395 days is equal to 1 year, 1 month and 5 days.
_TOTAL_SECONDS_PER_DATE_PART = {
    DatePart.DAY:  24 * 60 * 60,
    DatePart.HOUR: 60 * 60,
    DatePart.MINUTE: 60,
    DatePart.SECOND: 1,
    DatePart.MILLISECOND: 1e-3,
    DatePart.MICROSECOND: 1e-6,
}


class DateTimeOperation:
    def __init__(self, series: 'SeriesAbstractDateTime'):
        self._series = series

    def sql_format(self, format_str: str) -> SeriesString:
        """
        Allow formatting of this Series (to a string type).

        :param format_str: The format to apply to the date/time column.
            Currently, this uses Postgres' data format string syntax:
            https://www.postgresql.org/docs/14/functions-formatting.html

        .. warning::
            This method is deprecated, we recommend using :meth:`SeriesAbstractDateTime.dt.strftime` instead.

        .. code-block:: python

            df['year'] = df.some_date_series.dt.sql_format('YYYY')  # return year
            df['date'] = df.some_date_series.dt.sql_format('YYYYMMDD')  # return date

        :returns: a SeriesString containing the formatted date.
        """
        warnings.warn(
            'Call to deprecated method, we recommend to use SeriesAbstractDateTime.dt.strftime instead',
            category=DeprecationWarning,
        )

        expression = Expression.construct('to_char({}, {})',
                                          self._series, Expression.string_value(format_str))
        str_series = self._series.copy_override_type(SeriesString).copy_override(expression=expression)
        return str_series

    def strftime(self, format_str: str) -> SeriesString:
        """
        Allow formatting of this Series (to a string type).

        :param format_str: The format to apply to the date/time column.
            This uses  1989 C standard format codes:
            https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes

        .. code-block:: python

            df['year'] = df.some_date_series.dt.sql_format('%Y')  # return year
            df['date'] = df.some_date_series.dt.sql_format('%Y%m%d')  # return date

        :returns: a SeriesString containing the formatted date.
        """
        engine = self._series.engine

        if is_postgres(engine):
            parsed_format_str = parse_c_standard_code_to_postgres_code(format_str)
            expression = Expression.construct(
                'to_char({}, {})', self._series, Expression.string_value(parsed_format_str),
            )
        elif is_bigquery(engine):
            # BQ uses C Standard Codes
            # https://cloud.google.com/bigquery/docs/reference/standard-sql/format-elements#format_elements_date_time
            parsed_format_str = parse_c_code_to_bigquery_code(format_str)
            expression = Expression.construct(
                'format_date({}, {})',
                Expression.string_value(parsed_format_str),
                self._series,
            )
        else:
            raise DatabaseNotSupportedException(engine)

        str_series = self._series.copy_override_type(SeriesString).copy_override(expression=expression)
        return str_series

    def date_trunc(self, date_part: str) -> Series:
        """
        Truncates date value based on a specified date part.
        The value is always rounded to the beginning of date_part.

        This operation can be applied only on SeriesDate or SeriesTimestamp.

        :param date_part: Allowed values are 'second', 'minute',
            'hour', 'day', 'week', 'month', 'quarter', and 'year'.

        .. code-block:: python

            # return the date corresponding to the Monday of that week
            df['week'] = df.some_date_or_timestamp_series.dt.date_trunc('week')
            # return the first day of the quarter
            df['quarter'] = df.some_date_or_timestamp_series.dt.date_trunc('quarter')

        :returns: the truncated timestamp value with a granularity of date_part.

        """

        available_formats = ['second', 'minute', 'hour', 'day', 'week',
                             'month', 'quarter', 'year']
        if date_part not in available_formats:
            raise ValueError(f'{date_part} format is not available.')

        if not (isinstance(self._series, SeriesDate) or
                isinstance(self._series, SeriesTimestamp)):
            raise ValueError(f'{type(self._series)} type is not supported.')

        engine = self._series.engine

        if is_postgres(engine):
            expression = Expression.construct(
                'date_trunc({}, {})',
                Expression.string_value(date_part),
                self._series,
            )
        elif is_bigquery(engine):
            if date_part == 'week':
                date_part = 'week(monday)'
            expression = Expression.construct(
                'timestamp_trunc({}, {})',
                self._series,
                Expression.raw(date_part),
            )
        else:
            raise DatabaseNotSupportedException(engine)

        return self._series.copy_override(expression=expression)


class TimedeltaOperation(DateTimeOperation):
    def _get_conversion_df(self) -> 'DataFrame':
        """
        generates a dataframe containing the amounts of seconds a supported date part has.
        """
        from bach import DataFrame
        conversion_df = pandas.DataFrame(
            data=[
                {
                    self._format_converted_series_name(dp): ts
                    for dp, ts in _TOTAL_SECONDS_PER_DATE_PART.items()
                },
            ]
        )
        convert_df = DataFrame.from_pandas(df=conversion_df, engine=self._series.engine, convert_objects=True)
        return convert_df.reset_index(drop=True)

    @staticmethod
    def _format_converted_series_name(date_part: DatePart) -> str:
        return f'_SECONDS_IN_{date_part.name}'

    @property
    def components(self) -> DataFrame:
        """
        :returns: a DataFrame containing all date parts from the timedelta.
        """
        df = self.total_seconds.to_frame()
        df = df.merge(self._get_conversion_df(), how='cross')

        # justifies total seconds into the units of each date component
        # after adjustment, it converts it back into seconds
        for date_part in DatePart:
            converted_series_name = self._format_converted_series_name(DatePart(date_part))
            df[f'ts_{date_part}'] = df['total_seconds'] // df[converted_series_name]
            df[f'ts_{date_part}'] *= df[converted_series_name]

        # materialize to avoid complex subquery
        df = df.materialize(node_name='justified_date_components')

        components_series_names = []
        prev_ts = ''

        # extract actual date component from justified seconds
        # by getting the difference between current and previous components
        # this helps on normalizing negative time deltas and have only negative values
        # in days.
        for date_part in DatePart:
            converted_series_name = self._format_converted_series_name(DatePart(date_part))

            component_name = f'{date_part}'
            current_ts = f'ts_{date_part}'

            if not prev_ts:
                df[component_name] = df[current_ts] / df[converted_series_name]
            else:
                df[component_name] = (df[current_ts] - df[prev_ts]) / df[converted_series_name]

            df[component_name] = cast(SeriesFloat64, df[component_name]).round(decimals=0)

            components_series_names.append(component_name)
            prev_ts = current_ts

        return df[components_series_names].astype('int64')

    @property
    def days(self) -> SeriesInt64:
        """
        converts total seconds into days and returns only the integral part of the result
        """
        day_series = self.total_seconds // _TOTAL_SECONDS_PER_DATE_PART[DatePart.DAY]

        day_series = day_series.astype('int64')
        return (
            day_series
            .copy_override_type(SeriesInt64)
            .copy_override(name='days')
        )

    @property
    def seconds(self) -> SeriesInt64:
        """
        removes days from total seconds (self.total_seconds % _SECONDS_IN_DAY)
        and returns only the integral part of the result
        """
        seconds_series = (self.total_seconds % _TOTAL_SECONDS_PER_DATE_PART[DatePart.DAY]) // 1

        seconds_series = seconds_series.astype('int64')
        return (
            seconds_series
            .copy_override_type(SeriesInt64)
            .copy_override(name='seconds')
        )

    @property
    def microseconds(self) -> SeriesInt64:
        """
        considers only the fractional part of the total seconds and converts it into microseconds
        """
        microseconds_series = (
            (self.total_seconds % 1) / _TOTAL_SECONDS_PER_DATE_PART[DatePart.MICROSECOND]
        )

        microseconds_series = microseconds_series.astype('int64')
        return (
            microseconds_series
            .copy_override_type(SeriesInt64)
            .copy_override(name='microseconds')
        )

    @property
    def total_seconds(self) -> SeriesFloat64:
        """
        returns the total amount of seconds in the interval
        """

        if not is_bigquery(self._series.engine):
            # extract(epoch from source) returns the total number of seconds in the interval
            expression = Expression.construct(f'extract(epoch from {{}})', self._series)
        else:
            # bq cannot extract epoch from interval
            expression = Expression.construct(
                (
                    f"UNIX_MICROS(CAST('1970-01-01' AS TIMESTAMP) + {{}}) "
                    f"* {_TOTAL_SECONDS_PER_DATE_PART[DatePart.MICROSECOND]}"
                ),
                self._series,
            )

        return (
            self._series
            .copy_override_type(SeriesFloat64)
            .copy_override(name='total_seconds', expression=expression)
        )


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
        # Make sure we cast properly, and round similar to python datetime: add 12 hours and cast to date
        if series.dtype == 'date':
            td_12_hours = datetime.timedelta(seconds=3600 * 12)
            series_12_hours = SeriesTimedelta.from_value(base=series, value=td_12_hours, name='tmp')
            expr_12_hours = series_12_hours.expression

            return series.copy_override(
                expression=Expression.construct("cast({} + {} as date)", series, expr_12_hours)
            )
        else:
            return series


def dt_strip_timezone(value: Optional[datetime.datetime]) -> Optional[datetime.datetime]:
    if value is None:
        return None
    return value.replace(tzinfo=None)


class SeriesTimestamp(SeriesAbstractDateTime):
    """
    A Series that represents the timestamp/datetime type and its specific operations.

    Timestamps are assumed to be in UTC, or without a timezone, both cases are treated the same.
    These timestamps have a microsecond precision at best, in contrast to numpy's datetime64 which supports
    up to attoseconds precision.

    **Database support and types**

    * Postgres: utilizes the 'timestamp without time zone' database type.
    * BigQuery: utilizes the 'TIMESTAMP' database type.
    """
    dtype = 'timestamp'
    dtype_aliases = ('datetime64', 'datetime64[ns]', numpy.datetime64)
    supported_db_dtype = {
        DBDialect.POSTGRES: 'timestamp without time zone',
        DBDialect.BIGQUERY: 'TIMESTAMP',
    }
    supported_value_types = (datetime.datetime, numpy.datetime64, datetime.date, str)

    @classmethod
    def supported_literal_to_expression(cls, dialect: Dialect, literal: Expression) -> Expression:
        return Expression.construct(f'cast({{}} as {cls.get_db_dtype(dialect)})', literal)

    @classmethod
    def supported_value_to_literal(
        cls,
        dialect: Dialect,
        value: Union[datetime.datetime, numpy.datetime64, datetime.date, str, None],
        dtype: StructuredDtype
    ) -> Expression:
        if value is None:
            return Expression.raw('NULL')
        # if value is not a datetime or date, then convert it to datetime first
        dt_value: Union[datetime.datetime, datetime.date, None] = None
        if isinstance(value, str):
            formats = ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d']
            for format in formats:
                try:
                    dt_value = datetime.datetime.strptime(value, format)
                    break
                except ValueError:
                    continue
            if dt_value is None:
                raise ValueError(f'Not a valid timestamp string literal: {value}.'
                                 f'Supported formats: {formats}')
        elif isinstance(value, numpy.datetime64):
            if numpy.isnat(value):
                return Expression.raw('NULL')
            # Weird trick: count number of microseconds in datetime, but only works on timedelta, so convert
            # to a timedelta first, by subtracting 0 (epoch = 1970-01-01 00:00:00)
            # Rounding can be unpredictable because of limited precision, so always truncate excess precision
            microseconds = int((value - numpy.datetime64('1970', 'us')) // numpy.timedelta64(1, 'us'))
            dt_value = datetime.datetime.utcfromtimestamp(microseconds / 1_000_000)
        elif isinstance(value, (datetime.datetime, datetime.date)):
            dt_value = value

        if dt_value is None:
            raise ValueError(f'Not a valid timestamp literal: {value}')

        str_value = dt_value.strftime('%Y-%m-%d %H:%M:%S.%f')
        return Expression.string_value(str_value)

    @classmethod
    def dtype_to_expression(cls, dialect: Dialect, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'timestamp':
            return expression
        else:
            if source_dtype not in ['string', 'date']:
                raise ValueError(f'cannot convert {source_dtype} to timestamp')
            return Expression.construct(f'cast({{}} as {cls.get_db_dtype(dialect)})', expression)

    def to_pandas_info(self) -> Optional['ToPandasInfo']:
        if is_postgres(self.engine):
            return ToPandasInfo('datetime64[ns]', None)
        if is_bigquery(self.engine):
            return ToPandasInfo('datetime64[ns, UTC]', dt_strip_timezone)
        return None

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

    **Database support and types**

    * Postgres: utilizes the 'date' database type.
    * BigQuery: utilizes the 'DATE' database type.
    """
    dtype = 'date'
    dtype_aliases: Tuple[DtypeOrAlias, ...] = tuple()
    supported_db_dtype = {
        DBDialect.POSTGRES: 'date',
        DBDialect.BIGQUERY: 'DATE'
    }
    supported_value_types = (datetime.datetime, datetime.date, str)

    @classmethod
    def supported_literal_to_expression(cls, dialect: Dialect, literal: Expression) -> Expression:
        return Expression.construct(f'cast({{}} as date)', literal)

    @classmethod
    def supported_value_to_literal(
        cls,
        dialect: Dialect,
        value: Union[str, datetime.date],
        dtype: StructuredDtype
    ) -> Expression:
        if isinstance(value, datetime.date):
            value = str(value)
        # TODO: check here already that the string has the correct format
        return Expression.string_value(value)

    @classmethod
    def dtype_to_expression(cls, dialect: Dialect, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'date':
            return expression
        else:
            if source_dtype not in ['string', 'timestamp']:
                raise ValueError(f'cannot convert {source_dtype} to date')
            return Expression.construct(f'cast({{}} as {cls.get_db_dtype(dialect)})', expression)

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


    **Database support and types**

    * Postgres: utilizes the 'time without time zone' database type.
    * BigQuery: utilizes the 'TIME' database type.
    """
    dtype = 'time'
    dtype_aliases: Tuple[DtypeOrAlias, ...] = tuple()
    supported_db_dtype = {
        DBDialect.POSTGRES: 'time without time zone',
        DBDialect.BIGQUERY: 'TIME',
    }
    supported_value_types = (datetime.time, str)

    @classmethod
    def supported_literal_to_expression(cls, dialect: Dialect, literal: Expression) -> Expression:
        return Expression.construct(f'cast({{}} as {cls.get_db_dtype(dialect)})', literal)

    @classmethod
    def supported_value_to_literal(
        cls,
        dialect: Dialect,
        value: Union[str, datetime.time],
        dtype: StructuredDtype
    ) -> Expression:
        value = str(value)
        # TODO: check here already that the string has the correct format
        return Expression.string_value(value)

    @classmethod
    def dtype_to_expression(cls, dialect: Dialect, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'time':
            return expression
        else:
            if source_dtype not in ['string', 'timestamp']:
                raise ValueError(f'cannot convert {source_dtype} to time')
            return Expression.construct(f'cast({{}} as {cls.get_db_dtype(dialect)})', expression)

    # python supports no arithmetic on Time


class SeriesTimedelta(SeriesAbstractDateTime):
    """
    A Series that represents the timedelta type and its specific operations

    **Database support and types**

    * Postgres: utilizes the 'interval' database type.
    * BigQuery: support coming soon
    """

    dtype = 'timedelta'
    dtype_aliases = ('interval',)
    supported_db_dtype = {
        DBDialect.POSTGRES: 'interval',
        DBDialect.BIGQUERY: 'INTERVAL',
    }
    supported_value_types = (datetime.timedelta, numpy.timedelta64, str)

    @classmethod
    def supported_literal_to_expression(cls, dialect: Dialect, literal: Expression) -> Expression:
        return Expression.construct(f'cast({{}} as {cls.get_db_dtype(dialect)})', literal)

    @classmethod
    def supported_value_to_literal(
        cls,
        dialect: Dialect,
        value: Union[str, numpy.timedelta64, datetime.timedelta],
        dtype: StructuredDtype
    ) -> Expression:
        # pandas.Timedelta checks already that the string has the correct format
        # round it up to microseconds precision in order to avoid problems with BigQuery
        # pandas by default uses nanoseconds precision
        value_td = pandas.Timedelta(value).round(freq='us')

        if value_td is pandas.NaT:
            return Expression.construct('NULL')

        # interval values in iso format are allowed in SQL (both BQ and PG)
        # https://www.postgresql.org/docs/8.4/datatype-datetime.html#:~:text=interval%20values%20can%20also%20be%20written%20as%20iso%208601%20time%20intervals%2C
        return Expression.string_value(value_td.isoformat())

    def to_pandas_info(self) -> Optional[ToPandasInfo]:
        if is_bigquery(self.engine):
            return ToPandasInfo(dtype='object', function=self._parse_interval_bigquery)
        return None

    def _parse_interval_bigquery(self, value: Optional[Any]) -> Optional[pandas.Timedelta]:
        if value is None:
            return None

        # BigQuery returns a MonthDayNano object
        # we need to normalize months to days (1 month == 30 day period)
        return pandas.Timedelta(
            days=value.days + value.months * 30,
            nanoseconds=value.nanoseconds,
        )

    @classmethod
    def dtype_to_expression(cls, dialect: Dialect, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'timedelta':
            return expression
        else:
            if not source_dtype == 'string':
                raise ValueError(f'cannot convert {source_dtype} to timedelta')
            return Expression.construct(f'cast({{}} as {cls.get_db_dtype(dialect)})', expression)

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

    @property
    def dt(self) -> TimedeltaOperation:
        """
        Get access to date operations.

        .. autoclass:: bach.series.series_datetime.TimedeltaOperation
            :members:

        """
        return TimedeltaOperation(self)

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
        return result.copy_override_type(SeriesTimedelta)

    def mean(self, partition: WrappedPartition = None, skipna: bool = True) -> 'SeriesTimedelta':
        """
        :meta private:
        """
        result = self._derived_agg_func(
            partition=partition,
            expression='avg',
            skipna=skipna
        )
        result = result.copy_override_type(SeriesTimedelta)

        if is_bigquery(self.engine):
            result = result._remove_nano_precision_bigquery()

        return result

    def _remove_nano_precision_bigquery(self) -> 'SeriesTimedelta':
        """
        Helper function that removes nano-precision from intervals.
        """
        series = self.copy()
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types#interval_type
        _BQ_INTERVAL_FORMAT = '%d-%d %d %d:%d:%d.%06.0f'
        _BQ_SUPPORTED_INTERVAL_PARTS = [
            'YEAR', 'MONTH', 'DAY', 'HOUR', 'MINUTE', 'SECOND'
        ]

        # aggregating intervals by average might generate a result with
        # nano-precision, which is not supported by BigQuery TimeStamps
        # therefore we need to make sure we always generate values up to
        # microseconds precision
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types#timestamp_type
        all_extracted_parts_expr = [
            Expression.construct(f'EXTRACT({date_part} FROM {{}})', series)
            for date_part in _BQ_SUPPORTED_INTERVAL_PARTS
        ]
        # convert nanoseconds to microseconds
        all_extracted_parts_expr.append(
            Expression.construct(f'EXTRACT(NANOSECOND FROM {{}}) / 1000', series)
        )
        format_arguments_expr = join_expressions(all_extracted_parts_expr)

        # All parts will create a string with following format
        # '%d-%d %d %d:%d:%d.%06.0f'
        # where the first 6 digits are date parts from YEAR to SECOND
        # Format specifier %06.0f will format fractional part of seconds with maximum width of 6 digits
        # for example:
        # nanoseconds = 1142857, converting them into microseconds is 1142.857
        # when applying string formatting, the value will be rounded into 1143 (.0 precision)
        # and will be left padded by 2 leading zeros: 001143 (0 flag and 6 minimum width)
        # for more information:
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/string_functions#format_string
        format_expr = Expression.construct(
            f'format({{}}, {{}})',
            Expression.string_value(_BQ_INTERVAL_FORMAT),
            format_arguments_expr,
        )
        return series.copy_override(
            expression=self.dtype_to_expression(
                self.engine, source_dtype='string', expression=format_expr,
            )
        )

    def quantile(
        self, partition: WrappedPartition = None, q: Union[float, List[float]] = 0.5,
    ) -> 'SeriesTimedelta':
        """
        When q is a float or len(q) == 1, the resultant series index will remain
        In case multiple quantiles are calculated, the resultant series index will have all calculated
        quantiles as index values.
        """
        from bach.quantile import calculate_quantiles

        if not is_bigquery(self.engine):
            return (
                calculate_quantiles(series=self.copy(), partition=partition, q=q)
                .copy_override_type(SeriesTimedelta)
            )

        result = calculate_quantiles(series=self.dt.total_seconds, partition=partition, q=q)

        # result must be a timedelta
        return self._convert_total_seconds_to_timedelta(result.copy_override_type(SeriesFloat64))

    def mode(self, partition: WrappedPartition = None, skipna: bool = True) -> 'SeriesTimedelta':
        if not is_bigquery(self.engine):
            return super().mode(partition, skipna)

        # APPROX_TOP_COUNT does not support INTERVALS. So, we should calculate the mode based
        # on the total seconds
        total_seconds_mode = self.dt.total_seconds.mode(partition, skipna)
        return self._convert_total_seconds_to_timedelta(total_seconds_mode)

    def _convert_total_seconds_to_timedelta(
        self, total_seconds_series: 'SeriesFloat64',
    ) -> 'SeriesTimedelta':
        """
        helper function for converting series representing total seconds (epoch) to timedelta series.

        returns a SeriesTimedelta
        """

        # convert total seconds into microseconds
        # since TIMESTAMP_SECONDS accepts only integers, therefore
        # microseconds will be lost due to rounding
        total_microseconds_series = (
            total_seconds_series / _TOTAL_SECONDS_PER_DATE_PART[DatePart.MICROSECOND]
        )
        result = total_microseconds_series.copy_override(
            expression=Expression.construct(
                f"TIMESTAMP_MICROS({{}}) - CAST('1970-01-01' AS TIMESTAMP)",
                total_microseconds_series.astype('int64'),
            ),
            name=self.name,
        )
        return result.copy_override_type(SeriesTimedelta)
