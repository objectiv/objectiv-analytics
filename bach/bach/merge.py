"""
Copyright 2021 Objectiv B.V.
"""
import itertools
from copy import copy
from enum import Enum
from typing import Union, List, Tuple, Optional, Dict, Set, Hashable, cast, NamedTuple, Sequence, Mapping

from sqlalchemy.engine import Dialect

from bach import DataFrameOrSeries, DataFrame, ColumnNames, Series, SeriesBoolean
from bach.dataframe import DtypeNamePair

from bach.expression import (
    Expression, join_expressions, TableColumnReferenceToken,  ExpressionToken, ColumnReferenceToken,
)
from bach.utils import ResultSeries, get_result_series_dtype_mapping
from sql_models.constants import NotSet, not_set
from sql_models.model import Materialization, CustomSqlModelBuilder, SqlModel, SqlModelSpec
from bach.sql_model import BachSqlModel, construct_references


class How(Enum):
    """ Enum with all valid values of 'how' parameter """
    left = 'left'
    right = 'right'
    outer = 'outer'
    inner = 'inner'
    cross = 'cross'


_LEFT_NODE_ALIAS = 'l'
_RIGHT_NODE_ALIAS = 'r'


class MergeOn(NamedTuple):
    left: List[str]
    right: List[str]
    conditional: List[SeriesBoolean]

    @property
    def is_empty(self) -> bool:
        return not (self.left or self.right or self.conditional)


def _verify_on_conflicts(
    left: DataFrame,
    right: DataFrameOrSeries,
    how: How,
    on: Optional[Sequence[Union[str, SeriesBoolean]]],
    left_on: Optional[ColumnNames],
    right_on: Optional[ColumnNames],
    left_index: bool,
    right_index: bool,
) -> None:
    """
    Verifies that provided on parameters are valid for merge operation.
    Rules for valid merge:
        1. Any of "on", "left_on", "left_index", "right_on", "right_index"
            should be provided if how != 'cross'
        2. Both "left_on" and "left_index" must not be specified at the same time.
        3. Both "right_on" and "right_index" must not be specified at the same time.
        4. If "left_on"/"left_index" is specified, "right_on"/"right_index" must be specified as well.
        5. If "on" is specified (ignoring SeriesBoolean):
            "left_on", "left_index", "right_on", "right_index" must be None
        6. If "on" contains SeriesBoolean, each series should make reference to both left and right objects to
           be merged.
    """
    if how == How.cross and (on or left_on or right_on or left_index or right_index):
        raise ValueError(
            'Cannot specify on, left_on, right_on, left_index, or right_index if how == "cross"'
        )

    if (left_on is not None) and left_index:
        raise ValueError('Cannot specify both left_on and left_index.')

    if (right_on is not None) and right_index:
        raise ValueError('Cannot specify both right_on and right_index.')

    if bool(left_on or left_index) ^ bool(right_on or right_index):
        raise ValueError(
            'Either both left_on/left_index and right_on/right_index should be specified, '
            'or both should be None.'
        )

    on_conditions = [o for o in on or [] if isinstance(o, SeriesBoolean)] if on else []
    on_columns = [o for o in on or [] if not isinstance(o, SeriesBoolean)] if on else None

    if on_columns and (left_on or left_index) and (right_on or right_index):
        raise ValueError('Either specify on or, left_on and right_on, but not all three')

    if not on_conditions:
        return None

    if on_conditions and left.base_node == right.base_node:
        raise ValueError('"on" based SeriesBooleans is valid only when left.base_node != right.base_node. ')

    for col in on_conditions:
        refs = col.base_node.references.values()
        if not (left.base_node in refs and right.base_node in refs):
            raise ValueError('boolean series must have both base_nodes to be merged as references.')


