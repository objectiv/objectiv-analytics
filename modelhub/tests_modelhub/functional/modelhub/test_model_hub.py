"""
Copyright 2021 Objectiv B.V.
"""

# Any import from modelhub initializes all the types, do not remove
from modelhub import __version__
import pytest
from tests_modelhub.data_and_utils.utils import get_objectiv_dataframe_test
from tests.functional.bach.test_data_and_utils import assert_equals_data
from uuid import UUID

# map
def test_is_first_session(db_params):
    df, modelhub = get_objectiv_dataframe_test(db_params, time_aggregation='%Y-%m-%d')

    s = modelhub.map.is_first_session(df)

    assert_equals_data(
        s,
        expected_columns=['event_id', 'is_first_session'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac302'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac305'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac306'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac307'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac308'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac309'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac310'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), True]
        ],
        order_by='event_id',
        convert_uuid=True,
    )

    # use created series to filter dataframe
    df['s'] = s

    assert_equals_data(
        df[df.s].s,
        expected_columns=['event_id', 's'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac307'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac308'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac310'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), True]
        ],
        order_by='event_id',
        convert_uuid=True,
    )


def test_is_new_user(db_params):
    df, modelhub = get_objectiv_dataframe_test(db_params, time_aggregation='%Y-%m-%d')

    s = modelhub.map.is_new_user(df)

    assert_equals_data(
        s,
        expected_columns=['event_id', 'is_new_user'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac302'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac305'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac306'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac307'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac308'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac309'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac310'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), True]
        ],
        order_by='event_id',
        convert_uuid=True,
    )

    # use created series to filter dataframe
    df['s'] = s

    assert_equals_data(
        df[df.s].s,
        expected_columns=['event_id', 's'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac307'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac308'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac309'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac310'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), True]
        ],
        order_by='event_id',
        convert_uuid=True,
    )

    s = modelhub.map.is_new_user(df, time_aggregation='%Y-%m')

    assert_equals_data(
        s,
        expected_columns=['event_id', 'is_new_user'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac302'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac305'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac306'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac307'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac308'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac309'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac310'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), True]
        ],
        order_by='event_id',
        convert_uuid=True,
    )


def test_add_conversion_event(db_params):
    df, modelhub = get_objectiv_dataframe_test(db_params, time_aggregation='%Y-%m-%d')

    location_stack = df.location_stack.json[{'_type': 'LinkContext', 'id': 'cta-repo-button'}:]
    event_type = 'ClickEvent'
    conversion = 'github_clicks'
    modelhub.add_conversion_event(location_stack=location_stack,
                                  event_type=event_type,
                                  name=conversion)

    assert isinstance(modelhub._conversion_events, dict)
    assert len(modelhub._conversion_events) == 1
    assert modelhub._conversion_events[conversion] == (location_stack, event_type)

    ser = modelhub.map.is_conversion_event(df, 'github_clicks')
    assert_equals_data(
        ser,
        expected_columns=['event_id', 'is_conversion_event'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac302'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac305'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac306'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac307'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac308'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac309'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac310'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), False]
        ],
        order_by='event_id',
        convert_uuid=True,
    )

    # location_stack not set
    modelhub.add_conversion_event(event_type=event_type, name=conversion)
    assert modelhub._conversion_events[conversion] == (None, event_type)

    ser = modelhub.map.is_conversion_event(df, 'github_clicks')

    assert_equals_data(
        ser,
        expected_columns=['event_id', 'is_conversion_event'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac302'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac305'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac306'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac307'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac308'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac309'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac310'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), True]
        ],
        order_by='event_id',
        convert_uuid=True,
    )

    # event_type not set
    df, modelhub = get_objectiv_dataframe_test(db_params, time_aggregation='%Y-%m-%d')
    modelhub.add_conversion_event(location_stack=location_stack, name='github_clicks')
    assert len(modelhub._conversion_events) == 1
    assert modelhub._conversion_events[conversion] == (location_stack, None)

    ser = modelhub.map.is_conversion_event(df, 'github_clicks')

    assert_equals_data(
        ser,
        expected_columns=['event_id', 'is_conversion_event'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac302'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac305'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac306'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac307'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac308'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac309'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac310'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), False]
        ],
        order_by='event_id',
        convert_uuid=True,
    )

    # name not set
    modelhub.add_conversion_event(event_type='ClickEvent')
    assert len(modelhub._conversion_events) == 2
    assert modelhub._conversion_events['conversion_2'] == (None, event_type)

    ser = modelhub.map.is_conversion_event(df, 'conversion_2')

    assert_equals_data(
        ser,
        expected_columns=['event_id', 'is_conversion_event'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac302'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac305'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac306'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac307'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac308'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac309'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac310'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), True]
        ],
        order_by='event_id',
        convert_uuid=True,
    )


