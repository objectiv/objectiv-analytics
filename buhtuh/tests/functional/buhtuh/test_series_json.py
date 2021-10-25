"""
Copyright 2021 Objectiv B.V.
"""
from tests.functional.buhtuh.test_data_and_utils import get_bt_with_json_data, assert_equals_data


def test_json_get_value():
    bt = get_bt_with_json_data()
    bt['dict_column'] = bt.dict_column.astype('jsonb')
    bt['list_column'] = bt.list_column.astype('jsonb')
    bts = bt.dict_column.json.get_value('id')
    assert_equals_data(
        bts,
        expected_columns=['_index_row', 'dict_column'],
        expected_data=[
            [0, None],
            [1, "home"],
            [2, None],
            [3, None]
        ]
    )

# todo more tests
