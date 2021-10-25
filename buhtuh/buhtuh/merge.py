"""
Copyright 2021 Objectiv B.V.
"""
from enum import Enum
from typing import Union, List, Tuple, Optional, Dict, Set, NamedTuple, TYPE_CHECKING

from buhtuh import DataFrameOrSeries, BuhTuhDataFrame, ColumnNames, BuhTuhSeries
from buhtuh.expression import Expression
from sql_models.expression import quote_identifier
from sql_models.model import CustomSqlModel, SqlModel

if TYPE_CHECKING:
    from buhtuh.expression import Expression


class How(Enum):
    """ Enum with all valid values of 'how' parameter """
    left = 'left'
    right = 'right'
    outer = 'outer'
    inner = 'inner'
    cross = 'cross'


def _determine_left_on_right_on(
        left: BuhTuhDataFrame,
        right: DataFrameOrSeries,
        how: How,
        on: Optional[ColumnNames],
        left_on: Optional[ColumnNames],
        right_on: Optional[ColumnNames],
        left_index: bool,
        right_index: bool) -> Tuple[List[str], List[str]]:
    """
    Determine the columns that should be equal for the merge. Both for the left and the right
    dataframse/series a list of strings is returned indicating the names of the columns that should be
    matched.
    :return: tuple with left_on and right_on
    """
    if how == How.cross:
        if on or left_on or right_on or left_index or right_index:
            raise ValueError('Cannot specify on, left_on, right_on, left_index, or right_index'
                             'if how == "cross"')
        return [], []

    if (left_on is not None) and left_index:
        raise ValueError('Cannot specify both left_on and left_index.')
    if (right_on is not None) and right_index:
        raise ValueError('Cannot specify both right_on and right_index.')

    if left_index:
        left_on = list(_get_index_names(left))
    if right_index:
        right_on = list(_get_index_names(right))

    if (left_on is None) is not (right_on is None):
        raise ValueError('Either both left_on and right_on should be specified, or both should be None.')
    if on is not None and left_on is not None and right_on is not None:
        raise ValueError('Either specify on or, left_on and right_on, but not all three')

    left_cols = _get_data_columns(left)
    right_cols = _get_data_columns(right)
    intersection_columns = list(left_cols.intersection(right_cols))
    final_on = on if on is not None else intersection_columns
    final_left_on = _get_x_on(final_on, left_on, 'left_on')
    final_right_on = _get_x_on(final_on, right_on, 'right_on')
    if len(final_left_on) != len(final_right_on):
        raise ValueError(
            f'Len of left_on ({final_left_on}) does not match that of right_on ({final_right_on}).')
    if len(final_left_on) == 0:
        raise ValueError('No columns to perform merge on')
    missing_left = set(final_left_on) - _get_all_series_names(left)
    missing_right = set(final_right_on) - _get_all_series_names(right)
    if missing_left:
        raise ValueError(f'Specified column(s) do not exist. left_on: {left_on}. missing: {missing_left}')
    if missing_right:
        raise ValueError(f'Specified column(s) do not exist. right_on: {right_on}. missing: {missing_right}')
    return final_left_on, final_right_on


def _get_data_columns(df_series: DataFrameOrSeries) -> Set[str]:
    """ Get set with the names of all data columns. Works for both dataframe and series. """
    if isinstance(df_series, BuhTuhDataFrame):
        return set(df_series.data_columns)
    if isinstance(df_series, BuhTuhSeries):
        return {df_series.name}
    raise TypeError(f'Expected BuhTuhDataFrame or BuhTuhSeries, got {type(df_series)}')


def _get_index_names(df_series: DataFrameOrSeries) -> Set[str]:
    """ Get set the names of the index columns. Works for both dataframe and series. """
    if df_series.index:
        return set(df_series.index.keys())
    else:
        return set()


def _get_all_series_names(df_series: DataFrameOrSeries) -> Set[str]:
    """ Get set with the names of all series. Works for both dataframe and series. """
    return _get_index_names(df_series) | _get_data_columns(df_series)


