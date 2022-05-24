import numpy as np
import pandas as pd

from bach import Series, DataFrame
from bach.operations.cut import CutOperation, QCutOperation
from sql_models.util import quote_identifier, is_bigquery
from tests.functional.bach.test_data_and_utils import assert_equals_data

PD_TESTING_SETTINGS = {
    'check_dtype': False,
    'check_exact': False,
    'atol': 1e-3,
}


def compare_boundaries(expected: pd.Series, result: Series) -> None:
    for exp, res in zip(expected.to_numpy(), result.to_numpy()):
        if not isinstance(exp, pd.Interval):
            assert res is None or np.isnan(res)
            continue

        np.testing.assert_almost_equal(exp.left, float(res.left), decimal=2)
        np.testing.assert_almost_equal(exp.right, float(res.right), decimal=2)

        if exp.closed_left:
            assert res.closed_left

        if exp.closed_right:
            assert res.closed_right


def test_cut_operation_pandas(engine) -> None:
    p_series = pd.Series(range(100), name='a')
    series = DataFrame.from_pandas(engine=engine, df=p_series.to_frame(), convert_objects=True).a

    expected = pd.cut(p_series, bins=10)
    result = CutOperation(series=series, bins=10)()
    compare_boundaries(expected, result)

    expected_wo_right = pd.cut(p_series, bins=10, right=False)
    result_wo_right = CutOperation(series, bins=10, right=False)()
    compare_boundaries(expected_wo_right, result_wo_right)


def test_cut_operation_bach(engine) -> None:
    p_series = pd.Series(range(100), name='a')
    series = DataFrame.from_pandas(engine=engine, df=p_series.to_frame(), convert_objects=True).a

    ranges = [
        pd.Interval(0, 9.9, closed='both'),
        pd.Interval(9.9, 19.8, closed='right'),
        pd.Interval(19.8, 29.7, closed='right'),
        pd.Interval(29.7, 39.6, closed='right'),
        pd.Interval(39.6, 49.5, closed='right'),
        pd.Interval(49.5, 59.4, closed='right'),
        pd.Interval(59.4, 69.3, closed='right'),
        pd.Interval(69.3, 79.2, closed='right'),
        pd.Interval(79.2, 89.1, closed='right'),
        pd.Interval(89.1, 99, closed='right'),
    ]

    expected = pd.Series({num: ranges[int(num / 10)] for num in range(100)})
    result = CutOperation(series=series, bins=10, method='bach')().sort_index()
    compare_boundaries(expected, result)

    ranges_wo_right = [
        pd.Interval(0, 9.9, closed='left'),
        pd.Interval(9.9, 19.8, closed='left'),
        pd.Interval(19.8, 29.7, closed='left'),
        pd.Interval(29.7, 39.6, closed='left'),
        pd.Interval(39.6, 49.5, closed='left'),
        pd.Interval(49.5, 59.4, closed='left'),
        pd.Interval(59.4, 69.3, closed='left'),
        pd.Interval(69.3, 79.2, closed='left'),
        pd.Interval(79.2, 89.1, closed='left'),
        pd.Interval(89.1, 99, closed='both'),
    ]

    expected_wo_right = pd.Series({num: ranges_wo_right[int(num / 10)] for num in range(100)})
    result_wo_right = CutOperation(series=series, bins=10, method='bach', right=False)().sort_index()

    compare_boundaries(expected_wo_right, result_wo_right)


def test_cut_operation_boundary(engine) -> None:
    bins = 3
    p_series = pd.Series(data=[1, 2, 3, 4], name='a')
    series = DataFrame.from_pandas(engine=engine, df=p_series.to_frame(), convert_objects=True).a

    expected = pd.cut(p_series, bins=bins, right=True)
    result = CutOperation(series=series, bins=bins, right=True)()
    compare_boundaries(expected, result)


def test_cut_w_ignore_index(engine) -> None:
    bins = 3
    p_series = pd.Series(data=[1, 2, 3, 4], name='a')
    series = DataFrame.from_pandas(engine=engine, df=p_series.to_frame(), convert_objects=True).a

    result = CutOperation(series=series, bins=bins, right=True, ignore_index=False)()
    assert ['_index_0', 'a'] == list(result.index.keys())

    result_w_ignore = CutOperation(series=series, bins=bins, right=True, ignore_index=True)()
    assert ['a'] == list(result_w_ignore.index.keys())


