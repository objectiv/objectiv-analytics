import bach

from enum import Enum
from typing import Tuple, Dict, Any, List, Optional


class ObjectivSupportedColumns(Enum):
    EVENT_ID = 'event_id'
    DAY = 'day'
    MOMENT = 'moment'
    USER_ID = 'user_id'
    GLOBAL_CONTEXTS = 'global_contexts'
    LOCATION_STACK = 'location_stack'
    EVENT_TYPE = 'event_type'
    STACK_EVENT_TYPES = 'stack_event_type'
    SESSION_ID = 'session_id'
    SESSION_HIT_NUMBER = 'session_hit_number'

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

    @classmethod
    def get_extracted_context_columns(cls) -> Tuple[str, ...]:
        return cls._EXTRACTED_CONTEXT_COLUMNS.value

    @classmethod
    def get_sessionized_columns(cls) -> Tuple[str, ...]:
        return cls._SESSIONIZED_COLUMNS.value

    @classmethod
    def get_data_columns(cls) -> Tuple[str, ...]:
        return cls._DATA_SERIES.value

    @classmethod
    def get_index_columns(cls) -> Tuple[str, ...]:
        return cls._INDEX_SERIES.value

    @classmethod
    def get_all_columns(cls) -> Tuple[str]:
        return cls.get_index_columns() + cls.get_data_columns()


# mapping for series names and dtypes
_OBJECTIV_SUPPORTED_COLUMNS_X_SERIES_CLS = {
    ObjectivSupportedColumns.EVENT_ID: bach.SeriesUuid,
    ObjectivSupportedColumns.DAY: bach.SeriesDate,
    ObjectivSupportedColumns.MOMENT: bach.SeriesTimestamp,
    ObjectivSupportedColumns.USER_ID: bach.SeriesUuid,
    ObjectivSupportedColumns.GLOBAL_CONTEXTS: bach.SeriesJson,
    ObjectivSupportedColumns.LOCATION_STACK: bach.SeriesJson,
    ObjectivSupportedColumns.EVENT_TYPE: bach.SeriesString,
    ObjectivSupportedColumns.STACK_EVENT_TYPES: bach.SeriesJson,
    ObjectivSupportedColumns.SESSION_ID: bach.SeriesInt64,
    ObjectivSupportedColumns.SESSION_HIT_NUMBER: bach.SeriesInt64,
}


def get_supported_dtypes_per_objectiv_column() -> Dict[ObjectivSupportedColumns, str]:
    return {col.value: series_cls.dtype for col, series_cls in _OBJECTIV_SUPPORTED_COLUMNS_X_SERIES_CLS.items()}


def check_objectiv_dataframe(
    df: bach.DataFrame,
    columns_to_check: List[str] = None,
    check_index: bool = False,
    check_dtypes: bool = False,
) -> None:
    columns_to_check = columns_to_check or ObjectivSupportedColumns.get_all_columns()
    supported_dtypes = get_supported_dtypes_per_objectiv_column()

    for col in columns_to_check:
        supported_col = ObjectivSupportedColumns(col)
        if supported_col.value not in df.all_series:
            raise ValueError(f'{supported_col.value} is not present in DataFrame.')

        if (
            check_index
            and col in ObjectivSupportedColumns.get_index_columns()
            and col not in df.index
        ):
            raise ValueError(f'{supported_col.value} is not present in DataFrame index.')

        if check_dtypes:
            dtype = supported_dtypes[supported_col.value]
            if df.all_series[supported_col.value].dtype != dtype:
                raise ValueError(f'{supported_col.value} must be {dtype} dtype.')