def _get_x_on(on: ColumnNames, x_on: Optional[ColumnNames], var_name: str) -> List[str]:
    """ Helper for _determine_left_on_right_on: Give `x_on` as a List[str], or default to `on`. """
    if isinstance(x_on, str):
        return [x_on]
    if isinstance(x_on, list):
        return x_on
    if x_on is None:
        if isinstance(on, str):
            return [on]
        if isinstance(on, list):
            return on
        raise ValueError(f'Type of on is not supported. Type: {type(on)}')
    raise ValueError(f'Type of {var_name} is not supported. Type: {type(x_on)}')


class ResultColumn(NamedTuple):
    name: str
    expression: 'Expression'
    dtype: str


def _determine_result_columns(
        left: BuhTuhDataFrame,
        right: DataFrameOrSeries,
        left_on: List[str],
        right_on: List[str],
        suffixes: Tuple[str, str]
) -> Tuple[List[ResultColumn], List[ResultColumn]]:
    """
    Determine which columns should be in the DataFrame after merging left and right, with the given
    left_on and right_on values.
    """
    filter_columns_from_right = _get_filter_columns_from_right(left_on, right_on)
    left_index = left.index
    if right.index:
        right_index = {
            label: series for label, series in right.index.items()
            if label not in filter_columns_from_right
        }
    else:
        right_index = {}

    left_data = left.data
    if isinstance(right, BuhTuhDataFrame):
        right_data = right.data
    elif isinstance(right, BuhTuhSeries):
        right_data = {right.name: right}
    else:
        raise TypeError(f'Right should be DataFrameOrSeries type: {type(right)}')
    right_data = {
        label: series for label, series in right_data.items()
        if label not in filter_columns_from_right
    }

    conflicting = set({**left_index, **left_data}.keys()).intersection(set({**right_index, **right_data}))
    new_index_list = _get_column_name_expr_dtype(left_index, conflicting, suffixes[0], 'l')
    new_index_list += _get_column_name_expr_dtype(right_index, conflicting, suffixes[1], 'r')
    new_data_list = _get_column_name_expr_dtype(left_data, conflicting, suffixes[0], 'l')
    new_data_list += _get_column_name_expr_dtype(right_data, conflicting, suffixes[1], 'r')
    _check_no_column_name_conflicts(new_index_list + new_data_list)
    return new_index_list, new_data_list


def _check_no_column_name_conflicts(result_columns: List[ResultColumn]):
    """ Helper of _determine_result_columns, checks that there are no duplicate names in the list.  """
    seen = set()
    for rc in result_columns:
        if rc.name in seen:
            raise ValueError(f'Names are not unique. Result contains {rc.name} multiple times')
        seen.add(rc.name)


def _get_filter_columns_from_right(left_on, right_on) -> Set[str]:
    """
    Helper of _determine_result_columns: get all columns that should not be included from the right df,
    as they are matched on the same column on the left.
    """
    left_on_pos = {label: i for i, label in enumerate(left_on)}
    right_on_pos = {label: i for i, label in enumerate(right_on)}
    # don't add a column from the right to the result if we are joining on that column and the column in
    # left has the same name
    filter_column_from_right = {
        label for label in right_on_pos.keys()
        if right_on_pos[label] == left_on_pos.get(label)
    }
    return filter_column_from_right


def _get_column_name_expr_dtype(
        source_series: Dict[str, BuhTuhSeries],
        conflicting_names: Set[str],
        suffix: str,
        table_alias: str
) -> List[ResultColumn]:
    """ Helper of _determine_result_columns. """
    new_index_list: List[ResultColumn] = []
    for index_name, series in source_series.items():
        new_name = index_name
        if index_name in conflicting_names:
            new_name = index_name + suffix
        new_index_list.append(
                ResultColumn(
                    name=new_name,
                    expression=series.expression.resolve_column_references(table_alias),
                    dtype=series.dtype
                )
        )
    return new_index_list


