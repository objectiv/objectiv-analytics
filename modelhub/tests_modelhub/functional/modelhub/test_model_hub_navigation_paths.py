from tests.functional.bach.test_data_and_utils import assert_equals_data

from tests_modelhub.data_and_utils.utils import get_objectiv_dataframe_test


def test_get_navigation_paths(db_params):
    df, modelhub = get_objectiv_dataframe_test(db_params)
    df = df.sort_values(by='moment')

    # this is the order of all nice names when aggregated
    agg_nice_names = (
        df['location_stack'].ls.nice_name
        .sort_by_series(by=[df['moment']]).to_json_array()
    )
    assert_equals_data(
        agg_nice_names,
        expected_columns=['location_stack'],
        expected_data=[[[
            'Link: cta-docs-taxonomy located at Web Document: #document => Section: main => Section: taxonomy',
            'Link: logo located at Web Document: #document => Section: navbar-top',
            'Link: notebook-product-analytics located at Web Document: #document',
            'Link: GitHub located at Web Document: #document => Section: navbar-top => Overlay: hamburger-menu',
            'Link: cta-docs-location-stack located at Web Document: #document => Section: main => Section: location-stack',
            'Link: cta-repo-button located at Web Document: #document => Section: header',
            'Link: About Us located at Web Document: #document => Section: navbar-top => Overlay: hamburger-menu',
            'Link: Contact Us located at Web Document: #document => Section: navbar-top => Overlay: hamburger-menu',
            'Expandable Section: The Project located at Web Document: #document => Section: navbar-top => Overlay: hamburger-menu',
            'Link: Cookies located at Web Document: #document => Section: footer',
            'Link: About Us located at Web Document: #document => Section: navbar-top',
            'Link: Docs located at Web Document: #document => Section: navbar-top => Overlay: hamburger-menu',
        ]]],
        use_to_pandas=True,
    )

    bts = modelhub.aggregate.get_navigation_paths(data=df, steps=4)

    assert_equals_data(
        bts,
        expected_columns=[
            'location_stack_step_1', 'location_stack_step_2', 'location_stack_step_3', 'location_stack_step_4',
        ],
        expected_data=[
            [
                'Link: cta-docs-taxonomy located at Web Document: #document => Section: main => Section: taxonomy',
                'Link: logo located at Web Document: #document => Section: navbar-top',
                'Link: notebook-product-analytics located at Web Document: #document',
                'Link: GitHub located at Web Document: #document => Section: navbar-top => Overlay: hamburger-menu',
            ],
            [
                'Link: logo located at Web Document: #document => Section: navbar-top',
                'Link: notebook-product-analytics located at Web Document: #document',
                'Link: GitHub located at Web Document: #document => Section: navbar-top => Overlay: hamburger-menu',
                'Link: cta-docs-location-stack located at Web Document: #document => Section: main => Section: location-stack',
            ],
            [
                'Link: notebook-product-analytics located at Web Document: #document',
                'Link: GitHub located at Web Document: #document => Section: navbar-top => Overlay: hamburger-menu',
                'Link: cta-docs-location-stack located at Web Document: #document => Section: main => Section: location-stack',
                'Link: cta-repo-button located at Web Document: #document => Section: header',
            ],
            [
                'Link: GitHub located at Web Document: #document => Section: navbar-top => Overlay: hamburger-menu',
                'Link: cta-docs-location-stack located at Web Document: #document => Section: main => Section: location-stack',
                'Link: cta-repo-button located at Web Document: #document => Section: header',
                'Link: About Us located at Web Document: #document => Section: navbar-top => Overlay: hamburger-menu',
            ],
        ]
    )


