import numpy as np
import pandas as pd
import pytest

from buhtuh.partitioning import BuhTuhWindowFrameMode, BuhTuhWindowFrameBoundary
from tests.functional.buhtuh.test_data_and_utils import assert_equals_data, get_bt_with_test_data


def test_windowing_frame_clause():
    bt = get_bt_with_test_data(full_data_set=True)
    w = bt.window()
    # Check the default
    assert (w.frame_clause == "RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW")

    def frame_clause_equals(expected, **kwargs):
        w2 = w.set_frame_clause(**kwargs)
        assert(w2.frame_clause == expected)
        # Run a query to check whether the SQL is valid if we generated what we expected.
        bt.inhabitants.window_last_value(w2).head()

    # Again, check the default but through set_frame_clause in this case
    frame_clause_equals("RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW")

    # ROWS happy paths
    frame_clause_equals("ROWS BETWEEN CURRENT ROW AND CURRENT ROW",
                        mode=BuhTuhWindowFrameMode.ROWS,
                        start_boundary=BuhTuhWindowFrameBoundary.CURRENT_ROW,
                        end_boundary=BuhTuhWindowFrameBoundary.CURRENT_ROW)

    frame_clause_equals("ROWS BETWEEN CURRENT ROW AND CURRENT ROW",
                        mode=BuhTuhWindowFrameMode.ROWS,
                        start_boundary=BuhTuhWindowFrameBoundary.CURRENT_ROW,
                        start_value=None,
                        end_boundary=BuhTuhWindowFrameBoundary.CURRENT_ROW,
                        end_value=None)

    frame_clause_equals("ROWS BETWEEN 2 PRECEDING AND CURRENT ROW",
                        mode=BuhTuhWindowFrameMode.ROWS,
                        start_boundary=BuhTuhWindowFrameBoundary.PRECEDING,
                        start_value=2,
                        end_boundary=BuhTuhWindowFrameBoundary.CURRENT_ROW,
                        end_value=None)

    frame_clause_equals("ROWS BETWEEN 2 PRECEDING AND 1 PRECEDING",
                        mode=BuhTuhWindowFrameMode.ROWS,
                        start_boundary=BuhTuhWindowFrameBoundary.PRECEDING,
                        start_value=2,
                        end_boundary=BuhTuhWindowFrameBoundary.PRECEDING,
                        end_value=1)

    frame_clause_equals("ROWS BETWEEN 1 PRECEDING AND 2 FOLLOWING",
                        mode=BuhTuhWindowFrameMode.ROWS,
                        start_boundary=BuhTuhWindowFrameBoundary.PRECEDING,
                        start_value=1,
                        end_boundary=BuhTuhWindowFrameBoundary.FOLLOWING,
                        end_value=2)

    frame_clause_equals("ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING",
                        mode=BuhTuhWindowFrameMode.ROWS,
                        start_boundary=BuhTuhWindowFrameBoundary.PRECEDING,
                        start_value=None,
                        end_boundary=BuhTuhWindowFrameBoundary.PRECEDING,
                        end_value=1)

    frame_clause_equals("ROWS BETWEEN 1 PRECEDING AND UNBOUNDED FOLLOWING",
                        mode=BuhTuhWindowFrameMode.ROWS,
                        start_boundary=BuhTuhWindowFrameBoundary.PRECEDING,
                        start_value=1,
                        end_boundary=BuhTuhWindowFrameBoundary.FOLLOWING,
                        end_value=None)

    frame_clause_equals("ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING",
                        mode=BuhTuhWindowFrameMode.ROWS,
                        start_boundary=BuhTuhWindowFrameBoundary.PRECEDING,
                        start_value=None,
                        end_boundary=BuhTuhWindowFrameBoundary.FOLLOWING,
                        end_value=None)

    # RANGE happy paths
    frame_clause_equals("RANGE BETWEEN CURRENT ROW AND CURRENT ROW",
                        mode=BuhTuhWindowFrameMode.RANGE,
                        start_boundary=BuhTuhWindowFrameBoundary.CURRENT_ROW,
                        end_boundary=BuhTuhWindowFrameBoundary.CURRENT_ROW)

    frame_clause_equals("RANGE BETWEEN CURRENT ROW AND CURRENT ROW",
                        mode=BuhTuhWindowFrameMode.RANGE,
                        start_boundary=BuhTuhWindowFrameBoundary.CURRENT_ROW,
                        start_value=None,
                        end_boundary=BuhTuhWindowFrameBoundary.CURRENT_ROW,
                        end_value=None)

    frame_clause_equals("RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING",
                        mode=BuhTuhWindowFrameMode.RANGE,
                        start_boundary=BuhTuhWindowFrameBoundary.PRECEDING,
                        start_value=None,
                        end_boundary=BuhTuhWindowFrameBoundary.FOLLOWING,
                        end_value=None)

    #     The value PRECEDING and value FOLLOWING cases are currently only allowed in ROWS mode.
    #     They indicate that the frame starts or ends with the row that many rows before or after
    #     the current row.
    with pytest.raises(ValueError):
        frame_clause_equals("",
                            mode=BuhTuhWindowFrameMode.RANGE,
                            start_boundary=BuhTuhWindowFrameBoundary.PRECEDING,
                            start_value=1,
                            end_boundary=BuhTuhWindowFrameBoundary.FOLLOWING,
                            end_value = None)

    with pytest.raises(ValueError):
        frame_clause_equals("",
                            mode=BuhTuhWindowFrameMode.RANGE,
                            start_boundary=BuhTuhWindowFrameBoundary.PRECEDING,
                            start_value= None,
                            end_boundary=BuhTuhWindowFrameBoundary.FOLLOWING,
                            end_value = 2)

    #     Restrictions are that
    #     - frame_start cannot be UNBOUNDED FOLLOWING,
    with pytest.raises(ValueError):
        frame_clause_equals("",
                            mode=BuhTuhWindowFrameMode.RANGE,
                            start_boundary=BuhTuhWindowFrameBoundary.FOLLOWING,
                            start_value=None,
                            end_boundary=BuhTuhWindowFrameBoundary.FOLLOWING,
                            end_value = None)

    #     - frame_end cannot be UNBOUNDED PRECEDING
    with pytest.raises(ValueError):
        frame_clause_equals("",
                            mode=BuhTuhWindowFrameMode.RANGE,
                            start_boundary=BuhTuhWindowFrameBoundary.PRECEDING,
                            start_value=None,
                            end_boundary=BuhTuhWindowFrameBoundary.PRECEDING,
                            end_value = None)

    #     - frame_end choice cannot appear earlier in the above list than the frame_start choice:
    #         for example RANGE BETWEEN CURRENT ROW AND value PRECEDING is not allowed.
    with pytest.raises(ValueError):
        frame_clause_equals("",
                            mode=BuhTuhWindowFrameMode.ROWS,
                            start_boundary=BuhTuhWindowFrameBoundary.PRECEDING,
                            start_value=2,
                            end_boundary=BuhTuhWindowFrameBoundary.PRECEDING,
                            end_value = 3)

    with pytest.raises(ValueError):
        frame_clause_equals("",
                            mode=BuhTuhWindowFrameMode.ROWS,
                            start_boundary=BuhTuhWindowFrameBoundary.FOLLOWING,
                            start_value=3,
                            end_boundary=BuhTuhWindowFrameBoundary.FOLLOWING,
                            end_value = 2)

