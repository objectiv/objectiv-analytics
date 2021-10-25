"""
Copyright 2021 Objectiv B.V.
"""
from tests.functional.buhtuh.test_data_and_utils import get_bt_with_test_data, assert_equals_data


def test_column_names():
    bt = get_bt_with_test_data()[['city']]
    bt['With_Capitals'] = 1
    bt['with_capitals'] = 1
    bt['With A Space Too'] = 1
    bt['""with"_quotes""'] = 1
    bt['Aa_!#!$*(aA®Řﬦ‎	⛔'] = 1
    expected_columns = ['_index_skating_order', 'city', 'With_Capitals', 'with_capitals',
                        'With A Space Too', '""with"_quotes""', 'Aa_!#!$*(aA®Řﬦ‎	⛔']
    expected_data = [
        [1, 'Ljouwert', 1, 1, 1, 1, 1],
        [2, 'Snits',  1, 1, 1, 1, 1],
        [3, 'Drylts',  1, 1, 1, 1, 1]
    ]
    assert_equals_data(bt, expected_columns=expected_columns, expected_data=expected_data)
    # Make sure that after materializing the columns are unchanged.
    bt = bt.get_df_materialized_model()
    assert_equals_data(bt, expected_columns=expected_columns, expected_data=expected_data)


def test_column_names_merge():
    # When merging we construct a specific sql query that names each column, so test that separately here
    bt = get_bt_with_test_data()[['city']]
    bt['With_Capitals'] = 1
    bt['with_capitals'] = 1
    bt['With A Space Too'] = 1
    bt['""with"_quotes""'] = 1
    bt['Aa_!#!$*(aA®Řﬦ‎	⛔'] = 1
    bt2 = get_bt_with_test_data()[['city']]
    bt = bt.merge(bt2, on='city')
    expected_columns = ['_index_skating_order_x', '_index_skating_order_y', 'city',
                        'With_Capitals', 'with_capitals', 'With A Space Too',
                        '""with"_quotes""', 'Aa_!#!$*(aA®Řﬦ‎	⛔']
    expected_data = [
        [1, 1, 'Ljouwert', 1, 1, 1, 1, 1],
        [2, 2, 'Snits',  1, 1, 1, 1, 1],
        [3, 3, 'Drylts',  1, 1, 1, 1, 1]
    ]
    assert_equals_data(bt, expected_columns=expected_columns, expected_data=expected_data)

# TODO: tests for groupby and windowing