def test_cut_w_include_empty_bins(engine) -> None:
    bins = 3
    p_series = pd.Series(data=[1, 1, 2, 3, 6, 7, 8], name='a')
    series = DataFrame.from_pandas(engine=engine, df=p_series.to_frame(), convert_objects=True).a

    result = CutOperation(
        series=series, bins=bins, include_empty_bins=True,
    )().sort_index()

    empty_interval = pd.Interval(3.333, 5.667)
    expected_data = [
        pd.Interval(0.993, 3.333),
        pd.Interval(0.993, 3.333),
        pd.Interval(0.993, 3.333),
        pd.Interval(0.993, 3.333),
        pd.Interval(5.667, 8),
        pd.Interval(5.667, 8),
        pd.Interval(5.667, 8),
    ]
    expected_index = [1., 1., 2., 3., 6., 7., 8.]

    if is_bigquery(engine):
        # TODO: Remove this, None value should be last after sorting
        expected_data = [empty_interval] + expected_data
        expected_index = [np.nan] + expected_index
    else:
        expected_data.append(empty_interval)
        expected_index.append(np.nan)
    expected = pd.Series(data=expected_data, index=expected_index)
    compare_boundaries(expected, result)


def test_cut_operation_calculate_bucket_properties(engine) -> None:
    final_properties = ['a_min', 'a_max', 'bin_adjustment', 'step']
    bins = 2
    # min != max
    p_series_neq = pd.Series(data=[1, 3, 5, 16, 2, 20], name='a')
    series_neq = DataFrame.from_pandas(engine=engine, df=p_series_neq.to_frame(), convert_objects=True).a
    result_neq = CutOperation(series=series_neq, bins=bins)._calculate_bucket_properties()
    expected_neq = pd.DataFrame(
        data={
            'a_min': [1],  # min(a) - min_adjustment
            'a_max': [20],  # max(a) + max_adjustment
            'min_adjustment': [0],  # min(a) != max(a)
            'max_adjustment': [0],  # min(a) != max(a)
            'bin_adjustment': [0.019],  # (max(a) - min(a)) * range_adjustment
            'step': [9.5],  # (max(a) - min(a)) / bins
        },
    )
    pd.testing.assert_frame_equal(expected_neq[final_properties], result_neq.to_pandas(), check_dtype=False)

    # min == max
    p_series_eq = pd.Series(data=[2, 2], name='a')
    series_eq = DataFrame.from_pandas(engine=engine, df=p_series_eq.to_frame(), convert_objects=True).a
    result_eq = CutOperation(series=series_eq, bins=bins)._calculate_bucket_properties()
    expected_eq = pd.DataFrame(
        data={
            'a_min': [1.998],
            'a_max': [2.002],
            'min_adjustment': [0.002],  # if min(a) == max(a): range_adjustment * abs(min(a))
            'max_adjustment': [0.002],  # if min(a) == max(a): range_adjustment * abs(max(a))
            'bin_adjustment': [0.],
            'step': [0.002],
        },
    )
    pd.testing.assert_frame_equal(expected_eq[final_properties], result_eq.to_pandas(), **PD_TESTING_SETTINGS)

    # min == max == 0
    p_series_zero = pd.Series(data=[0, 0, 0, 0], name='a')
    series_zero = DataFrame.from_pandas(engine=engine, df=p_series_zero.to_frame(), convert_objects=True).a
    result_zero = CutOperation(series=series_zero, bins=bins)._calculate_bucket_properties()
    expected_zero = pd.DataFrame(
        data={
            'a_min': [-0.001],
            'a_max': [0.001],
            'min_adjustment': [0.001],  # if min(a) == max(a) == 0: range_adjustment
            'max_adjustment': [0.001],  # if min(a) == max(a) == 0: range_adjustment
            'bin_adjustment': [0.],
            'step': [0.001],
        },
    )
    pd.testing.assert_frame_equal(expected_zero[final_properties], result_zero.to_pandas(), **PD_TESTING_SETTINGS)