def test_windowing_windows():
    ## Just test that different windows don't generate SQL errors. Logic will be checked in different tests.
    bt = get_bt_with_test_data(full_data_set=True)

    # no sorting, no partition
    p0 = bt.window()

    # no sorting, simple partition
    p1 = bt.window('municipality')

    # no sorting, multi field partition
    p2 = bt.window(['municipality', 'city'])

    # no sorting, expression partition
    p3 = bt.window(['municipality', bt['inhabitants'] < 10000])

    for w in [p0,p1,p2,p3]:
        bt.inhabitants.window_first_value(w).head()

    with pytest.raises(ValueError):
        # Specific indow functions should fail on being passed a groupby
        bt.inhabitants.window_first_value(bt.groupby())


def test_windowing_functions_agg():
    bt = get_bt_with_test_data(full_data_set=True)
    window = bt.sort_values('inhabitants').window('municipality')
    bt['min'] = bt.inhabitants.min(window)
    bt['max'] = bt.inhabitants.max(window)
    bt['count'] = bt.inhabitants.count(window)

    with pytest.raises(Exception):
        # Not supported in window functions.
        bt['nunique'] = bt.inhabitants.nunique(window)

    assert_equals_data(
        bt,
        order_by='inhabitants',
        expected_columns=[
            '_index_skating_order', 'skating_order', 'city', 'municipality', 'inhabitants',
            'founding', 'min', 'max', 'count'
        ], expected_data=[
            [4, 4, 'Sleat', 'De Friese Meren', 700, 1426, 700, 700, 1],
            [6, 6, 'Hylpen', 'Súdwest-Fryslân', 870, 1225, 870, 870, 1],
            [5, 5, 'Starum', 'Súdwest-Fryslân', 960, 1061, 870, 960, 2],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 870, 3055, 3],
            [7, 7, 'Warkum', 'Súdwest-Fryslân', 4440, 1399, 870, 4440, 4],
            [8, 8, 'Boalsert', 'Súdwest-Fryslân', 10120, 1455, 870, 10120, 5],
            [11, 11, 'Dokkum', 'Noardeast-Fryslân', 12675, 1298, 12675, 12675, 1],
            [10, 10, 'Frjentsjer', 'Waadhoeke', 12760, 1374, 12760, 12760, 1],
            [9, 9, 'Harns', 'Harlingen', 14740, 1234, 14740, 14740, 1],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 870, 33520, 6],
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 93485, 93485, 1]
        ]
    )


