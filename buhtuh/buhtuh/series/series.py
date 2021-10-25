"""
Copyright 2021 Objectiv B.V.
"""
from abc import ABC, abstractmethod
from copy import copy
from typing import Optional, Dict, Tuple, Union, Type, Any, List, cast, TYPE_CHECKING, Callable
from uuid import UUID

from buhtuh import BuhTuhDataFrame, SortColumn, DataFrameOrSeries, get_series_type_from_dtype
from buhtuh.expression import quote_identifier, Expression
from buhtuh.types import value_to_dtype
from sql_models.model import SqlModel

if TYPE_CHECKING:
    from buhtuh.partitioning import BuhTuhGroupBy, BuhTuhWindow
    from buhtuh.series import BuhTuhSeriesBoolean


class BuhTuhSeries(ABC):
    """
    Mostly immutable* class representing a column/expression in a query.

    * Mostly immutable: The attributes of this class are either immutable, or this class is guaranteed not
        to modify them and the property accessors always return a copy. One exception tho: `engine` is mutable
        and is shared with other Series and DataFrames that can change it's state.
    """
    def __init__(self,
                 engine,
                 base_node: SqlModel,
                 index: Optional[Dict[str, 'BuhTuhSeries']],
                 name: str,
                 expression: Expression,
                 sorted_ascending: Optional[bool] = None):
        """
        Initialize a new BuhTuhSeries object.
        Normally a BuhTuhSeries is associated with a BuhTuhDataFrame. The engine, base_node and index should
        match in that case. Additionally the name should match the name of this Series object in the
        DataFrame.

        To create a new BuhTuhSeries object from scratch there are class helper methods get_instance(),
        get_class_instance(), and from_const().

        :param engine: db connection
        :param base_node: sql-model of a select statement that must contain the columns/expressions that
            expression relies on.
        :param index: None if this Series is part of an index. Otherwise a dict with the Series that are
                        this Series' index
        :param name: name of this Series
        :param expression: Expression that this Series represents
        :param sorted_ascending: None for no sorting, True for sorted ascending, False for sorted descending
        """
        self._engine = engine
        self._base_node = base_node
        self._index = index
        self._name = name
        self._expression = expression
        self._sorted_ascending = sorted_ascending

    @property
    @classmethod
    @abstractmethod
    def dtype(cls) -> str:
        """
        The dtype of this BuhTuhSeries. The dtype is used to uniquely identify data of the type that is
        represented by this BuhTuhSeries subclass. The dtype should be unique among all BuhTuhSeries
        subclasses.
        """
        raise NotImplementedError()

    @property
    @classmethod
    def dtype_aliases(cls) -> Tuple[Union[Type, str], ...]:
        """
        One or more aliases for the dtype.
        For example a BuhTuhBooleanSeries might have dtype 'bool', and as an alias the string 'boolean' and
        the builtin `bool`. An alias can be used in a similar way as the real dtype, e.g. to cast data to a
        certain type: `x.astype('boolean')` is the same as `x.astype('bool')`.

        Subclasses can override this value to indicate what strings they consider aliases for their dtype.
        """
        return tuple()

    @property
    @classmethod
    def supported_db_dtype(cls) -> Optional[str]:
        """
        Database level data type, that can be expressed using this BuhTuhSeries type.
        Example: 'double precision' for a float in Postgres

        Subclasses should override this value if they intend to be the default class to handle such types.
        When creating a BuhTuhDataFrame from existing data in a database, this field will be used to
        determine what BuhTuhSeries to instantiate for a column.
        """
        return None

    @property
    @classmethod
    def supported_value_types(cls) -> Tuple[Type, ...]:
        """
        List of python types that can be converted to database values using
        the `supported_value_to_expression()` method.

        Subclasses can override this value to indicate what types are supported
        by supported_value_to_expression().
        """
        return tuple()

    @classmethod
    @abstractmethod
    def supported_value_to_expression(cls, value: Any) -> Expression:
        """
        Give the expression for the given value. Consider calling the wrapper value_to_expression() instead.

        Implementations of this function are responsible for correctly quoting and escaping special
        characters in the given value. Either by using ExpressionTokens that allow unsafe values (e.g.
        StringValueToken), or by making sure that the quoting and escaping is done already on the value
        inside the ExpressionTokens.

        Implementations only need to be able to support the value specified by supported_value_types.

        :param value: All values of types listed by self.supported_value_types should be supported.
        :return: Expression representing the the value
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def dtype_to_expression(cls, source_dtype: str, expression: Expression) -> Expression:
        """
        Give the sql expression to convert the given expression, of the given source dtype to the dtype of
        this Series.
        :return: sql expression
        """
        raise NotImplementedError()

    @property
    def engine(self):
        return self._engine

    @property
    def base_node(self) -> SqlModel:
        return self._base_node

    @property
    def index(self) -> Optional[Dict[str, 'BuhTuhSeries']]:
        return copy(self._index)

    @property
    def name(self) -> str:
        return self._name

    @property
    def expression(self) -> Expression:
        return self._expression

    @classmethod
    def get_instance(
            cls,
            base: DataFrameOrSeries,
            name: str,
            dtype: str,
            expression: Expression,
            sorted_ascending: Optional[bool] = None
    ) -> 'BuhTuhSeries':
        """
        Create an instance of the right sub-class of BuhTuhSeries.
        The subclass is based on the provided dtype. See docstring of __init__ for other parameters.
        """
        series_type = get_series_type_from_dtype(dtype=dtype)
        return series_type.get_class_instance(
            base=base,
            name=name,
            expression=expression,
            sorted_ascending=sorted_ascending
        )

    @classmethod
    def get_class_instance(
            cls,
            base: DataFrameOrSeries,
            name: str,
            expression: Expression,
            sorted_ascending: Optional[bool] = None
    ):
        """ Create an instance of this class. """
        return cls(
            engine=base.engine,
            base_node=base.base_node,
            index=base.index,
            name=name,
            expression=expression,
            sorted_ascending=sorted_ascending
        )

    @classmethod
    def value_to_expression(cls, value: Optional[Any]) -> Expression:
        """
        Give the expression for the given value.
        Wrapper around cls.supported_value_to_expression() that handles two generic cases:
            If value is None a simple 'NULL' expresison is returned.
            If value is not in supported_value_types raises an error.
        :raises TypeError: if value is not an instance of cls.supported_value_types, and not None
        """
        if value is None:
            return Expression.raw('NULL')
        supported_types = cast(Tuple[Type, ...], cls.supported_value_types)  # help mypy
        if not isinstance(value, supported_types):
            raise TypeError(f'value should be one of {supported_types}'
                            f', actual type: {type(value)}')
        return cls.supported_value_to_expression(value)

    @classmethod
    def from_const(cls,
                   base: DataFrameOrSeries,
                   value: Any,
                   name: str) -> 'BuhTuhSeries':
        """
        Create an instance of this class, that represents a column with the given value.
        """
        result = cls.get_class_instance(
            base=base,
            name=name,
            expression=cls.value_to_expression(value)
        )
        return result

    def get_column_expression(self, table_alias='') -> str:
        expression_sql = self.expression.to_sql(table_alias)
        quoted_column_name = quote_identifier(self.name)
        if expression_sql == quoted_column_name:
            return expression_sql
        return f'{expression_sql} as {quoted_column_name}'

    def _check_supported(self, operation_name: str, supported_dtypes: List[str], other: 'BuhTuhSeries'):

        if self.base_node != other.base_node:
            raise ValueError(f'Cannot apply {operation_name} on two series with different base_node. '
                             f'Hint: make sure both series belong to or are derived from the same '
                             f'DataFrame. '
                             f'Alternative: use merge() to create a DataFrame with both series. ')

        if other.dtype.lower() not in supported_dtypes:
            raise TypeError(f'{operation_name} not supported between {self.dtype} and {other.dtype}.')

    def _get_derived_series(self, new_dtype: str, expression: Expression):
        return BuhTuhSeries.get_instance(
            base=self,
            name=self.name,
            dtype=new_dtype,
            expression=expression
        )

    def head(self, n: int = 5):
        """
        Return the first `n` rows.
        """
        # TODO get a series directly instead of ripping it out of the df?
        return self.to_frame().head(n)[self.name]

    def sort_values(self, ascending=True):
        """
        Returns a copy of this Series that is sorted by its values. Returns self if self is already sorted
        in that way.
        :param ascending: Whether to sort ascending (True) or descending (False)
        """
        if self._sorted_ascending is not None and self._sorted_ascending == ascending:
            return self
        return self.get_class_instance(
            base=self,
            name=self.name,
            expression=self.expression,
            sorted_ascending=ascending
        )

    def view_sql(self):
        return self.to_frame().view_sql()

    def to_frame(self) -> BuhTuhDataFrame:
        if self.index is None:
            raise Exception('to_frame() is not supported for Series that do not have an index')
        if self._sorted_ascending is not None:
            order_by = [SortColumn(expression=self.expression, asc=self._sorted_ascending)]
        else:
            order_by = []
        return BuhTuhDataFrame(
            engine=self.engine,
            base_node=self.base_node,
            index=self.index,
            series={self.name: self},
            order_by=order_by
        )

    def astype(self, dtype: Union[str, Type]) -> 'BuhTuhSeries':
        if dtype == self.dtype or dtype in self.dtype_aliases:
            return self
        series_type = get_series_type_from_dtype(dtype)
        expression = series_type.dtype_to_expression(self.dtype, self.expression)
        # get the real dtype, in case the provided dtype was an alias. mypy needs some help
        new_dtype = cast(str, series_type.dtype)
        return self._get_derived_series(new_dtype=new_dtype, expression=expression)

    def equals(self, other: Any) -> bool:
        """
        Checks whether other is the same as self. This implements the check that would normally be
        implemented in __eq__, but we already use that method for other purposes.
        This strictly checks that other is the same type as self. If other is a subclass this will return
        False.
        """
        if not isinstance(other, self.__class__) or not isinstance(self, other.__class__):
            return False
        if (self.index is None) != (other.index is None):
            return False
        if self.index is not None and other.index is not None:
            if list(self.index.keys()) != list(other.index.keys()):
                return False
            for key in self.index.keys():
                if not self.index[key].equals(other.index[key]):
                    return False
        return self.engine == other.engine and \
            self.base_node == other.base_node and \
            self.name == other.name and \
            self.expression == other.expression and \
            self._sorted_ascending == other._sorted_ascending

    def __getitem__(self, key: Union[Any, slice]):
        if isinstance(key, slice):
            raise NotImplementedError("index slices currently not supported")

        # any other value we treat as a literal index lookup
        # multiindex not supported atm
        if self.index is None:
            raise Exception('Function not supported on Series without index')
        if len(self.index) != 1:
            raise NotImplementedError('Index only implemented for simple indexes.')
        series = self.to_frame()[list(self.index.values())[0] == key]
        assert isinstance(series, self.__class__)

        # this is massively ugly
        return series.head(1).astype(series.dtype).values[0]

    # Below methods are not abstract, as they can be optionally be implemented by subclasses.
    def __add__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    def __sub__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    def __mul__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    # TODO, answer: What about __matmul__?

    def __truediv__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    def __floordiv__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    def __mod__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    # TODO, answer: What about __divmod__?

    def __pow__(self, other, modulo=None) -> 'BuhTuhSeries':
        raise NotImplementedError()

    def __lshift__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    def __rshift__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    def __and__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    def __xor__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    def __or__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    def _comparator_operator(self, other, comparator) -> 'BuhTuhSeriesBoolean':
        raise NotImplementedError()

    def __ne__(self, other) -> 'BuhTuhSeriesBoolean':  # type: ignore
        return self._comparator_operator(other, "<>")

    def __eq__(self, other) -> 'BuhTuhSeriesBoolean':  # type: ignore
        return self._comparator_operator(other, "=")

    def __lt__(self, other) -> 'BuhTuhSeriesBoolean':
        return self._comparator_operator(other, "<")

    def __le__(self, other) -> 'BuhTuhSeriesBoolean':
        return self._comparator_operator(other, "<=")

    def __ge__(self, other) -> 'BuhTuhSeriesBoolean':
        return self._comparator_operator(other, ">=")

    def __gt__(self, other) -> 'BuhTuhSeriesBoolean':
        return self._comparator_operator(other, ">")

    def aggregate(self,
                  func: Union[str, Callable, List[Union[str, Callable]]],
                  *args, **kwargs) -> 'BuhTuhDataFrame':
        """
        use agg(..)
        """
        return self.agg(func, *args, **kwargs)

    def agg(self,
            func: Union[str, Callable, List[Union[str, Callable]]],
            *args, **kwargs) -> 'BuhTuhDataFrame':
        """
        :param func: the aggregation function to look for on all series.
            See BuhTuhGroupby.agg() for supported arguments
        :param args: Positional arguments to pass through to the aggregation function
        :param kwargs: Keyword arguments to pass through to the aggregation function
        """
        if isinstance(func, (str, list)) or callable(func):
            aggregation_series = {}
            aggregation_series[self.name] = func

            # TODO this is quite broken. We should return a wrapped scalar here
            buhtuh = self.to_frame()
            return buhtuh.groupby().aggregate(aggregation_series, *args, **kwargs)
        else:
            raise TypeError(f'Unsupported type for func: {type(func)}')

    def _window_or_agg_func(
            self,
            partition: Optional['BuhTuhGroupBy'],
            expression: Expression,
            derived_dtype: str = None) -> 'BuhTuhSeries':
        """
        Creates a new Series for the given aggregation expression.

         If no partition is given, and empty groupby() is created on a new dataframe containing
         just this series.
         If a Window partition is given, it is used to generate an "OVER" clause.
        """

        from buhtuh.partitioning import BuhTuhWindow

        if derived_dtype is None:
            derived_dtype = self.dtype

        if partition is None:
            # Should we keep the partition with this new series?
            # It's not able to execute without it ... hmm.
            # We probably need a nice wrapper around single value series anyway..
            raise NotImplementedError("Please call aggegation functions through agg() or "
                                      "through Series.agg() for now.")

        if not isinstance(partition, BuhTuhWindow):
            return self._get_derived_series(derived_dtype, expression)
        else:
            return self._get_derived_series(derived_dtype, partition.get_window_expression(expression))

    def _skipna_unsupported(self, skipna):
        if not skipna:
            raise NotImplementedError('Not skipping n/a is not supported')

    def _derived_agg_func(self, partition, func, dtype: str = None, skipna: bool = True):
        self._skipna_unsupported(skipna)
        return self._window_or_agg_func(
            partition,
            Expression.construct(f'{func}({{}})', self),
            self.dtype if dtype is None else dtype
        )

    def fillna(self, constant_value):
        """
        Fill any n/a or NULL value with the given constant
        :param constant_value: the value to replace the na / NULL values with. Should be a supported
            type by the series, or a TypeError is raised.
        :note: you can replace None with None, have fun, forever!
        """
        return self._get_derived_series(
            self.dtype,
            Expression.construct('COALESCE({}, {})', self, self.value_to_expression(constant_value))
        )

    # If these aggregation methods are called with partition = None, we should return a single
    # value. TODO
    def count(self, partition: 'BuhTuhGroupBy' = None, skipna: bool = True):
        return self._derived_agg_func(partition, 'count', 'int64', skipna=skipna)

    def max(self, partition: 'BuhTuhGroupBy' = None, skipna: bool = True):
        return self._derived_agg_func(partition, 'max', skipna=skipna)

    def median(self, partition: 'BuhTuhGroupBy' = None, skipna: bool = True):
        self._skipna_unsupported(skipna)
        return self._window_or_agg_func(
            partition,
            Expression.construct(f'percentile_disc(0.5) WITHIN GROUP (ORDER BY {{}})', self)
        )

    def min(self, partition: 'BuhTuhGroupBy' = None, skipna: bool = True):
        return self._derived_agg_func(partition, 'min', skipna=skipna)

    def mode(self, partition: 'BuhTuhGroupBy' = None, skipna: bool = True):
        self._skipna_unsupported(skipna)
        return self._window_or_agg_func(
            partition,
            Expression.construct(f'mode() within group (order by {{}})', self)
        )

    def nunique(self, partition: 'BuhTuhGroupBy' = None, skipna: bool = True):
        from buhtuh.partitioning import BuhTuhWindow
        if partition is not None and isinstance(partition, BuhTuhWindow):
            raise NotImplementedError("unique counts in window functions not supported (by PG at least)")
        self._skipna_unsupported(skipna)
        return self._get_derived_series('int64', Expression.construct('count(distinct {})', self))

    # Window functions applicable for all types of data, but only with a window
    # TODO more specific docs
    # TODO make group_by optional, but for that we need to use current series sorting
    def _check_window(self, partition: Any):
        """
        Validate that the given partition is a true BuhTuhWindow or raise an exception
        """
        from buhtuh.partitioning import BuhTuhWindow
        if not isinstance(partition, BuhTuhWindow):
            raise ValueError("Window functions need a BuhTuhWindow")

    def window_row_number(self, window: 'BuhTuhWindow'):
        """
        Returns the number of the current row within its partition, counting from 1.
        """
        self._check_window(window)
        return self._window_or_agg_func(window, Expression.construct('row_number()'), 'int64')

    def window_rank(self, window: 'BuhTuhWindow'):
        """
        Returns the rank of the current row, with gaps; that is, the row_number of the first row
        in its peer group.
        """
        self._check_window(window)
        return self._window_or_agg_func(window, Expression.construct('rank()'), 'int64')

    def window_dense_rank(self, window: 'BuhTuhWindow'):
        """
        Returns the rank of the current row, without gaps; this function effectively counts peer
        groups.
        """
        self._check_window(window)
        return self._window_or_agg_func(window, Expression.construct('dense_rank()'), 'int64')

    def window_percent_rank(self, window: 'BuhTuhWindow'):
        """
        Returns the relative rank of the current row, that is
            (rank - 1) / (total partition rows - 1).
        The value thus ranges from 0 to 1 inclusive.
        """
        self._check_window(window)
        return self._window_or_agg_func(window, Expression.construct('percent_rank()'), "double precision")

    def window_cume_dist(self, window: 'BuhTuhWindow'):
        """
        Returns the cumulative distribution, that is
            (number of partition rows preceding or peers with current row) / (total partition rows).
        The value thus ranges from 1/N to 1.
        """
        self._check_window(window)
        return self._window_or_agg_func(window, Expression.construct('cume_dist()'), "double precision")

    def window_ntile(self, window: 'BuhTuhWindow', num_buckets: int = 1):
        """
        Returns an integer ranging from 1 to the argument value,
        dividing the partition as equally as possible.
        """
        self._check_window(window)
        return self._window_or_agg_func(window, Expression.construct(f'ntile({num_buckets})'), "int64")

    def window_lag(self, window: 'BuhTuhWindow', offset: int = 1, default: Any = None):
        """
        Returns value evaluated at the row that is offset rows before the current row
        within the partition; if there is no such row, instead returns default
        (which must be of the same type as value).

        Both offset and default are evaluated with respect to the current row.
        If omitted, offset defaults to 1 and default to None
        """
        self._check_window(window)
        default_expr = self.value_to_expression(default)
        return self._window_or_agg_func(
            window,
            Expression.construct(f'lag({{}}, {offset}, {{}})', self, default_expr),
            self.dtype
        )

    def window_lead(self, window: 'BuhTuhWindow', offset: int = 1, default: Any = None):
        """
        Returns value evaluated at the row that is offset rows after the current row within the partition;
        if there is no such row, instead returns default (which must be of the same type as value).
        Both offset and default are evaluated with respect to the current row.
        If omitted, offset defaults to 1 and default to None.
        """
        self._check_window(window)
        default_expr = self.value_to_expression(default)
        return self._window_or_agg_func(
            window,
            Expression.construct(f'lead({{}}, {offset}, {{}})', self, default_expr),
            self.dtype
        )

    def window_first_value(self, window: 'BuhTuhWindow'):
        """
        Returns value evaluated at the row that is the first row of the window frame.
        """
        self._check_window(window)
        return self._window_or_agg_func(
            window,
            Expression.construct('first_value({})', self),
            self.dtype
        )

    def window_last_value(self, window: 'BuhTuhWindow'):
        """
        Returns value evaluated at the row that is the last row of the window frame.
        """
        self._check_window(window)
        return self._window_or_agg_func(window, Expression.construct('last_value({})', self), self.dtype)

    def window_nth_value(self, window: 'BuhTuhWindow', n: int):
        """
        Returns value evaluated at the row that is the n'th row of the window frame
        (counting from 1); returns NULL if there is no such row.
        """
        self._check_window(window)
        return self._window_or_agg_func(
            window,
            Expression.construct(f'nth_value({{}}, {n})', self),
            self.dtype
        )


def const_to_series(base: Union[BuhTuhSeries, BuhTuhDataFrame],
                    value: Union[BuhTuhSeries, int, float, str, UUID],
                    name: str = None) -> BuhTuhSeries:
    """
    Take a value and return a BuhTuhSeries representing a column with that value.
    If value is already a BuhTuhSeries it is returned unchanged.
    If value is a constant then the right BuhTuhSeries subclass is found for that type and instantiated
    with the constant value.
    :param base: Base series or DataFrame. In case a new Series object is created and returned, it will
        share its engine, index, and base_node with this one. Only applies if value is not a BuhTuhSeries
    :param value: constant value for which to create a Series, or a BuhTuhSeries
    :param name: optional name for the series object. Only applies if value is not a BuhTuhSeries
    :return:
    """
    if isinstance(value, BuhTuhSeries):
        return value
    name = '__tmp' if name is None else name
    dtype = value_to_dtype(value)
    series_type = get_series_type_from_dtype(dtype)
    return series_type.from_const(base=base, value=value, name=name)
