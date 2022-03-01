"""
Copyright 2021 Objectiv B.V.
"""

# Any import from from bach_open_taxonomy initializes all the types, do not remove
from bach_open_taxonomy import __version__
from tests_bach_open_taxonomy.functional.objectiv_bach.data_and_utils import get_objectiv_frame
from tests.functional.bach.test_data_and_utils import assert_equals_data
from uuid import UUID


def test_get_objectiv_stack():
    get_objectiv_frame()


def test_filter():
    df = get_objectiv_frame()

    # test with same base node
    s = df.session_id<=4
    assert s.base_node == df.base_node
    fdf = df.mh.filter(s).session_id

    assert_equals_data(
        fdf,
        expected_columns=['event_id', 'session_id'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), 2],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac305'), 4],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac306'), 4],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), 1],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), 1],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), 3],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac302'), 3],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), 3]
        ]
    )

    # test with different base node
    s_different_base_node = df.session_id == df[s].session_id
    assert s_different_base_node.base_node != df.base_node
    fdf = df.mh.filter(s_different_base_node).session_id

    assert_equals_data(
        fdf,
        expected_columns=['event_id', 'session_id'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), 2],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac305'), 4],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac306'), 4],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), 1],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), 1],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), 3],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac302'), 3],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), 3]
        ]
    )

    # test with has_windowed_aggregate_function
    s_hwaf = df.groupby('session_id').window().session_hit_number.max()==1
    assert s_hwaf.expression.has_windowed_aggregate_function
    fdf = df.mh.filter(s_hwaf).session_id

    assert_equals_data(
        fdf,
        expected_columns=['event_id', 'session_id'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), 2],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac309'), 6],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac310'), 7]
        ]
    )

# map
def test_is_first_session():
    df = get_objectiv_frame(time_aggregation='YYYY-MM-DD')

    s = df.mh.map.is_first_session()

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
        order_by='event_id'
    )


def test_is_new_user():
    df = get_objectiv_frame(time_aggregation='YYYY-MM-DD')

    s = df.mh.map.is_new_user()

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
        order_by='event_id'
    )


def test_is_conversion_event():
    df = get_objectiv_frame(time_aggregation='YYYY-MM-DD')
    # add conversion event
    df.add_conversion_event(location_stack=df.location_stack.json[{'_type': 'LinkContext', 'id': 'cta-repo-button'}:],
                            event_type='ClickEvent',
                            name='github_clicks')
    s = df.mh.map.is_conversion_event('github_clicks')

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
        order_by='event_id'
    )


def test_conversion_count():
    df = get_objectiv_frame(time_aggregation='YYYY-MM-DD')
    # add conversion event
    df.add_conversion_event(location_stack=df.location_stack.json[{'_type': 'LinkContext', 'id': 'cta-repo-button'}:],
                            event_type='ClickEvent',
                            name='github_clicks')
    s = df.mh.map.conversion_count('github_clicks')

    assert_equals_data(
        s,
        expected_columns=['event_id', 'conversion_count'],
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
        order_by='event_id'
    )


def test_pre_conversion_hit_number():
    df = get_objectiv_frame(time_aggregation='YYYY-MM-DD')
    # add conversion event
    df.add_conversion_event(location_stack=df.location_stack.json[{'_type': 'LinkContext', 'id': 'cta-repo-button'}:],
                            event_type='ClickEvent',
                            name='github_clicks')
    s = df.mh.map.pre_conversion_hit_number('github_clicks')

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
        order_by='event_id'
    )


def test_time_agg():
    df = get_objectiv_frame()
    s = df.mh.time_agg()

    assert_equals_data(
        s,
        expected_columns=['event_id', 'time_aggregation'],
        expected_data=[
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac301'), '2021-11-30 10:23:36.287'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac302'), '2021-11-30 10:23:36.290'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac303'), '2021-11-30 10:23:36.291'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac304'), '2021-11-30 10:23:36.267'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac305'), '2021-12-01 10:23:36.276'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac306'), '2021-12-01 10:23:36.279'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac307'), '2021-12-02 10:23:36.281'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac308'), '2021-12-02 10:23:36.281'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac309'), '2021-12-02 14:23:36.282'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac310'), '2021-12-03 10:23:36.283'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac311'), '2021-11-29 10:23:36.286'],
            [UUID('12b55ed5-4295-4fc1-bf1f-88d64d1ac312'), '2021-11-29 10:23:36.287']
        ],
        order_by='event_id'
    )

    df = get_objectiv_frame(time_aggregation='YYYY-MM')
    s = df.mh.time_agg()

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
        order_by='event_id'
    )

    df = get_objectiv_frame()
    s = df.mh.time_agg(time_aggregation='YYYY-MM-DD')

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
        order_by='event_id'
    )

    df = get_objectiv_frame(time_aggregation='YYYY-MM-DD')
    s = df.mh.time_agg(time_aggregation='YYYY')

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
        order_by='event_id'
    )