def test_windowing_functions_basics():
    # just check the results in too many ways
    bt = get_bt_with_test_data(full_data_set=True)
    # Create an unbounded window to make sure we can easily relate to the results.
    window = bt.sort_values('inhabitants').window('municipality',
                                                  mode=BuhTuhWindowFrameMode.ROWS,
                                                  start_boundary=BuhTuhWindowFrameBoundary.PRECEDING,
                                                  start_value=None,
                                                  end_boundary=BuhTuhWindowFrameBoundary.FOLLOWING,
                                                  end_value=None)
    bt['row_number'] = bt.inhabitants.window_row_number(window)
    bt['rank'] = bt.inhabitants.window_rank(window)
    bt['dense_rank'] = bt.inhabitants.window_dense_rank(window)
    bt['percent_rank'] = bt.inhabitants.window_percent_rank(window)
    bt['cume_dist'] = bt.inhabitants.window_cume_dist(window)
    bt['ntile'] = bt.inhabitants.window_ntile(window, 3)
    bt['lag'] = bt.inhabitants.window_lag(window, 2, 9999)
    bt['lead'] = bt.inhabitants.window_lead(window, 2, 9999)
    bt['first_value'] = bt.inhabitants.window_first_value(window)
    bt['last_value'] = bt.inhabitants.window_last_value(window)
    bt['nth_value'] = bt.inhabitants.window_nth_value(window, 2)

    assert_equals_data(
        bt,
        order_by='inhabitants',
        expected_columns=[
            '_index_skating_order', 'skating_order', 'city', 'municipality', 'inhabitants',
            'founding', 'row_number', 'rank', 'dense_rank', 'percent_rank', 'cume_dist', 'ntile', 'lag', 'lead',
            'first_value', 'last_value', 'nth_value'
        ], expected_data=[
            [4, 4, 'Sleat', 'De Friese Meren', 700, 1426, 1, 1, 1, 0.0, 1.0, 1, 9999, 9999, 700, 700, None],
            [6, 6, 'Hylpen', 'Súdwest-Fryslân', 870, 1225, 1, 1, 1, 0.0, 0.16666666666666666, 1, 9999, 3055, 870, 33520, 960],
            [5, 5, 'Starum', 'Súdwest-Fryslân', 960, 1061, 2, 2, 2, 0.2, 0.3333333333333333, 1, 9999, 4440, 870, 33520, 960],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 3, 3, 3, 0.4, 0.5, 2, 870, 10120, 870, 33520, 960],
            [7, 7, 'Warkum', 'Súdwest-Fryslân', 4440, 1399, 4, 4, 4, 0.6, 0.6666666666666666, 2, 960, 33520, 870, 33520, 960],
            [8, 8, 'Boalsert', 'Súdwest-Fryslân', 10120, 1455, 5, 5, 5, 0.8, 0.8333333333333334, 3, 3055, 9999, 870, 33520, 960],
            [11, 11, 'Dokkum', 'Noardeast-Fryslân', 12675, 1298, 1, 1, 1, 0.0, 1.0, 1, 9999, 9999, 12675, 12675, None],
            [10, 10, 'Frjentsjer', 'Waadhoeke', 12760, 1374, 1, 1, 1, 0.0, 1.0, 1, 9999, 9999, 12760, 12760, None],
            [9, 9, 'Harns', 'Harlingen', 14740, 1234, 1, 1, 1, 0.0, 1.0, 1, 9999, 9999, 14740, 14740, None],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 6, 6, 6, 1.0, 1.0, 3, 4440, 9999, 870, 33520, 960],
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 1, 1, 1, 0.0, 1.0, 1, 9999, 9999, 93485, 93485, None]
        ]
    )


