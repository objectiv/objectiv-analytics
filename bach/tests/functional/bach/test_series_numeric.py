import math
from decimal import Decimal

import numpy as np
import pandas as pd
import pytest
from psycopg2._range import NumericRange

from tests.functional.bach.test_data_and_utils import get_bt_with_test_data, get_from_df, assert_equals_data


def _test_simple_arithmetic(a, b):
    bt = get_bt_with_test_data(full_data_set=True)[['inhabitants']]
    expected = []
    bt['a'] = a
    bt['b'] = b
    expected.extend([a, b])
    bt['plus'] = bt.a + bt.b
    bt['min'] = bt.a - bt.b
    bt['mul'] = bt.a * bt.b
    bt['div'] = bt.a / bt.b
    bt['floordiv1'] = bt.a // bt.b
    bt['floordiv2'] = bt.a // 5.1
    bt['pow'] = bt.a ** bt.b
    bt['mod'] = bt.b % bt.a
    expected.extend([a + b, a - b, a * b, a / b, a // b, a // 5.1, a ** b, b % a])

    # result should be constant because both a and b are constant
    assert all(s.expression.is_constant for s in list(bt.data.values())[-8:])

    # result should be single because both a and b are single
    assert all(s.expression.is_constant for s in list(bt.data.values())[-8:])

    assert_equals_data(
        bt[:1],
        expected_columns=list(bt.all_series.keys()),
        expected_data=[
            [1, 93485, *expected],
        ]
    )


def test_round():
    values = [1.9, 3.0, 4.123, 6.425124, 2.00000000001, 2.1, np.nan, 7.]
    pdf = pd.DataFrame(data=values)
    bt = get_from_df('test_round', pdf)
    bt['const'] = 14.12345
    assert bt.const.expression.is_constant

    for i in 0, 3, 5, 9:
        assert bt.const.round(i).expression.is_constant
        assert not bt['0'].round(i).expression.is_constant
        np.testing.assert_equal(pdf[0].round(i).to_numpy(), bt['0'].round(i).to_numpy())
        np.testing.assert_equal(pdf[0].round(decimals=i).to_numpy(), bt['0'].round(decimals=i).to_numpy())


def test_round_integer():
    values = [1, 3, 4, 6, 2, 2, 6, 7]
    pdf = pd.DataFrame(data=values)
    bt = get_from_df('test_round', pdf)

    for i in 0, 3, 5, 9:
        result = bt['0'].round(i).sort_values().to_pandas()
        expected = pdf[0].round(i).sort_values()
        pd.testing.assert_series_equal(expected, result, check_names=False, check_index=False)

        result2 = bt['0'].round(decimals=i).sort_values().to_pandas()
        expected2 = pdf[0].round(decimals=i).sort_values()
        pd.testing.assert_series_equal(expected2, result2, check_names=False, check_index=False)


def test_dataframe_agg_skipna_parameter():
    # test full parameter traversal
    bt = get_bt_with_test_data(full_data_set=True)[['inhabitants']]

    numeric_agg = ['sum', 'mean']
    stats_agg = ['sem', 'std', 'var']
    for agg in numeric_agg + stats_agg:
        with pytest.raises(NotImplementedError):
            # currently not supported anywhere, so needs to raise
            bt.agg(agg, skipna=False)

    numeric_agg = ['prod', 'product']
    stats_agg = ['kurt', 'kurtosis', 'skew', 'mad']
    for agg in numeric_agg + stats_agg:
        with pytest.raises(AttributeError):
            # methods not present at all, so needs to raise
            bt.agg(agg, skipna=False)


def test_dataframe_agg_dd_parameter():
    # test full parameter traversal
    bt = get_bt_with_test_data(full_data_set=True)[['inhabitants']]

    for agg in ['sem', 'std', 'var']:
        with pytest.raises(NotImplementedError):
            # currently not supported anywhere, so needs to raise
            bt.agg(agg, ddof=123)


def test_aggregations_simple_tests():
    values = [1, 3, 4, 6, 2, 2, np.nan, 7, 8]
    pdf = pd.DataFrame(data=values)
    bt = get_from_df('test_aggregations_simple_tests', pdf)

    numeric_agg = ['sum', 'mean']
    stats_agg = ['sem', 'std', 'var']
    for agg in numeric_agg + stats_agg:
        pd_agg = pdf[0].agg(agg)
        bt_agg = bt['0'].agg(agg)
        assert bt_agg.expression.has_aggregate_function
        assert not bt_agg.expression.is_constant
        assert bt_agg.expression.is_single_value
        assert pd_agg == bt_agg.value


def test_aggregations_sum_mincount():
    pdf = pd.DataFrame(data=[1, np.nan, 7, 8])
    bt = get_from_df('test_aggregations_sum_mincount', pdf)

    for i in [5, 4, 3]:
        pd_agg = pdf.sum(min_count=i)[0]
        bt_agg = bt.sum(min_count=i)['0_sum']

        # since sum is wrapped in a CASE WHEN, we need to make sure that these are still valid:
        assert bt_agg.expression.has_aggregate_function
        assert not bt_agg.expression.is_constant
        assert bt_agg.expression.is_single_value

        bt_agg_value = bt_agg.value

        # We have different nan handling: nan vs None
        assert (math.isnan(pd_agg) and bt_agg_value is None) or bt_agg_value == pd_agg


def test_aggregations_quantile():
    pdf = pd.DataFrame(data={'a': range(5), 'b': [1, 3, 5, 7, 9]})
    bt = get_from_df('test_aggregations_quantile', pdf)

    quantiles = [0.25, 0.3, 0.5, 0.75, 0.86]

    for column, quantile in zip(pdf.columns, quantiles):
        expected = pdf[column].quantile(q=quantile)
        result = bt[column].quantile(q=quantile).to_numpy()[0]
        assert expected == result

    for column in pdf.columns:
        expected_all_quantiles = pdf[column].quantile(q=quantiles)
        result_all_quantiles = bt[column].quantile(q=quantiles).sort_index()
        pd.testing.assert_series_equal(expected_all_quantiles, result_all_quantiles.to_pandas(), check_names=False)


def test_series_cut() -> None:
    bins = 4
    inhabitants = get_bt_with_test_data(full_data_set=True)['inhabitants']

    # right == true
    result_right = inhabitants.cut(bins=bins).sort_index()
    bounds_right = '(]'
    bin1_right = NumericRange(Decimal('607.215'),  Decimal('23896.25'), bounds=bounds_right)
    bin2_right = NumericRange(Decimal('23896.25'),  Decimal('47092.5'), bounds=bounds_right)
    bin4_right = NumericRange(Decimal('70288.75'), Decimal('93485'), bounds=bounds_right)
    assert_equals_data(
        result_right,
        expected_columns=['inhabitants', 'range'],
        expected_data=[
            [700, bin1_right],
            [870, bin1_right],
            [960, bin1_right],
            [3055, bin1_right],
            [4440, bin1_right],
            [10120, bin1_right],
            [12675, bin1_right],
            [12760, bin1_right],
            [14740, bin1_right],
            [33520, bin2_right],
            [93485, bin4_right],
        ],
    )

    # right == false
    result_not_right = inhabitants.cut(bins=bins, right=False).sort_index()
    bounds_not_right = '[)'
    bin1_not_right = NumericRange(Decimal('700'),  Decimal('23896.25'), bounds=bounds_not_right)
    bin2_not_right = NumericRange(Decimal('23896.25'),  Decimal('47092.5'), bounds=bounds_not_right)
    bin4_not_right = NumericRange(Decimal('70288.75'), Decimal('93577.785'), bounds=bounds_not_right)
    assert_equals_data(
        result_not_right,
        expected_columns=['inhabitants', 'range'],
        expected_data=[
            [700, bin1_not_right],
            [870, bin1_not_right],
            [960, bin1_not_right],
            [3055, bin1_not_right],
            [4440, bin1_not_right],
            [10120, bin1_not_right],
            [12675, bin1_not_right],
            [12760, bin1_not_right],
            [14740, bin1_not_right],
            [33520, bin2_not_right],
            [93485, bin4_not_right],
        ],
    )

    inhabitants_pdf = inhabitants.to_pandas()

    to_assert = [
        (pd.cut(inhabitants_pdf, bins=bins).sort_values(), result_right),
        (pd.cut(inhabitants_pdf, bins=bins, right=False).sort_values(), result_not_right),
    ]
    for expected_pdf, result in to_assert:
        for exp, res in zip(expected_pdf.to_numpy(), result.to_numpy()):
            np.testing.assert_almost_equal(exp.left, float(res.lower), decimal=2)
            np.testing.assert_almost_equal(exp.right, float(res.upper), decimal=2)


def test_series_qcut() -> None:
    bounds = '(]'
    inhabitants = get_bt_with_test_data(full_data_set=True)['inhabitants']

    result = inhabitants.qcut(q=4).sort_index()
    bin1 = NumericRange(Decimal('699.999'),  Decimal('2007.5'), bounds=bounds)
    bin2 = NumericRange(Decimal('2007.5'),  Decimal('10120'), bounds=bounds)
    bin3 = NumericRange(Decimal('10120'),  Decimal('13750'), bounds=bounds)
    bin4 = NumericRange(Decimal('13750'), Decimal('93485'), bounds=bounds)
    assert_equals_data(
        result,
        expected_columns=['inhabitants', 'q_range'],
        expected_data=[
            [700, bin1],
            [870, bin1],
            [960, bin1],
            [3055, bin2],
            [4440, bin2],
            [10120, bin2],
            [12675, bin3],
            [12760, bin3],
            [14740, bin4],
            [33520, bin4],
            [93485, bin4],
        ],
    )

    result2 = inhabitants.qcut(q=[0.25, 0.5]).sort_index()
    bin2 = NumericRange(Decimal('2007.499'),  Decimal('10120'), bounds=bounds)
    assert_equals_data(
        result2,
        expected_columns=['inhabitants', 'q_range'],
        expected_data=[
            [700, None],
            [870, None],
            [960, None],
            [3055, bin2],
            [4440, bin2],
            [10120, bin2],
            [12675, None],
            [12760, None],
            [14740, None],
            [33520, None],
            [93485, None],
        ],
    )

    inhabitants_pdf = inhabitants.to_pandas().sort_values()
    to_assert = [
        (pd.qcut(inhabitants_pdf, q=4), result),
        (pd.qcut(inhabitants_pdf, q=[0.25, 0.5]), result2),
    ]
    for expected_pdf, result in to_assert:
        for exp, res in zip(expected_pdf.to_numpy(), result.to_numpy()):
            if not isinstance(exp, pd.Interval):
                assert res is None
                continue
            np.testing.assert_almost_equal(exp.left, float(res.lower), decimal=2)
            np.testing.assert_almost_equal(exp.right, float(res.upper), decimal=2)
