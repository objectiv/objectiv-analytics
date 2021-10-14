"""
Copyright 2021 Objectiv B.V.
"""
from buhtuh import BuhTuhSeriesJson, BuhTuhSeriesString
from tests.functional.buhtuh.test_data_and_utils import _get_bt, assert_db_type, get_bt_with_test_data, \
    assert_equals_data


def test_set_json():
    #  todo make this work
    bt = get_bt_with_test_data()
    bt['json_column'] = {"a": "b"}


def test_all_supported_types():
    TEST_DATA_SUPPORTED_TYPES = [
        [0, '[{"a":"1"},{"b":"2"},{"c":"3","d":"4"}]'],
        [1, '{"a":"b"}']
    ]
    bt = _get_bt('test_supported_types_table',
                 TEST_DATA_SUPPORTED_TYPES,
                 ['int_column', 'string_column'],
                 convert_objects=True)

    #  now only way to load json from a pandas data frame
    bt['json_column'] = bt.string_column.astype('json')
    assert_db_type(bt['string_column'], 'text', BuhTuhSeriesString)
    assert_db_type(bt['json_column'], 'json', BuhTuhSeriesJson)


def test_json_get_element():
    TEST_DATA_SUPPORTED_TYPES = [
        [0, '[{"a":"1"},{"b":"2"},{"c":"3","d":"4"}]'],
        [1, '{"a":"b"}']
    ]
    bt = _get_bt('test_supported_types_table',
                 TEST_DATA_SUPPORTED_TYPES,
                 ['int_column', 'string_column'],
                 convert_objects=True)

    bt['json_column'] = bt.string_column.astype('json')
    selection_series = bt.json_column.json[0]
    assert_equals_data(
        selection_series,
        expected_columns=['_index_int_column', 'json_column'],
        expected_data=[
            [0,  {"a":"1"}],
            [1, None]
        ]
    )


def test_json_get_value():
    TEST_DATA_SUPPORTED_TYPES = [
        [0, '[{"a":"1"},{"b":"2"},{"c":"3","d":"4"}]'],
        [1, '{"a":"b"}']
    ]
    bt = _get_bt('test_supported_types_table',
                 TEST_DATA_SUPPORTED_TYPES,
                 ['int_column', 'string_column'],
                 convert_objects=True)

    bt['json_column'] = bt.string_column.astype('json')
    selection_series = bt.json_column.json.get_value("a")
    assert_equals_data(
        selection_series,
        expected_columns=['_index_int_column', 'json_column'],
        expected_data=[
            [0, None],
            [1, 'b']
        ]
    )
