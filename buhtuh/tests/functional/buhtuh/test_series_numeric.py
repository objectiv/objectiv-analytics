import numpy as np
import pandas as pd
import pytest

from tests.functional.buhtuh.test_data_and_utils import get_bt_with_test_data, get_from_df


def test_round():
    values = [ 1.9, 3.0, 4.123, 6.425124, 2.00000000001, 2.1, np.nan, 7.]
    pdf = pd.DataFrame(data=values)
    bt = get_from_df('test_round', pdf)
    for i in 0, 3, 5, 9:
        np.testing.assert_equal(pdf[0].round(i).values, bt['0'].round(i).head(10).values)
        np.testing.assert_equal(pdf[0].round(decimals=i).values, bt['0'].round(decimals=i).head(10).values)



def test_dataframe_agg_skipna_parameter():
    # test full parameter traversal
    bt = get_bt_with_test_data(full_data_set=True)[['inhabitants']]

    numeric_agg = ['prod', 'product', 'sum', 'mean']
    stats_agg = ['kurt', 'kurtosis', 'mad', 'skew', 'sem', 'std', 'var']
    for agg in numeric_agg + stats_agg:
        with pytest.raises(NotImplementedError):
            # currently not supported anywhere, so needs to raise
            bt.agg(agg, skipna=False)


def test_dataframe_agg_dd_parameter():
    # test full parameter traversal
    bt = get_bt_with_test_data(full_data_set=True)[['inhabitants']]

    for agg in ['sem', 'std', 'var']:
        with pytest.raises(NotImplementedError):
            # currently not supported anywhere, so needs to raise
            bt.agg(agg, ddof=123)


def test_aggregations_simple_tests():
    values = [ 1, 3, 4, 6, 2, 2, np.nan, 7, 8]
    pdf = pd.DataFrame(data=values)
    bt = get_from_df('test_aggregations_simple_tests', pdf)

    numeric_agg = ['prod', 'product', 'sum', 'mean']
    stats_agg = ['sem', 'std', 'var']
    for agg in numeric_agg + stats_agg:
        pdagg = pdf.agg(agg)[0]
        btagg = bt.agg(agg).head().iloc[0, 0]
        if agg.startswith('prod'):
            # round this, because our HORRIBLE prod implementation
            assert round(pdagg,7) == round(btagg,7)
        else:
            assert pdagg == btagg


def test_aggregations_sum_mincount():
    values = [ 1, np.nan, 7, 8]
    pdf = pd.DataFrame(data=values)
    bt = get_from_df('test_aggregations_sum_mincount', pdf)

    for i in [5,4,3]:
        pdagg = pdf.sum(min_count=i)[0]
        btagg = bt.sum(min_count=i).head().fillna(np.nan).iloc[0, 0]
        np.testing.assert_equal(pdagg, btagg)