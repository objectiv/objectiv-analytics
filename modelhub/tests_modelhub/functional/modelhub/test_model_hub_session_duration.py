"""
Copyright 2021 Objectiv B.V.
"""

# Any import from modelhub initializes all the types, do not remove
from modelhub import __version__
import pytest
from tests_modelhub.data_and_utils.utils import get_objectiv_dataframe_test
from tests.functional.bach.test_data_and_utils import assert_equals_data
import datetime


def test_defaults(db_params):
    # setting nothing, thus using all defaults (which is just moment without formatting)
    df, modelhub = get_objectiv_dataframe_test(db_params)
    s = modelhub.aggregate.session_duration(df)

    # with standard time_aggregation, all sessions are bounces
    assert len(s.to_numpy()) == 0


@pytest.mark.parametrize("exclude_bounces,expected_data", [
    (True, [[datetime.timedelta(microseconds=2667)]]),
    (False, [[datetime.timedelta(microseconds=1143)]])
])
def test_no_grouping(db_params, exclude_bounces, expected_data):
    # not grouping to anything
    df, modelhub = get_objectiv_dataframe_test(db_params)
    s = modelhub.aggregate.session_duration(df, groupby=None, exclude_bounces=exclude_bounces)

    assert_equals_data(
        s,
        expected_columns=['session_duration'],
        expected_data=expected_data,
        use_to_pandas=True,
    )


def test_time_aggregation_in_df(db_params):
    # using time_aggregation (and default groupby: mh.time_agg(df, ))
    df, modelhub = get_objectiv_dataframe_test(db_params, time_aggregation='%Y-%m-%d')
    s = modelhub.aggregate.session_duration(df)

    assert_equals_data(
        s,
        expected_columns=['time_aggregation', 'session_duration'],
        expected_data=[
            ['2021-11-29', datetime.timedelta(microseconds=1000)],
            ['2021-11-30', datetime.timedelta(microseconds=4000)],
            ['2021-12-01', datetime.timedelta(microseconds=3000)]
        ],
        use_to_pandas=True,
    )


def test_overriding_time_aggregation_in(db_params):
    # overriding time_aggregation
    df, modelhub = get_objectiv_dataframe_test(db_params)
    bts = modelhub.aggregate.session_duration(df, groupby=modelhub.time_agg(df, '%Y-%m'))

    assert_equals_data(
        bts,
        expected_columns=['time_aggregation', 'session_duration'],
        expected_data=[
            ['2021-11', datetime.timedelta(microseconds=2500)],
            ['2021-12', datetime.timedelta(microseconds=3000)]
        ],
        use_to_pandas=True,
    )

    bts = modelhub.aggregate.session_duration(df, groupby=modelhub.time_agg(df, '%Y-%m'), method='sum')

    assert_equals_data(
        bts,
        expected_columns=['time_aggregation', 'session_duration'],
        expected_data=[
            ['2021-11', datetime.timedelta(microseconds=5000)],
            ['2021-12', datetime.timedelta(microseconds=3000)],
        ],
        use_to_pandas=True,
    )


def test_groupby(db_params):
    # group by other columns
    df, modelhub = get_objectiv_dataframe_test(db_params, time_aggregation='%Y-%m-%d')
    s = modelhub.aggregate.session_duration(df, groupby='event_type')

    assert_equals_data(
        s,
        expected_columns=['event_type', 'session_duration'],
        expected_data=[['ClickEvent', datetime.timedelta(microseconds=2667)]],
        use_to_pandas=True,
    )


def test_groupby_incl_time_agg(db_params):
    # group by other columns (as series), including time_agg
    df, modelhub = get_objectiv_dataframe_test(db_params, time_aggregation='%Y-%m-%d')
    s = modelhub.aggregate.session_duration(df, groupby=[modelhub.time_agg(df, '%Y-%m'), df.session_id])

    assert_equals_data(
        s,
        expected_columns=['time_aggregation', 'session_id', 'session_duration'],
        expected_data=[
            ['2021-11', 1, datetime.timedelta(microseconds=1000)],
            ['2021-11', 3, datetime.timedelta(microseconds=4000)],
            ['2021-12', 4, datetime.timedelta(microseconds=3000)]
        ],
        use_to_pandas=True,
    )
