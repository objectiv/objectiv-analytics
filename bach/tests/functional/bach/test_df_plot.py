"""
Copyright 2022 Objectiv B.V.
"""
from decimal import Decimal

from matplotlib.testing.decorators import check_figures_equal
from psycopg2._range import NumericRange

from tests.functional.bach.test_data_and_utils import get_df_with_test_data, assert_equals_data


# generates and compares 2 matplotlib figures (png, pdf)
# For more information https://matplotlib.org/3.5.0/api/testing_api.html#module-matplotlib.testing

@check_figures_equal(extensions=['png', 'pdf'])
def test_plot_hist_basic(pg_engine, fig_test, fig_ref) -> None:
    engine = pg_engine  # TODO: BigQuery
    bt = get_df_with_test_data(engine, full_data_set=False)
    pbt = bt.to_pandas()

    ax_ref = fig_ref.add_subplot(111)
    ax_test = fig_test.add_subplot(111)
    pbt.plot.hist(ax=ax_ref)
    bt.plot.hist(ax=ax_test)

    result_calc_bins = bt.plot._calculate_hist_frequencies(
        bins=10, numeric_columns=['skating_order', 'inhabitants', 'founding'],
    )

    bin1 = NumericRange(Decimal('1'), Decimal('9349.4'), bounds='[]')
    bin2 = NumericRange(Decimal('9349.4'), Decimal('18697.8'), bounds='(]')
    bin3 = NumericRange(Decimal('18697.8'), Decimal('28046.2'), bounds='(]')
    bin4 = NumericRange(Decimal('28046.2'), Decimal('37394.6'), bounds='(]')
    bin5 = NumericRange(Decimal('37394.6'), Decimal('46743'), bounds='(]')
    bin6 = NumericRange(Decimal('46743'), Decimal('56091.4'), bounds='(]')
    bin7 = NumericRange(Decimal('56091.4'), Decimal('65439.8'), bounds='(]')
    bin8 = NumericRange(Decimal('65439.8'), Decimal('74788.2'), bounds='(]')
    bin9 = NumericRange(Decimal('74788.2'), Decimal('84136.6'), bounds='(]')
    bin10 = NumericRange(Decimal('84136.6'), Decimal('93485'), bounds='(]')

    assert_equals_data(
        result_calc_bins,
        expected_columns=['column_label', 'range', 'frequency'],
        order_by=['column_label', 'range'],
        expected_data=[
            ['empty_bins', bin2, 0],
            ['empty_bins', bin3, 0],
            ['empty_bins', bin5, 0],
            ['empty_bins', bin6, 0],
            ['empty_bins', bin7, 0],
            ['empty_bins', bin8, 0],
            ['empty_bins', bin9, 0],
            ['founding', bin1, 3],
            ['inhabitants', bin1, 1],
            ['inhabitants', bin4, 1],
            ['inhabitants', bin10, 1],
            ['skating_order', bin1, 3],
        ]
    )


@check_figures_equal(extensions=['png', 'pdf'])
def test_plot_hist_bins(pg_engine, fig_test, fig_ref) -> None:
    engine = pg_engine  # TODO: BigQuery
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

    bin1 = NumericRange(Decimal('700'), Decimal('19257'), bounds='[]')
    bin2 = NumericRange(Decimal('19257'), Decimal('37814'), bounds='(]')
    bin3 = NumericRange(Decimal('37814'), Decimal('56371'), bounds='(]')
    bin4 = NumericRange(Decimal('56371'), Decimal('74928'), bounds='(]')
    bin5 = NumericRange(Decimal('74928'), Decimal('93485'), bounds='(]')

    assert_equals_data(
        result_calc_bins,
        expected_columns=['column_label', 'range', 'frequency'],
        order_by=['column_label', 'range'],
        expected_data=[
            ['empty_bins', bin3, 0],
            ['empty_bins', bin4, 0],
            ['inhabitants', bin1, 9],
            ['inhabitants', bin2, 1],
            ['inhabitants', bin5, 1],
        ]
    )

