import pytest

from tests.functional.bach.test_data_and_utils import get_bt_with_test_data, assert_equals_data


def test_basic_unstack() -> None:
    bt = get_bt_with_test_data(full_data_set=False)

    with pytest.raises(NotImplementedError, match=r'index must be a multi level'):
        bt.unstack()

    bt = bt.set_index(keys=['city', 'municipality'])
    bt = bt.sort_values(by='municipality')

    result = bt.unstack()
    new_cols = [
        'Leeuwarden__skating_order',
        'Leeuwarden__inhabitants',
        'Leeuwarden__founding',
        'Súdwest-Fryslân__skating_order',
        'Súdwest-Fryslân__inhabitants',
        'Súdwest-Fryslân__founding',
    ]
    assert set(result.data_columns) == set(new_cols)
    result = result[new_cols]
    assert_equals_data(
        result.sort_index(),
        expected_columns=['city'] + new_cols,
        expected_data=[
            ['Drylts', None, None, None, 3., 3055., 1268.],
            ['Ljouwert', 1., 93485., 1285., None, None, None],
            ['Snits', None, None, None, 2., 33520., 1456.],
        ],
    )


def test_unstack_level() -> None:
    bt = get_bt_with_test_data(full_data_set=False)
    bt = bt.set_index(keys=['city', 'skating_order', 'municipality'])

    result = bt.unstack(level=1)

    new_cols = ['1__founding', '1__inhabitants', '2__founding', '2__inhabitants', '3__founding', '3__inhabitants']
    assert set(new_cols) == set(result.data_columns)

    assert_equals_data(
        result[new_cols].sort_index(),
        expected_columns=['city', 'municipality'] + new_cols,
        expected_data=[
            ['Drylts', 'Súdwest-Fryslân', None, None, None, None, 1268., 3055.],
            ['Ljouwert', 'Leeuwarden', 1285., 93485., None, None, None, None],
            ['Snits', 'Súdwest-Fryslân', None, None,  1456., 33520., None, None],
        ],
    )

    result2 = bt.unstack(level='city', fill_value=0)
    new_cols2 = [
        'Drylts__founding',
        'Drylts__inhabitants',
        'Ljouwert__founding',
        'Ljouwert__inhabitants',
        'Snits__founding',
        'Snits__inhabitants',
    ]
    assert set(new_cols2) == set(result2.data_columns)

    assert_equals_data(
        result2[new_cols2].sort_index(level='skating_order'),
        expected_columns=['skating_order', 'municipality'] + new_cols2,
        expected_data=[
            [1, 'Leeuwarden', 0, 0, 1285., 93485., 0, 0],
            [2, 'Súdwest-Fryslân', 0, 0, 0, 0, 1456., 33520.],
            [3, 'Súdwest-Fryslân', 1268., 3055., 0, 0, 0, 0],
        ],
    )

    with pytest.raises(IndexError, match=r'Too many levels'):
        bt.unstack(level=3)

    with pytest.raises(IndexError, match=r'does not exist in DataFrame/Series index'):
        bt.unstack(level='random')


def test_df_unstack_w_none():
    bt = get_bt_with_test_data(full_data_set=True)
    bt['municipality_none'] = bt[bt.skating_order < 10].municipality
    stacked_bt = bt.groupby(['city', 'municipality_none']).inhabitants.sum()

    with pytest.raises(Exception, match='index contains empty values, cannot be unstacked'):
        stacked_bt.unstack()