def _determine_merge_on(
    left: DataFrame,
    right: DataFrameOrSeries,
    how: How,
    on: Optional[Sequence[Union[str, SeriesBoolean]]],
    left_on: Optional[ColumnNames],
    right_on: Optional[ColumnNames],
    left_index: bool,
    right_index: bool,
) -> MergeOn:
    """
    Determine the columns that should be equal for the merge. Both for the left and the right
    dataframe/series a list of strings is returned indicating the names of the columns that should be
    matched.
    :return: Tuple containing left, right and conditional on
    """
    _verify_on_conflicts(
        left=left,
        right=right,
        how=how,
        on=on,
        left_on=left_on,
        right_on=right_on,
        left_index=left_index,
        right_index=right_index,
    )
    if how == How.cross:
        return MergeOn(left=[], right=[], conditional=[])

    left_on = left_on or list(_get_index_names(left)) if left_on or left_index else None
    right_on = right_on or list(_get_index_names(right)) if right_on or right_index else None

    if on is not None:
        final_on = [o for o in on or [] if not isinstance(o, SeriesBoolean)]
    else:
        final_on = list(_get_data_columns(left) & _get_data_columns(right))

    final_left_on = _get_x_on(final_on, left_on, 'left_on')
    final_right_on = _get_x_on(final_on, right_on, 'right_on')

    if len(final_left_on) != len(final_right_on):
        raise ValueError(
            f'Len of left_on ({final_left_on}) does not match that of right_on ({final_right_on}).')

    on_conditions = [o for o in on or [] if isinstance(o, SeriesBoolean)] if on else []

    if not final_left_on and not on_conditions:
        raise ValueError('No columns to perform merge on')

    missing_left = set(final_left_on) - _get_all_series_names(left)
    missing_right = set(final_right_on) - _get_all_series_names(right)

    if missing_left:
        raise ValueError(f'Specified column(s) do not exist. left_on: {left_on}. missing: {missing_left}')
    if missing_right:
        raise ValueError(f'Specified column(s) do not exist. right_on: {right_on}. missing: {missing_right}')

    return MergeOn(left=final_left_on, right=final_right_on, conditional=on_conditions)


def _get_data_columns(df_series: DataFrameOrSeries) -> Set[str]:
    """ Get set with the names of all data columns. Works for both dataframe and series. """
    if isinstance(df_series, DataFrame):
        return set(df_series.data_columns)
    if isinstance(df_series, Series):
        return {df_series.name}
    raise TypeError(f'Expected bach.DataFrame or bach.Series, got {type(df_series)}')


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


def _determine_result_columns(
    dialect: Dialect,
    left: DataFrame,
    right: DataFrameOrSeries,
    merge_on: MergeOn,
    suffixes: Tuple[str, str],
) -> Tuple[List[ResultSeries], List[ResultSeries]]:
    """
    Determine which columns should be in the DataFrame after merging left and right, with the given
    left_on and right_on values.
    """
    if not isinstance(right, (DataFrame, Series)):
        raise TypeError(f'Right should be DataFrameOrSeries type: {type(right)}')

    left_df = left.copy()
    right_df = right.copy() if isinstance(right, DataFrame) else right.to_frame()

    conflicting_on = {l_on for l_on, r_on in zip(merge_on.left, merge_on.right) if l_on == r_on}
    conflicting = (
        (set(left_df.index) | set(left_df.data)) & (set(right_df.index) | set(right_df.data))
    )
    # don't add suffixes to conflicted on columns
    # need to consider values from both objects (important when how = How.outer)
    conflicting -= conflicting_on

    # left dataframe has priority over index and data columns
    # final shared index and data series are based on left dataframe structure
    right_index = {}
    right_data = {}
    for series_name, series in right_df.all_series.items():
        data_columns = left_df.data_columns if series_name in conflicting_on else right_df.data_columns
        if series_name in data_columns:
            right_data[series_name] = series
        else:
            right_index[series_name] = series

    new_index_list = _get_merged_result_series(
        dialect=dialect,
        left_series=left_df.index,
        right_series=right_index,
        suffixes=suffixes,
        conflicting_names=conflicting,
        conflicting_on=conflicting_on,
    )

    new_data_list = _get_merged_result_series(
        dialect=dialect,
        left_series=left_df.data,
        right_series=right_data,
        suffixes=suffixes,
        conflicting_names=conflicting,
        conflicting_on=conflicting_on,
    )

    _check_no_column_name_conflicts(new_index_list + new_data_list)
    return new_index_list, new_data_list


