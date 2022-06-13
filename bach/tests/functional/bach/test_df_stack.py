import pandas as pd

from tests.functional.bach.test_data_and_utils import assert_equals_data, get_df_with_test_data


def test_stack(engine) -> None:
    bt = get_df_with_test_data(engine, full_data_set=True)[['city', 'municipality', 'inhabitants']]
    bt = bt.groupby(['municipality', 'city'])['inhabitants'].sum()

    unstacked_bt = bt.unstack()

    pbt = unstacked_bt.to_pandas()
    expected = pbt.stack()
    result = unstacked_bt.stack()

    pd.testing.assert_series_equal(
        expected.sort_index(),
        result.sort_index().to_pandas(),
        check_names=False,
        check_dtype=False,
    )
    assert_equals_data(
        result.sort_index(),
        expected_columns=['municipality', '__stacked_index', '__stacked'],
        expected_data=[
            ['De Friese Meren', 'Sleat', 700],
            ['Harlingen', 'Harns', 14740],
            ['Leeuwarden', 'Ljouwert', 93485],
            ['Noardeast-Fryslân', 'Dokkum', 12675],
            ['Súdwest-Fryslân', 'Boalsert', 10120],
            ['Súdwest-Fryslân', 'Drylts', 3055],
            ['Súdwest-Fryslân', 'Hylpen', 870],
            ['Súdwest-Fryslân', 'Snits', 33520],
            ['Súdwest-Fryslân', 'Starum', 960],
            ['Súdwest-Fryslân', 'Warkum', 4440],
            ['Waadhoeke', 'Frjentsjer', 12760],
        ],
    )

    stacked_bt_w_na = unstacked_bt['Snits'].to_frame()
    expected_w_na = pbt[['Snits']].stack(dropna=False)
    result_w_na = stacked_bt_w_na.stack(dropna=False)
    pd.testing.assert_series_equal(
        expected_w_na.sort_index(),
        # TODO: fix sorting with a constant
        result_w_na.to_frame().sort_index(level=0).to_pandas()['__stacked'],
        check_names=False,
        check_dtype=False,
    )

    assert_equals_data(
        result_w_na.to_frame().sort_index(level=0),
        expected_columns=['municipality', '__stacked_index', '__stacked'],
        expected_data=[
            ['De Friese Meren', 'Snits', None],
            ['Harlingen', 'Snits', None],
            ['Leeuwarden', 'Snits', None],
            ['Noardeast-Fryslân', 'Snits', None],
            ['Súdwest-Fryslân', 'Snits', 33520],
            ['Waadhoeke', 'Snits', None],
        ],
    )


def test_stack_diff_types(engine) -> None:
    bt = get_df_with_test_data(engine, full_data_set=False)[['city', 'inhabitants']]
    pbt = bt.to_pandas()

    result = bt.stack().sort_index()
    pd.testing.assert_series_equal(
        pbt.stack().sort_index().astype(str),
        result.to_pandas(),
        check_names=False,
    )

    assert_equals_data(
        result,
        expected_columns=['_index_skating_order', '__stacked_index', '__stacked'],
        expected_data=[
            [1, 'city', 'Ljouwert'],
            [1, 'inhabitants', '93485'],
            [2, 'city', 'Snits'],
            [2, 'inhabitants', '33520'],
            [3, 'city', 'Drylts'],
            [3, 'inhabitants', '3055'],
        ],
    )
