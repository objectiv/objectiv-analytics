import numpy as np
import pandas as pd

from bach import Series, DataFrame

from tests.functional.bach.test_data_and_utils import get_df_with_test_data, assert_equals_data


def test_categorical_describe(engine) -> None:
    series = get_df_with_test_data(engine, full_data_set=True)['municipality']
    result = series.describe()
    assert isinstance(result, Series)
    assert_equals_data(
        result,
        expected_columns=[
            '__stat',
            'municipality',
        ],
        expected_data=[
            ['count', '11'],
            ['min', 'De Friese Meren'],
            ['max', 'Waadhoeke'],
            ['nunique', '6'],
            ['mode', 'Súdwest-Fryslân'],
        ],
    )


def test_numerical_describe(engine) -> None:
    p_series = pd.Series(data=[1, 2, 3, 4, 5, 6, 7, 8, 1], name='numbers')
    series = DataFrame.from_pandas(engine=engine, df=p_series.to_frame(), convert_objects=True).numbers
    result = series.describe(percentiles=[0.88, 0.5, 0.75])

    assert isinstance(result, Series)
    assert len(result.order_by) == 1

    expected = pd.Series(
        index=pd.Index(
            ['count', 'mean', 'std', 'min', 'max', 'nunique', 'mode', '0.5', '0.75', '0.88'],
            name='__stat'
        ),
        data=[9., 4.11, 2.57, 1., 8., 8., 1., 4., 6., 7.04],
        name='numbers',
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

