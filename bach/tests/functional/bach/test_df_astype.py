"""
Copyright 2021 Objectiv B.V.
"""
from tests.functional.bach.test_data_and_utils import get_bt_with_test_data, assert_equals_data, \
    get_bt_with_json_data, CITIES_INDEX_AND_COLUMNS, get_df_with_test_data


def test_astype_dtypes(engine):
    # case 1: cast all columns to a type
    bt = get_df_with_test_data(engine)
    bt_int = bt[['inhabitants', 'founding']]
    bt_float = bt_int.astype('float64')
    assert bt_int.dtypes == {'founding': 'int64', 'inhabitants': 'int64'}
    assert bt_float.dtypes == {'founding': 'float64', 'inhabitants': 'float64'}

    # case 2: cast specific columns to a type
    # pre-test check
    assert bt.dtypes == {
        'city': 'string',
        'founding': 'int64',
        'inhabitants': 'int64',
        'municipality': 'string',
        'skating_order': 'int64'
    }
    # 2.1: no columns specified
    bt_none_changed = bt.astype({})
    assert bt_none_changed.dtypes == bt.dtypes
    # 2.1: one column specified
    bt_astype1 = bt.astype({
        'inhabitants': 'float64'
    })
    assert bt_astype1.dtypes == {
        'city': 'string',
        'founding': 'int64',
        'inhabitants': 'float64',   # changed
        'municipality': 'string',
        'skating_order': 'int64'
    }

    # 2.2: Multiple columns specified
    bt_astype2 = bt.astype({
        'founding': 'float64',
        'inhabitants': 'string',
        'city': 'string',  # not changed,
        'skating_order': 'string'
    })
    assert bt_astype2.dtypes == {
        'city': 'string',
        'founding': 'float64',
        'inhabitants': 'string',
        'municipality': 'string',
        'skating_order': 'string'
    }
    assert bt.data['city'] is bt_astype2.data['city']
    assert bt.data['founding'] is not bt_astype2.data['founding']
    assert bt.data['inhabitants'] is not bt_astype2.data['inhabitants']
    assert bt.data['municipality'] is bt_astype2.data['municipality']
    assert bt.data['skating_order'] is not bt_astype2.data['skating_order']
    assert_equals_data(
        bt_astype2,
        expected_columns=CITIES_INDEX_AND_COLUMNS,
        expected_data=[
            [1, '1', 'Ljouwert', 'Leeuwarden', '93485', 1285],
            [2, '2', 'Snits', 'Súdwest-Fryslân', '33520', 1456],
            [3, '3', 'Drylts', 'Súdwest-Fryslân', '3055', 1268]
        ]
    )


def test_astype_to_int(engine):
    bt = get_df_with_test_data(engine)
    bt = bt[['inhabitants']]
    bt['inhabitants'] = bt['inhabitants'] / 1000
    bt_int = bt.astype('int64')
    assert bt.dtypes == {'inhabitants': 'float64'}
    assert bt_int.dtypes == {'inhabitants': 'int64'}
    assert_equals_data(
        bt,
        expected_columns=['_index_skating_order', 'inhabitants'],
        expected_data=[
            [1, 93.485],
            [2, 33.520],
            [3, 3.055]
        ]
    )
    # When converted to ints, data will be rounded to nearest integer.
    assert_equals_data(
        bt_int,
        expected_columns=['_index_skating_order', 'inhabitants'],
        expected_data=[
            [1, 93],
            [2, 34],
            [3, 3]
        ]
    )


def test_astype_to_json():
    bt = get_bt_with_json_data(as_json=False)
    bt_json_dict = bt.dict_column.astype('jsonb')
    bt_json_list = bt.list_column.astype('jsonb')
    bt_json_mixed = bt.mixed_column.astype('jsonb')
    assert_equals_data(
        bt_json_dict,
        expected_columns=['_index_row', 'dict_column'],
        expected_data=[
            [0, {"a": "b"}],
            [1, {"_type": "SectionContext", "id": "home"}],
            [2, {"a": "b", "c": {"a": "c"}}],
            [3, {"a": "b", "e": [{"a": "b"}, {"c": "d"}]}]
        ]
    )
    assert_equals_data(
        bt_json_list,
        expected_columns=['_index_row', 'list_column'],
        expected_data=[
            [0, [{"a": "b"}, {"c": "d"}]],
            [1, ["a", "b", "c", "d"]],
            [2, [{"_type": "a", "id": "b"}, {"_type": "c", "id": "d"}, {"_type": "e", "id": "f"}]],
            [3, [{"_type": "WebDocumentContext", "id": "#document"}, {"_type": "SectionContext", "id": "home"}, {"_type": "SectionContext", "id": "top-10"}, {"_type": "ItemContext", "id": "5o7Wv5Q5ZE"}]]
        ]
    )
    assert_equals_data(
        bt_json_mixed,
        expected_columns=['_index_row', 'mixed_column'],
        expected_data=[
            [0, {"a": "b"}],
            [1, ["a", "b", "c", "d"]],
            [2, {"a": "b", "c": {"a": "c"}}],
            [3, [{"_type": "WebDocumentContext", "id": "#document"}, {"_type": "SectionContext", "id": "home"}, {"_type": "SectionContext", "id": "top-10"}, {"_type": "ItemContext", "id": "5o7Wv5Q5ZE"}]]
        ]
    )
