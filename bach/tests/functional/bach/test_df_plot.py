"""
Copyright 2022 Objectiv B.V.
"""
from decimal import Decimal

from matplotlib.testing.decorators import check_figures_equal
from psycopg2._range import NumericRange

from sql_models.util import is_bigquery, is_postgres
from tests.functional.bach.test_data_and_utils import get_df_with_test_data, assert_equals_data


# generates and compares 2 matplotlib figures (png, pdf)
# For more information https://matplotlib.org/3.5.0/api/testing_api.html#module-matplotlib.testing

@check_figures_equal(extensions=['png', 'pdf'])
def test_plot_hist_basic(engine, fig_test, fig_ref) -> None:
    bt = get_df_with_test_data(engine, full_data_set=False)
    pbt = bt.to_pandas()

    ax_ref = fig_ref.add_subplot(111)
    ax_test = fig_test.add_subplot(111)
    pbt.plot.hist(ax=ax_ref)
    bt.plot.hist(ax=ax_test)

    result_calc_bins = bt.plot._calculate_hist_frequencies(
        bins=10, numeric_columns=['skating_order', 'inhabitants', 'founding'],
    )
    if is_postgres(engine):
        bins_1 = NumericRange(lower=Decimal('1.'),  upper=Decimal('9349.4'), bounds='[]')
        bins_2 = NumericRange(lower=Decimal('9349.4'),  upper=Decimal('18697.8'), bounds='(]')
        bins_3 = NumericRange(lower=Decimal('18697.8'),  upper=Decimal('28046.2'), bounds='(]')
        bins_4 = NumericRange(lower=Decimal('28046.2'),  upper=Decimal('37394.6'), bounds='(]')
        bins_5 = NumericRange(lower=Decimal('37394.6'),  upper=Decimal('46743.'), bounds='(]')
        bins_6 = NumericRange(lower=Decimal('46743.'),  upper=Decimal('56091.4'), bounds='(]')
        bins_7 = NumericRange(lower=Decimal('56091.4'),  upper=Decimal('65439.8'), bounds='(]')
        bins_8 = NumericRange(lower=Decimal('65439.8'),  upper=Decimal('74788.2'), bounds='(]')
        bins_9 = NumericRange(lower=Decimal('74788.2'),  upper=Decimal('84136.6'), bounds='(]')
        bins_10 = NumericRange(lower=Decimal('84136.6'),  upper=Decimal('93485.'), bounds='(]')

    elif is_bigquery(engine):
        bins_1 = {'lower': 1.,  'upper': 9349.4, 'bounds': '[]'}
        bins_2 = {'lower': 9349.4,  'upper': 18697.8, 'bounds': '(]'}
        bins_3 = {'lower': 18697.8,  'upper': 28046.199999999997, 'bounds': '(]'}
        bins_4 = {'lower': 28046.199999999997,  'upper': 37394.6, 'bounds': '(]'}
        bins_5 = {'lower': 37394.6,  'upper': 46743., 'bounds': '(]'}
        bins_6 = {'lower': 46743.,  'upper': 56091.399999999994, 'bounds': '(]'}
        bins_7 = {'lower': 56091.399999999994,  'upper': 65439.799999999996, 'bounds': '(]'}
        bins_8 = {'lower': 65439.799999999996,  'upper': 74788.2, 'bounds': '(]'}
        bins_9 = {'lower': 74788.2,  'upper': 84136.59999999999, 'bounds': '(]'}
        bins_10 = {'lower': 84136.59999999999, 'upper': 93485., 'bounds': '(]'}
    else:
        raise Exception()

    assert_equals_data(
        result_calc_bins,
        expected_columns=['column_label',  'frequency', 'range'],
        order_by=['column_label', 'range'],
        expected_data=[
            ['empty_bins', 0, bins_2],
            ['empty_bins', 0, bins_3],
            ['empty_bins', 0, bins_5],
            ['empty_bins', 0, bins_6],
            ['empty_bins', 0, bins_7],
            ['empty_bins', 0, bins_8],
            ['empty_bins', 0, bins_9],
            ['founding',   3, bins_1],
            ['inhabitants', 1, bins_1],
            ['inhabitants', 1, bins_4],
            ['inhabitants', 1, bins_10],
            ['skating_order', 3, bins_1],
        ],
    )


@check_figures_equal(extensions=['png', 'pdf'])
def test_plot_hist_bins(engine, fig_test, fig_ref) -> None:
    bt = get_df_with_test_data(engine, full_data_set=True)[['inhabitants']]
    pbt = bt.to_pandas()
    bins = 5

    ax_ref = fig_ref.add_subplot(111)
    ax_test = fig_test.add_subplot(111)
    pbt.plot.hist(bins=bins, ax=ax_ref)
    bt.plot.hist(bins=bins, ax=ax_test)

    result_calc_bins = bt.plot._calculate_hist_frequencies(
        bins=5, numeric_columns=['inhabitants'],
    )
    if is_postgres(engine):
        bins_1 = NumericRange(lower=Decimal('700.'),  upper=Decimal('19257.'), bounds='[]')
        bins_2 = NumericRange(lower=Decimal('19257.'),  upper=Decimal('37814.'), bounds='(]')
        bins_3 = NumericRange(lower=Decimal('37814.'),  upper=Decimal('56371.'), bounds='(]')
        bins_4 = NumericRange(lower=Decimal('56371.'),  upper=Decimal('74928.'), bounds='(]')
        bins_5 = NumericRange(lower=Decimal('74928.'),  upper=Decimal('93485.'), bounds='(]')
    elif is_bigquery(engine):
        bins_1 = {'lower': 700., 'upper': 19257., 'bounds': '[]'}
        bins_2 = {'lower': 19257., 'upper': 37814., 'bounds': '(]'}
        bins_3 = {'lower': 37814., 'upper': 56371., 'bounds': '(]'}
        bins_4 = {'lower': 56371., 'upper': 74928., 'bounds': '(]'}
        bins_5 = {'lower': 74928., 'upper': 93485., 'bounds': '(]'}
    else:
        raise Exception()

    assert_equals_data(
        result_calc_bins,
        expected_columns=['column_label', 'frequency', 'range'],
        order_by=['column_label', 'range'],
        expected_data=[
            ['empty_bins', 0, bins_3],
            ['empty_bins', 0, bins_4],
            ['inhabitants', 9, bins_1],
            ['inhabitants', 1, bins_2],
            ['inhabitants', 1, bins_5],
        ],
        round_decimals=True,
    )

