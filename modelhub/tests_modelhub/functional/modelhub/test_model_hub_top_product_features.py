"""
Copyright 2022 Objectiv B.V.
"""

# Any import from modelhub initializes all the types, do not remove
from modelhub import __version__
from tests_modelhub.data_and_utils.utils import get_objectiv_dataframe_test
from tests.functional.bach.test_data_and_utils import assert_equals_data


def test_top_product_features(db_params):
    df, modelhub = get_objectiv_dataframe_test(db_params)
    initial_columns = df.data_columns
    # without location_stack
    tdf = modelhub.aggregate.top_product_features(df)
    assert len(tdf.index) == 3

    # index _application
    assert_equals_data(
        tdf.index['application'],
        expected_columns=['application'],
        expected_data=[
            ['objectiv-docs'],
            ['objectiv-docs'],
            ['objectiv-docs'],
            ['objectiv-website'],
            ['objectiv-website'],
            ['objectiv-website'],
            ['objectiv-website'],
            ['objectiv-website'],
            ['objectiv-website'],
            ['objectiv-website'],
            ['objectiv-website'],
            ['objectiv-website']
        ],
        order_by=['application'],
        use_to_pandas=True
    )

    # index feature_nice_name
    assert 'feature_nice_name' in tdf.index

    # index event_type
    assert set(tdf.index['event_type'].array) == {'ClickEvent'}

    # data info
    assert list(tdf.data.keys()) == ['user_id_nunique']
    assert set(tdf['user_id_nunique'].array) == {1}

    # with location_stack
    location_stack = df.location_stack.json[{'_type': 'LinkContext'}:]
    tdf = modelhub.aggregate.top_product_features(df, location_stack)
    # make sorting always the same (ignores potential case sensitivity)
    tdf['sort_str'] = tdf.reset_index().feature_nice_name.str[7:]
    assert_equals_data(
        tdf,
        expected_columns=['application', 'feature_nice_name', 'event_type', 'user_id_nunique', 'sort_str'],
        expected_data=[
            ['objectiv-docs', 'Link: logo', 'ClickEvent', 1, 'ogo'],
            ['objectiv-docs', 'Link: notebook-product-analytics', 'ClickEvent', 1, 'otebook-product-analytics'],
            ['objectiv-website', 'Link: About Us', 'ClickEvent', 2, 'bout Us'],
            ['objectiv-website', 'Link: GitHub', 'ClickEvent', 1, 'itHub'],
            ['objectiv-website', 'Link: Docs', 'ClickEvent', 1, 'ocs'],
            ['objectiv-website', 'Link: Contact Us', 'ClickEvent', 1, 'ontact Us'],
            ['objectiv-website', 'Link: Cookies', 'ClickEvent', 1, 'ookies'],
            ['objectiv-website', 'Link: cta-docs-location-stack', 'ClickEvent', 1, 'ta-docs-location-stack'],
            ['objectiv-website', 'Link: cta-docs-taxonomy', 'ClickEvent', 1, 'ta-docs-taxonomy'],
            ['objectiv-website', 'Link: cta-repo-button', 'ClickEvent', 1, 'ta-repo-button']]
,
        use_to_pandas=True,
        order_by=['application', 'sort_str', 'user_id_nunique']

    )

    # check if any new column is added to the original dataframe
    assert sorted(initial_columns) == sorted(df.data_columns)