def merge(
        left: BuhTuhDataFrame,
        right: DataFrameOrSeries,
        how: str,
        on: Union[str, List[str], None],
        left_on: Union[str, List[str],  None],  # todo: also support array-like arguments?
        right_on: Union[str, List[str], None],
        left_index: bool,
        right_index: bool,
        suffixes: Tuple[str, str]
) -> BuhTuhDataFrame:
    """
    Join the left and right Dataframes, or a DataFrame (left) and a Series (right). This will return a new
    DataFrame that contains the combined columns of both dataframes, and the rows that result from joining
    on the specified columns. The columns that are joined on can consists (partially or fully) out of index
    columns.

    If the column names on the left and right conflict, then the suffixes are used to distinguish them in the
    resulting DataFrame. The algorithm for determining the resulting columns and their names is similar to
    Pandas, but has slight differences when joining on indices and column names conflict.

    :param left: left DataFrame
    :param right: DataFrame or Series to join on left
    :param how: supported values: {‘left’, ‘right’, ‘outer’, ‘inner’, ‘cross’}
    :param on: optional, column(s) to join left and right on.
    :param left_on: optional, column(s) from the left df to join on
    :param right_on: optional, column(s) from the right df/series to join on
    :param left_index: If true uses the index of the left df as columns to join on
    :param right_index: If true uses the index of the right df/series as columns to join on
    :param suffixes: Tuple of two strings. Will be used to suffix duplicate column names. Must make column
        names unique
    :return: A new Dataframe. The original frames are not modified.
    """
    if how not in ('left', 'right', 'outer', 'inner', 'cross'):
        raise ValueError(f"how must be one of ('left', 'right', 'outer', 'inner', 'cross'), value: {how}")
    if left.group_by or right.group_by:
        raise ValueError('merge not supported for aggregated frames that have not been materialized')
    real_how = How(how)
    real_left_on, real_right_on = _determine_left_on_right_on(
        left=left,
        right=right,
        how=real_how,
        on=on,
        left_on=left_on,
        right_on=right_on,
        left_index=left_index,
        right_index=right_index
    )
    new_index_list, new_data_list = _determine_result_columns(
        left=left, right=right, left_on=real_left_on, right_on=real_right_on, suffixes=suffixes
    )

    model = _get_merge_sql_model(
        left=left,
        right=right,
        how=real_how,
        real_left_on=real_left_on,
        real_right_on=real_right_on,
        new_column_list=new_index_list + new_data_list
    )

    return BuhTuhDataFrame.get_instance(
        engine=left.engine,
        base_node=model,
        index_dtypes={rc.name: rc.dtype for rc in new_index_list},
        dtypes={rc.name: rc.dtype for rc in new_data_list},
        group_by=None,
        order_by=[]  # merging resets any sorting
    )


def _get_merge_sql_model(
        left: BuhTuhDataFrame,
        right: DataFrameOrSeries,
        how: How,
        real_left_on: List[str],
        real_right_on: List[str],
        new_column_list: List[ResultColumn],
) -> SqlModel:
    """
    Give the SqlModel to join left and right and select the new_column_list. This model also uses the
    join-type of how, matching rows on real_left_on and real_right_on.
    """
    merge_conditions = []
    for l_label, r_label in zip(real_left_on, real_right_on):
        l_expr = _get_expression(df_series=left, label=l_label)
        r_expr = _get_expression(df_series=right, label=r_label)
        merge_conditions.append(l_expr.resolve_column_references("l"))
        merge_conditions.append(r_expr.resolve_column_references("r"))

    if merge_conditions:
        fmt_str = 'on ' + 'and '.join(['({} = {})'] * (len(merge_conditions)//2))
        on_expr = Expression.construct(fmt_str, *merge_conditions)
    else:
        on_expr = Expression.construct('')

    columns_fmt_str = ", ".join(f'{{}} as {quote_identifier(rc.name)}' for rc in new_column_list)
    columns_expr = Expression.construct(columns_fmt_str, *[rc.expression for rc in new_column_list])
    join_type_expr = Expression.construct('full outer' if how == How.outer else how.value)

    sql = '''
        select {columns}
        from {{left_node}} as l {join_type}
        join {{right_node}} as r {on}
        '''
    model_builder = CustomSqlModel(name='merge_sql', sql=sql)
    model = model_builder(
        columns=columns_expr,
        join_type=join_type_expr,
        on=on_expr,
        left_node=left.base_node,
        right_node=right.base_node
    )
    return model


def _get_expression(df_series: DataFrameOrSeries, label: str) -> Expression:
    """ Helper of merge: give the expression for the column with the given label in df_series """
    if df_series.index and label in df_series.index:
        return df_series.index[label].expression
    if isinstance(df_series, BuhTuhDataFrame):
        return df_series.data[label].expression
    if isinstance(df_series, BuhTuhSeries):
        return df_series.expression
    raise TypeError(f'df_series should be DataFrameOrSeries. type: {type(df_series)}')