def _check_no_column_name_conflicts(result_columns: List[ResultSeries]):
    """ Helper of _determine_result_columns, checks that there are no duplicate names in the list.  """
    seen = set()
    for rc in result_columns:
        if rc.name in seen:
            raise ValueError(f'Names are not unique. Result contains {rc.name} multiple times')
        seen.add(rc.name)


def _get_merged_result_series(
    dialect: Dialect,
    left_series: Dict[str, Series],
    right_series: Dict[str, Series],
    conflicting_names: Set[str],
    conflicting_on: Set[str],
    suffixes: Tuple[str, str],
) -> List[ResultSeries]:
    """ Helper of _determine_result_columns. """
    new_column_results: List[ResultSeries] = []
    for suffix, source_series in zip(suffixes, (left_series, right_series)):
        table_alias = _LEFT_NODE_ALIAS if suffix == suffixes[0] else _RIGHT_NODE_ALIAS
        for series_name, series in source_series.items():
            new_name = series_name
            expr = series.expression.resolve_column_references(dialect, table_alias)

            if series_name in conflicting_on:
                if table_alias == _RIGHT_NODE_ALIAS:
                    continue
                r_expr = right_series[series_name].expression.resolve_column_references(
                    dialect, _RIGHT_NODE_ALIAS,
                )
                expr = Expression.construct(f'COALESCE({{}}, {{}})', expr, r_expr)
            elif series_name in conflicting_names:
                new_name = series_name + suffix

            new_column_results.append(
                ResultSeries(
                    name=new_name,
                    expression=expr,
                    dtype=series.dtype,
                )
            )
    return new_column_results


def merge(
    left: DataFrame,
    right: DataFrameOrSeries,
    how: str,
    on: Union[str, 'SeriesBoolean', List[Union[str, 'SeriesBoolean']], None],
    left_on: Union[str, List[str],  None],  # todo: also support array-like arguments?
    right_on: Union[str, List[str], None],
    left_index: bool,
    right_index: bool,
    suffixes: Tuple[str, str]
) -> DataFrame:
    """
    See :py:meth:`bach.DataFrame.merge` for more information.
    """
    if how not in ('left', 'right', 'outer', 'inner', 'cross'):
        raise ValueError(f"how must be one of ('left', 'right', 'outer', 'inner', 'cross'), value: {how}")

    if left.group_by:
        left = left.materialize(node_name='merge_left')

    if right.group_by:
        if isinstance(right, Series):
            right = right.to_frame()
        right = right.materialize(node_name='merge_right')

    dialect = left.engine.dialect

    real_how = How(how)
    merge_on = _determine_merge_on(
        left=left,
        right=right,
        how=real_how,
        on=[on] if on is not None and not isinstance(on, list) else on,
        left_on=left_on,
        right_on=right_on,
        left_index=left_index,
        right_index=right_index
    )

    new_index_list, new_data_list = _determine_result_columns(
        dialect=dialect,
        left=left,
        right=right,
        merge_on=merge_on,
        suffixes=suffixes,
    )

    if isinstance(right, Series):
        from bach.savepoints import Savepoints
        right_savepoints = Savepoints()
        right_variables = {}
    else:
        right_savepoints = right.savepoints
        right_variables = right.variables
    # copy right_variables, and then overwrite with left. This means that the left variables 'win' in case
    # where the same variable name/dtype exist in both left and right
    variables = copy(right_variables)
    variables.update(left.variables)

    model = _get_merge_sql_model(
        dialect=dialect,
        left=left,
        right=right,
        how=real_how,
        merge_on=merge_on,
        new_column_list=new_index_list + new_data_list,
        variables=variables
    )

    return left.copy_override(
        engine=left.engine,
        base_node=model,
        index_dtypes=get_result_series_dtype_mapping(new_index_list),
        series_dtypes=get_result_series_dtype_mapping(new_data_list),
        group_by=None,
        order_by=[],  # merging resets any sorting
        savepoints=left.savepoints.merge(right_savepoints),
        variables=variables
    )


