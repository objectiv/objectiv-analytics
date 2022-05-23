import pandas as pd
import pytest

from bach import DataFrame
from bach.series.series_multi_level import SeriesNumericInterval


@pytest.fixture()
def interval_data_pdf() -> pd.DataFrame:
    pdf = pd.DataFrame(
        {
            'lower': [0., 0., 3., 5., 1., 2., 3., 4., 5.],
            'upper': [1., 1., 4., 6., 2., 3., 4., 5., 6.],
            'a': [10, 15, 20, 25, 30, 35, 40, 45, 50],
        },
    )
    pdf['bounds'] = '(]'

    return pdf


def test_series_numeric_interval_to_pandas(engine, interval_data_pdf: pd.DataFrame) -> None:
    df = DataFrame.from_pandas(engine=engine, df=interval_data_pdf, convert_objects=True)
    df['range'] = SeriesNumericInterval.from_value(
        base=df,
        name='num_interval',
        value={
            'lower': df['lower'],
            'upper': df['upper'],
            'bounds': df['bounds'],
        }
    )

    expected = pd.DataFrame(
        {
            '_index_0': [0, 1, 2, 3, 4, 5, 6, 7, 8],
            'range': [
                pd.Interval(left=0., right=1., closed='right'),
                pd.Interval(left=0., right=1., closed='right'),
                pd.Interval(left=3., right=4., closed='right'),
                pd.Interval(left=5., right=6., closed='right'),
                pd.Interval(left=1., right=2., closed='right'),
                pd.Interval(left=2., right=3., closed='right'),
                pd.Interval(left=3., right=4., closed='right'),
                pd.Interval(left=4., right=5., closed='right'),
                pd.Interval(left=5., right=6., closed='right'),
            ]
        }
    ).set_index('_index_0')['range']
    result = df['range'].sort_index().to_pandas()
    pd.testing.assert_series_equal(expected, result)


def test_series_numeric_interval_sort_values(engine, interval_data_pdf: pd.DataFrame) -> None:
    df = DataFrame.from_pandas(engine=engine, df=interval_data_pdf, convert_objects=True)
    df['range'] = SeriesNumericInterval.from_value(
        base=df,
        name='num_interval',
        value={
            'lower': df['lower'],
            'upper': df['upper'],
            'bounds': df['bounds'],
        },
    )

    expected = pd.DataFrame(
        {
            'range': [
                pd.Interval(left=0., right=1., closed='right'),
                pd.Interval(left=0., right=1., closed='right'),
                pd.Interval(left=1., right=2., closed='right'),
                pd.Interval(left=2., right=3., closed='right'),
                pd.Interval(left=3., right=4., closed='right'),
                pd.Interval(left=3., right=4., closed='right'),
                pd.Interval(left=4., right=5., closed='right'),
                pd.Interval(left=5., right=6., closed='right'),
                pd.Interval(left=5., right=6., closed='right'),
            ],
        }
    )['range']
    result = df.reset_index()['range'].sort_values().to_pandas()
    pd.testing.assert_series_equal(expected, result, check_index=False, check_index_type=False)


def test_series_numeric_interval_append(engine, interval_data_pdf: pd.DataFrame) -> None:
    interval_data_pdf[['lower', 'upper']] = interval_data_pdf[['lower', 'upper']] .astype(int)
    df = DataFrame.from_pandas(engine=engine, df=interval_data_pdf, convert_objects=True)
    df['range_1'] = SeriesNumericInterval.from_value(
        base=df,
        name='range_1',
        value={
            'lower': df['lower'],
            'upper': df['upper'],
            'bounds': df['bounds'],
        },
    )
    df['range_2'] = SeriesNumericInterval.from_value(
        base=df,
        name='range_2',
        value={
            'lower': df['lower'] + 1,
            'upper': df['upper'] + 2,
            'bounds': df['bounds'],
        },
    )

    expected = pd.DataFrame(
        {
            '_index_0': [0, 4, 0, 5, 4, 2, 5, 7, 2, 3, 7, 3],
            'range_1': [
                pd.Interval(left=0., right=1., closed='right'),
                pd.Interval(left=1., right=2., closed='right'),
                pd.Interval(left=1., right=3., closed='right'),
                pd.Interval(left=2., right=3., closed='right'),
                pd.Interval(left=2., right=4., closed='right'),
                pd.Interval(left=3., right=4., closed='right'),
                pd.Interval(left=3., right=5., closed='right'),
                pd.Interval(left=4., right=5., closed='right'),
                pd.Interval(left=4., right=6., closed='right'),
                pd.Interval(left=5., right=6., closed='right'),
                pd.Interval(left=5., right=7., closed='right'),
                pd.Interval(left=6., right=8., closed='right'),
            ],
        }
    ).set_index('_index_0')['range_1']

    result = df['range_1'].append(df['range_2'])
    result = result.drop_duplicates().sort_values()
    pd.testing.assert_series_equal(expected, result.to_pandas())


def test_series_numeric_interval_dropna(engine, interval_data_pdf: pd.DataFrame) -> None:
    interval_data_pdf.loc[2, ['upper', 'lower', 'bounds']] = None
    df = DataFrame.from_pandas(engine=engine, df=interval_data_pdf, convert_objects=True)
    range = SeriesNumericInterval.from_value(
        base=df,
        name='range',
        value={
            'lower': df['lower'],
            'upper': df['upper'],
            'bounds': df['bounds'],
        },
    )

    expected = pd.DataFrame(
        {
            '_index_0': [0, 1, 3, 4, 5, 6, 7, 8],
            'range': [
                pd.Interval(left=0., right=1., closed='right'),
                pd.Interval(left=0., right=1., closed='right'),
                pd.Interval(left=5., right=6., closed='right'),
                pd.Interval(left=1., right=2., closed='right'),
                pd.Interval(left=2., right=3., closed='right'),
                pd.Interval(left=3., right=4., closed='right'),
                pd.Interval(left=4., right=5., closed='right'),
                pd.Interval(left=5., right=6., closed='right'),
            ]
        }
    ).set_index('_index_0')['range']
    result = range.dropna().sort_index().to_pandas()
    pd.testing.assert_series_equal(expected, result)


def test_series_numeric_value_counts(engine, interval_data_pdf: pd.DataFrame) -> None:
    df = DataFrame.from_pandas(engine=engine, df=interval_data_pdf, convert_objects=True)
    range = SeriesNumericInterval.from_value(
        base=df,
        name='range',
        value={
            'lower': df['lower'],
            'upper': df['upper'],
            'bounds': df['bounds'],
        },
    )

    expected = pd.DataFrame(
        {
            'value_counts': [2, 1, 1, 2, 1, 2],
            'range': [
                pd.Interval(left=0., right=1., closed='right'),
                pd.Interval(left=1., right=2., closed='right'),
                pd.Interval(left=2., right=3., closed='right'),
                pd.Interval(left=3., right=4., closed='right'),
                pd.Interval(left=4., right=5., closed='right'),
                pd.Interval(left=5., right=6., closed='right'),
            ]
        }
    ).set_index('range')['value_counts']
    result = range.value_counts().sort_index().to_pandas()

    pd.testing.assert_series_equal(expected, result)