def test_cut_calculate_pandas_adjustments(engine) -> None:
    pdf = pd.DataFrame(data={'min': [1], 'max': [100]})
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    to_adjust = df['min']
    to_compare = df['max']
    result = CutOperation(series=df['min'], bins=1)._calculate_pandas_adjustments(to_adjust, to_compare)
    assert isinstance(result, Series)

    result_case_sql = result.expression.to_sql(df.engine.dialect)
    max_identifier = quote_identifier(engine, 'max')
    min_idenfifier = quote_identifier(engine, 'min')
    expected_case_sql = (
        f'case when {max_identifier} = {min_idenfifier} then\n'
        f'case when {min_idenfifier} != 0 then 0.001 * abs({min_idenfifier}) else 0.001 end\n'
        'else 0 end'
    )

    assert expected_case_sql == result_case_sql


def test_cut_calculate_bucket_ranges(engine) -> None:
    bins = 3
    p_series = pd.Series(data=[1, 1, 2, 3, 4, 5, 6, 7, 8], name='a')
    series = DataFrame.from_pandas(engine=engine, df=p_series.to_frame(), convert_objects=True).a

    cut_operation = CutOperation(series=series, bins=bins)
    bucket_properties_df = cut_operation._calculate_bucket_properties()
    result = cut_operation._calculate_bucket_ranges(bucket_properties_df)
    assert_equals_data(
        result,
        order_by=['lower_bound'],
        expected_columns=['bucket', 'lower_bound', 'upper_bound', 'bounds'],
        expected_data=[
            [1, 0.993, 3.333, '(]'],
            [2, 3.333, 5.667, '(]'],
            [3, 5.667, 8, '(]'],
        ],
        round_decimals=True,
        decimal=3,
    )


def test_qcut_operation(engine) -> None:
    p_series = pd.Series(range(100), name='a')
    series = DataFrame.from_pandas(engine=engine, df=p_series.to_frame(), convert_objects=True).a

    expected_w_list = pd.qcut(p_series, q=[0.25, 0.3, 0.7, 0.9])
    result_w_list = QCutOperation(series=series, q=[0.25, 0.3, 0.7, 0.9])()
    compare_boundaries(expected_w_list, result_w_list)

    expected_q_num = pd.qcut(p_series, q=4)
    result_q_num = QCutOperation(series=series, q=4)()
    compare_boundaries(expected_q_num, result_q_num)


def test_qcut_operation_one_quantile(engine) -> None:
    p_series = pd.Series(range(10), name='a')
    series = DataFrame.from_pandas(engine=engine, df=p_series.to_frame(), convert_objects=True).a
    expected = pd.qcut(p_series, q=0)
    result = QCutOperation(series=series, q=0)()
    compare_boundaries(expected, result)

    expected2 = pd.qcut(p_series, q=[0.5])
    result2 = QCutOperation(series=series, q=[0.5])()
    compare_boundaries(expected2, result2)


def test_get_quantile_ranges(engine) -> None:
    p_series = pd.Series(data=[1, 1, 2, 3, 4, 5, 6, 7, 8], name='a')
    series = DataFrame.from_pandas(engine=engine, df=p_series.to_frame(), convert_objects=True).a

    qcut_operation = QCutOperation(series=series, q=[0.25, 0.5])
    result = qcut_operation._get_quantile_ranges()
    assert_equals_data(
        result,
        order_by=['lower_bound'],
        expected_columns=['lower_bound', 'upper_bound', 'bounds'],
        expected_data=[
            [1.999, 4., '(]'],
            [4., None, '(]'],
        ],
        round_decimals=True,
        decimal=3,
    )


def test_qcut_w_duplicated_quantiles(engine) -> None:
    p_series = pd.Series(data=[0, 1, 2, 2, 2, 2, 2], name='a')
    series = DataFrame.from_pandas(engine=engine, df=p_series.to_frame(), convert_objects=True).a

    expected = pd.qcut(p_series, q=[0.25, 0.5, 0.75], duplicates='drop')
    result = QCutOperation(series=series, q=[0.25, 0.5, 0.75])()
    compare_boundaries(expected, result.sort_index())
