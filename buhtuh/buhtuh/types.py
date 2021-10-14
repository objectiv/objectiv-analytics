from typing import Type, Tuple, Any, TypeVar, List, TYPE_CHECKING, Dict, Hashable, cast, Union
import datetime
from uuid import UUID

import numpy

"""
Copyright 2021 Objectiv B.V.

Functions for looking up the right classes to handle types and values, and for registering new custom
types.

To prevent cyclic imports, the functions in this file should not be used by pandasql.py before the file
is fully initialized (that is, only use within functions).
"""

if TYPE_CHECKING:
    from buhtuh.pandasql import BuhTuhSeries


def get_series_type_from_dtype(dtype: Union[Type, str]) -> Type['BuhTuhSeries']:
    """ Given a dtype, return the correct BuhTuhSeries subclass. """
    return _registry.get_series_type_from_dtype(dtype)


def get_series_type_from_db_dtype(db_dtype: str) -> Type['BuhTuhSeries']:
    """ Given a database datatype, return the correct BuhTuhSeries subclass. """
    return _registry.get_series_type_from_db_dtype(db_dtype)


def get_dtype_from_db_dtype(db_dtype: str) -> str:
    """ Given a database datatype, return the dtype of the BuhTuhSeries subclass for that datatype. """
    return get_series_type_from_db_dtype(db_dtype).dtype  # type: ignore


def value_to_dtype(value: Any) -> str:
    """
    Give the dtype, as a string of the given value.
    """
    return _registry.value_to_dtype(value)


T = TypeVar('T', bound='BuhTuhSeries')


def register_dtype(value_types: List[Type] = None, override_registered_types: bool = False):
    """
    Decorator to register a BuhTuhSeries subclass as dtype series
    :value_types: List of Types for which values should be instantiated as the registered class
    :override_registerd_types: If False an Exception is raised if the class' dtype or db_dtype conflict
        with existing registerd types or if one of the value_types are already coupled. If True this new
        registration will override the existing one.
    """
    if value_types is None:
        value_types = []

    def wrapper(cls: Type[T]) -> Type[T]:
        # Mypy needs some help here
        assert value_types is not None
        _registry.register_dtype_series(cls, value_types, override_registered_types)
        return cls
    return wrapper


