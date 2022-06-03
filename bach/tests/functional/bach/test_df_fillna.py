"""
Copyright 2022 Objectiv B.V.
"""
import itertools
from typing import Tuple
from unittest.mock import ANY

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


@pytest.fixture
def dataframes_sort(engine) -> Tuple[pd.DataFrame, DataFrame]:
    pdf = pd.DataFrame(
        [
            [None, 1,        2],
            [None, None,     3],
            [None, 4,     None],
            [1,    4,        5],
            [None, None,  None],
            [None, 2,        3],
            [1,    None,  None],
            [1,    None,     2],
            [1,       2,  None],
        ],
        columns=['A', 'B', 'C']
    )
    df = DataFrame.from_pandas(engine, pdf, convert_objects=True).reset_index(drop=True)

    return pdf, df


@pytest.mark.parametrize(
    "ascending",  [
        *[list(perm) for perm in itertools.permutations([True, False, False])],
        *[list(perm) for perm in itertools.permutations([True, True, False])],
        [True, True, True],
        [False, False, False],
    ]
)
def test_sorting_df(dataframes_sort, ascending) -> None:
    pdf, df = dataframes_sort
    sort_by = ['A', 'B', 'C']
    expected = pdf.sort_values(by=sort_by, ascending=ascending).reset_index(drop=True)
    result = df.sort_values(by=sort_by, ascending=ascending).to_pandas()
    pd.testing.assert_frame_equal(expected, result)


def test_fillna_w_methods_against_pandas(engine) -> None:
    pdf = pd.DataFrame(DATA, columns=list("ABCDEFG"))
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)

    sort_by = ['A', 'B', 'C']
    ascending = [False, True, False]

    check_sort_expected = pdf.sort_values(by=sort_by, ascending=ascending)
    check_sort_expected = check_sort_expected.dropna(subset=sort_by, how='all')

    check_sort_result = df.sort_values(by=sort_by, ascending=ascending)
    check_sort_result = check_sort_result.dropna(subset=sort_by, how='all')

    # check if sort performed in ffilna generates same order based on sortby
    # ignores when all columns involved in sort by are NULL (non-deterministic)
    pd.testing.assert_frame_equal(
        check_sort_expected, check_sort_result.to_pandas(), check_index_type=False, check_names=False,
    )

    fillna_check_ffill_expected = check_sort_expected.fillna(method='ffill')
    fillna_check_ffill_result = check_sort_result.fillna(method='ffill')
    pd.testing.assert_frame_equal(
        fillna_check_ffill_expected,
        fillna_check_ffill_result.to_pandas(),
        check_index_type=False,
        check_names=False,
    )

    fillna_check_bfill_expected = check_sort_expected.fillna(method='bfill')
    fillna_check_bfill_result = check_sort_result.fillna(method='bfill')
    pd.testing.assert_frame_equal(
        fillna_check_bfill_expected,
        fillna_check_bfill_result.to_pandas(),
        check_index_type=False,
        check_names=False,
    )


def test_fillna_w_methods(pg_engine) -> None:
    engine = pg_engine  # TODO: BigQuery
    pdf = pd.DataFrame(DATA, columns=list("ABCDEFG"))
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)

    sort_by = ['A', 'B', 'C']
    ascending = [False, True, False]

    assert_equals_data(
        df.sort_values(by=sort_by, ascending=ascending),
        expected_columns=['_index_0', 'A', 'B', 'C', 'D', 'E', 'F', 'G'],
        expected_data=[
            [1,    3,    4, None,    1,    1, None, datetime(2022, 1, 2)],
            [5,    1, None, None, None, None,  'd', datetime(2022, 1, 5)],
            [3, None,    2, None,    0, None,  'c',                 None],
            [2, None,    3, None,    4, None,  'b',                 None],
            [7, None, None,    1, None, None,  'f',                 None],
            # last 3 rows are non-deterministic because A, B, C are all nulls
            [ANY, None, None, None] + [ANY] * 4,
            [ANY, None, None, None] + [ANY] * 4,
            [ANY, None, None, None] + [ANY] * 4,
        ],
    )

    result_ffill = df.fillna(method='ffill', sort_by=sort_by, ascending=ascending)
    assert_equals_data(
        result_ffill,
        expected_columns=['_index_0', 'A', 'B', 'C', 'D', 'E', 'F', 'G'],
        expected_data=[
            [1,    3,    4, None,    1,    1, None, datetime(2022, 1, 2)],
            [5,    1,    4, None,    1,    1,  'd', datetime(2022, 1, 5)],
            [3,    1,    2, None,    0,    1,  'c', datetime(2022, 1, 5)],
            [2,    1,    3, None,    4,    1,  'b', datetime(2022, 1, 5)],
            [7,    1,    3,    1,    4,    1,  'f', datetime(2022, 1, 5)],
            # last 3 rows are non-deterministic because A, B, C were initially all nulls
            [ANY,  1,    3,    1] + [ANY] * 4,
            [ANY,  1,    3,    1] + [ANY] * 4,
            [ANY,  1,    3,    1] + [ANY] * 4,
        ],
    )

    result_bfill = df.fillna(
        method='bfill', sort_by=['A', 'B', 'C'], ascending=[False, True, False],
    )
    assert_equals_data(
        result_bfill,
        expected_columns=['_index_0', 'A', 'B', 'C', 'D', 'E', 'F', 'G'],
        expected_data=[
            [1,    3,    4,    1,    1,    1,  'd', datetime(2022, 1, 2)],
            [5,    1,    2,    1,    0,  ANY,  'd', datetime(2022, 1, 5)],
            [3, None,    2,    1,    0,  ANY,  'c',                 ANY],
            [2, None,    3,    1,    4,  ANY,  'b',                 ANY],
            [7, None, None,    1,  ANY,  ANY,  'f',                 ANY],
            # last 3 rows are non-deterministic because A, B, C are all nulls
            [ANY, None, None, None] + [ANY] * 4,
            [ANY, None, None, None] + [ANY] * 4,
            [ANY, None, None, None] + [ANY] * 4,
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

    with pytest.raises(Exception, match=r'"random" is not a valid propagation method.'):
        df.fillna(method='random')

    with pytest.raises(Exception, match=r'dataframe must be sorted'):
        df.fillna(method='ffill')
