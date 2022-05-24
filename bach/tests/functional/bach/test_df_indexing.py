from typing import Tuple

import pandas as pd
import pytest

from bach import Series, DataFrame
from sql_models.util import is_bigquery
from tests.functional.bach.test_data_and_utils import assert_equals_data, get_df_with_test_data


@pytest.fixture()
def indexing_dfs(engine) -> Tuple[pd.DataFrame, DataFrame]:
    pdf = pd.DataFrame(
        {
            'A': ['a', 'b', 'c', 'd', 'e'],
            'B': [0, 1, 2, 3, 4],
            'C': [5, 6, 7, 8, 9],
            'D': ['f', 'g', 'h', 'i', 'j'],
        },
    )
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    df = df.set_index('A', drop=True)
    pdf = pdf.set_index('A')

    return pdf, df


def test_basic_indexing(indexing_dfs: Tuple[pd.DataFrame, DataFrame]) -> None:
    pdf, df = indexing_dfs

    single_label_result = df.loc['b']
    assert isinstance(single_label_result, Series)
    pd.testing.assert_series_equal(
        pdf.loc['b'].astype(str),
        single_label_result.to_pandas(),
        check_names=False,
    )

    label_list_result = df.loc[['c', 'e']]
    assert isinstance(label_list_result, DataFrame)
    pd.testing.assert_frame_equal(
        pdf.loc[['c', 'e']],
        label_list_result.sort_index().to_pandas(),
        check_names=False,
    )

    bool_result = df.loc[df['D'] == 'g']
    assert isinstance(bool_result, DataFrame)
    pd.testing.assert_frame_equal(
        pdf.loc[pdf['D'] == 'g'],
        bool_result.sort_index().to_pandas(),
        check_names=False,
    )


def test_basic_indexing_column_based(indexing_dfs: Tuple[pd.DataFrame, DataFrame]) -> None:
    pdf, df = indexing_dfs

    single_label_column_result = df.loc['d', 'D']

    # pandas returns a scalar for this example
    assert_equals_data(
        single_label_column_result,
        expected_columns=['__stacked_index', '__stacked'],
        expected_data=[['D', 'i']],
    )
    isinstance(single_label_column_result, Series)

    list_label_column_result = df.loc['d', ['C', 'D']]
    pd.testing.assert_series_equal(
        pdf.loc['d', ['C', 'D']].astype(str),
        list_label_column_result.sort_index().to_pandas(),
        check_names=False,
    )


def test_index_slicing(indexing_dfs: Tuple[pd.DataFrame, DataFrame]) -> None:
    pdf, df = indexing_dfs

    if is_bigquery(df.engine):
        # TODO: BigQuery
        # indexing with slicing is still not supported for BigQuery
        return

    df = df.sort_index()
    result_slicing = df.loc['b':'d']
    pd.testing.assert_frame_equal(
        pdf.sort_index().loc['b':'d'],
        result_slicing.to_pandas(),
    )

    result_no_stop_slicing = df.loc['b':]
    pd.testing.assert_frame_equal(
        pdf.loc['b':],
        result_no_stop_slicing.to_pandas(),
    )

    result_no_start_slicing = df.loc[:'c']
    pd.testing.assert_frame_equal(
        pdf.loc[:'c'],
        result_no_start_slicing.to_pandas(),
    )

    result_column_slicing = df.loc[:, 'B':'D']

    pd.testing.assert_frame_equal(
        pdf.loc[:, 'B':'D'],
        result_column_slicing.to_pandas(),
    )

    result_column_no_stop_slicing = df.loc[:, 'B':]
    pd.testing.assert_frame_equal(
        pdf.loc[:, 'B':],
        result_column_no_stop_slicing.to_pandas(),
    )

    result_column_no_start_slicing = df.loc[:, :'C']
    pd.testing.assert_frame_equal(
        pdf.loc[:, :'C'],
        result_column_no_start_slicing.to_pandas(),
    )


