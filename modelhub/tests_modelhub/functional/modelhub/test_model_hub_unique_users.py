"""
Copyright 2021 Objectiv B.V.
"""

import pytest
# Any import from modelhub initializes all the types, do not remove
from modelhub import __version__
from tests_modelhub.data_and_utils.utils import get_objectiv_dataframe_test
from tests.functional.bach.test_data_and_utils import assert_equals_data


def test_defaults(db_params):
    # setting nothing, thus using all defaults (which is just moment without formatting)
    df, modelhub = get_objectiv_dataframe_test(db_params)
    s = modelhub.aggregate.unique_users(df)

    assert_equals_data(
        s,
        expected_columns=['time_aggregation', 'unique_users'],
        expected_data=[
            ['2021-11-29 10:23:36.286000', 1],
            ['2021-11-29 10:23:36.287000', 1],
            ['2021-11-30 10:23:36.267000', 1],
            ['2021-11-30 10:23:36.287000', 1],
            ['2021-11-30 10:23:36.290000', 1],
            ['2021-11-30 10:23:36.291000', 1],
            ['2021-12-01 10:23:36.276000', 1],
            ['2021-12-01 10:23:36.279000', 1],
            ['2021-12-02 10:23:36.281000', 1],
            ['2021-12-02 14:23:36.282000', 1],
            ['2021-12-03 10:23:36.283000', 1]
        ]
    )


def test_no_grouping(db_params):
    # not grouping to anything
    df, modelhub = get_objectiv_dataframe_test(db_params)
    s = modelhub.aggregate.unique_users(df, groupby=None)

    assert_equals_data(
        s,
        expected_columns=['unique_users'],
        expected_data=[
            [4]
        ]
    )


def test_time_aggregation_in_df(db_params):
    # using time_aggregation (and default groupby: mh.time_agg())
    df, modelhub = get_objectiv_dataframe_test(db_params, time_aggregation='%Y-%m-%d')
    s = modelhub.aggregate.unique_users(df)

    assert_equals_data(
        s,
        expected_columns=['time_aggregation', 'unique_users'],
        expected_data=[
            ['2021-11-29', 1],
            ['2021-11-30', 2],
            ['2021-12-01', 1],
            ['2021-12-02', 1],
            ['2021-12-03', 1]
        ]
    )


def test_overriding_time_aggregation_in(db_params):
    # overriding time_aggregation
    df, modelhub = get_objectiv_dataframe_test(db_params, time_aggregation='%Y-%m-%d')
    s = modelhub.aggregate.unique_users(df, groupby=modelhub.time_agg(df, '%Y-%m'))

    assert_equals_data(
        s,
        expected_columns=['time_aggregation', 'unique_users'],
        expected_data=[
            ['2021-11', 2],
            ['2021-12', 3]
        ]
    )


def test_groupby(db_params):
    # group by other columns
    df, modelhub = get_objectiv_dataframe_test(db_params, time_aggregation='%Y-%m-%d')
    s = modelhub.aggregate.unique_users(df, groupby='event_type')

    assert_equals_data(
        s,
        expected_columns=['event_type', 'unique_users'],
        expected_data=[['ClickEvent', 4]]
    )


def test_groupby_incl_time_agg(db_params):
    # group by other columns (as series), including time_agg
    df, modelhub = get_objectiv_dataframe_test(db_params, time_aggregation='%Y-%m-%d')
    s = modelhub.aggregate.unique_users(df, groupby=[modelhub.time_agg(df, '%Y-%m'), df.session_id])

    assert_equals_data(
        s,
        expected_columns=['time_aggregation', 'session_id', 'unique_users'],
        expected_data=[
            ['2021-11', 1, 1],
            ['2021-11', 2, 1],
            ['2021-11', 3, 1],
            ['2021-12', 4, 1],
            ['2021-12', 5, 1],
            ['2021-12', 6, 1],
            ['2021-12', 7, 1]
        ]

    )


def test_groupby_illegal_column(db_params):
    # include column that is used for grouping in groupby
    df, modelhub = get_objectiv_dataframe_test(db_params, time_aggregation='%Y-%m-%d')
    with pytest.raises(KeyError, match='is in groupby but is needed for aggregation: not allowed to '
                                         'group on that'):
        modelhub.aggregate.unique_users(df, groupby=[modelhub.time_agg(df, '%Y-%m'), df.user_id])
