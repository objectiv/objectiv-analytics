"""
Copyright 2021 Objectiv B.V.
"""
from tests.functional.bach.test_data_and_utils import get_bt_with_test_data, assert_equals_data


def test_copy():
    df1 = get_bt_with_test_data()
    df2 = df1.copy()
    assert df1 == df2
    expected_columns = [
        '_index_skating_order', 'skating_order', 'city', 'municipality', 'inhabitants', 'founding'
    ]
    expected_data = [
        [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285],
        [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456],
        [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268]
    ]
    assert_equals_data(df1, expected_columns, expected_data)
    assert_equals_data(df2, expected_columns, expected_data)

    # changes to df2 don't affect df1
    df2['x'] = 'abc'
    assert df1 != df2
    assert_equals_data(df1, expected_columns, expected_data)

    # changes to shared base_node graph do affect the other DataFrame, unless detach_base_node is set
    df3 = df1.copy(detach_base_node=True)
    assert_equals_data(df3, expected_columns, expected_data)
    assert df1.base_node == df2.base_node
    assert df1.base_node == df3.base_node
    assert df1.base_node.materialization_name is None
    assert df2.base_node.materialization_name is None
    assert df3.base_node.materialization_name is None
    # change base_node of df2, this will also change the base_node of df1 as those are shared, but not the
    # base_node of df3.
    df2.base_node.set_materialization_name('xyz')
    assert df1.base_node == df2.base_node
    assert df1.base_node != df3.base_node
    assert df1.base_node.materialization_name == 'xyz'
    assert df2.base_node.materialization_name == 'xyz'
    assert df3.base_node.materialization_name is None
