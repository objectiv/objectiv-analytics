import numpy as np
import pandas as pd

from bach import DataFrame
from tests.functional.bach.test_data_and_utils import assert_equals_data


def test_append_w_aligned_columns(engine) -> None:
    caller_pdf = pd.DataFrame({'a': [1, 2, 3, 4, 5], 'b': ['a', 'b', 'c', 'd', 'e']})
    other_pdf = pd.DataFrame({'a': [6, 7, 8, 9], 'b': ['f', 'g', 'h', 'i']})

    caller_df = DataFrame.from_pandas(engine=engine, df=caller_pdf, convert_objects=True)
    other_df = DataFrame.from_pandas(engine=engine, df=other_pdf, convert_objects=True)

    result = caller_df.append(other_df).sort_values('a').reset_index(drop=False)
    expected = caller_pdf.append(other_pdf).sort_values('a').reset_index(drop=False)
    np.testing.assert_equal(expected.to_numpy(), result.to_numpy())


def test_append_w_non_aligned_columns(engine) -> None:
    caller_pdf = pd.DataFrame({'a': [1, 2, 3, 4, 5], 'b': ['a', 'b', 'c', 'd', 'e']})
    other_pdf = pd.DataFrame({'d': [6, 7, 8, 9], 'c': ['f', 'g', 'h', 'i']})

    caller_df = DataFrame.from_pandas(engine=engine, df=caller_pdf, convert_objects=True)
    other_df = DataFrame.from_pandas(engine=engine, df=other_pdf, convert_objects=True)
    result = caller_df.append(other_df).sort_values('a').reset_index(drop=False)

    expected = caller_pdf.append(other_pdf).sort_values('a').reset_index(drop=False)
    expected = expected.rename(columns={'index': '_index_0'})

    result_pdf = result.to_pandas()
    pd.testing.assert_frame_equal(expected, result_pdf)

    assert_equals_data(
        result,
        expected_columns=['_index_0', 'a', 'b', 'd', 'c'],
        expected_data=[
            [0, 1, 'a', None, None],
            [1, 2, 'b', None, None],
            [2, 3, 'c', None, None],
            [3, 4, 'd', None, None],
            [4, 5, 'e', None, None],
            [0, None, None, 6, 'f'],
            [1, None, None, 7, 'g'],
            [2, None, None, 8, 'h'],
            [3, None, None, 9, 'i'],
        ],
    )


def test_append_w_ignore_index_n_sort(engine) -> None:
    caller_pdf = pd.DataFrame({'a': [1, 2, 3, 4, 5], 'b': ['a', 'b', 'c', 'd', 'e']})
    other_pdf = pd.DataFrame({'d': [6, 7, 8, 9], 'c': ['f', 'g', 'h', 'i']})

    caller_df = DataFrame.from_pandas(engine=engine, df=caller_pdf, convert_objects=True)

    other_df = DataFrame.from_pandas(engine=engine, df=other_pdf, convert_objects=True)
    other_df = other_df.set_index(['d'])

    result = caller_df.append(other_df, ignore_index=True).sort_values('a')

    expected = caller_pdf.append(other_pdf.set_index(['d']), ignore_index=True).sort_values('a')
    pd.testing.assert_frame_equal(expected, result.to_pandas())

    assert_equals_data(
        result,
        expected_columns=['a', 'b', 'c'],
        expected_data=[
            [1, 'a', None],
            [2, 'b', None],
            [3, 'c', None],
            [4, 'd', None],
            [5, 'e', None],
            [None, None, 'f'],
            [None, None, 'g'],
            [None, None, 'h'],
            [None, None, 'i'],
        ],
    )

    other_df2 = DataFrame.from_pandas(engine=engine, df=other_pdf, convert_objects=True)
    result2 = caller_df.append(other_df2, ignore_index=True, sort=True).sort_values('a')

    expected2 = caller_pdf.append(other_pdf, ignore_index=True, sort=True)
    pd.testing.assert_frame_equal(expected2, result2.to_pandas())
    assert_equals_data(
        result2,
        expected_columns=['a', 'b', 'c', 'd'],
        expected_data=[
            [1, 'a', None, None],
            [2, 'b', None, None],
            [3, 'c', None, None],
            [4, 'd', None, None],
            [5, 'e', None, None],
            [None, None, 'f', 6],
            [None, None, 'g', 7],
            [None, None, 'h', 8],
            [None, None, 'i', 9],
        ],
    )