class TypeRegistry:
    def __init__(self):
        # Do the real initialisation in _real_init, which we'll defer until usage so we won't get
        # problems with cyclic imports.

        # dtype_series: Mapping of dtype to a subclass of BuhTuhSeries
        self.dtype_to_series: Dict[Union[Type, str], Type['BuhTuhSeries']] = {}

        # db_type_to_dtype: Mapping of Postgres types to a subclass of BuhTuhSeries
        self.db_dtype_to_series: Dict[str, Type['BuhTuhSeries']] = {}

        # value_type_to_series: Mapping of python types to matching BuhTuhSeries types
        # note that some types could be in this dictionary multiple times. For a subtype its super types
        # might also be in the list. We resolve conflicts in arg_to_type by returning the latest matching
        # entry.
        # This is also the reason this is a list of typles instead of a dictionary: the order is important
        # and that is clearer with a list.
        self.value_type_to_series: List[Tuple[Type, Type['BuhTuhSeries']]] = []

    def _real_init(self):
        """
        Load the default dtype, db_dtype, and value-type mappings for the standard set of BuhTuhSeries types.

        The dtype_to_series mapping will be based on the dtype and dtype_aliases that the standard
            BuhTuhSeries declare.
        The db_dtype_to_series mapping will be similarly based on the supported_db_dtype that the standard
            BuhTuhSeries declare.
        The value_type_to_series is hardcoded here for the standard BuhTuhSeries.
        """
        if self.dtype_to_series or self.db_dtype_to_series or self.value_type_to_series:
            # Only initialise once
            return

        # Import locally to prevent cyclic imports
        from buhtuh.pandasql import BuhTuhSeriesBoolean, BuhTuhSeriesInt64, \
            BuhTuhSeriesFloat64, BuhTuhSeriesString, BuhTuhSeriesTimestamp, \
            BuhTuhSeriesDate, BuhTuhSeriesTime, BuhTuhSeriesTimedelta, BuhTuhSeriesUuid, BuhTuhSeriesJson
        standard_types: List[Type[BuhTuhSeries]] = [
            BuhTuhSeriesBoolean, BuhTuhSeriesInt64, BuhTuhSeriesFloat64, BuhTuhSeriesString,
            BuhTuhSeriesTimestamp, BuhTuhSeriesDate, BuhTuhSeriesTime, BuhTuhSeriesTimedelta,
            BuhTuhSeriesUuid, BuhTuhSeriesJson
        ]

        for klass in standard_types:
            self._register_dtype_klass(klass)
            self._register_db_dtype_klass(klass)

        # For the value_type_to_dtype list order can be important. The value_to_dtype() function starts at
        # end of this list and the first matching entry determines the return value.
        # A type might match multiple entries in the list, because it can be an instance of multiple (super)
        # classes. E.g. a `bool` is also an `int`
        # Therefore this list is hardcoded here, and not automatically derived from the base_types classes
        self._register_value_klass(int,                BuhTuhSeriesInt64)
        self._register_value_klass(numpy.int64,        BuhTuhSeriesInt64)
        self._register_value_klass(float,              BuhTuhSeriesFloat64)
        self._register_value_klass(numpy.float64,      BuhTuhSeriesFloat64)
        self._register_value_klass(bool,               BuhTuhSeriesBoolean)
        self._register_value_klass(str,                BuhTuhSeriesString)
        self._register_value_klass(datetime.date,      BuhTuhSeriesDate)
        self._register_value_klass(datetime.time,      BuhTuhSeriesTime)
        self._register_value_klass(datetime.datetime,  BuhTuhSeriesTimestamp)
        self._register_value_klass(datetime.timedelta, BuhTuhSeriesTimedelta)
        self._register_value_klass(numpy.timedelta64,  BuhTuhSeriesTimedelta)
        self._register_value_klass(UUID,               BuhTuhSeriesUuid)
        self._register_value_klass(dict,               BuhTuhSeriesJson)
        self._register_value_klass(list,               BuhTuhSeriesJson)

    def _register_dtype_klass(self, klass: Type['BuhTuhSeries'], override=False):
        dtype_and_aliases: List[Union[Type, str]] = [klass.dtype] + list(klass.dtype_aliases)  # type: ignore
        for dtype_alias in dtype_and_aliases:
            if dtype_alias in self.dtype_to_series and not override:
                raise Exception(f'Type {klass} claims dtype (or dtype alias) {dtype_alias}, which is '
                                f'already assigned to {self.dtype_to_series[dtype_alias]}')
            self.dtype_to_series[dtype_alias] = klass

    def _register_db_dtype_klass(self, klass: Type['BuhTuhSeries'], override=False):
        if klass.supported_db_dtype is None:
            return
        db_dtype = cast(str, klass.supported_db_dtype)
        if db_dtype in self.db_dtype_to_series and not override:
            raise Exception(f'Type {klass} claims db_dtype {db_dtype}, which is '
                            f'already assigned to dtype {self.db_dtype_to_series[db_dtype]}')
        self.db_dtype_to_series[db_dtype] = klass

    def _register_value_klass(self, value_type: Type, klass: Type['BuhTuhSeries'], override=False):
        for vt, kt in self.value_type_to_series:
            if vt == value_type and kt != klass and not override:
                raise Exception(f'Cannot register {value_type} twice, already coupled to {klass}')
        if value_type not in klass.supported_value_types:  # type: ignore
            raise ValueError(f'Cannot register {klass} for {value_type}. Type not supported.')
        type_tuple = value_type, klass
        self.value_type_to_series.append(type_tuple)

    def register_dtype_series(self,
                              series_type: Type['BuhTuhSeries'],
                              value_types: List[Type],
                              override_registered_types: bool = False):
        """
        Add a BuhTuhSeries sub-class to this registry.
        Will register the given series_type as the default type for its dtype and db_dtype
        """
        self._real_init()
        self._register_dtype_klass(series_type, override_registered_types)
        self._register_db_dtype_klass(series_type, override_registered_types)
        for value_type in value_types:
            self._register_value_klass(value_type, series_type, override_registered_types)

    def get_series_type_from_dtype(self, dtype: Union[Type, str]) -> Type['BuhTuhSeries']:
        """
        Given a dtype string, will return the correct BuhTuhSeries object to represent such data.
        """
        self._real_init()
        if dtype not in self.dtype_to_series:
            raise ValueError(f'Unknown dtype: {dtype}')
        return self.dtype_to_series[dtype]

    def get_series_type_from_db_dtype(self, db_dtype: str) -> Type['BuhTuhSeries']:
        """
        Given a db_dtype string, will return the correct BuhTuhSeries object to represent such data from the
        database..
        """
        self._real_init()
        if db_dtype not in self.db_dtype_to_series:
            raise ValueError(f'Unknown db_dtype: {db_dtype}')
        return self.db_dtype_to_series[db_dtype]

    def value_to_dtype(self, value: Any) -> str:
        """
        Given a python value, return the dtype string of the BuhTuhSeries that's registered as the default
        for the type of value.
        """
        self._real_init()
        # exception for values that are BuhTuhSeries. Check: do we need this exception?
        from buhtuh.pandasql import BuhTuhSeries
        if isinstance(value, BuhTuhSeries):
            return value.dtype
        # iterate in reverse, the last item added that matches is used in case where multiple entries
        # match.
        for type_object, series_type in self.value_type_to_series[::-1]:
            if isinstance(value, type_object):
                return series_type.dtype  # type: ignore
        raise ValueError(f'No dtype know for {type(value)}')


_registry = TypeRegistry()
