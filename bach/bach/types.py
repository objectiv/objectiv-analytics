"""
Copyright 2021 Objectiv B.V.

Functions for looking up the right classes to handle types and values, and for registering new custom
types.

To prevent cyclic imports, the functions in this file should not be used by dataframe.py before the file
is fully initialized (that is, only use within functions).
"""
from copy import copy
from typing import Type, Tuple, Any, TypeVar, List, TYPE_CHECKING, Dict, Union, Sequence, Mapping, Set
import datetime
from uuid import UUID

import numpy
import pandas

from sql_models.constants import DBDialect

if TYPE_CHECKING:
    from bach.series import Series


AllSupportedLiteralTypes = Union[
    int, numpy.int64,
    float, numpy.float64,
    bool,
    None,
    str,
    datetime.date, datetime.time, datetime.datetime, numpy.datetime64, datetime.timedelta, numpy.timedelta64,
    UUID,
    pandas.Interval,
    dict,
    list
]
"""
AllSupportedLiteralTypes are all the types for which a Series is registered to interpret the literal.
Of course when custom types are added, this definition will be incomplete, but as this is just for mypy
usage, that is fine.
"""


Dtype = str
StructuredDtype = Union[List[Any], Mapping[str, Any], Dtype]
# Real definition of StructuredDtype, but not supported by mypy:
# StructuredDtype = Union[List[StructuredDtype], Dict[str, StructuredDtype], str]
DtypeOrAlias = Union[Type, StructuredDtype]


def get_series_type_from_dtype(dtype: DtypeOrAlias) -> Type['Series']:
    """ Given a dtype, return the correct Series subclass. """
    return _registry.get_series_type_from_dtype(dtype)


def get_dtype_from_db_dtype(db_dialect: DBDialect, db_dtype: str) -> StructuredDtype:
    """ Given a database datatype, return the dtype of the Series subclass for that datatype. """
    return _registry.get_dtype_from_db_dtype(db_dialect=db_dialect, db_dtype=db_dtype)


def value_to_dtype(value: Any) -> Dtype:
    """ Give the dtype, as a string of the given value. """
    return _registry.value_to_dtype(value)


def get_series_type_from_db_dtype(db_dialect: DBDialect, db_dtype: str) -> Type['Series']:
    """ Given a database datatype, return the correct Series subclass. """
    dtype = get_dtype_from_db_dtype(db_dialect=db_dialect, db_dtype=db_dtype)
    return get_series_type_from_dtype(dtype)


def value_to_series_type(value: Any) -> Type['Series']:
    """ Return the Series subclass that can represent value as literal. """
    return get_series_type_from_dtype(dtype=value_to_dtype(value))


def get_all_db_dtype_to_series() -> Mapping[DBDialect, Mapping[Dtype, Type['Series']]]:
    """ Get all registered mappings from db_dtype to Series type"""
    return _registry.get_all_db_dtype_to_series()


def validate_is_dtype(dtype: StructuredDtype):
    """
    Validate that the given dtype is a valid dtype. Raises a ValueError otherwise.
    Note that here we don't consider dtype-aliasses to be valid.
    """
    return _registry.validate_is_dtype(dtype)


def validate_instance_dtype(static_dtype: Dtype, instance_dtype: StructuredDtype):
    """
    Validate that:
    1) instance_dtype is a valid instance dtype for the given static_dtype.
    2) instance_dtype is well-formed.

    Example: `['int64', 'float64']` is not a well formed instance-dtype. a list should have only one item.
    Example: `['int64']` is not well formed instance-dtype, and a correct instance_dtype
                if static_dtype='list', but not when static_dtype='bool'

    :raises ValueError: if any check fails
    """
    # hardcoded for now, make more elegant in the future when we have a lot of DBs to support
    structural_type_mapping: Dict[Dtype, Type] = {
        'list': list,
        'dict': dict
    }
    expected_type = structural_type_mapping.get(static_dtype)
    if expected_type is not None:
        if not isinstance(instance_dtype, expected_type):
            raise ValueError(f'Expected instance dtype of type "{expected_type}". '
                             f'instance_dtype type: {type(instance_dtype)}, '
                             f'instance_dtype: {instance_dtype}')
    else:
        if static_dtype != instance_dtype:
            raise ValueError(f'Expected instance dtype "{static_dtype}". '
                             f'instance_dtype: "{instance_dtype}"')

    return validate_is_dtype(instance_dtype)


