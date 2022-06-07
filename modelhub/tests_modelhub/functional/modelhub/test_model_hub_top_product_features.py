"""
Copyright 2022 Objectiv B.V.
"""

# Any import from modelhub initializes all the types, do not remove
from modelhub import __version__
from tests_modelhub.data_and_utils.utils import get_objectiv_dataframe_test
from tests.functional.bach.test_data_and_utils import assert_equals_data


def test_top_product_features():
    df, modelhub = get_objectiv_dataframe_test()
    initial_columns = df.data_columns

    # without location_stack
    tdf = modelhub.aggregate.top_product_features(df)
    assert len(tdf.index) == 3

    # index _application
    assert_equals_data(
        tdf.index['_application'],
        expected_columns=['_application'],
        expected_data=[
            ['objectiv-docs'],
            ['objectiv-website'],
            ['objectiv-website'],
            ['objectiv-website'],
            ['objectiv-docs'],
            ['objectiv-website'],
            ['objectiv-website'],
            ['objectiv-website'],
            ['objectiv-website'],
            ['objectiv-docs'],
            ['objectiv-website'],
            ['objectiv-website']],
    )

    # index feature_nice_name
    assert '_feature_nice_name' in tdf.index

    # index event_type
    assert set(tdf.index['event_type'].array) == {'ClickEvent'}

    # data info
    assert list(tdf.data.keys()) == ['user_id_nunique']
    assert set(tdf['user_id_nunique'].array) == {1}

    # with location_stack
    location_stack = df.location_stack.json[{'_type': 'LinkContext'}:]
    tdf = modelhub.aggregate.top_product_features(df, location_stack)

    assert_equals_data(
        tdf,
        expected_columns=['_application', '_feature_nice_name', 'event_type', 'user_id_nunique'],
        expected_data=[
            ['objectiv-docs', 'Link: logo', 'ClickEvent', 1],
            ['objectiv-docs', 'Link: notebook-product-analytics', 'ClickEvent', 1],
            ['objectiv-docs', None, 'ClickEvent', 1],
            ['objectiv-website', 'Link: About Us', 'ClickEvent', 2],
            ['objectiv-website', 'Link: Contact Us', 'ClickEvent', 1],
            ['objectiv-website', 'Link: Cookies', 'ClickEvent', 1],
            ['objectiv-website', 'Link: cta-docs-location-stack', 'ClickEvent', 1],
            ['objectiv-website', 'Link: cta-docs-taxonomy', 'ClickEvent', 1],
            ['objectiv-website', 'Link: cta-repo-button', 'ClickEvent', 1],
            ['objectiv-website', 'Link: Docs', 'ClickEvent', 1],
            ['objectiv-website', 'Link: GitHub', 'ClickEvent', 1],
        ],
        order_by=['_application', '_feature_nice_name', 'user_id_nunique']
    )

    # check if any new column is added to the original dataframe
    assert sorted(initial_columns) == sorted(df.data_columns)
