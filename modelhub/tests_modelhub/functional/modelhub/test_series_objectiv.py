"""
Copyright 2021 Objectiv B.V.
"""
import pytest
from modelhub import __version__  # Any import from modelhub initializes all the types, do not remove
from tests_modelhub.data_and_utils.utils import get_df_with_json_data_real, DBParams
from tests.functional.bach.test_data_and_utils import assert_equals_data


def test_get_real_data(db_params: DBParams):
    bt = get_df_with_json_data_real(db_params)
    assert_equals_data(
        bt,
        use_to_pandas=True,
        expected_columns=['_index_event_id', 'event_id', 'global_contexts', 'location_stack'],
        expected_data=[
            [1, 1, [{'id': 'rod-web-demo', '_type': 'ApplicationContext'}, {'id': 'http_context', '_type': 'HttpContext', 'referrer': 'https://rick.objectiv.io/', 'user_agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0', 'remote_address': '144.144.144.144'}, {'id': 'f84446c6-eb76-4458-8ef4-93ade596fd5b', '_type': 'CookieIdContext', 'cookie_id': 'f84446c6-eb76-4458-8ef4-93ade596fd5b'}], [{'id': '#document', 'url': 'https://rick.objectiv.io/', '_type': 'WebDocumentContext'}, {'id': 'home', '_type': 'SectionContext'}, {'id': 'yep', '_type': 'SectionContext'}, {'id': 'cc91EfoBh8A', '_type': 'SectionContext'}]],
            [2, 2, [{'id': 'rod-web-demo', '_type': 'ApplicationContext'}, {'id': 'http_context', '_type': 'HttpContext', 'referrer': 'https://rick.objectiv.io/', 'user_agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0', 'remote_address': '144.144.144.144'}, {'id': 'f84446c6-eb76-4458-8ef4-93ade596fd5b', '_type': 'CookieIdContext', 'cookie_id': 'f84446c6-eb76-4458-8ef4-93ade596fd5b'}], [{'id': '#document', 'url': 'https://rick.objectiv.io/', '_type': 'WebDocumentContext', '_types': ['AbstractContext', 'AbstractLocationContext', 'SectionContext', 'WebDocumentContext']}, {'id': 'navigation', '_type': 'NavigationContext', '_types': ['AbstractContext', 'AbstractLocationContext', 'NavigationContext', 'SectionContext']}]],
            [3, 3, [{'id': 'rod-web-demo', '_type': 'ApplicationContext'}, {'id': 'http_context', '_type': 'HttpContext', 'referrer': 'https://rick.objectiv.io/', 'user_agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0', 'remote_address': '144.144.144.144'}, {'id': 'f84446c6-eb76-4458-8ef4-93ade596fd5b', '_type': 'CookieIdContext', 'cookie_id': 'f84446c6-eb76-4458-8ef4-93ade596fd5b'}], [{'id': '#document', 'url': 'https://rick.objectiv.io/', '_type': 'WebDocumentContext'}, {'id': 'home', '_type': 'SectionContext'}, {'id': 'new', '_type': 'SectionContext'}, {'id': 'BeyEGebJ1l4', '_type': 'SectionContext'}]],
            [4, 4, [{'id': 'rod-web-demo', '_type': 'ApplicationContext'}, {'id': 'http_context', '_type': 'HttpContext', 'referrer': 'https://rick.objectiv.io/', 'user_agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0', 'remote_address': '144.144.144.144'}, {'id': 'f84446c6-eb76-4458-8ef4-93ade596fd5b', '_type': 'CookieIdContext', 'cookie_id': 'f84446c6-eb76-4458-8ef4-93ade596fd5b'}], [{'id': '#document', 'url': 'https://rick.objectiv.io/', '_type': 'WebDocumentContext'}, {'id': 'home', '_type': 'SectionContext'}, {'id': 'new', '_type': 'SectionContext'}, {'id': 'yBwD4iYcWC4', '_type': 'SectionContext'}]],
            [5, 5, [{'id': 'rod-web-demo', '_type': 'ApplicationContext'}, {'id': 'http_context', '_type': 'HttpContext', 'referrer': 'https://rick.objectiv.io/', 'user_agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0', 'remote_address': '144.144.144.144'}, {'id': 'f84446c6-eb76-4458-8ef4-93ade596fd5b', '_type': 'CookieIdContext', 'cookie_id': 'f84446c6-eb76-4458-8ef4-93ade596fd5b'}], [{'id': '#document', 'url': 'https://rick.objectiv.io/', '_type': 'WebDocumentContext'}, {'id': 'home', '_type': 'SectionContext'}, {'id': 'new', '_type': 'SectionContext'}, {'id': 'eYuUAGXN0KM', '_type': 'MediaPlayerContext'}]],
            [6, 6, [{'id': 'rod-web-demo', '_type': 'ApplicationContext'}, {'id': 'http_context', '_type': 'HttpContext', 'referrer': 'https://rick.objectiv.io/', 'user_agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0', 'remote_address': '144.144.144.144'}, {'id': 'f84446c6-eb76-4458-8ef4-93ade596fd5b', '_type': 'CookieIdContext', 'cookie_id': 'f84446c6-eb76-4458-8ef4-93ade596fd5b'}], [{'id': '#document', 'url': 'https://rick.objectiv.io/', '_type': 'WebDocumentContext'}]]
        ]
    )


