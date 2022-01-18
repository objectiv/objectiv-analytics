"""
Copyright 2022 Objectiv B.V.
"""
from sql_models.model import escape_format_string


def assert_escape_compare_value(value):
    """ helper for test__escape_value. Assert that the escaped value, after formatting equals the original"""
    escaped = escape_format_string(value)
    double_escaped = escape_format_string(value, times=2)
    assert escaped.format() == value
    assert double_escaped.format().format() == value


def test_escape_format_string():
    assert_escape_compare_value('test')
    assert_escape_compare_value('te{s}t')
    assert_escape_compare_value('te{{s}}t')
    assert_escape_compare_value('te{st')
    assert_escape_compare_value('te{{s}t')
    assert_escape_compare_value('te{{st')
    full_string = '{test}' + escape_format_string('{test}') + '{test}'
    assert full_string.format(test='x') == 'x{test}x'
    full_string = '{test}' + escape_format_string('{{test}}') + '{test}'
    assert full_string.format(test='x') == 'x{{test}}x'