def test_windowing_expressions():
    bt = get_bt_with_test_data(full_data_set=False)
    bt['lag'] = bt.inhabitants.window_lag(bt.sort_values('inhabitants').window())
    bt['test'] = bt['lag'] == 3055

    assert_equals_data(
        bt[['municipality','inhabitants', 'lag', 'test']],
        order_by='inhabitants',
        expected_columns=['_index_skating_order', 'municipality', 'inhabitants', 'lag', 'test'],
        expected_data=[
            [3, 'Súdwest-Fryslân', 3055, None, None], [2, 'Súdwest-Fryslân', 33520, 3055, True],
            [1, 'Leeuwarden', 93485, 33520, False]
        ]
    )


def test_windowing_boolean_functions():
    # Windowing function are not allowed as boolean row selectors.
    # TODO We need the flags to check for this though.
    pass


def test_rolling_defaults_vs_pandas():
    bt = get_bt_with_test_data(full_data_set=True)[['skating_order', 'founding', 'inhabitants']]

    # Create a pandas version of this stuff
    for series in bt.data_columns:
        for center in [False, True]:
            for window in range(1, 11):
                for min_periods in range(0, window):
                    pdf: pd.DataFrame = bt[[series]].to_df()
                    pd_values = pdf.rolling(window=window, min_periods=min_periods, center=center)\
                        .sum()
                    bt_values = bt.rolling(window=window, min_periods=min_periods, center=center)\
                        .sum()[[series + '_sum']].to_df()
                    np.testing.assert_equal(pd_values.values, bt_values.values)


def test_rolling_variations():
    bt = get_bt_with_test_data(full_data_set=True)[['skating_order', 'founding', 'inhabitants']]

    def _test_full_df_vs_selection(series, **kwargs):
        r1 = bt.rolling(**kwargs).sum()[[series + '_sum']]
        # the last [] is required because running this on a df will include the index as a series
        r2 = bt[[series]].rolling(**kwargs).sum()[[series + '_sum']]
        np.testing.assert_equal(r1.to_df().values, r2.to_df().values)

    def _test_series_vs_full_df(series, **kwargs):
        # get the series
        r1 = bt[series].sum(bt.rolling(**kwargs)).to_frame()
        # get the frame selection
        # the last [] is required because running this on a df will include the index as a series
        r2 = bt[[series]].rolling(**kwargs).sum()[[series + '_sum']]
        np.testing.assert_equal(r1.to_df().values, r2.to_df().values)

    for s in bt.data_columns:
        for window in [1, 5, 11]:
            _test_full_df_vs_selection(s, window=window)
            _test_series_vs_full_df(s, window=window)


def test_expanding_defaults_vs_pandas():
    bt = get_bt_with_test_data(full_data_set=True)[['skating_order', 'founding', 'inhabitants']]

    # Create a pandas version of this stuff
    for series in bt.data_columns:
        for min_periods in range(0, 11):
            pdf: pd.DataFrame = bt[[series]].to_df()
            pd_values = pdf.expanding(min_periods=min_periods).sum()
            bt_values = bt.expanding(min_periods=min_periods).sum()[[series + '_sum']].to_df()
            np.testing.assert_equal(pd_values.values, bt_values.values)


def test_expanding_variations():
    bt = get_bt_with_test_data(full_data_set=True)[['skating_order', 'founding', 'inhabitants']]

    def _test_full_df_vs_selection(series, **kwargs):
        r1 = bt.expanding(**kwargs).sum()[[series + '_sum']]
        # the last [] is required because running this on a df will include the index as a series
        r2 = bt[[series]].expanding(**kwargs).sum()[[series + '_sum']]
        np.testing.assert_equal(r1.to_df().values, r2.to_df().values)

    def _test_series_vs_full_df(series, **kwargs):
        # get the series
        r1 = bt[series].sum(bt.expanding(**kwargs)).to_frame()
        # get the frame selection
        # the last [] is required because running this on a df will include the index as a series
        r2 = bt[[series]].expanding(**kwargs).sum()[[series + '_sum']]
        np.testing.assert_equal(r1.to_df().values, r2.to_df().values)

    for series in bt.data_columns:
        for min_periods in [1,5,11]:
            _test_full_df_vs_selection(series, min_periods=min_periods)
            _test_series_vs_full_df(series, min_periods=min_periods)