from copy import copy
from enum import Enum
from typing import List, Dict, Optional, cast, TypeVar

from sqlalchemy.engine import Dialect

from bach import SeriesAbstractMultiLevel, SortColumn
from bach.series import Series
from bach.expression import Expression, WindowFunctionExpression
from bach.sql_model import BachSqlModel
from sql_models.util import is_postgres, is_bigquery, DatabaseNotSupportedException

G = TypeVar('G', bound='GroupBy')


class WindowFunction(Enum):
    FIRST_VALUE = 'first_value'
    LAST_VALUE = 'last_value'
    NTH_VALUE = 'nth_value'
    LEAD = 'lead'
    LAG = 'lag'

    RANK = 'rank'
    DENSE_RANK = 'dense_rank'
    PERCENT_RANK = 'percent_rank'
    CUME_DIST = 'cume_dist'
    NTILE = 'ntile'
    ROW_NUMBER = 'row_number'

    _BQ_FUNCTIONS_THAT_DO_NOT_SUPPORT_WINDOW_FRAME_CLAUSE = (
        RANK,
        DENSE_RANK,
        PERCENT_RANK,
        CUME_DIST,
        NTILE,
        ROW_NUMBER,
        LAG,
        LEAD,
    )

    def supports_window_frame_clause(self, dialect: Dialect) -> bool:
        if is_bigquery(dialect):
            return (
                self.value not in WindowFunction._BQ_FUNCTIONS_THAT_DO_NOT_SUPPORT_WINDOW_FRAME_CLAUSE.value
            )

        if is_postgres(dialect):
            return True
        raise DatabaseNotSupportedException(dialect)


class WindowFrameMode(Enum):
    """
    Class representing the frame mode in a Window
    """
    ROWS = 0
    RANGE = 1


class WindowFrameBoundary(Enum):
    """
    Class representing the frame boundaries in a Window
        """

    # Order is important here (see third restriction above)
    PRECEDING = 0
    CURRENT_ROW = 1
    FOLLOWING = 2

    def frame_clause(self, value: int = None) -> str:
        """
        Generate the frame boundary sub-string
        """
        if self == self.CURRENT_ROW:
            if value is not None:
                raise ValueError('Value not supported with CURRENT ROW')
            return 'CURRENT ROW'
        else:
            if value is None:
                return f'UNBOUNDED {self.name}'
            else:
                return f'{value} {self.name}'


class GroupBy:
    """
    Class to build GROUP BY expressions. This is the basic building block to create more complex
    expressions. This class represents a grouping/partitioning by columns/series or expressions
    thereof.

    For more complex grouping expressions, this class should be extended.

    Instances of this class and subclasses are **immutable**. Any modifying operations should
    return a fresh copy.
    """
    def __init__(self, group_by_columns: List[Series]):

        self._index = {}

        for col in group_by_columns:
            if not isinstance(col, Series):
                raise ValueError(f'Unsupported argument type: {type(col)}')

            if (
                isinstance(col, SeriesAbstractMultiLevel)
                and any(lvl.expression.is_constant for lvl in col.levels.values())
            ):
                raise ValueError(
                    'Level in multi-level series has a constant expression, '
                    'please materialize first.'
                )
            if col.expression.is_constant:
                # We don't support this currently. If we allow this we would generate sql of the form (this
                # assumes the constants is '5'): `... group by (5)`. The sql is valid, it groups by the
                # fifth column of the query. But it doesn't make any sense to support that, the user should
                # be explicit in naming the columns that he wants to group on.
                raise ValueError('Grouping on a Series whose expression is a constant, is not supported.')
            if col.expression.has_windowed_aggregate_function:
                raise ValueError('Window functions can not be used to group, '
                                 'please materialize first.')
            if col.expression.has_aggregate_function:
                raise ValueError('Aggregate functions can not be used to group, '
                                 'please materialize first.')

            # index columns have no index themselves, and can also be evaluated without group_by as
            # they will not be aggregated by this group_by
            self._index[col.name] = col.copy_override(index={}, group_by=None, order_by=[])

    @property
    def index(self) -> Dict[str, Series]:
        return copy(self._index)

    def __eq__(self, other):
        if not isinstance(other, GroupBy):
            return False
        return (
            list(self._index.keys()) == list(other.index.keys()) and
            all(self._index[n].equals(other.index[n], recursion='GroupBy')
                for n in self._index.keys())
        )

    def get_index_expressions(self) -> List[Expression]:
        from bach.series import SeriesAbstractMultiLevel
        exprs = []
        for idx in self.index.values():
            if isinstance(idx, SeriesAbstractMultiLevel):
                exprs += idx.level_expressions
                continue

            # BigQuery MUST use a reference for considering expression in GROUP BY clause
            # for example:
            # a) SELECT `x` + 1 as `x`, sum(y) from table GROUP BY `x`
            # is not equivalent to:
            # b) SELECT `x` + 1 as `x`, sum(y) from table GROUP BY `x` + 1
            # GROUP BY expression from b) actually is (`x` + 1) + 1
            # meanwhile GROUP BY expression from a) is (`x` + 1)
            # this logic does not applies in Postgres
            if is_bigquery(idx.engine):
                exprs.append(Expression.column_reference(idx.name))
            else:
                exprs.append(idx.expression)

        return exprs

    def get_group_by_column_expression(self) -> Optional[Expression]:
        """
        Get the group_by expression, including all the relevant columns and the way of grouping,
        but without the "group by" clause, as these potentially have to be nested into one group-by.

        Will return None if self.index is empty, i.e. there was a group-by but no columns are
        specified.
        """
        if not self.index:
            return None

        exprs = self.get_index_expressions()
        fmt_strs = ['{}'] * len(exprs)

        fmtstr = ', '.join(fmt_strs)
        return Expression.construct(f'{fmtstr}', *exprs)

    def copy_override_base_node(self: G, base_node: BachSqlModel) -> G:
        new_cols = [col.copy_override(base_node=base_node) for col in self.index.values()]
        return self.__class__(group_by_columns=new_cols)


