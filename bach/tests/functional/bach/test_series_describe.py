from unittest.mock import ANY

import numpy as np
import pandas as pd

from bach import Series, DataFrame
from tests.functional.bach.test_data_and_utils import assert_equals_data, get_df_with_test_data


def test_categorical_describe(engine) -> None:
    series = get_df_with_test_data(engine)['city']
    result = series.describe()
    assert isinstance(result, Series)
    assert_equals_data(
        result,
        expected_columns=[
            '__stat',
            'city',
        ],
        expected_data=[
            ['count', '3'],
            ['min', 'Drylts'],
            ['max', 'Snits'],
            ['nunique', '3'],
            ['mode', ANY],
        ],
    )


def test_numerical_describe(engine) -> None:
    series = get_df_with_test_data(engine)['skating_order']
    result = series.describe(percentiles=[0.88, 0.5, 0.75])
    assert isinstance(result, Series)
    assert len(result.order_by) == 1

    expected = pd.Series(
        index=pd.Index(
            ['count', 'mean', 'std', 'min', 'max', 'nunique', 'mode', '0.5', '0.75', '0.88'],
            name='__stat'
        ),
        data=[3., 2., 1., 1., 3., 3., ANY, 2, 2.5, 2.76],
        name='skating_order',
    )
    pd.testing.assert_series_equal(expected, result.to_pandas(), check_dtype=False)


def test_describe_datetime(pg_engine) -> None:
    engine = pg_engine  # TODO: BigQuery
    p_series = pd.Series(
        data=[np.datetime64("2000-01-01"), np.datetime64("2010-01-01"), np.datetime64("2010-01-01")],
        name='dt',
    )
    df = DataFrame.from_pandas(engine=engine, df=p_series.to_frame(), convert_objects=True)

    result = df.dt.describe()

    expected = pd.Series(
        index=pd.Index(['count', 'min', 'max', 'nunique', 'mode'], name='__stat'),
        data=['3', '2000-01-01 00:00:00', '2010-01-01 00:00:00', '2', '2010-01-01 00:00:00'],
        name='dt',
    )
    pd.testing.assert_series_equal(expected, result.to_pandas())