def test_basic_set_item_by_label(indexing_dfs: Tuple[pd.DataFrame, DataFrame]) -> None:
    pdf, df = indexing_dfs

    df_cp1 = df.copy()
    pdf_cp1 = pdf.copy()
    df_cp1.loc['b'] = 1
    pdf_cp1.loc['b'] = 1
    pdf_cp1['D'] = pdf_cp1['D'].astype(str)
    pd.testing.assert_frame_equal(pdf_cp1, df_cp1.to_pandas())

    # cannot check against Pandas, since pandas checks index lengths when setting items.
    df_cp2 = df.copy()
    df_cp2.loc['b', 'B'] = df_cp2['C']

    assert_equals_data(
        df_cp2,
        expected_columns=['A', 'B', 'C', 'D'],
        expected_data=[
            ['a', 0, 5, 'f'],
            ['b', 6, 6, 'g'],
            ['c', 2, 7, 'h'],
            ['d', 3, 8, 'i'],
            ['e', 4, 9, 'j'],
        ],
    )


def test_set_item_by_label_diff_node(indexing_dfs: Tuple[pd.DataFrame, DataFrame], engine) -> None:
    _, df = indexing_dfs
    extra_pdf = pd.DataFrame(
        {
            'A': ['a', 'b'],
            'B': [7, 8],
            'C': [11, 12],
        },
    )
    extra_df = DataFrame.from_pandas(engine, df=extra_pdf, convert_objects=True)
    extra_df = extra_df.set_index('A')

    # cannot check against Pandas, since pandas checks index lengths when setting items.
    df.loc['b', ['B', 'D']] = extra_df['C']
    assert_equals_data(
        df.sort_index(),
        expected_columns=['A', 'B', 'C', 'D'],
        expected_data=[
            ['a', 0, 5, 'f'],
            ['b', 12, 6, '12'],
            ['c', 2, 7, 'h'],
            ['d', 3, 8, 'i'],
            ['e', 4, 9, 'j'],
        ],
    )


def test_set_item_by_slicing(indexing_dfs: Tuple[pd.DataFrame, DataFrame], engine) -> None:
    pdf, df = indexing_dfs
    if is_bigquery(df.engine):
        # TODO: BigQuery
        # indexing with slicing is still not supported for BigQuery
        return
    df = df.sort_index()

    df.loc['b':'d'] = 1

    pdf.loc['b': 'd'] = 1
    pdf['D'] = pdf['D'].astype(str)
    pd.testing.assert_frame_equal(pdf, df.to_pandas())

    assert_equals_data(
        df.sort_index(),
        expected_columns=['A', 'B', 'C', 'D'],
        expected_data=[
            ['a', 0, 5, 'f'],
            ['b', 1, 1, '1'],
            ['c', 1, 1, '1'],
            ['d', 1, 1, '1'],
            ['e', 4, 9, 'j'],
        ],
    )

    extra_pdf = pd.DataFrame(
        {
            'A': ['a', 'b'],
            'B': [7, 8],
            'C': [11, 12],
        },
    )
    extra_df = DataFrame.from_pandas(engine, df=extra_pdf, convert_objects=True)
    extra_df = extra_df.set_index('A')

    # cannot check against Pandas, since pandas checks index lengths when setting items.
    df.loc['b':'d', ['B', 'D']] = extra_df['B']
    assert_equals_data(
        df.sort_index(),
        expected_columns=['A', 'B', 'C', 'D'],
        expected_data=[
            ['a', 0, 5, 'f'],
            ['b', 8, 1, '8'],
            ['c', None, 1, None],
            ['d', None, 1, None],
            ['e', 4, 9, 'j'],
        ],
    )


def test_indexing_wo_index(engine) -> None:
    bt = get_df_with_test_data(engine)[['city']]
    bt['city_normal'] = 'placeholder'
    bt = bt.reset_index()

    with pytest.raises(ValueError, match=r'Cannot access rows by label'):
        bt.loc[0, 'city_normal']

    bt.loc[bt.city == 'Snits', 'city_normal'] = 'Snake'
    assert_equals_data(
        bt,
        expected_columns=['_index_skating_order', 'city', 'city_normal'],
        expected_data=[
            [1, 'Ljouwert', 'placeholder'],
            [2, 'Snits', 'Snake'],
            [3, 'Drylts', 'placeholder'],
        ],
        order_by=['_index_skating_order'],
    )
