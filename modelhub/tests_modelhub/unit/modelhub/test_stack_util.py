"""
Copyright 2022 Objectiv B.V.
"""
import bach
import pandas as pd
import pytest

from modelhub.stack.util import get_supported_dtypes_per_objectiv_column, check_objectiv_dataframe
from tests_modelhub.data_and_utils.utils import create_engine_from_db_params


def test_get_supported_types_per_objectiv_column() -> None:
    result = get_supported_dtypes_per_objectiv_column()

    expected = {
        'event_id': 'uuid',
        'day': 'date',
        'moment': 'timestamp',
        'user_id': 'uuid',
        'global_contexts': 'json',
        'location_stack': 'json',
        'event_type': 'string',
        'stack_event_types': 'json',
        'session_id': 'int64',
        'session_hit_number': 'int64'
    }

    assert expected == result

    result = get_supported_dtypes_per_objectiv_column(with_md_dtypes=True)
    assert result['global_contexts'] == 'objectiv_global_context'
    assert result['location_stack'] == 'objectiv_location_stack'


def test_check_objectiv_dataframe(db_params) -> None:
    fake_objectiv_pdf = pd.DataFrame(
        {
            'event_id': ['1'],
            'day': ['2022-01-01'],
            'moment': ['2022-01-01 01:01:01'],
            'user_id': ['1'],
            'global_contexts': [[]],
            'location_stack': [[]],
            'event_type': ['event'],
            'stack_event_types': [[]],
            'session_id': ['1'],
            'session_hit_number': ['1']
        },
    )
    fake_objectiv_df = bach.DataFrame.from_pandas(
        engine=create_engine_from_db_params(db_params),
        df=fake_objectiv_pdf,
        convert_objects=True,
    )

    # should be ok
    check_objectiv_dataframe(columns_to_check=['event_id'], df=fake_objectiv_df[['event_id', 'day']])

    # checks all objectiv columns
    with pytest.raises(ValueError, match=r'is not present in DataFrame.'):
        check_objectiv_dataframe(df=fake_objectiv_df[['event_id', 'day']])

    # will check if event_id is in df index
    check_objectiv_dataframe(check_index=True, df=fake_objectiv_df.set_index('event_id'))

    with pytest.raises(ValueError, match=r'is not present in DataFrame index.'):
        check_objectiv_dataframe(check_index=True, df=fake_objectiv_df)

    check_objectiv_dataframe(
        columns_to_check=['session_id'],
        df=fake_objectiv_df[['session_id']].astype('int64'),
        check_dtypes=True,
    )
    with pytest.raises(ValueError, match=r'must be int64 dtype'):
        check_objectiv_dataframe(columns_to_check=['session_id'], df=fake_objectiv_df, check_dtypes=True)

    gc_series = fake_objectiv_df['global_contexts'].copy_override_dtype('json')
    check_objectiv_dataframe(
        columns_to_check=['global_contexts'],
        df=gc_series.to_frame(),
        check_dtypes=True,
    )

    with pytest.raises(ValueError, match=r'must be objectiv_global_context'):
        check_objectiv_dataframe(
            columns_to_check=['global_contexts'],
            df=gc_series.to_frame(),
            check_dtypes=True,
            with_md_dtypes=True,
        )
