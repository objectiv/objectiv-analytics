import numpy as np
from decimal import Decimal

import pytest
from psycopg2._range import NumericRange

from sql_models.util import is_postgres, is_bigquery
from tests.functional.bach.test_data_and_utils import assert_equals_data, \
    get_df_with_railway_data, get_df_with_test_data


def test_value_counts_basic(engine):
    bt = get_df_with_test_data(engine)['municipality']
    result = bt.value_counts()

    np.testing.assert_equal(
        bt.to_pandas().value_counts().to_numpy(),
        result.to_numpy(),
    )

    assert_equals_data(
        result.to_frame(),
        expected_columns=['municipality', 'value_counts'],
        expected_data=[
            ['Súdwest-Fryslân', 2],
            ['Leeuwarden', 1]
        ],
    )

    result_normalized = bt.value_counts(normalize=True)
    np.testing.assert_almost_equal(
        bt.to_pandas().value_counts(normalize=True).to_numpy(),
        result_normalized.to_numpy(),
        decimal=2,
    )
    assert_equals_data(
        result_normalized.to_frame(),
        expected_columns=['municipality', 'value_counts'],
        expected_data=[
            ['Súdwest-Fryslân', 2 / 3],
            ['Leeuwarden', 1 / 3]
        ],
    )


def test_value_counts_w_bins(engine) -> None:
    bins = 4
    inhabitants = get_df_with_test_data(engine, full_data_set=True)['inhabitants']
    result = inhabitants.value_counts(bins=bins)
    np.testing.assert_equal(
        inhabitants.to_pandas().value_counts(bins=bins).to_numpy(),
        result.to_numpy(),
    )
    bounds_right = '(]'
    if is_postgres(engine):
        bin1 = NumericRange(Decimal('607.215'),  Decimal('23896.25'), bounds=bounds_right)
        bin2 = NumericRange(Decimal('23896.25'),  Decimal('47092.5'), bounds=bounds_right)
        bin3 = NumericRange(Decimal('47092.5'),  Decimal('70288.75'), bounds=bounds_right)
        bin4 = NumericRange(Decimal('70288.75'), Decimal('93485'), bounds=bounds_right)
    elif is_bigquery(engine):
        bin1 = {'lower': 607.215, 'upper': 23896.25, 'bounds': bounds_right}
        bin2 = {'lower': 23896.25, 'upper': 47092.5, 'bounds': bounds_right}
        bin3 = {'lower': 47092.5, 'upper': 70288.75, 'bounds': bounds_right}
        bin4 = {'lower': 70288.75, 'upper': 93485, 'bounds': bounds_right}
    else:
        raise Exception()

    assert_equals_data(
        result.sort_index(),
        expected_columns=['range', 'value_counts'],
        expected_data=[
            [bin1, 9],
            [bin2, 1],
            [bin3, 0],
            [bin4, 1],
        ],
    )

    if is_postgres(engine):
        bin1_bach = NumericRange(Decimal('700'), Decimal('23896.25'), bounds='[]')
    elif is_bigquery(engine):
        bin1_bach = {'lower': 700, 'upper': 23896.25, 'bounds': '[]'}
    else:
        raise Exception()
    result_w_bach_method = inhabitants.value_counts(bins=bins, method='bach')
    assert_equals_data(
        result_w_bach_method.sort_index(),
        expected_columns=['range', 'value_counts'],
        expected_data=[
            [bin1_bach, 9],
            [bin2, 1],
            [bin3, 0],
            [bin4, 1],
        ],
    )


def test_value_counts_w_groupby(engine) -> None:
    bt = get_df_with_railway_data(engine)[['town', 'platforms', 'station_id']].reset_index(drop=True)
    result = bt.groupby(['town', 'platforms'])['station_id'].value_counts()
    assert_equals_data(
        result.to_frame().sort_index(),
        expected_columns=['town', 'platforms', 'station_id', 'value_counts'],
        expected_data=[
            ['Drylts', 1, 1, 1],
            ['It Hearrenfean', 1, 2, 1],
            ['It Hearrenfean', 2, 3, 1],
            ['Ljouwert', 1, 5, 1],
            ['Ljouwert', 4, 4, 1],
            ['Snits', 2, 6, 1],
            ['Snits', 2, 7, 1],
        ],
    )

    result_normalized = bt.groupby(['town', 'platforms'])['station_id'].value_counts(normalize=True)
    assert_equals_data(
        result_normalized.to_frame().sort_index(),
        expected_columns=['town', 'platforms', 'station_id', 'value_counts'],
        expected_data=[
            ['Drylts', 1, 1, 1 / 7],
            ['It Hearrenfean', 1, 2, 1 / 7],
            ['It Hearrenfean', 2, 3, 1 / 7],
            ['Ljouwert', 1, 5, 1 / 7],
            ['Ljouwert', 4, 4, 1 / 7],
            ['Snits', 2, 6, 1 / 7],
            ['Snits', 2, 7, 1 / 7],
        ],
    )


def test_bins_error(engine) -> None:
    with pytest.raises(ValueError, match='Cannot calculate bins for non numeric series.'):
        get_df_with_railway_data(engine)['town'].value_counts(bins=4)


def test_method_error(engine) -> None:
    with pytest.raises(ValueError, match=r'"whatever" is not a valid method'):
        get_df_with_railway_data(engine)['platforms'].value_counts(bins=4, method='whatever')
