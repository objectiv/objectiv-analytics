"""
Copyright 2021 Objectiv B.V.
"""
from tests.functional.buhtuh.test_data_and_utils import get_bt_with_test_data, assert_equals_data

EXPECTED_DATA = [
    [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285],
    [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456],
    [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268]
]


def test_rename_basic():
    bt = get_bt_with_test_data()
    nbt = bt.rename(columns={'city': 'stêd'})
    nnbt = nbt.rename(columns={'stêd': 'city'})

    expected_cols_original = ['_index_skating_order', 'skating_order', 'city', 'municipality', 'inhabitants', 'founding']
    expected_cols_changed = ['_index_skating_order', 'skating_order', 'stêd', 'municipality', 'inhabitants', 'founding']

    assert_equals_data(bt, expected_columns=expected_cols_original, expected_data=EXPECTED_DATA)
    assert_equals_data(nbt, expected_columns=expected_cols_changed, expected_data=EXPECTED_DATA)
    assert_equals_data(nnbt, expected_columns=expected_cols_original, expected_data=EXPECTED_DATA)


def test_rename_complex():
    # test: mapping function, mapping to same name, and circular mapping
    bt = get_bt_with_test_data()

    def rename_func(old: str) -> str:
        if old == 'city':
            return 'stêd'
        if old == 'municipality':
            return 'founding'
        if old == 'founding':
            return 'municipality'
        return old

    nbt = bt.rename(columns=rename_func)
    assert_equals_data(
        nbt,
        expected_columns=['_index_skating_order', 'skating_order', 'stêd', 'founding', 'inhabitants', 'municipality'],
        expected_data=EXPECTED_DATA
    )
