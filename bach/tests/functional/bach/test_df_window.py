import numpy as np
import pandas as pd
import pytest

from bach import DataFrame
from bach.partitioning import WindowFrameMode, WindowFrameBoundary
from tests.functional.bach.test_data_and_utils import assert_equals_data, get_bt_with_test_data, get_df_with_test_data


def test_windowing_frame_clause(pg_engine):
    engine = pg_engine  # TODO: BigQuery
    bt = get_df_with_test_data(engine, full_data_set=True)
    w = bt.window().group_by
    # Check the default
    assert (w.frame_clause == "RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW")

    def frame_clause_equals(expected, **kwargs):
        w2 = w.set_frame_clause(**kwargs)
        assert(w2.frame_clause == expected)
        # Run a query to check whether the SQL is valid if we generated what we expected.
        bt.inhabitants.window_last_value(w2).to_pandas()

    # Again, check the default but through set_frame_clause in this case
    frame_clause_equals("RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW")

    # ROWS happy paths
    frame_clause_equals("ROWS BETWEEN CURRENT ROW AND CURRENT ROW",
                        mode=WindowFrameMode.ROWS,
                        start_boundary=WindowFrameBoundary.CURRENT_ROW,
                        end_boundary=WindowFrameBoundary.CURRENT_ROW)

    frame_clause_equals("ROWS BETWEEN CURRENT ROW AND CURRENT ROW",
                        mode=WindowFrameMode.ROWS,
                        start_boundary=WindowFrameBoundary.CURRENT_ROW,
                        start_value=None,
                        end_boundary=WindowFrameBoundary.CURRENT_ROW,
                        end_value=None)

    frame_clause_equals("ROWS BETWEEN 2 PRECEDING AND CURRENT ROW",
                        mode=WindowFrameMode.ROWS,
                        start_boundary=WindowFrameBoundary.PRECEDING,
                        start_value=2,
                        end_boundary=WindowFrameBoundary.CURRENT_ROW,
                        end_value=None)

    frame_clause_equals("ROWS BETWEEN 2 PRECEDING AND 1 PRECEDING",
                        mode=WindowFrameMode.ROWS,
                        start_boundary=WindowFrameBoundary.PRECEDING,
                        start_value=2,
                        end_boundary=WindowFrameBoundary.PRECEDING,
                        end_value=1)

    frame_clause_equals("ROWS BETWEEN 1 PRECEDING AND 2 FOLLOWING",
                        mode=WindowFrameMode.ROWS,
                        start_boundary=WindowFrameBoundary.PRECEDING,
                        start_value=1,
                        end_boundary=WindowFrameBoundary.FOLLOWING,
                        end_value=2)

    frame_clause_equals("ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING",
                        mode=WindowFrameMode.ROWS,
                        start_boundary=WindowFrameBoundary.PRECEDING,
                        start_value=None,
                        end_boundary=WindowFrameBoundary.PRECEDING,
                        end_value=1)

    frame_clause_equals("ROWS BETWEEN 1 PRECEDING AND UNBOUNDED FOLLOWING",
                        mode=WindowFrameMode.ROWS,
                        start_boundary=WindowFrameBoundary.PRECEDING,
                        start_value=1,
                        end_boundary=WindowFrameBoundary.FOLLOWING,
                        end_value=None)

    frame_clause_equals("ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING",
                        mode=WindowFrameMode.ROWS,
                        start_boundary=WindowFrameBoundary.PRECEDING,
                        start_value=None,
                        end_boundary=WindowFrameBoundary.FOLLOWING,
                        end_value=None)

    # RANGE happy paths
    frame_clause_equals("RANGE BETWEEN CURRENT ROW AND CURRENT ROW",
                        mode=WindowFrameMode.RANGE,
                        start_boundary=WindowFrameBoundary.CURRENT_ROW,
                        end_boundary=WindowFrameBoundary.CURRENT_ROW)

    frame_clause_equals("RANGE BETWEEN CURRENT ROW AND CURRENT ROW",
                        mode=WindowFrameMode.RANGE,
                        start_boundary=WindowFrameBoundary.CURRENT_ROW,
                        start_value=None,
                        end_boundary=WindowFrameBoundary.CURRENT_ROW,
                        end_value=None)

    frame_clause_equals("RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING",
                        mode=WindowFrameMode.RANGE,
                        start_boundary=WindowFrameBoundary.PRECEDING,
                        start_value=None,
                        end_boundary=WindowFrameBoundary.FOLLOWING,
                        end_value=None)

    #     The value PRECEDING and value FOLLOWING cases are currently only allowed in ROWS mode.
    #     They indicate that the frame starts or ends with the row that many rows before or after
    #     the current row.
    with pytest.raises(ValueError):
        frame_clause_equals("",
                            mode=WindowFrameMode.RANGE,
                            start_boundary=WindowFrameBoundary.PRECEDING,
                            start_value=1,
                            end_boundary=WindowFrameBoundary.FOLLOWING,
                            end_value=None)

    with pytest.raises(ValueError):
        frame_clause_equals("",
                            mode=WindowFrameMode.RANGE,
                            start_boundary=WindowFrameBoundary.PRECEDING,
                            start_value= None,
                            end_boundary=WindowFrameBoundary.FOLLOWING,
                            end_value=2)

    #     Restrictions are that
    #     - frame_start cannot be UNBOUNDED FOLLOWING,
    with pytest.raises(ValueError):
        frame_clause_equals("",
                            mode=WindowFrameMode.RANGE,
                            start_boundary=WindowFrameBoundary.FOLLOWING,
                            start_value=None,
                            end_boundary=WindowFrameBoundary.FOLLOWING,
                            end_value=None)

    #     - frame_end cannot be UNBOUNDED PRECEDING
    with pytest.raises(ValueError):
        frame_clause_equals("",
                            mode=WindowFrameMode.RANGE,
                            start_boundary=WindowFrameBoundary.PRECEDING,
                            start_value=None,
                            end_boundary=WindowFrameBoundary.PRECEDING,
                            end_value=None)

    #     - frame_end choice cannot appear earlier in the above list than the frame_start choice:
    #         for example RANGE BETWEEN CURRENT ROW AND value PRECEDING is not allowed.
    with pytest.raises(ValueError):
        frame_clause_equals("",
                            mode=WindowFrameMode.ROWS,
                            start_boundary=WindowFrameBoundary.PRECEDING,
                            start_value=2,
                            end_boundary=WindowFrameBoundary.PRECEDING,
                            end_value=3)

    with pytest.raises(ValueError):
        frame_clause_equals("",
                            mode=WindowFrameMode.ROWS,
                            start_boundary=WindowFrameBoundary.FOLLOWING,
                            start_value=3,
                            end_boundary=WindowFrameBoundary.FOLLOWING,
                            end_value=2)

