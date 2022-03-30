"""
Copyright 2021 Objectiv B.V.

Functions for looking up the right classes to handle types and values, and for registering new custom
types.

To prevent cyclic imports, the functions in this file should not be used by dataframe.py before the file
is fully initialized (that is, only use within functions).
"""
from collections import defaultdict
from typing import Type, Tuple, Any, TypeVar, List, TYPE_CHECKING, Dict, Union, Sequence
import datetime
from uuid import UUID

import numpy

from sql_models.constants import DBDialect

if TYPE_CHECKING:
    from bach.series import Series


DtypeOrAlias = Union[Type, str]


def get_series_type_from_dtype(dtype: DtypeOrAlias) -> Type['Series']:
    """ Given a dtype, return the correct Series subclass. """
    return _registry.get_series_type_from_dtype(dtype)


def get_series_type_from_db_dtype(db_dialect: DBDialect, db_dtype: str) -> Type['Series']:
    """ Given a database datatype, return the correct Series subclass. """
    return _registry.get_series_type_from_db_dtype(db_dialect, db_dtype)


def get_dtype_from_db_dtype(db_dialect: DBDialect, db_dtype: str) -> str:
    """ Given a database datatype, return the dtype of the Series subclass for that datatype. """
    return get_series_type_from_db_dtype(db_dialect, db_dtype).dtype


def value_to_dtype(value: Any) -> str:
    """
    Give the dtype, as a string of the given value.
    """
    return _registry.value_to_dtype(value)


T = TypeVar('T', bound='Series')


