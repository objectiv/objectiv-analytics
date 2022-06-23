"""
Copyright 2022 Objectiv B.V.
"""

# Any import from modelhub initializes all the types, do not remove
from modelhub import __version__
import pytest
from tests_modelhub.data_and_utils.utils import get_objectiv_dataframe_test
from tests.functional.bach.test_data_and_utils import assert_equals_data


def test_top_product_features_before_conversion(db_params):
    df, modelhub = get_objectiv_dataframe_test(db_params)
    initial_columns = df.data_columns

    event_type = 'ClickEvent'
    name = 'clicks'

    # name checks
    modelhub.add_conversion_event(name=name,
                                  event_type=event_type)
    with pytest.raises(ValueError, match='Conversion event label is not provided.'):
        modelhub.aggregate.top_product_features_before_conversion(df, name=None)

    with pytest.raises(KeyError, match='Key some_name is not labeled as a conversion'):
        modelhub.aggregate.top_product_features_before_conversion(df, name='some_name')

    # without location_stack
    modelhub.add_conversion_event(event_type=event_type, name=name)
    cdf = modelhub.aggregate.top_product_features_before_conversion(df, name=name)

    # index checks
    expected_index = ['application', 'feature_nice_name', 'event_type']
    assert len(cdf.index) == 3
    for _index in expected_index:
        assert _index in cdf.index

    # data checks
    assert cdf.data_columns == ['unique_users']
    assert list(cdf.data.values()) == [1]

    # with location_stack
    location_stack = df.location_stack.json[{'id': 'main'}:]
    modelhub.add_conversion_event(location_stack=location_stack,
                                  event_type=event_type,
                                  name=name)
    cdf = modelhub.aggregate.top_product_features_before_conversion(df, name=name)
    assert len(cdf.index) == 3

    feature_name = 'Link: GitHub located at Web Document: #document => Section:' \
                   ' navbar-top => Overlay: hamburger-menu'
    assert_equals_data(
        cdf,
        expected_columns=['application', 'feature_nice_name', 'event_type', 'unique_users'],
        expected_data=[
            ['objectiv-website', feature_name, 'ClickEvent', 1],
        ],
        use_to_pandas=True
    )

    # check if any new column is added to the original dataframe
    assert sorted(initial_columns) == sorted(df.data_columns)

