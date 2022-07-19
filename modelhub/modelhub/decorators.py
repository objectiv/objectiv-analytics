import inspect
from functools import wraps
from typing import List, Union, Optional, TYPE_CHECKING
from typing_extensions import Protocol

import bach
from sql_models.constants import not_set


if TYPE_CHECKING:
    from modelhub import Map, Aggregate


class ModelFunctionType(Protocol):
    @property
    def __name__(self) -> str:
        ...

    def __call__(
        self, _self: Union['Map', 'Aggregate'], data: bach.DataFrame, *args, **kwargs
    ) -> bach.Series:
        ...


def use_only_required_objectiv_series(
    required_series: Optional[List[str]] = None,
    include_series_from_params: Optional[List[str]] = None,
):
    """
    Internal: Decorator for validating and limiting the series used on a function dedicated
    to generate new aggregated series based on supported objectiv columns.

    :param required_series: A list of objectiv series names that the DataFrame must have
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
    def check_objectiv_data_decorator(func: ModelFunctionType):
        @wraps(func)
        def wrapped_function(
            _self: Union['Map', 'Aggregate'],
            data: bach.DataFrame,
            *args,
            **kwargs,
        ) -> bach.Series:
            from modelhub.util import check_objectiv_dataframe, ObjectivSupportedColumns
            check_objectiv_dataframe(
                df=data,
                columns_to_check=required_series,
                check_index=True,
                check_dtypes=True,
                with_md_dtypes=True,
            )

            extra_series = _get_extra_series_to_include_from_params(
                func, data, include_series_from_params, *args, **kwargs,
            )
            series_to_include = (
                set(required_series or ObjectivSupportedColumns.get_data_columns()) | set(extra_series)
            )
            data = data[[s for s in data.data_columns if s in series_to_include]]
            return func(_self, data, *args, **kwargs)

        return wrapped_function

    return check_objectiv_data_decorator


def _get_extra_series_to_include_from_params(
    caller: ModelFunctionType,
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
