"""
Copyright 2021 Objectiv B.V.
"""

# Any import from from bach_open_taxonomy initializes all the types, do not remove
import pytest
from bach_open_taxonomy import __version__
from tests_bach_open_taxonomy.functional.objectiv_bach.data_and_utils import get_objectiv_dataframe
from tests.functional.bach.test_data_and_utils import assert_equals_data


def test_defaults():
    # setting nothing, thus using all defaults (which is just moment without formatting)
    df, modelhub = get_objectiv_dataframe()
    s = modelhub.aggregate.unique_users(df)

    assert_equals_data(
        s,
        expected_columns=['time_aggregation', 'unique_users'],
        expected_data=[
            ['2021-11-29 10:23:36.286', 1],
            ['2021-11-29 10:23:36.287', 1],
            ['2021-11-30 10:23:36.267', 1],
            ['2021-11-30 10:23:36.287', 1],
            ['2021-11-30 10:23:36.290', 1],
            ['2021-11-30 10:23:36.291', 1],
            ['2021-12-01 10:23:36.276', 1],
            ['2021-12-01 10:23:36.279', 1],
            ['2021-12-02 10:23:36.281', 1],
            ['2021-12-02 14:23:36.282', 1],
            ['2021-12-03 10:23:36.283', 1]
        ]
    )

def test_no_grouping():
    # not grouping to anything
    df, modelhub = get_objectiv_dataframe()
    s = modelhub.aggregate.unique_users(df, groupby=None)

    assert_equals_data(
        s,
        expected_columns=['unique_users'],
        expected_data=[
            [4]
        ]
    )

def test_time_aggregation_in_df():
    # using time_aggregation (and default groupby: mh.time_agg())
    df, modelhub = get_objectiv_dataframe(time_aggregation='YYYY-MM-DD')
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

def test_overriding_time_aggregation_in():
    # overriding time_aggregation
    df, modelhub = get_objectiv_dataframe(time_aggregation='YYYY-MM-DD')
    s = modelhub.aggregate.unique_users(df, groupby=modelhub.time_agg(df, 'YYYY-MM'))

    assert_equals_data(
        s,
        expected_columns=['time_aggregation', 'unique_users'],
        expected_data=[
            ['2021-11', 2],
            ['2021-12', 3]
        ]
    )

def test_groupby():
    # group by other columns
    df, modelhub = get_objectiv_dataframe(time_aggregation='YYYY-MM-DD')
    s = modelhub.aggregate.unique_users(df, groupby='event_type')

    assert_equals_data(
        s,
        expected_columns=['event_type', 'unique_users'],
        expected_data=[['ClickEvent', 4]]
    )

def test_groupby_incl_time_agg():
    # group by other columns (as series), including time_agg
    df, modelhub = get_objectiv_dataframe(time_aggregation='YYYY-MM-DD')
    s = modelhub.aggregate.unique_users(df, groupby=[modelhub.time_agg(df, 'YYYY-MM'), df.session_id])

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

def test_groupby_illegal_column():
    # include column that is used for grouping in groupby
    df, modelhub = get_objectiv_dataframe(time_aggregation='YYYY-MM-DD')
    with pytest.raises(KeyError, match='is in groupby but is needed for aggregation: not allowed to '
                                         'group on that'):
        modelhub.aggregate.unique_users(df, groupby=[modelhub.time_agg(df, 'YYYY-MM'), df.user_id])