def validate_dtype_value(
    static_dtype: Dtype,
    instance_dtype: StructuredDtype,
    value: Union['Series', AllSupportedLiteralTypes]
):
    """
    Check that static_dtype is a valid instance dtype for the given static_dtype, and that value is of the
    given instance-dtype.

    :param static_dtype: static dtype against which to validate the instance_dtype
    :param instance_dtype: instance dtype against which to validate value.
    :param value: Value to validate. Can either be a python value or a Series.
    :raises ValueError: if any checks fail
    """
    validate_instance_dtype(static_dtype=static_dtype, instance_dtype=instance_dtype)
    _validate_dtype_of_value(dtype=instance_dtype, value=value)


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

        # dtype_series: Mapping of dtype and dtype-alias to a subclass of Series
        self.dtype_to_series: Dict[DtypeOrAlias, Type['Series']] = {}

        # db_dtype_to_series: Mapping per database dialect, of database types to a subclass of Series
        self.db_dtype_to_series: Dict[DBDialect, Dict[Dtype, Type['Series']]] = {}

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
            SeriesUuid, SeriesJson, SeriesJsonPostgres, SeriesNumericInterval, SeriesList, SeriesDict

        standard_types: List[Type[Series]] = [
            SeriesBoolean, SeriesInt64, SeriesFloat64, SeriesString,
            SeriesTimestamp, SeriesDate, SeriesTime, SeriesTimedelta,
            SeriesUuid, SeriesJson, SeriesJsonPostgres, SeriesNumericInterval, SeriesList, SeriesDict
        ]

        for klass in standard_types:
            self._register_dtype_klass(klass)
            self._register_db_dtype_klass(klass)

        # For the value_type_to_dtype list order can be important. The value_to_dtype() function starts at
        # end of this list and the first matching entry determines the return value.
        # A type might match multiple entries in the list, because it can be an instance of multiple (super)
        # classes. E.g. a `bool` is also an `int`
        # Therefore this list is hardcoded here, and not automatically derived from the base_types classes
        # When adding an item here, make sure to update AllSupportedLiteralTypes above
        self._register_value_klass(int, SeriesInt64)
        self._register_value_klass(numpy.int64, SeriesInt64)
        self._register_value_klass(float, SeriesFloat64)
        self._register_value_klass(numpy.float64, SeriesFloat64)
        self._register_value_klass(bool, SeriesBoolean)
        self._register_value_klass(type(None), SeriesString)  # NoneType ends up as a string for now
        self._register_value_klass(str, SeriesString)
        self._register_value_klass(pandas.Interval, SeriesNumericInterval)

        self._register_value_klass(datetime.date, SeriesDate)
        self._register_value_klass(datetime.time, SeriesTime)
        self._register_value_klass(datetime.datetime, SeriesTimestamp)
        self._register_value_klass(numpy.datetime64, SeriesTimestamp)
        self._register_value_klass(datetime.timedelta, SeriesTimedelta)
        self._register_value_klass(numpy.timedelta64, SeriesTimedelta)
        self._register_value_klass(UUID, SeriesUuid)
        self._register_value_klass(dict, SeriesJson)
        self._register_value_klass(list, SeriesJson)

    def _register_dtype_klass(self, klass: Type['Series'], override=False):
        klass_dtype: DtypeOrAlias = klass.dtype
        dtype_and_aliases: Sequence[DtypeOrAlias] = [klass_dtype] + list(klass.dtype_aliases)
        for dtype_alias in dtype_and_aliases:
            if dtype_alias in self.dtype_to_series and not override:
                raise Exception(f'Type {klass} claims dtype (or dtype alias) {dtype_alias}, which is '
                                f'already assigned to {self.dtype_to_series[dtype_alias]}')
            self.dtype_to_series[dtype_alias] = klass

    def _register_db_dtype_klass(self, klass: Type['Series'], override=False):
        for db_dialect in klass.supported_db_dtype.keys():
            if db_dialect not in self.db_dtype_to_series:
                self.db_dtype_to_series[db_dialect] = {}
        for db_dialect, db_dtype in klass.supported_db_dtype.items():
            if db_dtype is None:
                continue
            if db_dtype in self.db_dtype_to_series.get(db_dialect, {}) and not override:
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
        # lists and dicts are hardcoded exceptions for now.
        # TODO: make this nicer, e.g. make sure that no class can register this as an alias
        #  maybe switch to all strings, e.g. `'list[int64]'` instead of `list['int64']` ?
        if isinstance(dtype, list):
            dtype = 'list'
        elif isinstance(dtype, dict):
            dtype = 'dict'

        if dtype not in self.dtype_to_series:
            raise ValueError(f'Unknown dtype: {dtype}')
        return self.dtype_to_series[dtype]

    def get_dtype_from_db_dtype(self, db_dialect: DBDialect, db_dtype: str) -> StructuredDtype:
        """
        Given a db_dtype string, will return the full StructuredDtype.

        :return: dtype can be a simple dtype such as 'int64', or a structured dtype, such
                as {'a': 'int64', 'b': 'float64'}
        """
        self._real_init()
        if db_dtype in self.db_dtype_to_series[db_dialect]:
            return self.db_dtype_to_series[db_dialect][db_dtype].dtype
        if db_dialect == DBDialect.BIGQUERY:
            # TODO: make this nicer. clean up when we support more than two databases
            from bach.types_bq import bq_db_dtype_to_dtype
            return bq_db_dtype_to_dtype(db_dtype=db_dtype)
        raise ValueError(f'Unknown db_dtype: {db_dtype}')

    def get_all_db_dtype_to_series(self) -> Mapping[DBDialect, Mapping[Dtype, Type['Series']]]:
        """ Get all registered mappings from db_dtype to Series type"""
        self._real_init()
        return {db_dialect: copy(mapping) for db_dialect, mapping in self.db_dtype_to_series.items()}

    def value_to_dtype(self, value: Any) -> Dtype:
        """
        Given a python value, return the dtype string of the Series that's registered as the default
        for the type of value.
        For non-scalar types this will give the base Dtype, not the StructuredDtype. E.g. for an list of
            integers this will return 'list' and not ['int64']
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

    def validate_is_dtype(self, dtype: StructuredDtype):
        """
        Validate that dtype is a valid dtype, either as a regular dtype string that is one of the registered
        dtypes, or a structured dtype that is well-formed.
        :raises ValueError: if dtype is not a valid Dtype
        """
        self._real_init()
        base_dtypes = set(series.dtype for series in self.dtype_to_series.values())
        _assert_is_valid_dtype(base_dtypes=base_dtypes, dtype=dtype)


_registry = TypeRegistry()


def _validate_dtype_of_value(dtype: StructuredDtype, value: Union['Series', AllSupportedLiteralTypes]):
    """
    Recursively validate that value has the given dtype.
    Assumes dtype is a well-formed dtype.
    """
    from bach.series import Series

    if isinstance(value, Series):
        # If value is already a series with a dtype, it should match dtype exactly.
        if dtype != value.dtype:
            raise ValueError(f'Dtype does not match dtype of series. '
                             f'Dtype: {dtype}, series.dtype: {value.dtype}')

    elif isinstance(dtype, Dtype):
        series = get_series_type_from_dtype(dtype)
        if type(value) not in series.supported_value_types:
            raise ValueError(f'Dtype does not match value. '
                             f'Dtype: {dtype}, '
                             f'supported value types: {series.supported_value_types}, '
                             f'value: {value}')
    elif isinstance(dtype, list):
        if not isinstance(value, list):
            raise ValueError(f'Dtype is a list, value is not a list. Value: {value}')
        sub_dtype = dtype[0]
        for sub_value in value:
            _validate_dtype_of_value(sub_dtype, sub_value)

    elif isinstance(dtype, dict):
        if not isinstance(value, dict):
            raise ValueError(f'Dtype is a dict, value is not a dict. Value: {value}')
        dtype_keys = set(dtype.keys())
        value_keys = set(value.keys())
        if dtype_keys != value_keys:
            raise ValueError(f'Dtype keys do not match value keys. '
                             f'Dtype keys: {dtype_keys}, value keys: {value_keys}')
        for key, sub_dtype in dtype.items():
            sub_value = value[key]
            _validate_dtype_of_value(sub_dtype, sub_value)
    else:
        raise ValueError(f'Dtype not supported. Dtype: {dtype}')


def _assert_is_valid_dtype(base_dtypes: Set[Dtype], dtype: StructuredDtype):
    """
    Validate that dtype is a valid dtype, either a regular dtype or a recursively defined structural dtype.
    :raise ValueError: if dtype is not a valid Dtype
    """
    if isinstance(dtype, Dtype):
        if dtype not in base_dtypes:
            raise ValueError(f'Unknown dtype string: {dtype}')
    elif isinstance(dtype, list):
        if len(dtype) != 1:
            raise ValueError(f'Expected list of length one, got: {dtype}')
        sub_dtype = dtype[0]
        _assert_is_valid_dtype(base_dtypes=base_dtypes, dtype=sub_dtype)
    elif isinstance(dtype, dict):
        non_string_keys = sorted(key for key in dtype.keys() if not isinstance(key, str))
        if non_string_keys:
            raise ValueError(f'Expected all keys to be strings. '
                             f'Found non string keys: {non_string_keys}')
        for sub_dtype in dtype.values():
            _assert_is_valid_dtype(base_dtypes=base_dtypes, dtype=sub_dtype)
    else:
        raise ValueError(f'Unknown dtype: {dtype}')
