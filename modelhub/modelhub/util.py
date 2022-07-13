"""
Copyright 2021 Objectiv B.V.
"""
import bach

from enum import Enum
from typing import Dict, List

from modelhub.series import series_objectiv


# Columns that Modelhub expects in an Objectiv dataframe
class ObjectivSupportedColumns(Enum):
    EVENT_ID = 'event_id'
    DAY = 'day'
    MOMENT = 'moment'
    USER_ID = 'user_id'
    GLOBAL_CONTEXTS = 'global_contexts'
    LOCATION_STACK = 'location_stack'
    EVENT_TYPE = 'event_type'
    STACK_EVENT_TYPES = 'stack_event_types'
    SESSION_ID = 'session_id'
    SESSION_HIT_NUMBER = 'session_hit_number'

    IDENTITY_USER_ID = 'identity_user_id'

    _DATA_SERIES = (
        DAY, MOMENT, USER_ID, GLOBAL_CONTEXTS, LOCATION_STACK, EVENT_TYPE,
        STACK_EVENT_TYPES, SESSION_ID, SESSION_HIT_NUMBER,
    )

    _INDEX_SERIES = (EVENT_ID, )

    _EXTRACTED_CONTEXT_COLUMNS = (
        EVENT_ID, DAY, MOMENT, USER_ID, GLOBAL_CONTEXTS, LOCATION_STACK, EVENT_TYPE, STACK_EVENT_TYPES,
    )

    _SESSIONIZED_COLUMNS = (
        SESSION_ID, SESSION_HIT_NUMBER,
    )

    _IDENTITY_RESOLUTION_COLUMNS = (IDENTITY_USER_ID, )

    @classmethod
    def get_extracted_context_columns(cls) -> List[str]:
        return list(cls._EXTRACTED_CONTEXT_COLUMNS.value)

    @classmethod
    def get_sessionized_columns(cls) -> List[str]:
        return list(cls._SESSIONIZED_COLUMNS.value)

    @classmethod
    def get_data_columns(cls) -> List[str]:
        return list(cls._DATA_SERIES.value)

    @classmethod
    def get_index_columns(cls) -> List[str]:
        return list(cls._INDEX_SERIES.value)

    @classmethod
    def get_all_columns(cls) -> List[str]:
        return cls.get_index_columns() + cls.get_data_columns()


# mapping for series names and bach series dtypes
_OBJECTIV_SUPPORTED_COLUMNS_X_SERIES_DTYPE = {
    ObjectivSupportedColumns.EVENT_ID: bach.SeriesUuid.dtype,
    ObjectivSupportedColumns.DAY: bach.SeriesDate.dtype,
    ObjectivSupportedColumns.MOMENT: bach.SeriesTimestamp.dtype,
    ObjectivSupportedColumns.USER_ID: bach.SeriesUuid.dtype,
    ObjectivSupportedColumns.GLOBAL_CONTEXTS: bach.SeriesJson.dtype,
    ObjectivSupportedColumns.LOCATION_STACK: bach.SeriesJson.dtype,
    ObjectivSupportedColumns.EVENT_TYPE: bach.SeriesString.dtype,
    ObjectivSupportedColumns.STACK_EVENT_TYPES: bach.SeriesJson.dtype,
    ObjectivSupportedColumns.SESSION_ID: bach.SeriesInt64.dtype,
    ObjectivSupportedColumns.SESSION_HIT_NUMBER: bach.SeriesInt64.dtype,

    ObjectivSupportedColumns.IDENTITY_USER_ID: bach.SeriesString.dtype,
}

# mapping for series names and modelhub series dtypes
_OBJECTIV_SUPPORTED_COLUMNS_X_MODELHUB_SERIES_DTYPE = {
    ObjectivSupportedColumns.GLOBAL_CONTEXTS: series_objectiv.SeriesGlobalContexts.dtype,
    ObjectivSupportedColumns.LOCATION_STACK: series_objectiv.SeriesLocationStack.dtype,
}


def get_supported_dtypes_per_objectiv_column(
    with_md_dtypes: bool = False, with_identity_resolution: bool = True,
) -> Dict[str, str]:
    """
    Helper function that returns mapping between Objectiv series name and dtype
    If with_md_types is true, it will return mapping against modelhub own dtypes
    If with_identity_resolution is true, the supported dtype for user_id is string
        instead of UUID.
    """
    supported_dtypes = _OBJECTIV_SUPPORTED_COLUMNS_X_SERIES_DTYPE.copy()
    if with_md_dtypes:
        supported_dtypes.update(_OBJECTIV_SUPPORTED_COLUMNS_X_MODELHUB_SERIES_DTYPE)

    if with_identity_resolution:
        supported_dtypes.update({ObjectivSupportedColumns.USER_ID: bach.SeriesString.dtype})

    return {col.value: dtype for col, dtype in supported_dtypes.items()}


def check_objectiv_dataframe(
    df: bach.DataFrame,
    columns_to_check: List[str] = None,
    check_index: bool = False,
    check_dtypes: bool = False,
    with_md_dtypes: bool = False,
    infer_identity_resolution: bool = True,
) -> None:
    """
    Helper function that determines if provided dataframe is an objectiv dataframe.
    :param df: bach DataFrame to be checked
    :param columns_to_check: list of columns to verify,
        if not provided, all expected objectiv columns will be used instead.
    :param check_index: if true, will check if dataframe has expected index series
    :param check_dtypes: if true, will check if each series has expected dtypes
    :param with_md_dtypes: if true, will check if series has expected modelhub dtype
    :param infer_identity_resolution: if true, will check if user_id series has string dtype
    """
    columns = columns_to_check if columns_to_check else ObjectivSupportedColumns.get_all_columns()

    with_identity_resolution = False
    if infer_identity_resolution:
        if ObjectivSupportedColumns.IDENTITY_USER_ID.value in df.all_series:
            # if df has identity_user_id series, we can infer user_id series was changed
            # by IdentityResolutionPipeline
            with_identity_resolution = True
        elif (
            ObjectivSupportedColumns.USER_ID.value in df.all_series
            and df.all_series[ObjectivSupportedColumns.USER_ID.value].dtype == bach.SeriesString.dtype
        ):
            # user_id is dtype string, it was changed by IdentityResolutionPipeline
            with_identity_resolution = True

    supported_dtypes = get_supported_dtypes_per_objectiv_column(
        with_md_dtypes=with_md_dtypes, with_identity_resolution=with_identity_resolution,
    )

    for col in columns:
        if col not in supported_dtypes:
            raise ValueError(f'{col} is not present in Objectiv supported columns.')

        if col not in df.all_series:
            raise ValueError(f'{col} is not present in DataFrame.')

        if (
            check_index
            and col in ObjectivSupportedColumns.get_index_columns()
            and col not in df.index
        ):
            raise ValueError(f'{col} is not present in DataFrame index.')

        if check_dtypes:
            dtype = supported_dtypes[col]
            if df.all_series[col].dtype != dtype:
                raise ValueError(f'{col} must be {dtype} dtype.')
