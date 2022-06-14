import inspect
from enum import Enum
from functools import wraps
from typing import Callable, List, Union, Optional, TYPE_CHECKING, Tuple, Any

import bach

from modelhub.stack.util import ObjectivSupportedColumns

if TYPE_CHECKING:
    from modelhub import Map, Aggregate


class MapCalculatedSeriesFunc(str, Enum):
    IS_FIRST_SESSION = 'is_first_session'
    IS_NEW_USER = 'is_new_user'
    IS_CONVERSION_EVENT = 'is_conversion_event'
    CONVERSIONS_COUNTER = 'conversions_counter'
    CONVERSIONS_IN_TIME = 'conversions_in_time'
    PRE_CONVERSION_HIT_NUMBER = 'pre_conversion_hit_number'

    def get_func_dependencies(self) -> List['MapCalculatedSeriesFunc']:
        if self == MapCalculatedSeriesFunc.CONVERSIONS_COUNTER:
            # conversions_counter is dependent to conversions_in_time
            # and also on conversions_in_time dependencies
            return [
                MapCalculatedSeriesFunc.CONVERSIONS_IN_TIME,
                MapCalculatedSeriesFunc.IS_CONVERSION_EVENT,
            ]

        if self == MapCalculatedSeriesFunc.CONVERSIONS_IN_TIME:
            # conversions_in_time is dependent to is_conversion_event
            return [MapCalculatedSeriesFunc.IS_CONVERSION_EVENT]

        return []


class AggregateCalculatedSeriesFunc(str, Enum):
    UNIQUE_USERS = 'unique_users'
    UNIQUE_SESSIONS = 'unique_sessions'
    SESSION_DURATION = 'sesison_duration'
    FREQUENCY = 'frequency'
    TOP_PRODUCT_FEATURES = 'top_product_features'
    TOP_PRODUCT_FEATURES_BEFORE_CONVERSION = 'top_product_features_before_conversion'

    def get_func_dependencies(self) -> List['MapCalculatedSeriesFunc']:
        return []


_REQUIRED_OBJECTIV_SERIES_PER_MAP_FUNC = {
    MapCalculatedSeriesFunc.IS_FIRST_SESSION: [
        ObjectivSupportedColumns.USER_ID, ObjectivSupportedColumns.SESSION_ID,
    ],
    MapCalculatedSeriesFunc.IS_NEW_USER: [
        ObjectivSupportedColumns.SESSION_ID,
        ObjectivSupportedColumns.USER_ID,
        ObjectivSupportedColumns.MOMENT,
    ],
    MapCalculatedSeriesFunc.IS_CONVERSION_EVENT: [ObjectivSupportedColumns.EVENT_TYPE],
    MapCalculatedSeriesFunc.CONVERSIONS_COUNTER: [ObjectivSupportedColumns.SESSION_ID],
    MapCalculatedSeriesFunc.CONVERSIONS_IN_TIME: [
        ObjectivSupportedColumns.SESSION_ID, ObjectivSupportedColumns.MOMENT,
    ],
    MapCalculatedSeriesFunc.PRE_CONVERSION_HIT_NUMBER: [
      ObjectivSupportedColumns.SESSION_ID, ObjectivSupportedColumns.SESSION_HIT_NUMBER,
    ],
}

_REQUIRED_OBJECTIV_SERIES_PER_AGGREGATE_FUNC = {
    AggregateCalculatedSeriesFunc.UNIQUE_USERS: [
        ObjectivSupportedColumns.USER_ID, ObjectivSupportedColumns.MOMENT,
    ],
    AggregateCalculatedSeriesFunc.UNIQUE_SESSIONS: [
        ObjectivSupportedColumns.SESSION_ID, ObjectivSupportedColumns.MOMENT,
    ],
    AggregateCalculatedSeriesFunc.SESSION_DURATION: [
        ObjectivSupportedColumns.SESSION_ID, ObjectivSupportedColumns.MOMENT,
    ],
    AggregateCalculatedSeriesFunc.FREQUENCY: [
        ObjectivSupportedColumns.USER_ID, ObjectivSupportedColumns.SESSION_ID,
    ],
    AggregateCalculatedSeriesFunc.TOP_PRODUCT_FEATURES: [
        ObjectivSupportedColumns.GLOBAL_CONTEXTS,
        ObjectivSupportedColumns.LOCATION_STACK,
        ObjectivSupportedColumns.USER_ID,
    ],
    AggregateCalculatedSeriesFunc.TOP_PRODUCT_FEATURES_BEFORE_CONVERSION: [
        ObjectivSupportedColumns.GLOBAL_CONTEXTS,
        ObjectivSupportedColumns.LOCATION_STACK,
    ],
}

