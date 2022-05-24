"""
Copyright 2022 Objectiv B.V.
"""

import pandas as pd
import pytest
from datetime import datetime

from bach import DataFrame
from tests.functional.bach.test_data_and_utils import assert_equals_data

DATA = [
    [None, None, None, None, None, 'a',   datetime(2022, 1, 1)],
    [3,    4,    None, 1,    1,     None, datetime(2022, 1, 2)],
    [None, 3,    None, 4,    None,  'b',  None],
    [None, 2,    None, 0,    None,  'c',  None],
    [None, None, None, None, 2,     None, None],
    [1,    None, None, None, None,  'd',  datetime(2022, 1, 5)],
    [None, None, None, None, 3,     'e',  datetime(2022, 1, 6)],
    [None, None, 1,    None, None,  'f',  None],
]


def test_basic_fillna(engine) -> None:
    pdf = pd.DataFrame(DATA, columns=list("ABCDEFG"))
    pdf = pdf[list("ABCDE")]
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    df = df.astype('int64')

    result = df.fillna(value=0)
    assert_equals_data(
        result,
        expected_columns=['_index_0', 'A', 'B', 'C', 'D', 'E'],
        expected_data=[
            [0, 0, 0, 0, 0, 0],
            [1, 3, 4, 0, 1, 1],
            [2, 0, 3, 0, 4, 0],
            [3, 0, 2, 0, 0, 0],
            [4, 0, 0, 0, 0, 2],
            [5, 1, 0, 0, 0, 0],
            [6, 0, 0, 0, 0, 3],
            [7, 0, 0, 1, 0, 0],
        ],
    )
    pd.testing.assert_frame_equal(
        pdf.fillna(value=0),
        result.sort_index().to_pandas(),
        check_names=False,
        check_dtype=False,
    )


def test_fillna_w_methods(pg_engine) -> None:
    engine = pg_engine  # TODO: BigQuery
    pdf = pd.DataFrame(DATA, columns=list("ABCDEFG"))
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)

    result_ffill = df.fillna(
        method='ffill', sort_by=['A', 'B', 'C'], ascending=[False, True, False],
    )
    result_ffill = result_ffill.sort_values(['A', 'B', 'C'], ascending=[False, True, False])
    assert_equals_data(
        result_ffill,
        expected_columns=['_index_0', 'A', 'B', 'C', 'D', 'E', 'F', 'G'],
        expected_data=[
            [3, None, 2, None, 0,  None, 'c',  None],
            [2, None, 3, None, 4,  None, 'b',  None],
            [0, None, 3, None, 4,  None, 'a',  datetime(2022, 1, 1)],
            [4, None, 3, None, 4,  2,    'a',  datetime(2022, 1, 1)],
            [6, None, 3, None, 4,  3,    'e',  datetime(2022, 1, 6)],
            [7, None, 3, 1,    4,  3,    'f',  datetime(2022, 1, 6)],
            [1, 3,    4, 1,    1,  1,    'f',  datetime(2022, 1, 2)],
            [5, 1,    4, 1,    1,  1,    'd',  datetime(2022, 1, 5)],
        ],
    )

    result_bfill = df.fillna(
        method='bfill', sort_by=['A', 'B', 'C'], ascending=[False, True, False],
    )
    assert_equals_data(
        result_bfill,
        expected_columns=['_index_0', 'A', 'B', 'C', 'D', 'E', 'F', 'G'],
        expected_data=[
            [3, 3, 2,    1,    0,    3,    'c', datetime(2022, 1, 6)],
            [2, 3, 3,    1,    4,    3,    'b', datetime(2022, 1, 6)],
            [1, 3, 4,    None, 1,    1,    'd', datetime(2022, 1, 2)],
            [6, 3, 4,    1,    1,    3,    'e', datetime(2022, 1, 6)],
            [0, 3, 4,    1,    1,    2,    'a', datetime(2022, 1, 1)],
            [7, 3, 4,    1,    1,    1,    'f', datetime(2022, 1, 2)],
            [4, 3, 4,    1,    1,    2,    'f', datetime(2022, 1, 2)],
            [5, 1, None, None, None, None, 'd', datetime(2022, 1, 5)],
        ],
    )


def test_fillna_w_methods_w_sorted_df(pg_engine) -> None:
    engine = pg_engine  # TODO: BigQuery

    pdf = pd.DataFrame(DATA, columns=list("ABCDEFG"))
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True).sort_index()

    result_ffill = df.fillna(method='ffill')
    assert_equals_data(
        result_ffill,
        expected_columns=['_index_0', 'A', 'B', 'C', 'D', 'E', 'F', 'G'],
        expected_data=[
            [0, None, None, None, None, None, 'a', datetime(2022, 1, 1)],
            [1, 3,    4,    None, 1,    1,    'a', datetime(2022, 1, 2)],
            [2, 3,    3,    None, 4,    1,    'b', datetime(2022, 1, 2)],
            [3, 3,    2,    None, 0,    1,    'c', datetime(2022, 1, 2)],
            [4, 3,    2,    None, 0,    2,    'c', datetime(2022, 1, 2)],
            [5, 1,    2,    None, 0,    2,    'd', datetime(2022, 1, 5)],
            [6, 1,    2,    None, 0,    3,    'e', datetime(2022, 1, 6)],
            [7, 1,    2,    1,    0,    3,    'f', datetime(2022, 1, 6)],
        ],
    )

    result_bfill = df.fillna(method='bfill')
    assert_equals_data(
        result_bfill,
        expected_columns=['_index_0', 'A', 'B', 'C', 'D', 'E', 'F', 'G'],
        expected_data=[
            [0, 3,    4,    1, 1,    1,    'a', datetime(2022, 1, 1)],
            [1, 3,    4,    1, 1,    1,    'b', datetime(2022, 1, 2)],
            [2, 1,    3,    1, 4,    2,    'b', datetime(2022, 1, 5)],
            [3, 1,    2,    1, 0,    2,    'c', datetime(2022, 1, 5)],
            [4, 1,    None, 1, None, 2,    'd', datetime(2022, 1, 5)],
            [5, 1,    None, 1, None, 3,    'd', datetime(2022, 1, 5)],
            [6, None, None, 1, None, 3,    'e', datetime(2022, 1, 6)],
            [7, None, None, 1, None, None, 'f', None],
        ],
    )


def test_fillna_errors(engine):
    pdf = pd.DataFrame(DATA, columns=list("ABCDEFG"))
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    with pytest.raises(ValueError, match=r'cannot specify both "method" and "value".'):
        df.fillna(value=0, method='ffill')

    with pytest.raises(Exception, match=r'"random" is not a valid method.'):
        df.fillna(method='random')

    with pytest.raises(Exception, match=r'dataframe must be sorted'):
        df.fillna(method='ffill')