def test_is_conversion_event(db_params):
    df, modelhub = get_objectiv_dataframe_test(db_params, time_aggregation='%Y-%m-%d')

    # add conversion event
    modelhub.add_conversion_event(location_stack=df.location_stack.json[{'_type': 'LinkContext',
                                                                         'id': 'cta-repo-button'}:],
                                  event_type='ClickEvent', name='github_clicks')
    s = modelhub.map.is_conversion_event(df, 'github_clicks')

    assert_equals_data(
        s,
        expected_columns=['event_id', 'is_conversion_event'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac302'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), True],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac305'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac306'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac307'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac308'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac309'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac310'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), False],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), False]
        ],
        order_by='event_id',
        convert_uuid=True,
    )

    # use created series to filter dataframe
    df['s'] = s

    assert_equals_data(
        df[df.s].s,
        expected_columns=['event_id', 's'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), True]
        ],
        order_by='event_id',
        convert_uuid=True,
    )

    # wrong conversion_event name
    with pytest.raises(KeyError, match="not labeled as a conversion"):
        modelhub.map.is_conversion_event(df, 'some_clicks')

    with pytest.raises(KeyError, match="not labeled as a conversion"):
        modelhub.map.is_conversion_event(df, None)


def test_conversions_counter(db_params):
    df, modelhub = get_objectiv_dataframe_test(db_params, time_aggregation='%Y-%m-%d')

    # add conversion event
    modelhub.add_conversion_event(location_stack=df.location_stack.json[{'_type': 'LinkContext', 'id': 'cta-repo-button'}:],
                            event_type='ClickEvent',
                            name='github_clicks')
    s = modelhub.map.conversions_counter(df, 'github_clicks')

    assert_equals_data(
        s,

        expected_columns=['event_id', 'converted'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), 1],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac302'), 1],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), 1],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac305'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac306'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac307'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac308'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac309'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac310'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), 0]
        ],
        order_by='event_id',
        convert_uuid=True,
    )

    # use created series to filter dataframe
    df['s'] = s == 1

    assert_equals_data(
        df[df.s].s,
        expected_columns=['event_id', 's'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), 1],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac302'), 1],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), 1]
        ],
        order_by='event_id',
        convert_uuid=True,
    )

    s = modelhub.map.conversions_counter(df, 'github_clicks', partition='user_id')

    assert_equals_data(
        s,
        expected_columns=['event_id', 'converted'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), 1],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac302'), 1],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), 1],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac305'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac306'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac307'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac308'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac309'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac310'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), 1],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), 1]
        ],
        order_by='event_id',
        convert_uuid=True,
    )


def test_conversions_in_time(db_params):
    df, modelhub = get_objectiv_dataframe_test(db_params, time_aggregation='%Y-%m-%d')

    # add conversion event
    modelhub.add_conversion_event(
        location_stack=df.location_stack.json[{'_type': 'LinkContext', 'id': 'cta-repo-button'}:],
        event_type='ClickEvent',
        name='github_clicks')
    s = modelhub.map.conversions_in_time(df, 'github_clicks')

    assert_equals_data(
        s,
        expected_columns=['event_id', 'conversions_in_time'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac302'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), 1],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac305'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac306'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac307'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac308'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac309'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac310'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), 0],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), 0]
        ],
        order_by='event_id',
        convert_uuid=True,
    )

    # use created series to filter dataframe
    df['s'] = s == 1

    assert_equals_data(
        df[df.s].s,
        expected_columns=['event_id', 's'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), True]
        ],
        order_by='event_id',
        convert_uuid=True,
    )


