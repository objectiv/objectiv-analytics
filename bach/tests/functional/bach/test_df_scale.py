from sklearn.preprocessing import StandardScaler, MinMaxScaler

from tests.functional.bach.test_data_and_utils import (
    get_df_with_test_data, assert_equals_data, \
    get_bt_with_test_data, TEST_DATA_CITIES_FULL, CITIES_COLUMNS
)
import numpy as np

from tests.unit.bach.util import get_pandas_df


def test_standard_scale(engine) -> None:
    numerical_cols = ['skating_order', 'inhabitants', 'founding']
    all_cols = ['city'] + numerical_cols
    bt = get_df_with_test_data(engine, full_data_set=True)[all_cols]
    pdf = get_pandas_df(TEST_DATA_CITIES_FULL, CITIES_COLUMNS)

    so_values = pdf.skating_order.to_numpy()
    so_avg = np.mean(so_values)
    so_std = np.var(so_values)
    so_scale = so_std ** 0.5

    inhbt_values = pdf.inhabitants.to_numpy()
    inhbt_avg = np.mean(inhbt_values)
    inhbt_std = np.var(inhbt_values)
    inhbt_scale = inhbt_std ** 0.5

    fnd_values = pdf.founding.to_numpy()
    fnd_avg = np.mean(fnd_values)
    fnd_std = np.var(fnd_values)
    fnd_scale = fnd_std ** 0.5

    result_w_mean_std = bt.scale()

    expected_data_w_mean_std = [
        [1, 'Ljouwert', (1 - so_avg) / so_scale, (93485 - inhbt_avg) / inhbt_scale, (1285 - fnd_avg) / fnd_scale],
        [2, 'Snits', (2 - so_avg) / so_scale, (33520 - inhbt_avg) / inhbt_scale, (1456 - fnd_avg) / fnd_scale],
        [3, 'Drylts', (3 - so_avg) / so_scale, (3055 - inhbt_avg) / inhbt_scale, (1268 - fnd_avg) / fnd_scale],
        [4, 'Sleat', (4 - so_avg) / so_scale, (700 - inhbt_avg) / inhbt_scale, (1426 - fnd_avg) / fnd_scale],
        [5, 'Starum', (5 - so_avg) / so_scale, (960 - inhbt_avg) / inhbt_scale, (1061 - fnd_avg) / fnd_scale],
        [6, 'Hylpen', (6 - so_avg) / so_scale, (870 - inhbt_avg) / inhbt_scale, (1225 - fnd_avg) / fnd_scale],
        [7, 'Warkum', (7 - so_avg) / so_scale, (4440 - inhbt_avg) / inhbt_scale, (1399 - fnd_avg) / fnd_scale],
        [8, 'Boalsert', (8 - so_avg) / so_scale, (10120 - inhbt_avg) / inhbt_scale, (1455 - fnd_avg) / fnd_scale],
        [9, 'Harns', (9 - so_avg) / so_scale, (14740 - inhbt_avg) / inhbt_scale, (1234 - fnd_avg) / fnd_scale],
        [10, 'Frjentsjer', (10 - so_avg) / so_scale, (12760 - inhbt_avg) / inhbt_scale, (1374 - fnd_avg) / fnd_scale],
        [11, 'Dokkum', (11 - so_avg) / so_scale, (12675 - inhbt_avg) / inhbt_scale, (1298 - fnd_avg) / fnd_scale],
    ]
    result_w_mean_std_db = assert_equals_data(
        result_w_mean_std,
        expected_columns=['_index_skating_order', 'city', 'skating_order', 'inhabitants', 'founding'],
        expected_data=expected_data_w_mean_std,
        round_decimals=True,
    )
    expected_w_mean_std = StandardScaler(with_mean=True, with_std=True).fit_transform(pdf[numerical_cols])
    np.testing.assert_almost_equal(
        expected_w_mean_std,
        (np.array(result_w_mean_std_db)[:, 2:]).astype(float),
        decimal=4,
    )

    result_w_std = bt.scale(with_mean=False, with_std=True)
    expected_data_w_std = [
        [1, 'Ljouwert', 1 / so_scale, 93485 / inhbt_scale, 1285 / fnd_scale],
        [2, 'Snits', 2 / so_scale, 33520 / inhbt_scale, 1456 / fnd_scale],
        [3, 'Drylts', 3 / so_scale, 3055 / inhbt_scale, 1268 / fnd_scale],
        [4, 'Sleat', 4 / so_scale, 700 / inhbt_scale, 1426 / fnd_scale],
        [5, 'Starum', 5 / so_scale, 960 / inhbt_scale, 1061 / fnd_scale],
        [6, 'Hylpen', 6 / so_scale, 870 / inhbt_scale, 1225 / fnd_scale],
        [7, 'Warkum', 7 / so_scale, 4440 / inhbt_scale, 1399 / fnd_scale],
        [8, 'Boalsert', 8 / so_scale, 10120 / inhbt_scale, 1455 / fnd_scale],
        [9, 'Harns', 9 / so_scale, 14740 / inhbt_scale, 1234 / fnd_scale],
        [10, 'Frjentsjer', 10 / so_scale, 12760 / inhbt_scale, 1374 / fnd_scale],
        [11, 'Dokkum', 11 / so_scale, 12675 / inhbt_scale, 1298 / fnd_scale],
    ]
    expected_w_std = StandardScaler(with_mean=False, with_std=True).fit_transform(pdf[numerical_cols])
    result_w_std_db = assert_equals_data(
        result_w_std,
        expected_columns=['_index_skating_order', 'city', 'skating_order', 'inhabitants', 'founding'],
        expected_data=expected_data_w_std,
        round_decimals=True,
    )
    np.testing.assert_almost_equal(
        expected_w_std,
        (np.array(result_w_std_db)[:, 2:]).astype(float),
        decimal=4,
    )

    result_w_mean = bt.scale(with_mean=True, with_std=False)

    expected_data_w_mean = [
        [1, 'Ljouwert', 1 - so_avg, 93485 - inhbt_avg, 1285 - fnd_avg],
        [2, 'Snits', 2 - so_avg, 33520 - inhbt_avg, 1456 - fnd_avg],
        [3, 'Drylts', 3 - so_avg, 3055 - inhbt_avg, 1268 - fnd_avg],
        [4, 'Sleat', 4 - so_avg, 700 - inhbt_avg, 1426 - fnd_avg],
        [5, 'Starum', 5 - so_avg, 960 - inhbt_avg, 1061 - fnd_avg],
        [6, 'Hylpen', 6 - so_avg, 870 - inhbt_avg, 1225 - fnd_avg],
        [7, 'Warkum', 7 - so_avg, 4440 - inhbt_avg, 1399 - fnd_avg],
        [8, 'Boalsert', 8 - so_avg, 10120 - inhbt_avg, 1455 - fnd_avg],
        [9, 'Harns', 9 - so_avg, 14740 - inhbt_avg, 1234 - fnd_avg],
        [10, 'Frjentsjer', 10 - so_avg, 12760 - inhbt_avg, 1374 - fnd_avg],
        [11, 'Dokkum', 11 - so_avg, 12675 - inhbt_avg, 1298 - fnd_avg],
    ]
    result_w_mean_db = assert_equals_data(
        result_w_mean,
        expected_columns=['_index_skating_order', 'city', 'skating_order', 'inhabitants', 'founding'],
        expected_data=expected_data_w_mean,
        round_decimals=True,
    )

    expected_w_mean = StandardScaler(with_mean=True, with_std=False).fit_transform(pdf[numerical_cols])
    np.testing.assert_almost_equal(
        expected_w_mean,
        (np.array(result_w_mean_db)[:, 2:]).astype(float),
        decimal=4,
    )


