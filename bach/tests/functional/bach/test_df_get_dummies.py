import pandas as pd
import pytest

from bach import DataFrame
from tests.functional.bach.test_data_and_utils import assert_equals_data


def test_basic_get_dummies(engine) -> None:
    pdf = pd.DataFrame(
        {'A': ['a', 'b', 'a'], 'B': ['b', 'a', 'c'], 'C': [1, 2, 3]},
    )

    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    expected = pd.get_dummies(pdf, dtype='int')
    expected.index.name = '_index_0'
    expected_columns = ['C', 'A_a', 'A_b', 'B_a', 'B_b', 'B_c']

    result = df.get_dummies().sort_index()
    assert set(expected_columns) == set(result.data_columns)
    result = result[expected_columns]
    assert_equals_data(
        result[expected_columns],
        expected_columns=['_index_0'] + expected_columns,
        expected_data=[
            [0, 1, 1, 0, 0, 1, 0],
            [1, 2, 0, 1, 1, 0, 0],
            [2, 3, 1, 0, 0, 0, 1]
        ],
    )
    pd.testing.assert_frame_equal(
        expected,
        result.to_pandas(),
    )


def test_get_dummies_dtype(engine) -> None:
    pdf = pd.DataFrame(
        {'A': ['a', 'b', 'a'], 'B': ['b', 'a', 'c'], 'C': [1, 2, 3]},
    )

    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    expected_columns = ['C', 'A_a', 'A_b', 'B_a', 'B_b', 'B_c']

    # comparison with pandas is different, pandas will return empty space instead of 0.
    result = df.get_dummies(dtype='string').sort_index()
    assert set(expected_columns) == set(result.data_columns)
    result = result[expected_columns]
    assert_equals_data(
        result[expected_columns],
        expected_columns=['_index_0'] + expected_columns,
        expected_data=[
            [0, 1, '1', '0', '0', '1', '0'],
            [1, 2, '0', '1', '1', '0', '0'],
            [2, 3, '1', '0', '0', '0', '1']
        ],
    )


def test_get_dummies_prefix(engine) -> None:
    pdf = pd.DataFrame(
        {'A': ['a', 'b', 'a'], 'B': ['b', 'a', 'c'], 'C': [1, 2, 3]},
    )

    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    prefix = ['col1', 'col2']

    expected = pd.get_dummies(pdf, prefix=prefix, prefix_sep='__', dtype='int')
    expected.index.name = '_index_0'
    expected_columns = ['C', 'col1__a', 'col1__b', 'col2__a', 'col2__b', 'col2__c']

    result = df.get_dummies(prefix=prefix, prefix_sep='__').sort_index()[expected_columns]
    assert set(expected_columns) == set(result.data_columns)

    result = result[expected_columns]
    assert_equals_data(
        result,
        expected_columns=['_index_0'] + expected_columns,
        expected_data=[
            [0, 1, 1, 0, 0, 1, 0],
            [1, 2, 0, 1, 1, 0, 0],
            [2, 3, 1, 0, 0, 0, 1]
        ],
    )

    pd.testing.assert_frame_equal(
        expected,
        result.to_pandas(),
    )


def test_get_dummies_w_na(engine) -> None:
    pdf = pd.DataFrame(
        {'A': ['a', None, 'a', None], 'B': ['c', 'd', None, None], 'C': [1, 2, 3, 4]},
    )
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    expected = pd.get_dummies(pdf, dtype='int64')
    # bach adds prefix always
    expected = expected.rename(columns={'a': 'A_a', 'c': 'B_c', 'd': 'B_d'})
    expected.index.name = '_index_0'
    expected_columns = ['C', 'A_a', 'B_c', 'B_d']

    result = df.get_dummies().sort_index()
    assert set(expected_columns) == set(result.data_columns)

    result = result[expected_columns]
    assert_equals_data(
        result,
        expected_columns=['_index_0'] + expected_columns,
        expected_data=[
            [0, 1, 1, 1, 0],
            [1, 2, 0, 0, 1],
            [2, 3, 1, 0, 0],
            [3, 4, 0, 0, 0],
        ],
    )
    pd.testing.assert_frame_equal(
        expected,
        result.to_pandas(),
    )


def test_get_dummies_include_na(engine) -> None:
    pdf = pd.DataFrame(
        {'A': ['a', None, 'a'], 'B': ['c', 'd', None], 'C': [1, 2, 3]},
    )
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    expected = pd.get_dummies(pdf,dummy_na=True, dtype='int64')
    # bach adds prefix always
    expected = expected.rename(columns={'a': 'A_a', 'c': 'B_c', 'd': 'B_d'})
    expected.index.name = '_index_0'
    expected_columns = ['C', 'A_a', 'A_nan', 'B_c', 'B_d', 'B_nan']

    result = df.get_dummies(dummy_na=True).sort_index()
    assert set(expected_columns) == set(result.data_columns)

    result = result[expected_columns]
    assert_equals_data(
        result,
        expected_columns=['_index_0'] + expected_columns,
        expected_data=[
            [0, 1, 1, 0, 1, 0, 0],
            [1, 2, 0, 1, 0, 1, 0],
            [2, 3, 1, 0, 0, 0, 1],
        ],
    )
    pd.testing.assert_frame_equal(
        expected,
        result.to_pandas(),
    )


def test_get_dummies_errors(engine) -> None:
    pdf = pd.DataFrame({'A': ['a'], 'B': ['c'], 'C': [1]})
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)

    with pytest.raises(ValueError, match=r'are not valid columns'):
        df.get_dummies(columns=['C'])

    with pytest.raises(ValueError, match=r'are not valid columns'):
        df.get_dummies(columns=['X'])

    with pytest.raises(IndexError, match=r' at least one index level'):
        df.reset_index().get_dummies()