def revert_merge(base: DataFrame) -> Tuple[DataFrame, DataFrame]:
    """
    Splits a merged dataframe into two new frames that have the same structure as the original frames
    that were combined. Base dataframe should not be aggregated since original indexes can be lost.
    """
    if not isinstance(base.base_node, MergeSqlModel):
        raise Exception('can only revert merge if DataFrame base_node is MergeSqlModel instance.')

    if base.group_by:
        raise Exception('cannot revert merge on aggregated frame.')

    left_node = cast(BachSqlModel, base.base_node.references['left_node'])
    right_node = cast(BachSqlModel, base.base_node.references['right_node'])

    left_index, right_index = _determine_series_per_source(
        base=base, series_to_unmerge=base.index_columns, left_index={}, right_index={},
    )

    left_series, right_series = _determine_series_per_source(
        base=base,
        series_to_unmerge=list(set(base.base_node.columns) - set(base.index_columns)),
        left_index=left_index,
        right_index=right_index,
    )

    left = base.copy_override(base_node=left_node, series=left_series, index=left_index)
    right = base.copy_override(base_node=right_node, series=right_series, index=right_index)

    return left, right


def _determine_series_per_source(
    base: 'DataFrame',
    series_to_unmerge: List[str],
    left_index: Dict[str, 'Series'],
    right_index: Dict[str, 'Series'],
) -> Tuple[Dict[str, 'Series'], Dict[str, 'Series']]:
    """
    Determine which series are on each original dataframe based on the node references
    from current MergeSqlModel. When identifying each column original source, a new series
    will be created and replicate the original structure.

    .. note::
    Series without table column references are added to both final results.
    """

    left_series = {}
    right_series = {}

    left_node = cast(BachSqlModel, base.base_node.references['left_node'])
    right_node = cast(BachSqlModel, base.base_node.references['right_node'])

    expressions_to_parse: Dict[str, List[Expression]] = {}

    merge_node = cast(MergeSqlModel, base.base_node)
    merge_on = merge_node.merge_on

    coalesced_series = [
        left_on for left_on, right_on in zip(merge_on.left, merge_on.right) if left_on == right_on
    ]
    for series_name, original_expr in base.base_node.column_expressions.items():
        if series_name not in series_to_unmerge:
            continue

        if series_name not in coalesced_series:
            expressions_to_parse[series_name] = [original_expr]
            continue

        # removes first-level tokens from COALESCE expression
        # I.e COALESCE(expr1, expr2)
        # expression_to_parse[series] = [expr1, expr2]
        expressions_to_parse[series_name] = [
            sub_expr
            for sub_expr in original_expr.data
            if isinstance(sub_expr, Expression)
        ]

    default_series = base.all_series[base.data_columns[0]]
    for series_name, expressions in expressions_to_parse.items():
        if series_name in base.all_series:
            series = base.all_series[series_name]
        else:
            series = default_series.copy()

        for sub_expr in expressions:
            table_name, column_name, expr = sub_expr.remove_table_column_references()

            column_name = column_name if sub_expr.has_table_column_references else series_name
            if table_name == _LEFT_NODE_ALIAS or not sub_expr.has_table_column_references:
                left_series[column_name] = series.copy_override(
                    base_node=left_node,
                    index=left_index,
                    name=column_name,
                    expression=expr,
                )
            if table_name == _RIGHT_NODE_ALIAS or not sub_expr.has_table_column_references:
                right_series[column_name] = series.copy_override(
                    base_node=right_node,
                    index=right_index,
                    name=column_name,
                    expression=expr,
                )

    # sort mapping based in order from node's columns
    ordered_left_series = {
        **{col: left_series[col] for col in left_node.columns if col in left_series},
        **{
            series_name: series for series_name, series in left_series.items()
            if series_name not in left_node.columns
        },
    }
    ordered_right_series = {
        **{col: right_series[col] for col in right_node.columns if col in right_series},
        **{
            series_name: series for series_name, series in right_series.items()
            if series_name not in right_node.columns
        },
    }
    return ordered_left_series, ordered_right_series