def test_min_max_scale() -> None:
    numerical_cols = ['skating_order', 'inhabitants', 'founding']
    all_cols = ['city'] + numerical_cols
    pdf = get_pandas_df(TEST_DATA_CITIES_FULL, CITIES_COLUMNS)
    bt = get_bt_with_test_data(full_data_set=True)[all_cols]
    # bt = bt.sort_index()  # TODO: This breaks later on, it shouldn't.
                            #  Required to make this test deterministicly pass/fail

    min_so = 1
    max_so = 11
    diff_so = max_so - min_so

    min_inh = 700
    max_inh = 93485
    diff_inh = max_inh - min_inh

    min_fnd = 1061
    max_fnd = 1456
    diff_fnd = max_fnd - min_fnd

    expected_default = MinMaxScaler().fit_transform(pdf[numerical_cols])
    result_default = bt.minmax_scale().sort_index()

    np.testing.assert_almost_equal(expected_default, result_default[numerical_cols].to_numpy(), decimal=4)

    expected_data_default = [
        [1, 'Ljouwert', (1 - min_so) / diff_so, (93485 - min_inh) / diff_inh, (1285 - min_fnd) / diff_fnd],
        [2, 'Snits', (2 - min_so) / diff_so, (33520 - min_inh) / diff_inh, (1456 - min_fnd) / diff_fnd],
        [3, 'Drylts', (3 - min_so) / diff_so, (3055 - min_inh) / diff_inh, (1268 - min_fnd) / diff_fnd],
        [4, 'Sleat', (4 - min_so) / diff_so, (700 - min_inh) / diff_inh, (1426 - min_fnd) / diff_fnd],
        [5, 'Starum', (5 - min_so) / diff_so, (960 - min_inh) / diff_inh, (1061 - min_fnd) / diff_fnd],
        [6, 'Hylpen', (6 - min_so) / diff_so, (870 - min_inh) / diff_inh, (1225 - min_fnd) / diff_fnd],
        [7, 'Warkum', (7 - min_so) / diff_so, (4440 - min_inh) / diff_inh, (1399 - min_fnd) / diff_fnd],
        [8, 'Boalsert', (8 - min_so) / diff_so, (10120 - min_inh) / diff_inh, (1455 - min_fnd) / diff_fnd],
        [9, 'Harns', (9 - min_so) / diff_so, (14740 - min_inh) / diff_inh, (1234 - min_fnd) / diff_fnd],
        [10, 'Frjentsjer', (10 - min_so) / diff_so, (12760 - min_inh) / diff_inh, (1374 - min_fnd) / diff_fnd],
        [11, 'Dokkum', (11 - min_so) / diff_so, (12675 - min_inh) / diff_inh, (1298 - min_fnd) / diff_fnd],
    ]
    assert_equals_data(
        result_default,
        expected_columns=['_index_skating_order', 'city', 'skating_order', 'inhabitants', 'founding'],
        expected_data=expected_data_default,
        round_decimals=True,
    )

    expected_w_fr = MinMaxScaler(feature_range=(2, 4)).fit_transform(pdf[numerical_cols])
    result_w_fr = bt.minmax_scale(feature_range=(2, 4)).sort_index()
    np.testing.assert_almost_equal(expected_w_fr, result_w_fr[numerical_cols].to_numpy(), decimal=4)

    expected_data_fr = []
    for row in expected_data_default:
        expected_data_fr.append([val if idx < 2 else val * 2 + 2 for idx, val in enumerate(row)])

    assert_equals_data(
        result_w_fr,
        expected_columns=['_index_skating_order', 'city', 'skating_order', 'inhabitants', 'founding'],
        expected_data=expected_data_fr,
        round_decimals=True,
    )