def register_dtype(value_types: List[Type] = None, override_registered_types: bool = False):
    """
    Decorator to register a Series subclass as dtype series
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

        # dtype_series: Mapping of dtype to a subclass of Series
        self.dtype_to_series: Dict[DtypeOrAlias, Type['Series']] = {}

        # db_type_to_dtype: Mapping per database dialect, of database types to a subclass of Series
        self.db_dtype_to_series: Dict[DBDialect, Dict[str, Type['Series']]] = defaultdict(dict)

        # value_type_to_series: Mapping of python types to matching Series types
        # note that some types could be in this dictionary multiple times. For a subtype its super types
        # might also be in the list. We resolve conflicts in arg_to_type by returning the latest matching
        # entry.
        # This is also the reason this is a list of typles instead of a dictionary: the order is important
        # and that is clearer with a list.
        self.value_type_to_series: List[Tuple[Type, Type['Series']]] = []

    def _real_init(self):
        """
        Load the default dtype, db_dtype, and value-type mappings for the standard set of Series types.

        The dtype_to_series mapping will be based on the dtype and dtype_aliases that the standard
            Series declare.
        The db_dtype_to_series mapping will be similarly based on the supported_db_dtype that the standard
            Series declare.
        The value_type_to_series is hardcoded here for the standard Series.
        """
        if self.dtype_to_series or self.db_dtype_to_series or self.value_type_to_series:
            # Only initialise once
            return

        # Import locally to prevent cyclic imports
        from bach.series import \
            SeriesBoolean, SeriesInt64, SeriesFloat64, SeriesString,\
            SeriesTimestamp, SeriesDate, SeriesTime, SeriesTimedelta,\
            SeriesUuid, SeriesJsonb, SeriesJson

        standard_types: List[Type[Series]] = [
            SeriesBoolean, SeriesInt64, SeriesFloat64, SeriesString,
            SeriesTimestamp, SeriesDate, SeriesTime, SeriesTimedelta,
            SeriesUuid, SeriesJsonb, SeriesJson
        ]

        for klass in standard_types:
            self._register_dtype_klass(klass)
            self._register_db_dtype_klass(klass)

        # For the value_type_to_dtype list order can be important. The value_to_dtype() function starts at
        # end of this list and the first matching entry determines the return value.
        # A type might match multiple entries in the list, because it can be an instance of multiple (super)
        # classes. E.g. a `bool` is also an `int`
        # Therefore this list is hardcoded here, and not automatically derived from the base_types classes
        self._register_value_klass(int, SeriesInt64)
        self._register_value_klass(numpy.int64, SeriesInt64)
        self._register_value_klass(float, SeriesFloat64)
        self._register_value_klass(numpy.float64, SeriesFloat64)
        self._register_value_klass(bool, SeriesBoolean)
        self._register_value_klass(type(None), SeriesString)  # NoneType ends up as a string for now
        self._register_value_klass(str, SeriesString)
        self._register_value_klass(datetime.date, SeriesDate)
        self._register_value_klass(datetime.time, SeriesTime)
        self._register_value_klass(datetime.datetime, SeriesTimestamp)
        self._register_value_klass(datetime.timedelta, SeriesTimedelta)
        self._register_value_klass(numpy.timedelta64, SeriesTimedelta)
        self._register_value_klass(UUID, SeriesUuid)
        self._register_value_klass(dict, SeriesJsonb)
        self._register_value_klass(list, SeriesJsonb)

    def _register_dtype_klass(self, klass: Type['Series'], override=False):
        klass_dtype: DtypeOrAlias = klass.dtype
        dtype_and_aliases: Sequence[DtypeOrAlias] = [klass_dtype] + list(klass.dtype_aliases)
        for dtype_alias in dtype_and_aliases:
            if dtype_alias in self.dtype_to_series and not override:
                raise Exception(f'Type {klass} claims dtype (or dtype alias) {dtype_alias}, which is '
                                f'already assigned to {self.dtype_to_series[dtype_alias]}')
            self.dtype_to_series[dtype_alias] = klass

    def _register_db_dtype_klass(self, klass: Type['Series'], override=False):
        for db_dialect, db_dtype in klass.supported_db_dtype.items():
            if db_dtype in self.db_dtype_to_series[db_dialect] and not override:
                raise Exception(f'Type {klass} claims db_dtype {db_dtype} for {db_dialect.value}, which is '
                                f'already assigned to dtype {self.db_dtype_to_series[db_dialect][db_dtype]}')
            self.db_dtype_to_series[db_dialect][db_dtype] = klass

    def _register_value_klass(self, value_type: Type, klass: Type['Series'], override=False):
        for vt, kt in self.value_type_to_series:
            if vt == value_type and kt != klass and not override:
                raise Exception(f'Cannot register {value_type} twice, already coupled to {klass}')
        if value_type not in klass.supported_value_types:
            raise ValueError(f'Cannot register {klass} for {value_type}. Type not supported.')
        type_tuple = value_type, klass
        self.value_type_to_series.append(type_tuple)

    def register_dtype_series(self,
                              series_type: Type['Series'],
                              value_types: List[Type],
                              override_registered_types: bool = False):
        """
        Add a Series sub-class to this registry.
        Will register the given series_type as the default type for its dtype and db_dtype
        """
        self._real_init()
        self._register_dtype_klass(series_type, override_registered_types)
        self._register_db_dtype_klass(series_type, override_registered_types)
        for value_type in value_types:
            self._register_value_klass(value_type, series_type, override_registered_types)

    def get_series_type_from_dtype(self, dtype: DtypeOrAlias) -> Type['Series']:
        """
        Given a dtype string or a dtype alias, will return the correct Series object to represent such data.
        """
        self._real_init()
        if dtype not in self.dtype_to_series:
            raise ValueError(f'Unknown dtype: {dtype}')
        return self.dtype_to_series[dtype]

    def get_series_type_from_db_dtype(self, db_dialect: DBDialect, db_dtype: str) -> Type['Series']:
        """
        Given a db_dtype string, will return the correct Series object to represent such data from the
        database.
        """
        self._real_init()
        if db_dtype not in self.db_dtype_to_series[db_dialect]:
            raise ValueError(f'Unknown db_dtype: {db_dtype}')
        return self.db_dtype_to_series[db_dialect][db_dtype]

    def value_to_dtype(self, value: Any) -> str:
        """
        Given a python value, return the dtype string of the Series that's registered as the default
        for the type of value.
        """
        self._real_init()
        # exception for values that are Series. Check: do we need this exception?
        from bach.series import Series
        if isinstance(value, Series):
            return value.dtype
        # iterate in reverse, the last item added that matches is used in case where multiple entries
        # match.
        for type_object, series_type in self.value_type_to_series[::-1]:
            if isinstance(value, type_object):
                return series_type.dtype
        raise ValueError(f'No dtype known for {type(value)}')


_registry = TypeRegistry()