def test_append_w_list_dfs(engine) -> None:
    caller_pdf = pd.DataFrame({'a': [1, 2, 3, 4, 5], 'b': ['a', 'b', 'c', 'd', 'e']})
    other_pdf = pd.DataFrame({'d': [6, 7, 8, 9], 'c': ['f', 'g', 'h', 'i']})

    caller_df = DataFrame.from_pandas(engine=engine, df=caller_pdf, convert_objects=True)
    other_dfs = [
        DataFrame.from_pandas(engine=engine, df=other_pdf, convert_objects=True, name=f'other_{i}_df')
        for i in range(3)
    ]

    result = caller_df.append(other_dfs).sort_values('a')

    expected = caller_pdf.append([other_pdf] * 3).sort_values('a')

    pd.testing.assert_frame_equal(expected, result.to_pandas(), check_names=False)

    assert_equals_data(
        result,
        expected_columns=['_index_0', 'a', 'b', 'd', 'c'],
        expected_data=[
            [0, 1, 'a', None, None],
            [1, 2, 'b', None, None],
            [2, 3, 'c', None, None],
            [3, 4, 'd', None, None],
            [4, 5, 'e', None, None],
            [0, None, None, 6, 'f'],
            [1, None, None, 7, 'g'],
            [2, None, None, 8, 'h'],
            [3, None, None, 9, 'i'],
            [0, None, None, 6, 'f'],
            [1, None, None, 7, 'g'],
            [2, None, None, 8, 'h'],
            [3, None, None, 9, 'i'],
            [0, None, None, 6, 'f'],
            [1, None, None, 7, 'g'],
            [2, None, None, 8, 'h'],
            [3, None, None, 9, 'i'],
        ],
    )


def test_append_w_different_dtypes(engine) -> None:
    caller_pdf = pd.DataFrame({'a': ['f', 'g', 'h', 'i'], 'b': [1, 2, 3, 4], 'c': [1, 2, 3, 4]})
    other_pdf = pd.DataFrame({'a': [1, 2, 3, 4, 5], 'b': [1.1, 2.2, 3.3, 4.4, 5.5], 'c': [5, 6, 7, 8, 9]})

    caller_df = DataFrame.from_pandas(engine=engine, df=caller_pdf, convert_objects=True)
    other_df = DataFrame.from_pandas(engine=engine, df=other_pdf, convert_objects=True)

    result = caller_df.append(other_df).sort_values('a')

    assert_equals_data(
        result,
        expected_columns=['_index_0', 'a', 'b', 'c'],
        expected_data=[
            [0, '1', 1.1, 5],
            [1, '2', 2.2, 6],
            [2, '3', 3.3, 7],
            [3, '4', 4.4, 8],
            [4, '5', 5.5, 9],
            [0, 'f', 1.0, 1],
            [1, 'g', 2.0, 2],
            [2, 'h', 3.0, 3],
            [3, 'i', 4.0, 4],
        ],
    )


def test_append_w_non_materialized_df(engine) -> None:
    caller_pdf = pd.DataFrame({'b': [1, 2, 3, 4], 'c': [1, 2, 3, 4]})
    other_pdf = pd.DataFrame({'b': [1.1, 2.2, 3.3, 4.4, 5.5], 'c': [5, 6, 7, 8, 9]})

    caller_df = DataFrame.from_pandas(engine=engine, df=caller_pdf, convert_objects=True)
    other_df = DataFrame.from_pandas(engine=engine, df=other_pdf, convert_objects=True)

    caller_df['d'] = caller_df['b'] + caller_df['c']

    caller_df = caller_df.set_index('c')
    other_df = other_df.groupby(['c'])[['b']].sum()

    result = caller_df.append(other_df).sort_values(by='c')
    assert_equals_data(
        result,
        expected_columns=['c', 'b', 'd', 'b_sum'],
        expected_data=[
            [1, 1, 2, None],
            [2, 2, 4, None],
            [3, 3, 6, None],
            [4, 4, 8, None],
            [5, None, None, 1.1],
            [6, None, None, 2.2],
            [7, None, None, 3.3],
            [8, None, None, 4.4],
            [9, None, None, 5.5],
        ],
    )