def test_get_navigation_paths_grouped(db_params) -> None:
    df, modelhub = get_objectiv_dataframe_test(db_params)

    agg_nice_names_per_session = (
        df['location_stack'].ls.nice_name
        .sort_by_series(by=[df['moment']]).to_json_array(df.groupby('session_id').group_by)
    )
    assert_equals_data(
        agg_nice_names_per_session,
        expected_columns=['session_id', 'location_stack'],
        expected_data=[
            [
                1,
                [
                    'Link: cta-docs-taxonomy located at Web Document: #document => Section: main => Section: taxonomy',
                    'Link: logo located at Web Document: #document => Section: navbar-top',
                ],
            ],
            [
                2, ['Link: notebook-product-analytics located at Web Document: #document'],
            ],
            [
                3,
                [
                    'Link: GitHub located at Web Document: #document => Section: navbar-top => Overlay: hamburger-menu',
                    'Link: cta-docs-location-stack located at Web Document: #document => Section: main => Section: location-stack',
                    'Link: cta-repo-button located at Web Document: #document => Section: header'
                ],
            ],
            [
                4,
                [
                    'Link: About Us located at Web Document: #document => Section: navbar-top => Overlay: hamburger-menu',
                    'Link: Contact Us located at Web Document: #document => Section: navbar-top => Overlay: hamburger-menu',
                ],
            ],
            [
                5,
                [
                    'Expandable Section: The Project located at Web Document: #document => Section: navbar-top => Overlay: hamburger-menu',
                    'Link: Cookies located at Web Document: #document => Section: footer',
                ],
            ],
            [
                6, ['Link: About Us located at Web Document: #document => Section: navbar-top'],
            ],
            [
                7, ['Link: Docs located at Web Document: #document => Section: navbar-top => Overlay: hamburger-menu'],
            ],
        ],
        use_to_pandas=True,
    )

    bts = modelhub.aggregate.get_navigation_paths(data=df, steps=3, groupby=['session_id'])

    assert_equals_data(
        bts,
        expected_columns=['session_id', 'location_stack_step_1', 'location_stack_step_2', 'location_stack_step_3'],
        expected_data=[
            [
                1,
                'Link: cta-docs-taxonomy located at Web Document: #document => Section: main => Section: taxonomy',
                'Link: logo located at Web Document: #document => Section: navbar-top',
                None,
            ],
            [
                1,
                'Link: logo located at Web Document: #document => Section: navbar-top',
                None,
                None,
            ],
            [
                2,
                'Link: notebook-product-analytics located at Web Document: #document',
                None,
                None,
            ],
            [
                3,
                'Link: GitHub located at Web Document: #document => Section: navbar-top => Overlay: hamburger-menu',
                'Link: cta-docs-location-stack located at Web Document: #document => Section: main => Section: location-stack',
                'Link: cta-repo-button located at Web Document: #document => Section: header',
            ],
            [
                3,
                'Link: cta-docs-location-stack located at Web Document: #document => Section: main => Section: location-stack',
                'Link: cta-repo-button located at Web Document: #document => Section: header',
                None,
            ],
            [
                3,
                'Link: cta-repo-button located at Web Document: #document => Section: header',
                None,
                None,
            ],
            [
                4,
                'Link: About Us located at Web Document: #document => Section: navbar-top => Overlay: hamburger-menu',
                'Link: Contact Us located at Web Document: #document => Section: navbar-top => Overlay: hamburger-menu',
                None,
            ],
            [
                4,
                'Link: Contact Us located at Web Document: #document => Section: navbar-top => Overlay: hamburger-menu',
                None,
                None,
            ],
            [
                5,
                'Expandable Section: The Project located at Web Document: #document => Section: navbar-top => Overlay: hamburger-menu',
                'Link: Cookies located at Web Document: #document => Section: footer',
                None,
            ],
            [
                5,
                'Link: Cookies located at Web Document: #document => Section: footer',
                None,
                None,
            ],
            [
                6,
                'Link: About Us located at Web Document: #document => Section: navbar-top',
                None,
                None,
            ],
            [
                7,
                'Link: Docs located at Web Document: #document => Section: navbar-top => Overlay: hamburger-menu',
                None,
                None,
            ],
        ]
    )
