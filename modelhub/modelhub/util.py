import inspect
import itertools
from enum import Enum
from functools import wraps
from typing import List, Union, Optional, TYPE_CHECKING, Protocol

import bach
from sql_models.constants import not_set

from modelhub.stack.util import ObjectivSupportedColumns

if TYPE_CHECKING:
    from modelhub import Map, Aggregate


class SupportedAggregationFunctions(str, Enum):
    # Map
    IS_FIRST_SESSION = 'is_first_session'
    IS_NEW_USER = 'is_new_user'
    IS_CONVERSION_EVENT = 'is_conversion_event'
    CONVERSIONS_COUNTER = 'conversions_counter'
    CONVERSIONS_IN_TIME = 'conversions_in_time'
    PRE_CONVERSION_HIT_NUMBER = 'pre_conversion_hit_number'

    # Aggregate
    UNIQUE_USERS = 'unique_users'
    UNIQUE_SESSIONS = 'unique_sessions'
    SESSION_DURATION = 'session_duration'
    FREQUENCY = 'frequency'
    TOP_PRODUCT_FEATURES = 'top_product_features'
    TOP_PRODUCT_FEATURES_BEFORE_CONVERSION = 'top_product_features_before_conversion'

    def get_func_dependencies(self) -> List['SupportedAggregationFunctions']:
        if self == SupportedAggregationFunctions.CONVERSIONS_COUNTER:
            return [
                SupportedAggregationFunctions.CONVERSIONS_IN_TIME,
            ]

        if self == SupportedAggregationFunctions.CONVERSIONS_IN_TIME:
            return [SupportedAggregationFunctions.IS_CONVERSION_EVENT]

        if self == SupportedAggregationFunctions.TOP_PRODUCT_FEATURES_BEFORE_CONVERSION:
            return [
                SupportedAggregationFunctions.CONVERSIONS_COUNTER,
                SupportedAggregationFunctions.CONVERSIONS_IN_TIME,
            ]

        if self == SupportedAggregationFunctions.PRE_CONVERSION_HIT_NUMBER:
            return [
                SupportedAggregationFunctions.CONVERSIONS_IN_TIME,
            ]

        return []


_REQUIRED_OBJECTIV_SERIES_PER_AGG_FUNC = {
    SupportedAggregationFunctions.IS_FIRST_SESSION: [
        ObjectivSupportedColumns.USER_ID, ObjectivSupportedColumns.SESSION_ID,
    ],
    SupportedAggregationFunctions.IS_NEW_USER: [
        ObjectivSupportedColumns.SESSION_ID,
        ObjectivSupportedColumns.USER_ID,
        ObjectivSupportedColumns.MOMENT,
    ],
    SupportedAggregationFunctions.IS_CONVERSION_EVENT: [ObjectivSupportedColumns.EVENT_TYPE],
    SupportedAggregationFunctions.CONVERSIONS_COUNTER: [ObjectivSupportedColumns.SESSION_ID],
    SupportedAggregationFunctions.CONVERSIONS_IN_TIME: [
        ObjectivSupportedColumns.SESSION_ID, ObjectivSupportedColumns.MOMENT,
    ],
    SupportedAggregationFunctions.PRE_CONVERSION_HIT_NUMBER: [
      ObjectivSupportedColumns.SESSION_ID, ObjectivSupportedColumns.SESSION_HIT_NUMBER,
    ],

    SupportedAggregationFunctions.UNIQUE_USERS: [
        ObjectivSupportedColumns.USER_ID, ObjectivSupportedColumns.MOMENT,
    ],
    SupportedAggregationFunctions.UNIQUE_SESSIONS: [
        ObjectivSupportedColumns.SESSION_ID, ObjectivSupportedColumns.MOMENT,
    ],
    SupportedAggregationFunctions.SESSION_DURATION: [
        ObjectivSupportedColumns.SESSION_ID, ObjectivSupportedColumns.MOMENT,
    ],
    SupportedAggregationFunctions.FREQUENCY: [
        ObjectivSupportedColumns.USER_ID, ObjectivSupportedColumns.SESSION_ID,
    ],
    SupportedAggregationFunctions.TOP_PRODUCT_FEATURES: [
        ObjectivSupportedColumns.GLOBAL_CONTEXTS,
        ObjectivSupportedColumns.LOCATION_STACK,
        ObjectivSupportedColumns.USER_ID,
        ObjectivSupportedColumns.STACK_EVENT_TYPES,
        ObjectivSupportedColumns.EVENT_TYPE,
    ],
    SupportedAggregationFunctions.TOP_PRODUCT_FEATURES_BEFORE_CONVERSION: [
        ObjectivSupportedColumns.GLOBAL_CONTEXTS,
        ObjectivSupportedColumns.LOCATION_STACK,
        ObjectivSupportedColumns.USER_ID,
        ObjectivSupportedColumns.STACK_EVENT_TYPES,
    ],
}


