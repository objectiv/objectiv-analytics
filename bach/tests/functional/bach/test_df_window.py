import pandas as pd
import pytest

from bach.partitioning import WindowFrameMode, WindowFrameBoundary
from tests.functional.bach.test_data_and_utils import (
    assert_equals_data, get_df_with_test_data,
    TEST_DATA_CITIES_FULL, CITIES_COLUMNS,
)
from tests.unit.bach.util import get_pandas_df


def test_windowing_frame_clause(engine):
    bt = get_df_with_test_data(engine, full_data_set=True)
    bt = bt.sort_index()
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


def test_windowing_windows(engine):
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
        bt.inhabitants.window_row_number(window=w).to_pandas()

    with pytest.raises(ValueError):
        # Specific window functions should fail on being passed a groupby
        bt.inhabitants.window_row_number(window=bt.groupby())


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


def test_rolling_basics(engine):
    bt = get_df_with_test_data(engine, full_data_set=False)[['skating_order', 'inhabitants']]
    # make the rolling deterministic
    bt = bt.sort_index()
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


def test_rolling_group_by_basics(engine):
    bt = get_df_with_test_data(engine, full_data_set=True)[['skating_order', 'municipality', 'inhabitants']]
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


@pytest.mark.parametrize('center', [False, True])
def test_rolling_defaults_vs_pandas(engine, center):
    columns = ['skating_order', 'municipality', 'inhabitants']
    bdf = get_df_with_test_data(engine, full_data_set=True)[columns].reset_index(drop=True)
    pdf = get_pandas_df(TEST_DATA_CITIES_FULL, CITIES_COLUMNS)[columns].reset_index(drop=True)

    bdf = bdf.sort_values(by='skating_order')
    pdf = pdf.sort_values(by='skating_order')

    empty_gb_bdf = bdf.copy()
    gb_bdf = bdf.groupby('municipality')

    empty_gb_pdf = pdf.copy()
    # keep skating order as index for sorting final results
    gb_pdf = pdf.set_index('skating_order', append=False).groupby('municipality')

    # can not set aggregated series to grouped df
    gb_bdf_rolled_series = {}
    gb_pdf_rolled_series = {}

    for window in range(1, 11):
        for min_periods in range(0, window):
            rolling_params = {
                'window': window,
                'min_periods': min_periods,
                'center': center,
            }

            series_name = f'inhabitants_w_{window}_p_{min_periods}'
            # roll values with empty groupby
            empty_gb_bdf[series_name] = empty_gb_bdf.rolling(**rolling_params).inhabitants.sum()
            empty_gb_pdf[series_name] = empty_gb_pdf.rolling(**rolling_params).inhabitants.sum()

            # roll values with groupby
            gb_bdf_rolled_series[series_name] = gb_bdf.rolling(**rolling_params).inhabitants.sum()
            gb_pdf_rolled_series[series_name] = gb_pdf.rolling(**rolling_params).inhabitants.sum()

    pd.testing.assert_frame_equal(empty_gb_pdf, empty_gb_bdf.to_pandas(), check_dtype=False)
    gb_bdf_result = gb_bdf.copy_override(
        series={
            **{
                s_name: s.copy_override(name=s_name)
                for s_name, s in gb_bdf_rolled_series.items()
            },
            'skating_order': gb_bdf['skating_order'].copy_override(group_by=None)
        },
        group_by=None,
    )
    gb_bdf_result = gb_bdf_result.set_index('skating_order', append=True).sort_index()
    gb_pdf_result = pd.DataFrame(data=gb_pdf_rolled_series).sort_index()
    pd.testing.assert_frame_equal(
        gb_pdf_result, gb_bdf_result.to_pandas(), check_dtype=False
    )


@pytest.mark.parametrize('group_by', [[], ['municipality']])
def test_rolling_variations(engine, group_by):
    columns_to_roll = ['skating_order', 'inhabitants', 'founding']

    bt = get_df_with_test_data(engine, full_data_set=True)
    bt = bt[group_by + columns_to_roll]
    bt = bt.sort_values(by='skating_order')
    bt = bt.groupby(group_by)

    windows_to_test = [1, 5, 11]
    expected_column_names = sorted(
        f'{col}_sum_w_{w}'
        for col in columns_to_roll
        for w in windows_to_test
    )
    sorting_column = 'skating_order_sum_w_1'

    full_df_rolling_results = {}
    for window in windows_to_test:
        full_df_roll = bt.rolling(window=window).sum()
        full_df_rolling_results.update(
            {
                f'{s.name}_w_{window}': s.copy_override(name=f'{s.name}_w_{window}')
                for s in full_df_roll.data.values()
            }
        )

    per_series_rolling_results = {}
    for s in bt.data_columns:
        for window in windows_to_test:
            series_name = f'{s}_sum_w_{window}'
            per_series_rolling_results[series_name] = (
                bt[[s]].rolling(window=window).sum()[s + '_sum'].copy_override(name=series_name)
            )

    fdf_base = full_df_rolling_results[sorting_column]
    full_df_result = bt.copy_override(
        series=full_df_rolling_results,
        group_by=None,
        index=fdf_base.index,
    )[expected_column_names]

    sdf_base = per_series_rolling_results[sorting_column]
    per_series_result = bt.copy_override(
        series=per_series_rolling_results, group_by=None, index=sdf_base.index,
    )[expected_column_names]

    full_df_result = full_df_result.sort_values(by=sorting_column)
    per_series_result = per_series_result.sort_values(by=sorting_column)
    pd.testing.assert_frame_equal(full_df_result.to_pandas(), per_series_result.to_pandas())