class Cube(GroupBy):
    """
    Very simple abstraction to support cubes
    """
    def __init__(self, group_by_columns: List[Series]):
        if len(group_by_columns) == 0:
            raise ValueError('Can not create a cube without group by columns')
        super().__init__(group_by_columns)

    def get_group_by_column_expression(self) -> Optional[Expression]:
        # help mypy, our parent always returns an Expression
        return Expression.construct('cube ({})', cast(Expression, super().get_group_by_column_expression()))


class Rollup(GroupBy):
    """
    Very simple abstraction to support rollups
    """

    def __init__(self, group_by_columns: List[Series]):
        if len(group_by_columns) == 0:
            raise ValueError('Can not create a rollup without group by columns')
        super().__init__(group_by_columns)

    def get_group_by_column_expression(self) -> Optional[Expression]:
        # help mypy, our parent always returns an Expression
        return Expression.construct('rollup ({})', cast(Expression, super().get_group_by_column_expression()))


class GroupingList(GroupBy):
    """
    Abstraction to support SQL's
    GROUP BY (colA,colB), CUBE(ColC,ColD), ROLLUP(ColC,ColE)
    like expressions
    """
    _grouping_list: List[GroupBy]

    def __init__(self, grouping_list: List[GroupBy]):
        """
        Given the list of groupbys, construct a combined groupby
        """
        self._grouping_list = grouping_list

        group_by_columns = {}

        for g in grouping_list:
            if not isinstance(g, GroupBy):
                raise ValueError("Only GroupBy items are supported")

            for name, series in g._index.items():
                if name not in group_by_columns:
                    group_by_columns[name] = series

        super().__init__(group_by_columns=list(group_by_columns.values()))

    def get_group_by_column_expression(self) -> Optional[Expression]:
        grouping_optional_expr_list = [g.get_group_by_column_expression() for g in self._grouping_list]
        grouping_expr_list: List[Expression] = []
        for expr in grouping_optional_expr_list:
            if expr is None:
                grouping_expr_list.append(Expression.construct(''))
            else:
                grouping_expr_list.append(expr)

        fmtstr = ', '.join(["({})"] * len(grouping_expr_list))
        return Expression.construct(fmtstr, *grouping_expr_list)


class GroupingSet(GroupingList):
    """
    Abstraction to support SQLs
    GROUP BY GROUPING SETS ((colA,colB),(ColA),(ColC))
    """
    def get_group_by_column_expression(self) -> Optional[Expression]:
        grouping_optional_expr_list = [g.get_group_by_column_expression() for g in self._grouping_list]
        grouping_expr_list: List[Expression] = []
        for expr in grouping_optional_expr_list:
            if expr is None:
                grouping_expr_list.append(Expression.construct(''))
            else:
                grouping_expr_list.append(expr)

        fmtstr = ', '.join(["({})"] * len(grouping_expr_list))
        fmtstr = f'grouping sets ({fmtstr})'
        return Expression.construct(fmtstr, *grouping_expr_list)