class CalculatedFuncType(Protocol):
    @property
    def __name__(self) -> str:
        ...

    def __call__(
        self, _self: Union['Map', 'Aggregate'], data: bach.DataFrame, *args, **kwargs
    ) -> bach.Series:
        ...


def use_only_required_objectiv_series(include_series_from_params: Optional[List[str]] = None):
    """
    Internal: Decorator for validating and limiting the series used on a function dedicated
    to generate new aggregated series based on supported objectiv columns.

    :param include_series_from_params: A list of parameters containing series names to be considered
    in the dataframe.

    The main purposes of the decorator are to:
        * Validate that the dataframe passed to the function contains all required series for the
        calculation,
        * Optimize the base node of the returned series, as materialization is always applied after
        aggregations. If the passed dataframe includes unused series containing complex expressions,
        such expressions will remain on the final base node's history, meaning that the final query
        might contain extra information that is not related to the expected result. Currently, bach
        does not perform any optimization over this scenario, therefore ModelHub must be in charge
        of ensuring the final query contains only the columns needed for all calculations.
    """
    def check_objectiv_data_decorator(func: CalculatedFuncType):
        @wraps(func)
        def wrapped_function(
            _self: Union['Map', 'Aggregate'],
            data: bach.DataFrame,
            *args,
            **kwargs,
        ) -> bach.Series:
            from modelhub.stack.util import check_objectiv_dataframe
            columns_to_check = _get_required_objectiv_series(func.__name__)
            check_objectiv_dataframe(
                df=data,
                columns_to_check=columns_to_check,
                check_index=True,
                check_dtypes=True,
                with_md_dtypes=True,
            )

            extra_series = _get_extra_series_to_include_from_params(
                func, data, include_series_from_params, *args, **kwargs,
            )
            series_to_include = list(set(columns_to_check) | set(extra_series))
            data = data[series_to_include]
            return func(_self, data, *args, **kwargs)

        return wrapped_function

    return check_objectiv_data_decorator


def _get_required_objectiv_series(func_name: str) -> List[str]:
    """
    Helper for use_only_required_objectiv_series decorator. Will return all required
    ObjectivSupportedColumns by the caller. If the caller's name is not registered under
    SupportedAggregationFunctions, then all supported objectiv columns will be required.

    returns list of caller's required objectiv columns
    """
    if not any(agg_func.value == func_name for agg_func in SupportedAggregationFunctions):
        # return all objectiv columns if the caller is not registered as supported
        return ObjectivSupportedColumns.get_data_columns()

    supported_agg_func = SupportedAggregationFunctions(func_name)
    required_obj_series = [
        col.value for col in _REQUIRED_OBJECTIV_SERIES_PER_AGG_FUNC[supported_agg_func]
    ]
    func_dependencies = supported_agg_func.get_func_dependencies()
    if func_dependencies:
        required_obj_series += list(itertools.chain.from_iterable([
            _get_required_objectiv_series(dep_calc_series.value)
            for dep_calc_series in func_dependencies
        ]))

    return required_obj_series


def _get_extra_series_to_include_from_params(
    caller: CalculatedFuncType,
    data: bach.DataFrame,
    include_series_from_params: Optional[List[str]] = None,
    *args,
    **kwargs
) -> List[str]:
    """
    Helper for use_only_required_objectiv_series decorator. Gets extra series provided via
    the caller's parameters. Will validate that all keyword params exist on the caller's signature
    and that all of them are type string. If a value or default is provided for the parameter, then
    it will be checked if it exists in the objectiv dataframe.

    returns a list of series names
    """
    from modelhub.aggregate import GroupByType
    if not include_series_from_params:
        return []

    extra_series = []
    signature = inspect.signature(caller)
    valid_parameters = list(signature.parameters.keys())

    for keyword_series_incl in include_series_from_params:
        if keyword_series_incl not in valid_parameters:
            raise Exception(f'{keyword_series_incl} does not exist in signature for {caller.__name__}.')

        param = signature.parameters[keyword_series_incl]
        param_index = valid_parameters.index(keyword_series_incl) - 2
        if param.annotation not in (str, GroupByType):
            raise Exception(f'{keyword_series_incl} must be str type.')

        if keyword_series_incl in kwargs:
            series_value = kwargs[keyword_series_incl]
        else:
            series_value = args[param_index] if len(args) > param_index else param.default

        series_to_check = series_value if isinstance(series_value, list) else [series_value]
        for series in series_to_check:
            # ignore if it's None, not_set or a Series
            if series is None or isinstance(series, bach.Series) or series == not_set:
                continue

            if series not in data.data_columns:
                raise ValueError(f'{series} does not exist in objectiv dataframe.')

            extra_series.append(series)
    return extra_series