def _get_merge_sql_model(
    dialect: Dialect,
    left: DataFrame,
    right: DataFrameOrSeries,
    how: How,
    merge_on: MergeOn,
    new_column_list: List[ResultSeries],
    variables: Dict['DtypeNamePair', Hashable]
) -> BachSqlModel:
    """
    Give the SqlModel to join left and right and select the new_column_list. This model also uses the
    join-type of how, matching rows on real_left_on and real_right_on.
    """
    if merge_on.is_empty:
        on_clause = Expression.construct('')
    else:
        on_clause = _get_merge_on_clause(dialect, left, right, merge_on)

    columns_expr = join_expressions(
        [Expression.construct_expr_as_name(rc.expression, rc.name) for rc in new_column_list]
    )
    join_type_expr = Expression.construct('full outer' if how == How.outer else how.value)

    return MergeSqlModel.get_instance(
        column_expressions={rc.name: rc.expression for rc in new_column_list},
        dialect=dialect,
        columns_expr=columns_expr,
        join_type_expr=join_type_expr,
        on_clause=on_clause,
        merge_on=merge_on,
        left_node=left.base_node,
        right_node=right.base_node,
        variables=variables,
    )


def _get_merge_on_clause(
    dialect: Dialect,
    left: DataFrame,
    right: DataFrameOrSeries,
    merge_on: MergeOn,
) -> Expression:
    """
    Generates the expression used as criteria to match rows when merging.
    """
    left_x_right_on_merge_expressions = list(itertools.chain.from_iterable(
        [
            _get_expression(df_series=left, label=l_label).resolve_column_references(
                dialect, _LEFT_NODE_ALIAS,
            ),
            _get_expression(df_series=right, label=r_label).resolve_column_references(
                dialect, _RIGHT_NODE_ALIAS,
            ),
        ]
        for l_label, r_label in zip(merge_on.left, merge_on.right)
    ))

    conditional_merge_expressions = _resolve_merge_expression_references(dialect, left, right, merge_on)

    all_conditions = (
        ['({} = {})'] * (len(left_x_right_on_merge_expressions) // 2)
        + ['({})'] * len(conditional_merge_expressions)
    )
    fmt_str = 'on ' + ' and '.join(all_conditions)

    return Expression.construct(
        fmt_str, *left_x_right_on_merge_expressions, *conditional_merge_expressions,
    )


def _resolve_merge_expression_references(
    dialect: Dialect,
    left: DataFrame,
    right: DataFrameOrSeries,
    merge_on: MergeOn
) -> List[Expression]:
    expressions = []
    df_series: DataFrameOrSeries
    for cond in merge_on.conditional:
        new_tokens: List[Union[ExpressionToken, 'Expression']] = []
        for token in cond.expression.get_all_tokens():
            if not isinstance(token, ColumnReferenceToken):
                new_tokens.append(token)
                continue

            prev_expression = cond.base_node.column_expressions[token.column_name]
            resolved_nested_tokens: List[Union[Expression, ExpressionToken]] = []

            for nested_token in prev_expression.get_all_tokens():
                if not isinstance(nested_token, TableColumnReferenceToken):
                    resolved_nested_tokens.append(nested_token)
                    continue

                ref_name = 'left_node' if nested_token.table_name == _LEFT_NODE_ALIAS else 'right_node'
                ref_node = cond.base_node.references[ref_name]

                if ref_node == left.base_node:
                    df_series = left
                    table_alias = _LEFT_NODE_ALIAS
                else:
                    df_series = right
                    table_alias = _RIGHT_NODE_ALIAS

                # nested_token.column_name might not be the same to token.column_name
                # since series can be renamed
                expr_label = (
                    nested_token.column_name
                    if nested_token.column_name == cond.name
                    else token.column_name
                )
                resolved_expr = _get_expression(df_series=df_series, label=expr_label)
                resolved_expr = resolved_expr.resolve_column_references(dialect, table_alias)
                resolved_nested_tokens.append(resolved_expr)

            new_tokens.extend(resolved_nested_tokens)

        expressions.append(Expression(new_tokens))

    return expressions


def _get_expression(df_series: DataFrameOrSeries, label: str) -> Expression:
    """ Helper of merge: give the expression for the column with the given label in df_series """
    if df_series.index and label in df_series.index:
        return df_series.index[label].expression
    if isinstance(df_series, DataFrame):
        return df_series.data[label].expression
    if isinstance(df_series, Series):
        return df_series.expression
    raise TypeError(f'df_series should be DataFrameOrSeries. type: {type(df_series)}')


class MergeSqlModel(BachSqlModel):
    def __init__(self, merge_on: MergeOn, *args, **kwargs):
        self._merge_on = merge_on
        super().__init__(*args,  **kwargs)

    @property
    def merge_on(self) -> MergeOn:
        return self._merge_on

    @classmethod
    def get_instance(
        cls,
        *,
        dialect: Dialect,
        column_expressions: Dict[str, Expression],
        columns_expr: Expression,
        join_type_expr: Expression,
        on_clause: Expression,
        merge_on: MergeOn,
        left_node: BachSqlModel,
        right_node: BachSqlModel,
        variables: Dict['DtypeNamePair', Hashable],
    ) -> 'MergeSqlModel':
        """
        :param column_expressions: mapping between column_names and their expressions (in order)
        :param columns_expr: A single expression that expresses projecting all needed columns from either
            left or right
        :param join_type_expr: expression expressing the join type, e.g. an expression that represents
            the string 'inner', 'cross', or similar
        :param on_clause: single expression that expresses the on clause
        :param left_node, sql-model of the materialized left side of the join
        :param right_node, sql-model of the materialized right side of the join
        :param variables: Dictionary of all variable values
        """
        columns_str = columns_expr.to_sql(dialect)
        join_type_str = join_type_expr.to_sql(dialect)
        on_str = on_clause.to_sql(dialect)

        sql = f'''
            select {columns_str}
            from {{{{left_node}}}} as l {join_type_str}
            join {{{{right_node}}}} as r {on_str}
            '''
        name = 'merge_sql'

        # Add all references found in the Expressions to self.references
        all_expressions = [columns_expr, join_type_expr, on_clause]
        references = construct_references(
            base_references={'left_node': left_node, 'right_node': right_node},
            expressions=all_expressions
        )

        return MergeSqlModel(
            model_spec=CustomSqlModelBuilder(sql=sql, name=name),
            placeholders=cls._get_placeholders(dialect, variables, all_expressions),
            references=references,
            materialization=Materialization.CTE,
            materialization_name=None,
            column_expressions=column_expressions,
            merge_on=merge_on,
        )

    def copy_override(
        self: 'MergeSqlModel',
        *,
        model_spec: SqlModelSpec = None,
        placeholders: Mapping[str, Hashable] = None,
        references: Mapping[str, 'SqlModel'] = None,
        materialization: Materialization = None,
        materialization_name: Union[Optional[str], NotSet] = not_set,
        column_expressions: Dict[str, Expression] = None,
        merge_on: MergeOn = None
    ) -> 'MergeSqlModel':
        """
        Similar to super class's implementation, but adds optional 'merge_on' parameter
        """
        materialization_name_value = (
            self.materialization_name if materialization_name is not_set else materialization_name
        )
        return self.__class__(
            model_spec=self.model_spec if model_spec is None else model_spec,
            placeholders=self.placeholders if placeholders is None else placeholders,
            references=self.references if references is None else references,
            materialization=self.materialization if materialization is None else materialization,
            materialization_name=materialization_name_value,
            column_expressions=self.column_expressions if column_expressions is None else column_expressions,
            merge_on=self.merge_on if merge_on is None else merge_on
        )
