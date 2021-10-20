from enum import Enum
from typing import List, Union, Dict, Any, Callable

from buhtuh import Expression
from buhtuh.pandasql import BuhTuhSeries, BuhTuhSeriesInt64, BuhTuhDataFrame, BuhTuhSeriesAbstractNumeric
from sql_models.model import CustomSqlModel


class BuhTuhWindowFrameMode(Enum):
    """
    Class representing the frame mode in a BuhTuhWindow
    """
    ROWS = 0
    RANGE = 1


class BuhTuhWindowFrameBoundary(Enum):
    """
    Class representing the frame boundaries in a BuhTuhWindow
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


class BuhTuhGroupBy:
    """
    Class to build GROUP BY expressions. This is the basic building block to create more complex
    expressions. This class represents a grouping/partitioning by columns/series or expressions
    thereof.

    For more complex grouping expressions, this class should be extended.
    """
    buh_tuh: BuhTuhDataFrame
    groupby: Dict[str, BuhTuhSeries]
    aggregated_data: Dict[str, BuhTuhSeries]

    def __init__(self,
                 buh_tuh: BuhTuhDataFrame,
                 group_by_columns: List[BuhTuhSeries]):
        self.buh_tuh = buh_tuh

        self.groupby = {}
        for col in group_by_columns:
            if not isinstance(col, BuhTuhSeries):
                raise ValueError(f'Unsupported groupby argument type: {type(col)}')
            assert col.base_node == buh_tuh.base_node
            self.groupby[col.name] = col

        if len(group_by_columns) == 0:
            # create new dummy column so we can aggregate over everything
            self.groupby = {
                'index': BuhTuhSeriesInt64.get_instance(base=buh_tuh,
                                                        name='index',
                                                        dtype='int64',
                                                        expression=Expression.construct('1'))
            }

        self.aggregated_data = {name: series
                                for name, series in buh_tuh.all_series.items()
                                if name not in self.groupby.keys()}

    def _get_group_by_expression(self):
        return ', '.join(g.get_expression() for g in self.groupby.values())

    def aggregate(self,
                  func: Union[str, Callable, List[Union[str, Callable]],
                              Dict[str, Union[str, Callable, List[Union[str, Callable]]]]],
                  *args,
                  **kwargs) -> BuhTuhDataFrame:
        return self.agg(func, *args, **kwargs)

    def agg(self,
            func: Union[str, Callable, List[Union[str, Callable]],
                        Dict[str, Union[str, Callable, List[Union[str, Callable]]]]],
            *args,
            **kwargs) -> BuhTuhDataFrame:
        """
        Aggregate using one or more operations over the specified axis.
        :param func:    function, str, list or dict
            Function to use for aggregating the data. If a function, must work when passed a
            BuhTuhSeries.

            Accepted combinations are:
            - function
            - string function name
            - list of functions and/or function names, e.g. [BuhTuhSeriesInt64.sum, 'mean']
            - dict of axis labels -> functions, function names or list of such.
        :param args: positional arguments to be passed to the aggregation func
        :param kwargs: keywords arguments to be passed to the aggregation func

        :return a new BuhTuhDataFrame containing the requested aggregations
        """
        new_series_dtypes = {}
        aggregate_columns = []

        aggregations: Dict[str, List[Union[str, Callable]]] = {}
        if isinstance(func, dict):
            # make sure the keys are series we know
            series = list(self.aggregated_data.keys())
            for k, v in func.items():
                if k not in series:
                    raise ValueError(f'{k} not found in group by series')
                if isinstance(v, str) or callable(v):
                    aggregations[k] = [v]
                elif isinstance(v, list):
                    aggregations[k] = v
                else:
                    raise TypeError(f'Unsupported value type {type(func)} in func dict for key {k}')
        elif isinstance(func, str) or callable(func):
            aggregations = {k: [func] for k in self.aggregated_data.keys()}
        elif isinstance(func, list):
            aggregations = {k: func for k in self.aggregated_data.keys()}
        else:
            raise TypeError(f'Unsupported argument type for func:  {type(func)}')

        for name, aggregation_list in aggregations.items():
            for aggregation in aggregation_list:
                data_series = self.aggregated_data[name]
                if callable(aggregation):
                    agg_func = aggregation
                    agg_series_name = f'{data_series.name}_{agg_func.__name__}'
                else:
                    agg_func = getattr(data_series, aggregation)
                    agg_series_name = f'{data_series.name}_{aggregation}'

                # If the method is bound yet (__self__ set), we need to use the unbound function
                # to make sure call the method on the right series
                if hasattr(agg_func, '__self__'):
                    agg_func = agg_func.__func__  # type: ignore[attr-defined]

                agg_series = agg_func(data_series, self, *args, **kwargs)

                agg_series = BuhTuhSeries.get_instance(base=self.buh_tuh,
                                                       name=agg_series_name,
                                                       dtype=agg_series.dtype,
                                                       expression=agg_series.expression)
                aggregate_columns.append(agg_series.get_column_expression())
                new_series_dtypes[agg_series.name] = agg_series.dtype

        group_by_expression = self._get_group_by_expression()
        if group_by_expression is None:
            group_by_expression = ''
        else:
            group_by_expression = f'group by {group_by_expression}'

        model_builder = CustomSqlModel(  # setting this stuff could also be part of __init__
            sql="""
                select {group_by_columns}, {aggregate_columns}
                from {{prev}}
                {group_by_expression}
                """
        )
        model = model_builder(
            group_by_columns=', '.join(g.get_column_expression() for g in self.groupby.values()),
            aggregate_columns=', '.join(aggregate_columns),
            group_by_expression=group_by_expression,
            # TODO: get final node, or at least make sure we 'freeze' the node?
            prev=self.buh_tuh.base_node
        )

        return BuhTuhDataFrame.get_instance(
            engine=self.buh_tuh.engine,
            base_node=model,
            index_dtypes={n: t.dtype for n, t in self.groupby.items()},
            dtypes=new_series_dtypes,
            order_by=[]
        )

    def __getattr__(self, attr_name: str) -> Any:
        """ All methods that do not exists yet are potential aggregation methods. """
        try:
            return super().__getattribute__(attr_name)
        except AttributeError:
            return lambda *args, **kwargs: self.aggregate(attr_name, *args, **kwargs)

    def _get_getitem_selection(self, key: Union[str, List[str]]) -> BuhTuhDataFrame:
        assert isinstance(key, (str, list, tuple)), \
            f'a buhtuh `selection` should be a str or list but got {type(key)} instead.'

        if isinstance(key, str):
            key = [key]

        key_set = set(key)
        # todo: check that the key_set is not in group_by_data, or make sure we fix the
        # duplicate column name problem?
        assert key_set.issubset(set(self.aggregated_data.keys()))

        selected_data = {key: data for key, data in self.aggregated_data.items() if key in key_set}
        return BuhTuhDataFrame(
            engine=self.buh_tuh.engine,
            base_node=self.buh_tuh.base_node,
            index=self.groupby,
            series=selected_data,
            # We don't guarantee sorting after groupby(), so we can just set order_by to None
            order_by=[]
        )

    def __getitem__(self, key: Union[str, List[str]]) -> 'BuhTuhGroupBy':
        return type(self)(buh_tuh=self._get_getitem_selection(key),
                          group_by_columns=list(self.groupby.values()))

    def window(self, mode: BuhTuhWindowFrameMode = BuhTuhWindowFrameMode.RANGE,
               start_boundary: BuhTuhWindowFrameBoundary = BuhTuhWindowFrameBoundary.PRECEDING,
               start_value: int = None,
               end_boundary: BuhTuhWindowFrameBoundary = BuhTuhWindowFrameBoundary.CURRENT_ROW,
               end_value: int = None) -> 'BuhTuhWindow':
        """
        Convenience function to turn this groupby into a window.
        :see: BuhTuhWindow __init__ for frame args
        """
        return BuhTuhWindow(buh_tuh=self.buh_tuh,
                            group_by_columns=list(self.groupby.values()),
                            mode=mode,
                            start_boundary=start_boundary, start_value=start_value,
                            end_boundary=end_boundary, end_value=end_value)

    def cube(self) -> 'BuhTuhCube':
        """
        Convenience function to turn this groupby into a cube.
        :see: BuhTuhCube for more info
        """
        return BuhTuhCube(buh_tuh=self.buh_tuh, group_by_columns=list(self.groupby.values()))

    def rollup(self) -> 'BuhTuhRollup':
        """
        Convenience function to turn this groupby into a rollup.
        :see: BuhTuhRollup for more info
        """
        return BuhTuhRollup(buh_tuh=self.buh_tuh, group_by_columns=list(self.groupby.values()))


class BuhTuhCube(BuhTuhGroupBy):
    """
    Very simple abstraction to support cubes
    """
    def _get_group_by_expression(self):
        return f'CUBE ({super()._get_group_by_expression()})'


class BuhTuhRollup(BuhTuhGroupBy):
    """
    Very simple abstraction to support rollups
    """
    def _get_group_by_expression(self):
        return f'ROLLUP ({super()._get_group_by_expression()})'


class BuhTuhGroupingList(BuhTuhGroupBy):
    """
    Abstraction to support SQL's
    GROUP BY (colA,colB), CUBE(ColC,ColD), ROLLUP(ColC,ColE)
    like expressions
    """
    grouping_list: List[BuhTuhGroupBy]

    def __init__(self, grouping_list: List[BuhTuhGroupBy]):
        """
        Given the list of groupbys, construct a combined groupby
        """
        self.grouping_list = grouping_list

        self.groupby = {}
        self.aggregated_data = {}

        buh_tuh = None

        for g in grouping_list:
            if not isinstance(g, BuhTuhGroupBy):
                raise ValueError("Only BuhTuhGroupBy items are supported")
            if buh_tuh is None:
                buh_tuh = g.buh_tuh
            if buh_tuh.base_node != g.buh_tuh.base_node:
                raise ValueError("BuhTuhGroupBy items should have the same underlying base node")
            for name, series in g.groupby.items():
                if name not in self.groupby:
                    self.groupby[name] = series

            for name, series in g.aggregated_data.items():
                if name not in self.groupby and name not in self.aggregated_data:
                    self.aggregated_data[name] = series

        if buh_tuh is None:
            # Mainly to keep mypy happy, but doesn't hurt.
            raise ValueError("Not a single useable dataframe in list")
        self.buh_tuh = buh_tuh

    def __getitem__(self, key: Union[str, List[str]]) -> 'BuhTuhGroupBy':
        """
        Delegate to underyling groupbys' __getitem__
        :see: BuhTuhGroupBy.__getitem__()
        """
        new_grouping_list = []
        for g in self.grouping_list:
            new_grouping_list.append(g.__getitem__(key))
        return type(self)(new_grouping_list)

    def _get_group_by_expression(self):
        grouping_str_list: List[str] = []
        for g in self.grouping_list:
            grouping_str_list.append(f'({g._get_group_by_expression()})')
        return f'{", ".join(grouping_str_list)}'


class BuhTuhGroupingSet(BuhTuhGroupingList):
    """
    Abstraction to support SQLs
    GROUP BY GROUPING SETS ((colA,colB),(ColA),(ColC))
    """

    def _get_group_by_expression(self):
        grouping_str_list: List[str] = []
        for g in self.grouping_list:
            grouping_str_list.append(f'({g._get_group_by_expression()})')
        return f'GROUPING SETS ({", ".join(grouping_str_list)})'


class BuhTuhWindow(BuhTuhGroupBy):
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
    frame_clause: str
    min_values: int

    def __init__(self, buh_tuh: BuhTuhDataFrame,
                 group_by_columns: List['BuhTuhSeries'],
                 mode: BuhTuhWindowFrameMode = BuhTuhWindowFrameMode.RANGE,
                 start_boundary: BuhTuhWindowFrameBoundary = BuhTuhWindowFrameBoundary.PRECEDING,
                 start_value: int = None,
                 end_boundary: BuhTuhWindowFrameBoundary = BuhTuhWindowFrameBoundary.CURRENT_ROW,
                 end_value: int = None,
                 min_values: int = None):
        """
        Define a window on a DataFrame, by giving the partitioning series and the frame definition
        :see: class definition for more info on the frame definition, and BuhTuhGroupBy for more
              info on grouping / partitioning
        """
        super().__init__(buh_tuh, group_by_columns)

        if mode is None:
            raise ValueError("Mode needs to be defined")

        if start_boundary is None:
            raise ValueError("At least start_boundary needs to be defined")

        if start_boundary == BuhTuhWindowFrameBoundary.FOLLOWING \
                and start_value is None:
            raise ValueError("Start of frame can not be unbounded following")

        if end_boundary == BuhTuhWindowFrameBoundary.PRECEDING \
                and end_value is None:
            raise ValueError("End of frame can not be unbounded preceding")

        if (start_value is not None and start_value < 0) or \
                (end_value is not None and end_value < 0):
            raise ValueError("start_value and end_value must be greater than or equal to zero.")

        if mode == BuhTuhWindowFrameMode.RANGE \
                and (start_value is not None or end_value is not None):
            raise ValueError("start_value or end_value cases only supported in ROWS mode.")

        if end_boundary is not None:
            if start_boundary.value > end_boundary.value:
                raise ValueError("frame boundaries defined in wrong order.")

            if start_boundary == end_boundary:
                if start_boundary == BuhTuhWindowFrameBoundary.PRECEDING \
                        and start_value is not None \
                        and end_value is not None \
                        and start_value < end_value:
                    raise ValueError("frame boundaries defined in wrong order.")

            if start_boundary == end_boundary:
                if start_boundary == BuhTuhWindowFrameBoundary.FOLLOWING \
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

        if end_boundary is None:
            self.frame_clause = f'{mode.name} {start_boundary.frame_clause(start_value)}'
        else:
            self.frame_clause = f'{mode.name} BETWEEN {start_boundary.frame_clause(start_value)}' \
                            f' AND {end_boundary.frame_clause(end_value)}'

    def __getitem__(self, key: Union[str, List[str]]) -> 'BuhTuhWindow':
        return type(self)(buh_tuh=self._get_getitem_selection(key),
                          group_by_columns=list(self.groupby.values()),
                          mode=self._mode,
                          start_boundary=self._start_boundary,
                          start_value=self._start_value,
                          end_boundary=self._end_boundary,
                          end_value=self._end_value,
                          min_values=self._min_values)

    def sort_values(self, **kwargs) -> 'BuhTuhWindow':
        """
        Convenience pass-through for
        :see: BuhTuhDataFrame.sort_values()
        """
        new_bt = self.buh_tuh.sort_values(**kwargs)
        return BuhTuhWindow(buh_tuh=new_bt,
                            group_by_columns=list(self.groupby.values()),
                            mode=self._mode,
                            start_boundary=self._start_boundary, start_value=self._start_value,
                            end_boundary=self._end_boundary, end_value=self._end_value)

    def set_frame_clause(self,
                         mode:
                         BuhTuhWindowFrameMode = BuhTuhWindowFrameMode.RANGE,
                         start_boundary:
                         BuhTuhWindowFrameBoundary = BuhTuhWindowFrameBoundary.PRECEDING,
                         start_value: int = None,
                         end_boundary:
                         BuhTuhWindowFrameBoundary = BuhTuhWindowFrameBoundary.CURRENT_ROW,
                         end_value: int = None) -> 'BuhTuhWindow':
        """
        Convenience function to clone this window with new frame parameters
        :see: __init__()
        """
        return BuhTuhWindow(buh_tuh=self.buh_tuh,
                            group_by_columns=list(self.groupby.values()),
                            mode=mode,
                            start_boundary=start_boundary, start_value=start_value,
                            end_boundary=end_boundary, end_value=end_value)

    def get_window_expression(self, window_func: Expression) -> Expression:
        """
        Given the window_func generate a statement like:
            {window_func} OVER (PARTITION BY .. ORDER BY ... frame_clause)
        """
        partition = ', '.join(g.get_expression() for g in self.groupby.values())

        # TODO implement NULLS FIRST / NULLS LAST, probably not here but in the sorting logic.
        order_by = self.buh_tuh.get_order_by_expression()

        if self.frame_clause is None:
            frame_clause = ''
        else:
            frame_clause = self.frame_clause

        over = f'OVER (PARTITION BY {partition} {order_by} {frame_clause})'

        if self._min_values is None or self._min_values == 0:
            return Expression.construct(f'{{}} {over}', window_func)
        else:
            # Only return a value when then minimum amount of observations (including NULLs)
            # has been reached.
            return Expression.construct(f"""
                CASE WHEN (count(1) {over}) >= {self._min_values}
                THEN {{}} {over}
                ELSE NULL END""", window_func)

    def _get_group_by_expression(self):
        """
        On a Window, there is no default group_by clause
        """
        return None