def test_windowing_windows(pg_engine):
    engine = pg_engine  # TODO: BigQuery
    ## Just test that different windows don't generate SQL errors. Logic will be checked in different tests.
    bt = get_df_with_test_data(engine, full_data_set=True)

    # no sorting, no partition
    p0 = bt.window()

    # no sorting, simple partition
    p1 = bt.groupby('municipality').window()

    # no sorting, multi field partition
    p2 = bt.groupby(['municipality', 'city']).window()

    # no sorting, expression partition
    p3 = bt.groupby(['municipality', bt['inhabitants'] < 10000]).window()

    for w in [p0,p1,p2,p3]:
        bt.inhabitants.window_first_value(window=w).to_pandas()

    with pytest.raises(ValueError):
        # Specific window functions should fail on being passed a groupby
        bt.inhabitants.window_first_value(window=bt.groupby())


def test_windowing_functions_agg(engine):

    ## Test window as an argument to agg func
    arg = get_df_with_test_data(engine, full_data_set=True)
    window = arg.sort_values('inhabitants').groupby('municipality').window()
    arg['min'] = arg.inhabitants.min(window)
    arg['max'] = arg.inhabitants.max(window)
    arg['count'] = arg.inhabitants.count(window)

    with pytest.raises(Exception):
        # Not supported in window functions.
        arg['nunique'] = arg.inhabitants.nunique(window)

    ## Test window as the dataframe that caries it.
    df = get_df_with_test_data(engine, full_data_set=True)
    window = df.sort_values('inhabitants').groupby('municipality').window()
    df['min'] = window.inhabitants.min()
    df['max'] = window.inhabitants.max()
    df['count'] = window.inhabitants.count()

    with pytest.raises(ValueError):
        # Not supported in window functions.
        df['nunique'] = window.inhabitants.nunique()

    for result in [arg, df]:
        assert_equals_data(
            result,
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



def test_windowing_functions_basics_argument(engine):
    # just check the results in too many ways, first by calling the aggregation funcs with a window argument
    arg = get_df_with_test_data(engine, full_data_set=True)
    # Create an unbounded window to make sure we can easily relate to the results.
    window = arg.sort_values('inhabitants').groupby('municipality').window(
        mode=WindowFrameMode.ROWS,
        start_boundary=WindowFrameBoundary.PRECEDING,
        start_value=None,
        end_boundary=WindowFrameBoundary.FOLLOWING,
        end_value=None)
    arg['row_number'] = arg.inhabitants.window_row_number(window)
    arg['rank'] = arg.inhabitants.window_rank(window)
    arg['dense_rank'] = arg.inhabitants.window_dense_rank(window)
    arg['percent_rank'] = arg.inhabitants.window_percent_rank(window)
    arg['cume_dist'] = arg.inhabitants.window_cume_dist(window)
    arg['ntile'] = arg.inhabitants.window_ntile(3, window=window)
    arg['lag'] = arg.inhabitants.window_lag(2, 9999, window=window)
    arg['lead'] = arg.inhabitants.window_lead(2, 9999, window=window)
    arg['first_value'] = arg.inhabitants.window_first_value(window)
    arg['last_value'] = arg.inhabitants.window_last_value(window)
    arg['nth_value'] = arg.inhabitants.window_nth_value(2, window=window)

    # just check the results in too many ways, first by calling the aggregation funcs with a window argument
    df = get_df_with_test_data(engine, full_data_set=True)
    # Create an unbounded window to make sure we can easily relate to the results.
    window = df.sort_values('inhabitants').groupby('municipality').window(
        mode=WindowFrameMode.ROWS,
        start_boundary=WindowFrameBoundary.PRECEDING,
        start_value=None,
        end_boundary=WindowFrameBoundary.FOLLOWING,
        end_value=None)
    df['row_number'] = window.inhabitants.window_row_number()
    df['rank'] = window.inhabitants.window_rank()
    df['dense_rank'] = window.inhabitants.window_dense_rank()
    df['percent_rank'] = window.inhabitants.window_percent_rank()
    df['cume_dist'] = window.inhabitants.window_cume_dist()
    df['ntile'] = window.inhabitants.window_ntile(3)
    df['lag'] = window.inhabitants.window_lag(2, 9999)
    df['lead'] = window.inhabitants.window_lead(2, 9999)
    df['first_value'] = window.inhabitants.window_first_value()
    df['last_value'] = window.inhabitants.window_last_value()
    df['nth_value'] = window.inhabitants.window_nth_value(2)

    for result in arg, df:
        assert_equals_data(
            result,
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


def test_windowing_expressions(engine):
    bt = get_df_with_test_data(engine, full_data_set=False)
    bt['lag'] = bt.inhabitants.window_lag(window=bt.sort_values('inhabitants').window())
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


def test_rolling_basics():
    bt = get_bt_with_test_data(full_data_set=False)[['skating_order', 'inhabitants']]
    bt['rolling'] = bt.rolling(window=2).inhabitants.sum()

    assert_equals_data(
        bt[['skating_order', 'inhabitants', 'rolling']],
        order_by='skating_order',
        expected_columns=['_index_skating_order', 'skating_order',  'inhabitants', 'rolling'],
        expected_data=[
            [1, 1, 93485, None],
            [2, 2, 33520, 127005],
            [3, 3, 3055, 36575]
        ]
    )


def test_rolling_group_by_basics():
    bt = get_bt_with_test_data(full_data_set=True)[['skating_order', 'municipality', 'inhabitants']]
    bt['rolling'] = bt.groupby('municipality').sort_values('skating_order').rolling(window=2).inhabitants.sum()

    assert_equals_data(
        bt[['skating_order', 'municipality','inhabitants', 'rolling']],
        order_by=['municipality', 'skating_order'],
        expected_columns=['_index_skating_order', 'skating_order', 'municipality', 'inhabitants', 'rolling'],
        expected_data=[
            [4, 4, 'De Friese Meren', 700, None],
            [9, 9, 'Harlingen', 14740, None],
            [1, 1, 'Leeuwarden', 93485, None],
            [11, 11, 'Noardeast-Fryslân', 12675, None],
            [2, 2, 'Súdwest-Fryslân', 33520, None],
            [3, 3, 'Súdwest-Fryslân', 3055, 36575],
            [5, 5, 'Súdwest-Fryslân', 960, 4015],
            [6, 6, 'Súdwest-Fryslân', 870, 1830],
            [7, 7, 'Súdwest-Fryslân', 4440, 5310],
            [8, 8, 'Súdwest-Fryslân', 10120, 14560],
            [10, 10, 'Waadhoeke', 12760, None]]
    )

def test_rolling_defaults_vs_pandas():
    import numpy as np

    bdf = get_bt_with_test_data(full_data_set=True)
    pdf = bdf.to_pandas()

    def get_rolling_values(df, window, min_periods, center, group_by):
        r = df[['skating_order', 'municipality']]
        # the first sort_order is for the window order
        t = df.sort_values('skating_order')
        t = t.groupby(group_by) if group_by else t

        rolling = t.rolling(
            window=window, min_periods=min_periods, center=center
        ).inhabitants.sum()

        if isinstance(df, DataFrame):
            # pandas can retain the sorting order and apply group_by,
            # but bach can not. We need to do one final sort in the larger df
            r['rolling'] = rolling
            return r.sort_values([*group_by, 'skating_order'])['rolling'].to_numpy()
        else:
            # we can't return the entire frame as in pandas it's not possible
            # to add the grouped, rolled up values back into the df, due to an
            # index mismatch.
            return rolling.to_numpy()

    for center in [False, True]:
        for window in range(1, 11):
            for min_periods in range(0, window):
                for group_by in ([], ['municipality']):
                    bdf_values = get_rolling_values(
                        bdf, group_by=group_by, window=window, min_periods=min_periods, center=center)
                    pdf_values = get_rolling_values(
                        pdf, group_by=group_by, window=window, min_periods=min_periods, center=center)
                    try:
                        # Because the returned values have nan / None mixture,
                        # it's really hard to compare them easily.
                        for x, y in zip(bdf_values.tolist(), pdf_values.tolist()):
                            xnan = x is None or np.isnan(x)
                            ynan = y is None or np.isnan(y)
                            if xnan != ynan or (not xnan and x != y):
                                # this looks ridiculous. but actually gives a nice error
                                assert(x == y)

                    except Exception as e:
                        print(bdf_values)
                        print(pdf_values)
                        raise e


def test_rolling_variations():
    bt = get_bt_with_test_data(full_data_set=True)
    bt = bt[['skating_order', 'municipality', 'inhabitants', 'founding']]

    def _test_full_df_vs_selection(df, series, **kwargs):
        r1 = df.rolling(**kwargs).sum()[[series + '_sum']]
        # the last [] is required because running this on a df will include the index as a series
        r2 = df[[series]].rolling(**kwargs).sum()[[series + '_sum']]
        np.testing.assert_equal(r1.to_numpy(), r2.to_numpy())

    def _test_series_vs_full_df(df, series, **kwargs):
        # get the series
        r1 = df[series].sum(df.rolling(**kwargs)).to_frame()
        # get the frame selection
        # the last [] is required because running this on a df will include the index as a series
        r2 = df[[series]].rolling(**kwargs).sum()[[series + '_sum']]
        np.testing.assert_equal(r1.to_numpy(), r2.to_numpy())

    for df in bt[['skating_order', 'inhabitants', 'founding']], bt.groupby('municipality'):
        for s in df.data_columns:
            for window in [1, 5, 11]:
                _test_full_df_vs_selection(df, s, window=window)
                _test_series_vs_full_df(df, s, window=window)


def test_expanding_defaults_vs_pandas():
    bt = get_bt_with_test_data(full_data_set=True)[['skating_order', 'founding', 'inhabitants']]

    # Create a pandas version of this stuff
    for series in bt.data_columns:
        for min_periods in range(0, 11):
            pdf: pd.DataFrame = bt[[series]].to_pandas()
            pd_values = pdf.expanding(min_periods=min_periods).sum().to_numpy()
            bt_values = bt.expanding(min_periods=min_periods).sum()[[series + '_sum']].to_numpy()
            np.testing.assert_equal(pd_values, bt_values)


def test_expanding_variations():
    bt = get_bt_with_test_data(full_data_set=True)
    bt = bt[['skating_order', 'founding', 'inhabitants']]
    def _test_full_df_vs_selection(series, **kwargs):
        r1 = bt.expanding(**kwargs).sum()[[series + '_sum']]
        # the last [] is required because running this on a df will include the index as a series
        r2 = bt[[series]].expanding(**kwargs).sum()[[series + '_sum']]
        np.testing.assert_equal(r1.to_numpy(), r2.to_numpy())

    def _test_series_vs_full_df(series, **kwargs):
        # get the series
        r1 = bt[series].sum(bt.expanding(**kwargs)).to_frame()
        # get the frame selection
        # the last [] is required because running this on a df will include the index as a series
        r2 = bt[[series]].expanding(**kwargs).sum()[[series + '_sum']]
        np.testing.assert_equal(r1.to_numpy(), r2.to_numpy())

    for series in bt.data_columns:
        for min_periods in [1,5,11]:
            _test_full_df_vs_selection(series, min_periods=min_periods)
            _test_series_vs_full_df(series, min_periods=min_periods)


def test_window_functions_not_in_where_having_groupby():
    # window functions are not allowed in where if constructed externally
    bt = get_bt_with_test_data(full_data_set=True)
    btg_min_fnd = bt.founding.min(bt.sort_values('inhabitants').window())
    with pytest.raises(ValueError,
                       match='Cannot apply a Boolean series containing a window function to DataFrame.'):
        x = bt[btg_min_fnd == 4]

    # seperate windowed series groupby should not be okay
    with pytest.raises(ValueError, match='Window functions can not be used to group.'):
        x = bt.groupby(bt.inhabitants.window_lag(window=bt.sort_values('inhabitants').window()))

    # window functions are not allowed in where even if part of df
    # adds 'lag' to df for following three tests
    bt['lag'] = bt.inhabitants.window_lag(window=bt.sort_values('inhabitants').window())
    with pytest.raises(ValueError,
                       match='Cannot apply a Boolean series containing a window function to DataFrame.'):
        x = bt[bt.lag == 4]

    # named groupby should not be okay
    with pytest.raises(ValueError, match='Window functions can not be used to group.'):
        x = bt.groupby('lag')

    # column groupby should not be okay
    with pytest.raises(ValueError, match='Window functions can not be used to group.'):
        x = bt.groupby(bt.lag)

    # window functions not allowed in having (chosen over where when groupby is set)
    bt = get_bt_with_test_data(full_data_set=True)
    bt = bt.window().min()
    with pytest.raises(ValueError,
                       match='Cannot apply a Boolean series containing a window function to DataFrame.'):
        x = bt[bt.founding_min == 4]
