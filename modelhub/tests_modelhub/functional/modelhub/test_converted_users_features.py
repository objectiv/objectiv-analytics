"""
Copyright 2022 Objectiv B.V.
"""

# Any import from modelhub initializes all the types, do not remove
from modelhub import __version__
from tests_modelhub.data_and_utils.utils import get_objectiv_dataframe_test
from tests.functional.bach.test_data_and_utils import assert_equals_data


def test_converted_users_features():
    df, modelhub = get_objectiv_dataframe_test()
    initial_columns = df.data_columns

    event_type = 'ClickEvent'

    location_stack = df.location_stack.json[{'id': 'main'}:]
    modelhub.add_conversion_event(location_stack=location_stack,
                                  event_type=event_type,
                                  name=None)

    # without location_stack (the corner case)
    modelhub.add_conversion_event(event_type=event_type)
    cdf = modelhub.aggregate.converted_users_features(df)

    # index checks
    expected_index = ['_application', '_feature_nice_name', 'event_type']
    assert len(cdf.index) == 3
    for _index in expected_index:
        assert _index in cdf.index

    # data checks
    assert cdf.data_columns == ['unique_users']
    assert list(cdf.data.values()) == [1]

    # with location_stack
    location_stack = df.location_stack.json[{'id': 'main'}:]
    modelhub.add_conversion_event(location_stack=location_stack,
                                  event_type=event_type)
    cdf = modelhub.aggregate.converted_users_features(df)
    assert len(cdf.index) == 3

    feature_name = 'Link: GitHub located at Web Document: #document => Section:' \
                   ' navbar-top => Overlay: hamburger-menu'
    assert_equals_data(
        cdf,
        expected_columns=['_application', '_feature_nice_name', 'event_type', 'unique_users'],
        expected_data=[
            ['objectiv-website', feature_name, 'ClickEvent', 1],
        ],
    )

    # check if any new column is added to the original dataframe
    assert sorted(initial_columns) == sorted(df.data_columns)

