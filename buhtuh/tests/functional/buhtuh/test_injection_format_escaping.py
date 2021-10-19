"""
Copyright 2021 Objectiv B.V.

We use(d) format() in multiple places, the test below are to prevent regressions in the escaping logic.
"""
from tests.functional.buhtuh.test_data_and_utils import get_bt_with_test_data, assert_equals_data


def test_format_injection_simple():
    # We use(d) format() in multiple places, this test is to prevent regressions in correct escaping
    bt1 = get_bt_with_test_data()[['city']]
    bt1['city'] = bt1['city'] + ' {{test}}'
    assert_equals_data(
        bt1,
        expected_columns=['_index_skating_order', 'city'],
        expected_data=[
            [1, 'Ljouwert {{test}}'],
            [2, 'Snits {{test}}'],
            [3, 'Drylts {{test}}']
        ]
    )


def test_format_injection_more():
    bt2 = get_bt_with_test_data()[['city']]
    bt2['city'] = bt2['city'] + ' {test} {{test2}} {{{test3}}} {{}{}'
    assert_equals_data(
        bt2,
        expected_columns=['_index_skating_order', 'city'],
        expected_data=[
            [1, 'Ljouwert {test} {{test2}} {{{test3}}} {{}{}'],
            [2, 'Snits {test} {{test2}} {{{test3}}} {{}{}'],
            [3, 'Drylts {test} {{test2}} {{{test3}}} {{}{}']
        ]
    )


def test_format_injection_merge():
    # We use(d) format() in multiple places, this test is to prevent regressions in correct escaping
    bt1 = get_bt_with_test_data()[['city']]
    bt1['city'] = bt1['city'] + ' {{test}}'
    bt2 = get_bt_with_test_data()[['city']]
    bt2['city'] = bt2['city'] + ' {test} {{test2}} {{{test3}}} {{}{}'
    bt = bt1.merge(bt2, on='_index_skating_order')
    assert_equals_data(
        bt,
        expected_columns=['_index_skating_order', 'city_x', 'city_y'],
        expected_data=[
            [1, 'Ljouwert {{test}}', 'Ljouwert {test} {{test2}} {{{test3}}} {{}{}'],
            [2, 'Snits {{test}}', 'Snits {test} {{test2}} {{{test3}}} {{}{}'],
            [3, 'Drylts {{test}}', 'Drylts {test} {{test2}} {{{test3}}} {{}{}']
        ]
    )