def test_objectiv_stack_type(db_params):
    bt = get_df_with_json_data_real(db_params)

    bt['a'] = bt.global_contexts.astype('objectiv_global_context')
    bts = bt.a.objectiv.get_from_context_with_type_series("CookieIdContext", "cookie_id")
    assert_equals_data(
        bts,
        expected_columns=['_index_event_id', 'a'],
        expected_data=[
            [1, 'f84446c6-eb76-4458-8ef4-93ade596fd5b'],
            [2, 'f84446c6-eb76-4458-8ef4-93ade596fd5b'],
            [3, 'f84446c6-eb76-4458-8ef4-93ade596fd5b'],
            [4, 'f84446c6-eb76-4458-8ef4-93ade596fd5b'],
            [5, 'f84446c6-eb76-4458-8ef4-93ade596fd5b'],
            [6, 'f84446c6-eb76-4458-8ef4-93ade596fd5b']
        ]
    )


def test_objectiv_stack_type2(db_params):
    bt = get_df_with_json_data_real(db_params)

    bt['a'] = bt.global_contexts.astype('objectiv_global_context')
    bts = bt.a.global_contexts.user_agent
    assert_equals_data(
        bts,
        expected_columns=['_index_event_id', 'a'],
        expected_data=[
            [1, 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0'],
            [2, 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0'],
            [3, 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0'],
            [4, 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0'],
            [5, 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0'],
            [6, 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0']
        ]
    )


def test_objectiv_stack_type3(db_params):
    bt = get_df_with_json_data_real(db_params)

    bt['b'] = bt.location_stack.astype('objectiv_location_stack')
    bts = bt.b.location_stack.navigation_features
    assert_equals_data(
        bts,
        expected_columns=['_index_event_id', 'b'],
        expected_data=[
            [1, []],
            [2, [{'id': 'navigation', '_type': 'NavigationContext', '_types': ['AbstractContext', 'AbstractLocationContext', 'NavigationContext', 'SectionContext']}]],
            [3, []],
            [4, []],
            [5, []],
            [6, []]
        ],
        use_to_pandas=True,
    )


def test_objectiv_stack_type4(db_params):
    bt = get_df_with_json_data_real(db_params)

    bt['b'] = bt.location_stack.astype('objectiv_location_stack')
    bts = bt.b.location_stack.feature_stack
    assert_equals_data(
        bts,
        use_to_pandas=True,
        expected_columns=['_index_event_id', 'b'],
        expected_data=[
            [1, [{'id': '#document', '_type': 'WebDocumentContext'}, {'id': 'home', '_type': 'SectionContext'}, {'id': 'yep', '_type': 'SectionContext'}, {'id': 'cc91EfoBh8A', '_type': 'SectionContext'}]],
            [2, [{'id': '#document', '_type': 'WebDocumentContext'}, {'id': 'navigation', '_type': 'NavigationContext'}]],
            [3, [{'id': '#document', '_type': 'WebDocumentContext'}, {'id': 'home', '_type': 'SectionContext'}, {'id': 'new', '_type': 'SectionContext'}, {'id': 'BeyEGebJ1l4', '_type': 'SectionContext'}]],
            [4, [{'id': '#document', '_type': 'WebDocumentContext'}, {'id': 'home', '_type': 'SectionContext'}, {'id': 'new', '_type': 'SectionContext'}, {'id': 'yBwD4iYcWC4', '_type': 'SectionContext'}]],
            [5, [{'id': '#document', '_type': 'WebDocumentContext'}, {'id': 'home', '_type': 'SectionContext'}, {'id': 'new', '_type': 'SectionContext'}, {'id': 'eYuUAGXN0KM', '_type': 'MediaPlayerContext'}]],
            [6, [{'id': '#document', '_type': 'WebDocumentContext'}]]
        ]

    )


def test_objectiv_stack_type5(db_params):
    bt = get_df_with_json_data_real(db_params)

    bt['b'] = bt.location_stack.astype('objectiv_location_stack')
    bts = bt.b.location_stack.nice_name
    assert_equals_data(
        bts,
        expected_columns=['_index_event_id', 'b'],
        expected_data=[
            [1, 'Section: cc91EfoBh8A located at Web Document: #document => Section: home => Section: yep'],
            [2, 'Navigation: navigation located at Web Document: #document'],
            [3, 'Section: BeyEGebJ1l4 located at Web Document: #document => Section: home => Section: new'],
            [4, 'Section: yBwD4iYcWC4 located at Web Document: #document => Section: home => Section: new'],
            [5, 'Media Player: eYuUAGXN0KM located at Web Document: #document => Section: home => Section: new'],
            [6, 'Web Document: #document']
        ]
    )
