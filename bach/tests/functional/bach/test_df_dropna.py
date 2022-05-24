import pandas as pd
import numpy as np

from bach import DataFrame

DATA = {
    "name": ['Alfred', 'Batman', 'Catwoman'],
    "toy": [np.nan, 'Batmobile', 'Bullwhip'],
    "born": [pd.NaT, pd.Timestamp("1940-04-25"), pd.NaT]
}


def test_dropna_w_nan(engine) -> None:
    pdf = pd.DataFrame(
        {
            'a': ['a', 'b', None, 'a', 'b', None],
            'b': [np.nan, np.nan, np.nan, 1, 2, 3],
        },
    )
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)

    expected = pdf.dropna()
    result = df.dropna()
    pd.testing.assert_frame_equal(
        expected,
        result.sort_index().to_pandas(),
        check_names=False,
        check_index_type=False,
    )

    expected_w_thresh = pdf.dropna(thresh=2)
    result_w_thresh = df.dropna(thresh=2)
    pd.testing.assert_frame_equal(
        expected_w_thresh,
        result_w_thresh.sort_index().to_pandas(),
        check_names=False,
    )


def test_basic_dropna(engine) -> None:
    pdf = pd.DataFrame(DATA)

    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    result = df.dropna()
    pd.testing.assert_frame_equal(
        pdf.dropna(),
        result.to_pandas(),
        check_names=False,
    )


def test_dropna_all(engine) -> None:
    pdf = pd.DataFrame(DATA)

    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    result = df.dropna(how='all')
    pd.testing.assert_frame_equal(
        pdf.dropna(how='all'),
        result.to_pandas(),
        check_names=False,
    )


def test_dropna_thresh(engine) -> None:
    pdf = pd.DataFrame(DATA)

    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    result = df.dropna(thresh=2)
    pd.testing.assert_frame_equal(
        pdf.dropna(thresh=2),
        result.to_pandas(),
        check_names=False,
    )