def test_pre_conversion_hit_number(db_params):
    df, modelhub = get_objectiv_dataframe_test(db_params, time_aggregation='%Y-%m-%d')

    # add conversion event
    modelhub.add_conversion_event(location_stack=df.location_stack.json[{'_type': 'LinkContext', 'id': 'cta-repo-button'}:],
                            event_type='ClickEvent',
                            name='github_clicks')
    s = modelhub.map.pre_conversion_hit_number(df, 'github_clicks')

    assert_equals_data(
        s,
        expected_columns=['event_id', 'pre_conversion_hit_number'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), 2],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac302'), 1],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), None],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), None],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac305'), None],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac306'), None],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac307'), None],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac308'), None],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac309'), None],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac310'), None],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), None],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), None]
        ],
        order_by='event_id',
        convert_uuid=True,
    )

    # use created series to filter dataframe
    df['s'] = s == 2

    assert_equals_data(
        df[df.s].s,
        expected_columns=['event_id', 's'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), True],
        ],
        order_by='event_id',
        convert_uuid=True,
    )

    s = modelhub.map.pre_conversion_hit_number(df, 'github_clicks', partition='user_id')

    assert_equals_data(
        s,
        expected_columns=['event_id', 'pre_conversion_hit_number'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), 2],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac302'), 1],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), None],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), None],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac305'), None],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac306'), None],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac307'), None],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac308'), None],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac309'), None],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac310'), None],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), 4],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), 3]
        ],
        order_by='event_id',
        convert_uuid=True,
    )


def test_time_agg(db_params):
    df, modelhub = get_objectiv_dataframe_test(db_params)
    s = modelhub.time_agg(df)

    assert_equals_data(
        s,
        expected_columns=['event_id', 'time_aggregation'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), '2021-11-30 10:23:36.287000'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac302'), '2021-11-30 10:23:36.290000'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), '2021-11-30 10:23:36.291000'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), '2021-11-30 10:23:36.267000'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac305'), '2021-12-01 10:23:36.276000'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac306'), '2021-12-01 10:23:36.279000'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac307'), '2021-12-02 10:23:36.281000'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac308'), '2021-12-02 10:23:36.281000'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac309'), '2021-12-02 14:23:36.282000'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac310'), '2021-12-03 10:23:36.283000'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), '2021-11-29 10:23:36.286000'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), '2021-11-29 10:23:36.287000']
        ],
        order_by='event_id',
        convert_uuid=True,
    )

    df, modelhub = get_objectiv_dataframe_test(db_params, time_aggregation='%Y-%m')
    s = modelhub.time_agg(df)

    assert_equals_data(
        s,
        expected_columns=['event_id', 'time_aggregation'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), '2021-11'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac302'), '2021-11'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), '2021-11'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), '2021-11'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac305'), '2021-12'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac306'), '2021-12'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac307'), '2021-12'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac308'), '2021-12'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac309'), '2021-12'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac310'), '2021-12'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), '2021-11'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), '2021-11']
        ],
        order_by='event_id',
        convert_uuid=True,
    )

    df, modelhub = get_objectiv_dataframe_test(db_params)
    s = modelhub.time_agg(df, time_aggregation='%Y-%m-%d')

    assert_equals_data(
        s,
        expected_columns=['event_id', 'time_aggregation'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), '2021-11-30'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac302'), '2021-11-30'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), '2021-11-30'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), '2021-11-30'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac305'), '2021-12-01'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac306'), '2021-12-01'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac307'), '2021-12-02'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac308'), '2021-12-02'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac309'), '2021-12-02'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac310'), '2021-12-03'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), '2021-11-29'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), '2021-11-29']],
        order_by='event_id',
        convert_uuid=True,
    )

    df, modelhub = get_objectiv_dataframe_test(db_params, time_aggregation='%Y-%m-%d')
    s = modelhub.time_agg(df, time_aggregation='%Y')

    assert_equals_data(
        s,
        expected_columns=['event_id', 'time_aggregation'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), '2021'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac302'), '2021'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), '2021'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), '2021'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac305'), '2021'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac306'), '2021'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac307'), '2021'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac308'), '2021'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac309'), '2021'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac310'), '2021'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), '2021'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), '2021']],
        order_by='event_id',
        convert_uuid=True,
    )