CALCULATED_FUNC_TYPE = Callable[[Union['Map', 'Aggregate'], bach.DataFrame, Tuple[Any, ...]], bach.Series]


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
    def check_objectiv_data_decorator(func: CALCULATED_FUNC_TYPE):
        @wraps(func)
        def wrapped_function(
            _self: Union['Map', 'Aggregate'],
            data: bach.DataFrame,
            *args,
            **kwargs,
        ) -> bach.Series:
            from modelhub.stack.util import check_objectiv_dataframe
            columns_to_check = [
                col.value for col in _get_required_objectiv_series(func.__name__)
            ]
            check_objectiv_dataframe(
                df=data,
                columns_to_check=columns_to_check,
                check_index=True,
                check_dtypes=True,
                with_md_dtypes=True,
            )

            extra_series = _get_extra_series_to_include_from_params(func, data, include_series_from_params,)
            series_to_include = list(set(columns_to_check) | set(extra_series))
            data = data[series_to_include]
            return func(_self, data, *args, **kwargs)

        return wrapped_function

    return check_objectiv_data_decorator


def _get_required_objectiv_series(func_name: str) -> List[ObjectivSupportedColumns]:
    """
    Helper for use_only_required_objectiv_series decorator. Will return all required
    ObjectivSupportedColumns by the caller. If the caller's name is not registered under
    AggregateCalculatedSeriesFunc or MapCalculatedSeriesFunc it will raise an error.

    returns list of caller's required objectiv columns
    """
    if any(agg_func.value == func_name for agg_func in AggregateCalculatedSeriesFunc):
        series_func = AggregateCalculatedSeriesFunc(func_name)
        required_obj_series = _REQUIRED_OBJECTIV_SERIES_PER_AGGREGATE_FUNC[series_func]
    elif any(map_func.value == func_name for map_func in MapCalculatedSeriesFunc):
        series_func = MapCalculatedSeriesFunc(func_name)
        required_obj_series = _REQUIRED_OBJECTIV_SERIES_PER_MAP_FUNC[series_func]
    else:
        raise Exception(
            f'{func_name} does not exist in '
            'AggregateCalculatedSeries or MapCalculatedSeries. Please define it.'
        )

    func_dependencies = series_func.get_func_dependencies()
    if func_dependencies:
        required_obj_series += [
            _get_required_objectiv_series(dep_calc_series.value)
            for dep_calc_series in func_dependencies
        ]
    return required_obj_series


def _get_extra_series_to_include_from_params(
    caller: CALCULATED_FUNC_TYPE,
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
    if not include_series_from_params:
        return []

    extra_series = []
    signature = inspect.signature(caller)
    valid_parameters = list(signature.parameters.keys())

    for keyword_series_incl in include_series_from_params:
        if keyword_series_incl not in valid_parameters:
            raise Exception(f'{keyword_series_incl} does not exist in signature for {caller.__name__}.')

        param = signature.parameters.get(keyword_series_incl)
        param_index = valid_parameters.index(keyword_series_incl) - 2
        if param.annotation != str:
            raise Exception(f'{keyword_series_incl} must be str type.')

        if keyword_series_incl in kwargs:
            series_name = kwargs[keyword_series_incl]
        else:
            series_name = args[param_index] if len(args) > param_index else param.default

        if series_name is None:
            continue

        if series_name not in data.data_columns:
            raise ValueError(f'{series_name} does not exist in objectiv dataframe.')

        extra_series.append(series_name)
    return extra_series

