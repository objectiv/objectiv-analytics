import numpy as np
import pandas as pd

from bach import Series, DataFrame
from tests.functional.bach.test_data_and_utils import get_bt_with_test_data, assert_equals_data


def test_categorical_describe() -> None:
    series = get_bt_with_test_data()['city']
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
            ['max', 'Snits'],
            ['min', 'Drylts'],
            ['mode', 'Drylts'],
            ['nunique', '3'],
        ],
    )


def test_numerical_describe() -> None:
    series = get_bt_with_test_data()['skating_order']
    result = series.describe(percentiles=[0.5])
    assert isinstance(result, Series)

    expected = pd.Series(
        index=pd.Index(['count', 'mean', 'std', 'min', 'max', 'nunique', 'mode', '0.5'], name='__stat'),
        data=[3., 2., 1., 1., 3., 3., 1., 2.],
        name='skating_order',
    )
    pd.testing.assert_series_equal(expected, result.to_pandas())


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