class Window(GroupBy):
    """
    Class representing an "immutable" window as defined in the SQL standard. Any operation on this
    class that would alter it returns a fresh copy. It can be reused many time if the window
    is reused.

    A Window for us is basically a partitioned, sorted view on a DataFrame, where the frame
    boundaries as given in the constructor, or in set_frame_clause(), define the window.

    A frame is defined in PG as follows:
    (See https://www.postgresql.org/docs/14/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS)

    { RANGE | ROWS } frame_start
    { RANGE | ROWS } BETWEEN frame_start AND frame_end
    where frame_start and frame_end can be one of

    UNBOUNDED PRECEDING
    value PRECEDING
    CURRENT ROW
    value FOLLOWING
    UNBOUNDED FOLLOWING

    The frame_clause specifies the set of rows constituting the window frame, for those window
    functions that act on the frame instead of the whole partition.

    If frame_end is omitted it
    defaults to CURRENT ROW.

    Restrictions are that
    - frame_start cannot be UNBOUNDED FOLLOWING,
    - frame_end cannot be UNBOUNDED PRECEDING
    - frame_end choice cannot appear earlier in the above list than the frame_start choice:
        for example RANGE BETWEEN CURRENT ROW AND value PRECEDING is not allowed.

    The default framing option is RANGE UNBOUNDED PRECEDING, which is the same as
    RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW; it sets the frame to be all rows from
    the partition start up through the current row's last peer in the ORDER BY ordering
    (which means all rows if there is no ORDER BY).

    In general, UNBOUNDED PRECEDING means that the frame starts with the first row of the
    partition, and similarly UNBOUNDED FOLLOWING means that the frame ends with the last row
    of the partition (regardless of RANGE or ROWS mode).

    In ROWS mode, CURRENT ROW means that the frame starts or ends with the current row;
    In RANGE mode it means that the frame starts or ends with the current row's first or
    last peer in the ORDER BY ordering.

    The value PRECEDING and value FOLLOWING cases are currently only allowed in ROWS mode.
    They indicate that the frame starts or ends with the row that many rows before or after
    the current row.

    value must be an integer expression not containing any variables, aggregate functions,
    or window functions. The value must not be null or negative; but it can be zero,
    which selects the current row itself.
    """
    def __init__(self,
                 group_by_columns: List['Series'],
                 order_by: List[SortColumn],
                 nulls_last: bool = False,
                 mode: WindowFrameMode = WindowFrameMode.RANGE,
                 start_boundary: Optional[WindowFrameBoundary] = WindowFrameBoundary.PRECEDING,
                 start_value: int = None,
                 end_boundary: Optional[WindowFrameBoundary] = WindowFrameBoundary.CURRENT_ROW,
                 end_value: int = None,
                 min_values: int = None):
        """
        Define a window on a DataFrame, by giving the partitioning series and the frame definition
        :see: class definition for more info on the frame definition, and GroupBy for more
              info on grouping / partitioning
        """
        super().__init__(group_by_columns=group_by_columns)

        if mode is None:
            raise ValueError("Mode needs to be defined")

        if start_boundary is None and end_boundary is not None:
            raise ValueError("start_boundary needs to be defined if end_boundary is present.")

        if start_boundary == WindowFrameBoundary.FOLLOWING and start_value is None:
            raise ValueError("Start of frame can not be unbounded following")

        if end_boundary == WindowFrameBoundary.PRECEDING and end_value is None:
            raise ValueError("End of frame can not be unbounded preceding")

        if (start_value is not None and start_value < 0) or \
                (end_value is not None and end_value < 0):
            raise ValueError("start_value and end_value must be greater than or equal to zero.")

        if mode == WindowFrameMode.RANGE \
                and (start_value is not None or end_value is not None):
            raise ValueError("start_value or end_value cases only supported in ROWS mode.")

        if start_boundary is not None and end_boundary is not None:
            if start_boundary.value > end_boundary.value:
                raise ValueError("frame boundaries defined in wrong order.")

            if start_boundary == end_boundary:
                if start_boundary == WindowFrameBoundary.PRECEDING \
                        and start_value is not None \
                        and end_value is not None \
                        and start_value < end_value:
                    raise ValueError("frame boundaries defined in wrong order.")

            if start_boundary == end_boundary:
                if start_boundary == WindowFrameBoundary.FOLLOWING \
                        and start_value is not None \
                        and end_value is not None \
                        and start_value > end_value:
                    raise ValueError("frame boundaries defined in wrong order.")

        self._mode = mode
        self._start_boundary = start_boundary
        self._start_value = start_value
        self._end_boundary = end_boundary
        self._end_value = end_value
        self._min_values = 0 if min_values is None else min_values

        # TODO This should probably be an expression
        self._frame_clause: str = ''
        if start_boundary and end_boundary is None:
            self._frame_clause = f'{mode.name} {start_boundary.frame_clause(start_value)}'
        elif start_boundary and end_boundary:
            self._frame_clause = f'{mode.name} BETWEEN {start_boundary.frame_clause(start_value)}'\
                                f' AND {end_boundary.frame_clause(end_value)}'

        self._order_by = order_by
        self._nulls_last = nulls_last

    @property
    def frame_clause(self) -> str:
        return self._frame_clause

    @property
    def order_by(self) -> List[SortColumn]:
        return self._order_by

    @property
    def min_values(self) -> int:
        return self._min_values

    def set_frame_clause(self,
                         mode:
                         WindowFrameMode = WindowFrameMode.RANGE,
                         start_boundary:
                         Optional[WindowFrameBoundary] = WindowFrameBoundary.PRECEDING,
                         start_value: int = None,
                         end_boundary:
                         Optional[WindowFrameBoundary] = WindowFrameBoundary.CURRENT_ROW,
                         end_value: int = None) -> 'Window':
        """
        Convenience function to clone this window with new frame parameters
        :see: __init__()
        """
        return Window(group_by_columns=list(self._index.values()),
                      order_by=self._order_by,
                      nulls_last=self._nulls_last,
                      mode=mode,
                      start_boundary=start_boundary, start_value=start_value,
                      end_boundary=end_boundary, end_value=end_value)

    def _get_order_by_expression(self) -> Expression:
        """
        Get a properly formatted order by clause based on this df's order_by.
        Will return an empty string in case ordering in not requested.
        """
        if self._order_by:
            exprs = [sc.expression for sc in self._order_by]
            nulls_last_stmt = 'nulls last' if self._nulls_last else ''
            fmtstr = [
                f"{{}} {'asc' if sc.asc else 'desc'} {nulls_last_stmt}".strip()
                for sc in self._order_by
            ]
            return Expression.construct(f'order by {", ".join(fmtstr)}', *exprs)
        else:
            return Expression.construct('')

    def get_index_expressions(self) -> List[Expression]:
        from bach.series import SeriesAbstractMultiLevel
        exprs = []
        for idx in self.index.values():
            if isinstance(idx, SeriesAbstractMultiLevel):
                exprs += idx.level_expressions
                continue

            exprs.append(idx.expression)

        return exprs

    def get_window_expression(self, window_func: Expression) -> Expression:
        """
        Given the window_func generate a statement like:
            {window_func} OVER (PARTITION BY .. ORDER BY ... frame_clause)
        """
        # TODO implement NULLS FIRST / NULLS LAST, probably not here but in the sorting logic.
        order_by = self._get_order_by_expression()

        if self.frame_clause is None:
            frame_clause = ''
        else:
            frame_clause = self.frame_clause

        index_exprs = []
        if len(self._index) == 0:
            partition_fmt = ''
        else:
            index_exprs = self.get_index_expressions()
            fmt_stmts = ['{}'] * len(index_exprs)
            partition_fmt = 'partition by ' + ', '.join(fmt_stmts)

        over_fmt = f'over ({partition_fmt} {{}} {frame_clause})'
        over_expr = Expression.construct(over_fmt, *index_exprs, order_by)

        if self._min_values is None or self._min_values == 0:
            return WindowFunctionExpression.construct(f'{{}} {{}}', window_func, over_expr)
        else:
            # Only return a value when then minimum amount of observations (including NULLs)
            # has been reached.
            return WindowFunctionExpression.construct(f"""
                case when (count(1) {{}}) >= {self._min_values}
                then {{}} {{}}
                else NULL end""", over_expr, window_func, over_expr)

    def get_group_by_column_expression(self) -> Optional[Expression]:
        """
        On a Window, there is no default group_by clause
        """
        return None
