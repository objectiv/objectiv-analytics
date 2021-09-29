from typing import Type, Tuple, Any, TypeVar, List, TYPE_CHECKING, cast

"""
Copyright 2021 Objectiv B.V.

Functions for looking up the right classes to handle types and values, and for registering new custom
types.

To prevent cyclic imports, the functions in this file should not be used by pandasql.py before the file
is fully initialized (that is, only use within functions).
"""

if TYPE_CHECKING:
    from buhtuh.pandasql import BuhTuhSeries


def get_series_type_from_dtype(dtype: str) -> Type['BuhTuhSeries']:
    """ Given a dtype, return the correct BuhTuhSeries subclass. """
    return _registry.get_series_type_from_dtype(dtype)


def arg_to_type(value: Any) -> str:
    """
    Give the dtype, as a string of the given value.
    """
    # todo: rename to value_to_dtype()
    return _registry.value_to_dtype(value)


T = TypeVar('T', bound='BuhTuhSeries')


def register_dtype(value_types: List[Type] = None):
    """ Decorator to register a BuhTuhSeries subclass as dtype series"""
    if value_types is None:
        value_types = []

    def wrapper(cls: Type[T]) -> Type[T]:
        dtype = cls.dtype
        # Mypy needs some help here
        assert value_types is not None
        assert isinstance(dtype, str)
        _registry.register_dtype_series(dtype, cls, value_types)
        return cls
    return wrapper


class TypeRegistry:
    def __init__(self):
        # Do the real initialisation in _real_init, which we'll defer until usage so we won't get
        # problems with cyclic imports.
        # mapping of dtype to a subclass of BuhTuhSeries
        self.dtype_series = {}
        # mapping of python types to matching dtype
        # note that some types could be in this dictionary multiple times. For a subtype its super types
        # might also be in the list. We resolve conflicts in arg_to_type by returning the latest matching
        # entry.
        self.value_type_dtype: List[Tuple[Type, str]] = []

    def _real_init(self):
        """
        Load the default dtype and value-type mappings
        """
        if self.dtype_series:
            return
        # Import locally to prevent cyclic imports
        from buhtuh.pandasql import BuhTuhSeriesBoolean, BuhTuhSeriesInt64, \
            BuhTuhSeriesFloat64, BuhTuhSeriesString, BuhTuhSeriesTimestamp, \
            BuhTuhSeriesDate, BuhTuhSeriesTime, BuhTuhSeriesTimedelta
        import datetime
        import numpy

        self.dtype_series = {
            'boolean': BuhTuhSeriesBoolean,
            'bool': BuhTuhSeriesBoolean,
            'integer': BuhTuhSeriesInt64,
            'bigint': BuhTuhSeriesInt64,
            'int64': BuhTuhSeriesInt64,
            'double precision': BuhTuhSeriesFloat64,
            'float64': BuhTuhSeriesFloat64,
            'string': BuhTuhSeriesString,
            'text': BuhTuhSeriesString,
            'json': BuhTuhSeriesString,
            'uuid': BuhTuhSeriesString,

            'timestamp': BuhTuhSeriesTimestamp,
            'timestamp without time zone': BuhTuhSeriesTimestamp,
            'datetime64[ns]': BuhTuhSeriesTimestamp,
            'date': BuhTuhSeriesDate,
            'time without time zone': BuhTuhSeriesTime,
            'time': BuhTuhSeriesTime,

            'interval': BuhTuhSeriesTimedelta,
            'timedelta': BuhTuhSeriesTimedelta
        }
        # note that order can be important here. value_to_dtype starts at end of this list and for example a
        # bool can become and 'int64' if int would be later in this list.
        self.value_type_dtype = [
            (int, 'int64'),
            (numpy.int64, 'int64'),
            (float, 'float64'),
            (bool, 'bool'),
            (str, 'string'),

            (datetime.date, 'date'),
            (datetime.time, 'time'),
            (datetime.datetime, 'timestamp'),

            (datetime.timedelta, 'timedelta'),
            (numpy.timedelta64, 'timedelta')
        ]

    def register_dtype_series(self,
                              dtype: str,
                              series_type: Type['BuhTuhSeries'],
                              value_types: List[Type]):
        """ TODO: comments"""
        self._real_init()
        # todo: use dtypes consistently, so we don't have to lower() it in some places
        dtype = dtype.lower()
        self.dtype_series[dtype] = series_type
        for value_type in value_types:
            self.value_type_dtype.append((value_type, dtype))

    def get_series_type_from_dtype(self, dtype: str) -> Type['BuhTuhSeries']:
        self._real_init()
        # todo: use dtypes consistently, so we don't have to lower() it in some places
        dtype = dtype.lower()
        if dtype not in self.dtype_series:
            raise ValueError(f'Unknown dtype: {dtype}')
        return self.dtype_series[dtype]

    def value_to_dtype(self, value: Any) -> str:
        self._real_init()
        # exception for values that are BuhTuhSeries. Check: do we need this exception?
        from buhtuh.pandasql import BuhTuhSeries
        if isinstance(value, BuhTuhSeries):
            # todo: use dtypes consistently, so we don't have to lower() it in some places
            return value.dtype.lower()
        # iterate in reverse, the last item added that matches is used in case where multiple entries
        # match.
        for type_object, dtype in self.value_type_dtype[::-1]:
            if isinstance(value, type_object):
                return dtype
        raise ValueError(f'No dtype know for {type(value)}')


_registry = TypeRegistry()