def test_expanding_defaults_vs_pandas(engine):
    columns = ['skating_order', 'founding', 'inhabitants']
    bt = get_df_with_test_data(engine, full_data_set=True)[columns]
    bt = bt.sort_values(by='skating_order')

    pdf = get_pandas_df(TEST_DATA_CITIES_FULL, CITIES_COLUMNS)[columns]
    pdf.index = pdf.index.rename(name='_index_skating_order')
    pdf = pdf.sort_values(by='skating_order')

    result_bt = bt.reset_index(drop=True)
    result_pdf = pdf.reset_index(drop=True)

    for min_periods in range(0, 11):
        expanding_bdf = bt.expanding(min_periods=min_periods).sum()
        expanding_bdf = expanding_bdf.rename(
            columns={f'{col}_sum': f'{col}_mn_{min_periods}' for col in columns}
        )
        result_bt = result_bt.copy_override(series={**result_bt.data, **expanding_bdf.data})

        expanding_pdf = pdf.expanding(min_periods=min_periods).sum()
        expanding_pdf = expanding_pdf.rename(
            columns={col: f'{col}_mn_{min_periods}' for col in columns}
        )
        result_pdf = result_pdf.merge(
            expanding_pdf,
            left_on='skating_order',
            right_on='_index_skating_order',
            how='left'
        )

    pd.testing.assert_frame_equal(result_pdf, result_bt.to_pandas(), check_dtype=False)


def test_expanding_variations(engine):
    columns_to_expand = ['skating_order', 'founding', 'inhabitants']
    bt = get_df_with_test_data(engine, full_data_set=True)[columns_to_expand]
    bt = bt.sort_index()

    min_periods_to_test = [1, 5, 11]
    expected_column_names = sorted(
        f'{col}_sum_mn_{mn}'
        for col in columns_to_expand
        for mn in min_periods_to_test
    )
    sorting_column = 'skating_order_sum_mn_1'

    full_df_expanding_results = {}
    for min_periods in min_periods_to_test:
        full_df_roll = bt.expanding(min_periods=min_periods).sum()
        full_df_expanding_results.update(
            {
                f'{s.name}_mn_{min_periods}': s.copy_override(name=f'{s.name}_mn_{min_periods}')
                for s in full_df_roll.data.values()
            }
        )

    per_series_expanding_results = {}
    for s in bt.data_columns:
        for min_periods in min_periods_to_test:
            series_name = f'{s}_sum_mn_{min_periods}'
            per_series_expanding_results[series_name] = (
                bt[[s]].expanding(min_periods=min_periods).sum()[s + '_sum'].copy_override(name=series_name)
            )

    fdf_base = full_df_expanding_results[sorting_column]
    full_df_result = bt.copy_override(
        series=full_df_expanding_results,
        group_by=None,
        index=fdf_base.index,
    )[expected_column_names]

    sdf_base = per_series_expanding_results[sorting_column]
    per_series_result = bt.copy_override(
        series=per_series_expanding_results, group_by=None, index=sdf_base.index,
    )[expected_column_names]

    full_df_result = full_df_result.sort_values(by=sorting_column)
    per_series_result = per_series_result.sort_values(by=sorting_column)
    pd.testing.assert_frame_equal(full_df_result.to_pandas(), per_series_result.to_pandas())


def test_window_functions_not_in_where_having_groupby(engine):
    # window functions are not allowed in where if constructed externally
    bt = get_df_with_test_data(engine, full_data_set=True)
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
    bt = get_df_with_test_data(engine, full_data_set=True)
    bt = bt.window().min()
    with pytest.raises(ValueError,
                       match='Cannot apply a Boolean series containing a window function to DataFrame.'):
        x = bt[bt.founding_min == 4]
