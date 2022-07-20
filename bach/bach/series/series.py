"""
Copyright 2021 Objectiv B.V.
"""
from abc import ABC, abstractmethod
from copy import copy, deepcopy
from typing import Optional, Dict, Tuple, Union, Type, Any, List, cast, TYPE_CHECKING, Callable, Mapping, \
    TypeVar, Sequence, NamedTuple
from uuid import UUID

import numpy
import pandas
from sqlalchemy.engine import Dialect, Engine

from bach import DataFrame, DataFrameOrSeries, get_series_type_from_dtype

from bach.dataframe import ColumnFunction, dict_name_series_equals
from bach.expression import Expression, NonAtomicExpression, ConstValueExpression, \
    IndependentSubqueryExpression, SingleValueExpression, AggregateFunctionExpression

from bach.sql_model import BachSqlModel

from bach.types import StructuredDtype, Dtype, validate_instance_dtype, DtypeOrAlias,\
    AllSupportedLiteralTypes, value_to_series_type
from bach.utils import (
    is_valid_column_name, validate_node_column_references_in_sorting_expressions, SortColumn
)
from sql_models.constants import NotSet, not_set, DBDialect
from sql_models.model import Materialization
from sql_models.util import is_bigquery, DatabaseNotSupportedException

if TYPE_CHECKING:
    from bach.partitioning import GroupBy, Window, WindowFunction
    from bach.series import SeriesBoolean, SeriesInt64, SeriesFloat64

SeriesSubType = TypeVar('SeriesSubType', bound='Series')

WrappedPartition = Union['GroupBy', 'DataFrame']
WrappedWindow = Union['Window', 'DataFrame']


class ToPandasInfo(NamedTuple):
    """
    INTERNAL: Used to encode how to go from raw database result to pandas object, see Series.to_pandas_info.
    """
    dtype: str
    function: Optional[Callable[[Any], Any]]


class Series(ABC):
    """
    Series is an abstract class. An instance of Series represents a column of data. Specific subclasses are
    used to represent specific types of data and enable operations on that data.

    It can be used as a separate object to just deal with a single list of values. There are many standard
    operations on Series available to do operations like add or subtract, to create aggregations like
    :py:meth:`nunique()` or :py:meth:`count()`, or to create new sub-Series, like :py:meth:`unique()`.
    """
    # A series is defined by an expression and a name, and it exists within the scope of the base_node.
    # Its index can be a simple (dict of) Series in case of an already materialised base_node.
    #
    # If group_by has been set, Series.index represents the future index of this Series. The series is now
    # part of the aggregation as defined by the GroupBy and base_node and can only be evaluated as such.
    # If no group_by is set, the expression can be used as is, as is the case for normal column expressions
    # as well as correctly setup window expressions.
    #
    # The rule here: If a series needs a `group_by` to be evaluated, then and only then it should carry that
    # `group_by`. This implies that index Series coming from `GroupBy.index`, do not carry that `group_by`.
    # Only the data Series that actually need the aggregation to happen do.
    #
    # When a Series is used as an index, it should be free from any pending aggregation (and thus group_by
    # should be None, and its index should be {}.
    #
    # * Mostly immutable *
    # The attributes of this class are either immutable, or this class is guaranteed not
    # to modify them and the property accessors always return a copy. One exception tho: `engine` is mutable
    # and is shared with other Series and DataFrames that can change it's state.

    dtype: str = ''
    """
    The dtype of this Series. Must be overridden by subclasses.

    The dtype is used to uniquely identify data of the type that is
    represented by this Series subclass. The dtype must be unique among all Series subclasses.
    """

    dtype_aliases: Tuple[DtypeOrAlias, ...] = tuple()
    """
    INTERNAL: One or more aliases for the dtype.
    For example a SeriesBoolean might have dtype 'bool', and as an alias the string 'boolean' and
    the builtin `bool`. An alias can be used in a similar way as the real dtype, e.g. to cast data to a
    certain type: `x.astype('boolean')` is the same as `x.astype('bool')`.

    Subclasses can override this value to indicate what strings they consider aliases for their dtype.
    """

    supported_db_dtype: Mapping[DBDialect, Optional[str]] = {}
    """
    INTERNAL: Per supported database, the database's data type that can be expressed using this Series type.
    Example: {DBDialect.POSTGRES: 'double precision'} for a float in Postgres

    Subclasses must override this with a mapping containing all databases that they support.
    If subclasses intend to be the default class to handle a certain database type, then they must express
    that in the returned mapping.

    Main use of this field is two fold:
    1. Determining what databases are supported by a Series
    2. When creating a DataFrame from existing data in a database, this field will be used to determine what
        Series to instantiate for a column.
    """

    supported_value_types: Tuple[Type, ...] = tuple()
    """
    INTERNAL: List of python types that can be converted to database values using
    the :meth:`supported_value_to_literal()` and :meth:`supported_literal_to_expression()` methods.

    Subclasses can override this value to indicate what types are supported
    by :meth:`supported_value_to_literal()`.
    """

    def __init__(
        self,
        engine: Engine,
        base_node: BachSqlModel,
        index: Dict[str, 'Series'],
        name: str,
        expression: Expression,
        group_by: Optional['GroupBy'],
        instance_dtype: StructuredDtype,
        order_by: Optional[List[SortColumn]] = None,
        **kwargs,
    ) -> None:
        """
        Initialize a new Series object.
        If a Series is associated with a DataFrame. The engine, base_node and index
        should match, as well as group_by (can be None, but then both are). Additionally the name
        should match the name of this Series object in the DataFrame.

        A Series can also become a future aggregation, and thus decoupled from its current
        DataFrame. In that case, the index will be set to the future index. If this Series is
        decoupled from its dataframe, by df['series'] for example, the series will have group_by
        set to the dataframe's groupby, to express that aggregation still has to take place.
        A series in that state can be combined back into a dataframe that has the same aggregation
        set-up (e.g. matching base_node, index and group_by)

        To create a new Series object from scratch there are class helper methods
        from_value(), get_class_instance().
        It is very common to clone a Series with little changes. Use copy_override() for that.

        :param engine: db connection
        :param base_node: sql-model of a select statement that must contain the columns/expressions that
            expression relies on.
        :param index: {} if this Series is part of an index, or a dict with the Series that are
            this Series' index. If this series is part of an aggregation that still needs to take place,
            the index will be a GroupBy instance expressing that future aggregation.
        :param name: name of this Series
        :param expression: Expression that this Series represents
        :param group_by: The requested aggregation for this series.
        :param instance_dtype: dtype of this specific instance. For basic scalar types this should be the
            same value as self.dtype. For structured types (e.g. SeriesDict) this should indicate what the
            structure of the data is.
        :param order_by: Optional list of sort-columns to order the Series by. Columns referenced on sorting
            expressions must be valid for current base node.
        """
        # Series is an abstract class, besides the abstractmethods subclasses must/may override some
        #   properties:
        #   * non-abstract subclasses MUST override some class properties: 'dtype', and 'supported_db_dtype'
        #   * subclasses MAY also override class properties: 'dtype_aliases', and 'supported_value_types'
        # Unfortunately defining these properties as an "abstract-classmethod-property" makes it hard
        # to understand for mypy, sphinx, and python. Therefore, we check here that we are instantiating a
        # proper subclass, instead of just relying on @abstractmethod.
        # related links:
        # https://github.com/python/mypy/issues/8532#issuecomment-600132991
        # https://github.com/python/mypy/issues/11619 https://bugs.python.org/issue45356
        if self.__class__ == Series:
            raise TypeError("Cannot instantiate Series directly. Instantiate a subclass.")
        if self.dtype == '':
            raise NotImplementedError("Non-abstract Series subclasses must override `dtype` class property")
        if self.supported_db_dtype == {}:
            raise NotImplementedError(
                "Non-abstract Series subclasses must override `supported_db_dtype` class property")
        # End of Abstract-class check

        self.assert_engine_dialect_supported(engine)
        if index == {} and group_by and group_by.index != {}:
            # not a completely watertight check, because a group_by on {} is valid.
            raise ValueError(f'Index Series should be free of pending aggregation.')
        if group_by and not dict_name_series_equals(group_by.index, index):
            raise ValueError(f'Series and aggregation index do not match: {group_by.index} != {index}')
        if not group_by and expression.has_aggregate_function:
            raise ValueError('Expression has an aggregation function set, but there is no group_by')
        if not is_valid_column_name(dialect=engine.dialect, name=name):
            raise ValueError(f'Column name "{name}" is not valid for SQL dialect {engine.dialect}')

        for value in index.values():
            if value.base_node != base_node:
                raise ValueError(
                    (
                        f'Base_node in `index` should match series. '
                        f'series: {base_node}, {value.name}.base_node: {value.base_node}'
                    )
                )

        if order_by:
            validate_node_column_references_in_sorting_expressions(node=base_node, order_by=order_by)

        validate_instance_dtype(static_dtype=self.dtype, instance_dtype=instance_dtype)

        self._engine = engine
        self._base_node = base_node
        self._index = copy(index)
        self._name = name
        self._expression = expression
        self._group_by = group_by
        self._instance_dtype = instance_dtype
        self._order_by = order_by or []

    @classmethod
    @abstractmethod
    def supported_literal_to_expression(cls, dialect: Dialect, literal: Expression) -> Expression:
        """
        INTERNAL: Given an expression representing a literal as returned by
        :meth:`supported_value_to_literal()`, this returns an Expression representing the actual value with
        the correct type.

        Example for dtype `int64`, with Postgres Dialect (`pgd`):
            supported_value_to_literal(pgd, 123) will return an expression representing '123'
            supported_literal_to_expression(pgd, '123') should then turn that into 'cast(123 to bigint)'
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def supported_value_to_literal(
            cls,
            dialect: Dialect,
            value: Any,
            dtype: StructuredDtype
    ) -> Expression:
        """
        INTERNAL: Gives an expression for the sql-literal of the given value.

        Note that this is not always the same as the sql representation of the given value!
        e.g. for the int64 value `123`, the literal we generate on Postgres is `123` (excluding the quotes),
        which is a smallint, not a bigint. We then add the cast to 'bigint', but this function _only_ returns
        the literal not the cast.

        Implementations of this function are responsible for correctly quoting and escaping special
        characters in the given value. Either by using ExpressionTokens that allow unsafe values (e.g.
        StringValueToken), or by making sure that the quoting and escaping is done already on the value
        inside the ExpressionTokens.

        Implementations only need to be able to support the value specified by supported_value_types.

        :param dialect: Database dialect
        :param value: All values of types listed by self.supported_value_types should be supported.
        :param dtype: instance-dtype. For scalar values this should simply be cls.dtype, for structural types
            this should be a dtype that describes the structure of value.
        :return: Expression of a sql-literal for the value
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def dtype_to_expression(cls, dialect: Dialect, source_dtype: str, expression: Expression) -> Expression:
        """
        INTERNAL: Give the sql expression to convert the given expression, of the given source dtype to the
        dtype of this Series.

        :param dialect: Database dialect
        :param source_dtype: dtype of the expression parameter
        :param expression: expression to cast
        :return: a new expression that casts the given expression to the dialect's db type for the dtype of
        this class
        """
        raise NotImplementedError()

    @property
    def engine(self) -> Engine:
        """
        INTERNAL: Get the engine
        """
        return self._engine

    @property
    def base_node(self) -> BachSqlModel:
        """
        Get this Series' base_node
        """
        return self._base_node

    @property
    def index(self) -> Dict[str, 'Series']:
        """
        Get this Series' index dictionary {name: Series}
        """
        return copy(self._index)

    @property
    def name(self) -> str:
        """
        Get this Series' name
        """
        return self._name

    @property
    def group_by(self) -> Optional['GroupBy']:
        """
        Get this Series' group_by, if any.
        """
        return copy(self._group_by)

    @property
    def order_by(self) -> List[SortColumn]:
        """
        Get the series expressions for sorting this Series.
        """
        return copy(self._order_by)

    @property
    def expression(self) -> Expression:
        """ INTERNAL: Get the expression"""
        return self._expression

    @property
    def instance_dtype(self) -> StructuredDtype:
        """
        Get the instance_dtype. For basic scalar types this should be the same value as self.dtype. For
        structured types (e.g. SeriesDict) this should indicate what the structure of the data is. See the
        class docstring of structured types for more information on the structure.
        """
        return deepcopy(self._instance_dtype)

    @property
    def is_materialized(self) -> bool:
        """
        Return true if this Series is in a materialized state, i.e. all information about the
        Series's values is encoded in self.base_node.

        :returns: True if this Series is in a materialized state, False otherwise
        """
        return self.to_frame().is_materialized

    @classmethod
    def get_class_instance(
        cls: Type[SeriesSubType],
        engine: Engine,
        base_node: BachSqlModel,
        index: Dict[str, 'Series'],
        name: str,
        expression: Expression,
        group_by: Optional['GroupBy'],
        order_by: Optional[List[SortColumn]],
        instance_dtype: StructuredDtype,
        **kwargs
    ) -> SeriesSubType:
        """ INTERNAL: Create an instance of this class. """
        return cls(
            engine=engine,
            base_node=base_node,
            index=index,
            name=name,
            expression=expression,
            group_by=group_by,
            order_by=order_by,
            instance_dtype=instance_dtype,
            **kwargs
        )

    @classmethod
    def get_db_dtype(cls, dialect: Dialect) -> Optional[str]:
        """
        Give the static db_dtype of this Series, for the given database dialect.

        :raises DatabaseNotSupportedException: If the Series subclass doesn't support the database dialect.
        :return: database type as string, or None if this Series has no database type for which it is the
            standard Series for that database, or if that type is a structural type whose exact type depends
            on the data of the subtypes (e.g. SeriesList will return None on BigQuery, as it can handle all
            ARRAY<*> subtypes)
        """
        db_dialect = DBDialect.from_dialect(dialect)
        if db_dialect not in cls.supported_db_dtype:
            message_override = f'{cls.__name__} is not supported for database dialect {dialect.name}'
            raise DatabaseNotSupportedException(dialect, message_override=message_override)
        return cls.supported_db_dtype[db_dialect]

    @classmethod
    def value_to_literal(
            cls,
            dialect: Dialect,
            value: Optional[Any],
            dtype: StructuredDtype
    ) -> Expression:
        """
        INTERNAL: Give the literal for the given value.

        This is similar to :meth:`Series.value_to_expression()`, but does not call
        :meth:`Series.supported_literal_to_expression()` on the result. In most cases you'd want to use
        :meth:`Series.value_to_expression()`.

        This function handles three generic cases:
        1. If value is None a simple 'NULL' expression is returned.
        2. If value is not in supported_value_types raises an error.
        3. if dtype is a simple dtype and does not match cls.dtype, raises an error.
        """
        if value is None:
            return Expression.raw('NULL')
        if not isinstance(value, cls.supported_value_types):
            raise TypeError(f'value should be one of {cls.supported_value_types}'
                            f', actual type: {type(value)}')
        if isinstance(dtype, Dtype) and dtype != cls.dtype:
            raise ValueError(f'Dtype "{dtype}" does not match class dtype: {cls.dtype}')

        return cls.supported_value_to_literal(dialect=dialect, value=value, dtype=dtype)

    @classmethod
    def value_to_expression(
            cls,
            dialect: Dialect,
            value: Optional[Any],
            dtype: StructuredDtype
    ) -> ConstValueExpression:
        """
        INTERNAL: Give the expression for the given value.

        Wrapper around the methods :meth:`Series.supported_value_to_literal()` and
        :meth:`Series.supported_literal_to_expression()`, which are implemented in sub-classes.
        This function handles some generic cases that are not handled in the subclasses. Additionally the
        result is wrapped in a ConstValueExpression.

        See :meth:`Series.value_to_literal()` on information on what cases are handled in the wrappers.

        :param dialect: Database dialect
        :param value: value to convert to an expression
        :param dtype: instance-dtype. For scalar values this should simply be cls.dtype, for structural types
            this should be a dtype that describes the structure of value.
        :raises TypeError: if value is not an instance of cls.supported_value_types, and not None
        """
        literal = cls.value_to_literal(dialect=dialect, value=value, dtype=dtype)
        const_expression = cls.supported_literal_to_expression(dialect=dialect, literal=literal)
        return ConstValueExpression(const_expression)

    @classmethod
    def from_value(cls: Type[SeriesSubType],
                   base: DataFrameOrSeries,
                   value: Any,
                   name: str,
                   dtype: Optional[StructuredDtype] = None) -> SeriesSubType:
        """
        Create an instance of this class, that represents a column with the given value.
        The given base Series/DataFrame will be used to set the engine, base_node, and index.

        :param base:    The DataFrame or Series that the internal parameters are taken from
        :param value:   The value that this constant Series will have
        :param name:    The name that it will be known by (only for representation)
        :param dtype:   Optional dtype for structural types. Will default to cls.dtype
        """
        if dtype is None:
            dtype = cls.dtype
        expression = cls.value_to_expression(dialect=base.engine.dialect, value=value, dtype=dtype)
        result = cls.get_class_instance(
            engine=base.engine,
            base_node=base.base_node,
            index=base.index,
            name=name,
            expression=expression,
            group_by=None,
            order_by=[],
            instance_dtype=dtype
        )
        return result

    @classmethod
    def assert_engine_dialect_supported(cls, dialect_engine: Union[Dialect, Engine]) -> None:
        """
        INTERNAL: check that the given dialect/engine is in cls.supported_db_dtype.
        :raises DatabaseNotSupportedException: if dialect/engine is not supported.
        """
        if isinstance(dialect_engine, Engine):
            db_dialect = DBDialect.from_engine(dialect_engine)
        else:
            db_dialect = DBDialect.from_dialect(dialect_engine)
        if db_dialect not in cls.supported_db_dtype:
            message_override = f'{cls.__name__} is not supported for database dialect {dialect_engine.name}'
            raise DatabaseNotSupportedException(dialect_engine, message_override=message_override)

    def copy(self: SeriesSubType) -> SeriesSubType:
        """
        Return a copy of this Series.

        As this series only represents data in the backing SQL store, and does not contain any data,
        this is a metadata copy only, no actual data is duplicated and changes to the underlying data
        will represented in both copy and original.
        Changes to index, sorting, grouping etc. on the copy will not affect the original.

        If you want to create a snapshot of the data, have a look at :py:meth:`bach.DataFrame.get_sample()`

        :returns: a copy of the series
        """
        return self.copy_override()

    def copy_override(
        self: SeriesSubType,
        *,
        engine: Optional[Engine] = None,
        base_node: Optional[BachSqlModel] = None,
        index: Optional[Dict[str, 'Series']] = None,
        name: Optional[str] = None,
        expression: Optional['Expression'] = None,
        group_by: Optional[Union['GroupBy', NotSet]] = not_set,
        instance_dtype: Optional[StructuredDtype] = None,
        order_by: Optional[Union[List[SortColumn]]] = None,
        **kwargs
    ) -> SeriesSubType:
        """
        INTERNAL: Copy this instance into a new one, with the given overrides
        """
        return self.__class__(
            engine=self._engine if engine is None else engine,
            base_node=self._base_node if base_node is None else base_node,
            index=self._index if index is None else index,
            name=self._name if name is None else name,
            expression=self._expression if expression is None else expression,
            group_by=self._group_by if group_by is not_set else group_by,
            instance_dtype=self.instance_dtype if instance_dtype is None else instance_dtype,
            order_by=self.order_by if order_by is None else order_by,
            **kwargs
        )

    def copy_override_dtype(
        self,
        dtype: Optional[str],
        *,
        instance_dtype: Optional[StructuredDtype] = None
    ) -> 'Series':
        """
        INTERNAL: create an instance of the Series subtype with the given dtype, and copy
        all values from self into that instance.
        """
        klass: Type['Series'] = get_series_type_from_dtype(self.dtype if dtype is None else dtype)
        return self.copy_override_type(klass, instance_dtype=instance_dtype)

    def copy_override_type(
        self,
        series_type: Type[SeriesSubType],
        *,
        instance_dtype: Optional[StructuredDtype] = None,
        **kwargs
    ) -> SeriesSubType:
        """
        INTERNAL: create an instance of the given Series subtype, copy all values from self.
        """
        instance_dtype = series_type.dtype if instance_dtype is None else instance_dtype
        return series_type(
            engine=self._engine,
            base_node=self._base_node,
            index=self._index,
            name=self._name,
            expression=self._expression,
            group_by=self._group_by,
            instance_dtype=instance_dtype,
            order_by=self.order_by,
            **kwargs,
        )

    def to_pandas_info(self) -> Optional['ToPandasInfo']:
        """
        INTERNAL: Optional information on how to map query-results to pandas types.
        Subclasses can override this function as needed. By default, this returns None.

        ToPandasInfo defines both the pandas-dtype of the data, and an optional function to apply to query
        results. If defined for a given DBDialect, we use this information in :meth:`DataFrame.to_pandas()`,
        by setting the dtype and applying the function to columns of the resulting pandas DataFrame.

        Example usage: UUIDs in BigQuery are represented as strings, we convert these strings to UUID
        objects in to_pandas().
        """
        return None

    def unstack(
        self,
        level: Union[int, str] = -1,
        fill_value: Optional[Union[int, float, str, UUID]] = None,
        aggregation: str = 'max',
    ) -> 'DataFrame':
        """
        Pivot a level of the index labels.

        Returns a(n unsorted) DataFrame with the values of the unstacked index as columns. In case of
        duplicate index values that are unstacked, `aggregation` is used to aggregate the values.

        Series' index should be of at least two levels to unstack.

        :param level: selects the level of the index that is unstacked.
        :param fill_value: replace missing values resulting from unstacking. Should be of same type as the
            series that is unstacked.
        :param aggregation: method of aggregation, in case of duplicate index values. Supports all aggregation
            methods that :py:meth:`aggregate` supports.

        :returns: DataFrame

        .. note::
            This function queries the database.
        """
        result = self.to_frame().unstack(level, fill_value, aggregation)
        return result.rename(columns={col: col.replace(f'__{self.name}', '') for col in result.data_columns})

    def get_column_expression(self, table_alias: Optional[str] = None) -> Expression:
        """ INTERNAL: Get the column expression for this Series """
        expression = self.expression.resolve_column_references(self.engine.dialect, table_alias)
        return Expression.construct_expr_as_name(expression, self.name)

    def _get_supported(
        self,
        operation_name: str,
        supported_dtypes: Tuple[str, ...],
        other: 'Series'
    ) -> Tuple['Series', 'Series']:
        """
        Check whether `other` is supported for this operation, and if not, possibly do something
        about it by using subquery / materialization / aligning base nodes using a merge.

        :returns: the (modified) series and (modified) other.
        """
        if not (other.expression.is_constant or other.expression.is_independent_subquery):
            # we should maybe create a subquery
            if self.base_node != other.base_node or self.group_by != other.group_by:
                if other.expression.is_single_value:
                    other = self.as_independent_subquery(other)
                else:
                    return self.__set_item_with_merge(other)

        if other.dtype.lower() not in supported_dtypes:
            raise TypeError(f'{operation_name} not supported between {self.dtype} and {other.dtype}.')
        return self, other

    def __set_item_with_merge(self, other: 'Series') -> Tuple['Series', 'Series']:
        """
        Aligns caller series and other series base nodes by using a merge based on their indexes.
        If caller's base node makes reference to the other's base node, caller's node should be
        updated in order to include other's column reference.

        :returns: the (modified) series and (modified) other.

        .. note::
            If both caller and other series have the same name, (modified) other will be renamed as:
            `f"{other.name}__other"`.

            If other series has the same name as any one of caller's index series,
            (modified) other will be renamed as:
            `f"{other.name}__data_column"`.
        """
        if not self.index or not other.index:
            raise ValueError('both series must have at least one index level')

        if any(
            caller_idx.dtype != other_idx.dtype
            for caller_idx, other_idx in zip(self.index.values(), other.index.values())
        ):
            raise ValueError('dtypes of indexes to be merged should be the same')

        from bach.merge import MergeSqlModel, revert_merge

        update_column_references = (
            isinstance(self.base_node, MergeSqlModel)
            and other.base_node in self.base_node.references.values()
        )
        if not update_column_references:
            left = self.to_frame()
            right = other.to_frame()
        else:
            # other's base node is already referenced on the caller's base node
            # revert the merge from previous __set_item_with_merge and include other
            # this way we can reference all needed columns for the operation
            left, right = revert_merge(self.to_frame())
            if left.base_node == other.base_node:
                left[other.name] = other.copy_override(index=left.index)
            else:
                right[other.name] = other.copy_override(index=right.index)

        # rename conflicted right data columns with left index names, and align left <> right indexes
        right = right.materialize() if right.group_by else right
        right = right.rename(
            columns={col: f'{col}__data_column' for col in right.data_columns if col in self.index}
        )
        # TODO: replace this with right.rename(index={...})
        aligned_right_indexes = [
            right_idx.copy_override(name=left_idx.name)
            for left_idx, right_idx in zip(left.index.values(), right.index.values())
        ]
        right = right.set_index(aligned_right_indexes, drop=True)

        df = left.merge(right, on=list(right.index.keys()), how='outer', suffixes=('', '__other'))

        mod_other_name = other.name
        if (
            (other.base_node == right.base_node or not update_column_references)
            and set(df.all_series) & {f'{other.name}__other', f'{other.name}__data_column'}
        ):
            post_fix = '__other' if other.name not in self.index else '__data_column'
            mod_other_name = f'{other.name}{post_fix}'

        if not update_column_references:
            caller_series = df.all_series[self.name]
            other_series = df.all_series[mod_other_name]
            return caller_series, other_series

        caller_index = {
            idx_name: idx.copy_override(base_node=df.base_node)
            for idx_name, idx in self.index.items()
        }
        if (
            other.base_node == left.base_node
            and not set(self.base_node.columns) >= {other.name, f'{other.name}__other'}
            and f'{other.name}__other' in df.all_series
        ):
            # column was referenced before from right node
            # check if other.name has conflict with other referenced columns
            # example: left.a + right.b - left.b
            # first expression = a + b
            # incorrect second expression = a + b - b
            # correct second expression = a + b__other - b
            caller_expr = self.expression.replace_column_references(other.name, f'{other.name}__other')
            caller_series = self.copy_override(
                base_node=df.base_node,
                expression=caller_expr,
                index=caller_index,
            )
        else:
            # just update base node
            caller_series = self.copy_override(
                base_node=df.base_node, index=caller_index,
            )
        other_series = df.all_series[mod_other_name]
        return caller_series, other_series

    def to_pandas(self, limit: Union[int, slice] = None) -> pandas.Series:
        """
        Get the data from this series as a pandas.Series
        :param limit: The limit to apply, either as a max amount of rows or a slice.
        """
        return self.to_frame().to_pandas(limit=limit)[self.name]

    def head(self, n: int = 5) -> pandas.Series:
        """
        Get the first n rows from this Series as a pandas.Series.
        :param n: The amount of rows to return.

        .. note::
            This function queries the database.
        """
        return self.to_pandas(limit=n)

    @property
    def value(self) -> Any:
        """
        Retrieve the actual single value of this series. If it's not sure that there is only one value,
        a ValueError is raised. In that case use Series.values[0] to retrieve the value.

        .. note::
            This function queries the database.
        """
        if not self.expression.is_single_value:
            raise ValueError('value accessor only supported for single value expressions. '
                             'Use .values instead')
        return self.to_numpy()[0]

    @property
    def array(self) -> pandas.core.arrays.ExtensionArray:
        """
        .array property accessor akin pandas.Series.array

        .. note::
            This function queries the database.
        """
        return self.to_pandas().array

    def to_numpy(self) -> numpy.ndarray:
        """
        Return a Numpy representation of the Series akin :py:attr:`pandas.Series.to_numpy`

        :returns: Returns the values of the Series as numpy.ndarray.

        .. note::
            This function queries the database.
        """
        return self.to_pandas().to_numpy()

    def materialize(
            self,
            node_name: str = 'manual_materialize',
            limit: Optional[Union[int, slice]] = None,
            distinct: bool = False,
            materialization: Union[Materialization, str] = Materialization.CTE
    ) -> 'Series':
        """
        Create a copy of this Series with as base_node the current Series's state.

        This effectively adds a node to the underlying SqlModel graph. Generally adding nodes increases
        the size of the generated SQL query. But this can be useful if the current Series contains
        expressions that you want to evaluate before further expressions are build on top of them. This might
        make sense for very large expressions, or for non-deterministic expressions (e.g. see
        :py:meth:`SeriesUuid.random`). Additionally, materializing as a temporary table can
        improve performance in some instances.

        Note this function does NOT query the database or materializes any data in the database. It merely
        changes the underlying SqlModel graph, which gets executed by data transfer functions (e.g.
        :meth:`to_pandas()`)

        :param node_name: The name of the node that's going to be created
        :param limit: The limit (slice, int) to apply.
        :param distinct: Apply distinct statement if ``distinct=True``
        :param materialization: Set the materialization of the SqlModel in the graph. Only
            Materialization.CTE / 'cte' and Materialization.TEMP_TABLE / 'temp_table' are supported.
        :returns: Series with the current Series's state as base_node

        .. note::
            Calling materialize() resets the order of the series. Call :py:meth:`sort_values()` again on
            the result if order is important.

            Argument inplace should be always False.
        """
        result = self.to_frame().materialize(node_name=node_name, limit=limit, distinct=distinct,
                                             inplace=False, materialization=materialization)
        return result.all_series[self.name]

    def reset_index(
        self,
        level: Optional[Union[str, Sequence[str]]] = None,
        drop: bool = False,
    ) -> DataFrameOrSeries:
        """
        Drops the current index.

        :param level: Removes given levels from index. Removes all levels by default
        :param drop: if False, the dropped index is added to the data columns of the DataFrame. If True it
            is removed.
        :returns: Series or DataFrame with the index dropped.
        """

        result = self.to_frame().reset_index(level, drop)

        if drop:
            return result.all_series[self.name]

        return result

    def sort_values(self: SeriesSubType, *, ascending: bool = True) -> SeriesSubType:
        """
        Sort this Series by its values.
        Returns a new instance and does not actually modify the instance it is called on.

        :param ascending: Whether to sort ascending (True) or descending (False)
        """
        return self.sort_by_series(by=[self.copy()], ascending=ascending)

    def sort_by_series(
        self: SeriesSubType, by: List['Series'], *, ascending: Union[bool, List[bool]] = True,
    ) -> SeriesSubType:
        """
        Sort this Series by other Series that have the same base node as this Series.
        Returns a new instance and does not actually modify the instance it is called on.

        :param by:  list of Series to sort by.
        :param ascending: Whether to sort ascending (True) or descending (False)
        """
        if any(series.base_node != self.base_node for series in by):
            raise ValueError('All series provided as keys must have the same base_node as caller.')

        if isinstance(ascending, bool):
            ascending = [ascending] * len(by)
        if len(by) != len(ascending):
            raise ValueError(f'Length of ascending ({len(ascending)}) != length of by ({len(by)})')

        order_by = [
            SortColumn(expression=series.expression, asc=asc)
            for series, asc in zip(by, ascending)
        ]
        return self.copy_override(order_by=order_by)

    def sort_index(self: SeriesSubType, *, ascending: Union[List[bool], bool] = True) -> SeriesSubType:
        """
        Sort this Series by its index.
        Returns a new instance and does not modify the instance it is called on.

        :param ascending: either a bool indicating whether to sort ascending or descending, or a list of
            bools indicating ascending/descending for each of the index levels/columns.

        """
        if isinstance(ascending, list):
            if len(ascending) != len(self.index):
                raise ValueError(f'Length of ascending ({len(ascending)}) should match '
                                 f'index levels ({len(self.index)}).')
            ascending_list = ascending
        else:
            ascending_list = [ascending] * len(self.index)
        if not all(isinstance(asc, bool) for asc in ascending_list):
            raise ValueError('Parameter ascending should be a bool or a list of bools')

        return self.sort_by_series(
            by=list(self.index.values()), ascending=ascending_list,
        )

    def view_sql(self) -> str:
        return self.to_frame().view_sql()

    def to_frame(self) -> DataFrame:
        """
        Create a DataFrame with the index and data from this Series.

        The DataFrame returned has the grouping and sorting also set like this Series had.
        """
        from bach.savepoints import Savepoints
        return DataFrame(
            engine=self._engine,
            base_node=self._base_node,
            index=self._index,
            series={self._name: self},
            group_by=self._group_by,
            order_by=self.order_by,
            savepoints=Savepoints(),
            variables={}
        )

    @staticmethod
    def as_independent_subquery(series: 'Series', operation: str = None, dtype: str = None) -> 'Series':
        """
        INTERNAL: Get a series representing an independent subquery, created by materializing the series
        given and crafting a subquery expression from it, possibly adding the given operation.

        .. note::
            This will maintain Expression.is_single_value status
        """
        # This will give us a dataframe that contains our series as a materialized column in the base_node
        if series.expression.has_multi_level_expressions:
            raise NotImplementedError(
                'Series with multiple level expressions cannot be used as independent subquery.'
            )

        if series.expression.is_independent_subquery:
            expr = series.expression
        else:
            df = series.to_frame()
            if df.group_by:
                df = series.to_frame().materialize('independent_subquery_w_groupby')
            expr = IndependentSubqueryExpression.construct('(SELECT {} FROM {})',
                                                           df[series.name].get_column_expression(),
                                                           Expression.model_reference(df.base_node))

        if operation:
            expr = IndependentSubqueryExpression.construct(f'{operation} {{}}', expr)

        if series.expression.is_single_value and not expr.is_single_value:
            # The expression is lost when materializing
            expr = SingleValueExpression(expr)

        s = series\
            .copy_override_dtype(dtype=dtype)\
            .copy_override(expression=expr, index={}, group_by=None)
        return s

    def exists(self) -> 'SeriesBoolean':
        """
        Boolean operation that returns True if there are one or more values in this Series
        """
        s = Series.as_independent_subquery(self, 'exists', dtype='bool')
        return cast('SeriesBoolean', s.copy_override(expression=SingleValueExpression(s.expression)))

    def any_value(self) -> 'Series':
        """
        For every row in this Series, do multiple evaluations where _any_ sub-evaluation should be True

        Example: a > b.any() evaluates to True is a > b for any value of b.
        """
        return Series.as_independent_subquery(self, 'any')

    def all_values(self) -> 'Series':
        """
        For every row in this Series, do multiple evaluations where _all_ sub-evaluations should be True

        Example: a > b.all() evaluates to True is a > b for all values of b.
        """
        return Series.as_independent_subquery(self, 'all')

    def isin(self, other: 'Series') -> 'SeriesBoolean':
        """
        Evaluate for every row in this series whether the value is contained in other

        Example: a.isin(b) evaluates to True for a specific row if a > b for all values of b.
        """
        in_expr = Expression.construct('{} {}', self, Series.as_independent_subquery(other, 'in'))
        from bach import SeriesBoolean
        return self.copy_override_type(SeriesBoolean).copy_override(expression=in_expr)

    def astype(self, dtype: Union[str, Type]) -> 'Series':
        """
        Convert this Series to another type.

        A Series will be returned with the correct type set, if the conversion is available. An appropriate
        Exception will be raised if impossible to convert.
        :param dtype: dtype or a dtype alias
        """
        if dtype == self.dtype or dtype in self.dtype_aliases:
            return self
        series_type = get_series_type_from_dtype(dtype)
        expression = series_type.dtype_to_expression(
            dialect=self.engine.dialect,
            source_dtype=self.dtype,
            expression=self.expression
        )
        new_dtype = series_type.dtype
        return self.copy_override_dtype(dtype=new_dtype).copy_override(expression=expression)

    def equals(self, other: Any, recursion: Optional[str] = None) -> bool:
        """
        INTERNAL: Checks whether other is the same as self. This implements the check that would normally be
        implemented in __eq__, but we already use that method for other purposes.
        This strictly checks that other is the same type as self. If other is a subclass this will return
        False.
        """
        if not isinstance(other, self.__class__) or not isinstance(self, other.__class__):
            return False
        return (
                dict_name_series_equals(self.index, other.index) and
                self.engine == other.engine and
                self.base_node == other.base_node and
                self.name == other.name and
                self.expression == other.expression and
                # avoid loops here.
                (recursion == 'GroupBy' or self.group_by == other.group_by) and
                self.order_by == other.order_by and
                self.instance_dtype == other.instance_dtype
        )

    def __getitem__(self: SeriesSubType, key: Union[Any, slice]) -> SeriesSubType:
        """
        Get a single value from the series. This is not returning the value,
        use the .value accessor for that instead.

        :note: When slicing, the caller is responsible for the order of the sliced Series as data returned
            can be ordered non-deterministically.
        """
        frame = self.to_frame()
        if isinstance(key, slice):
            if self.expression.is_single_value:
                raise ValueError('Slicing on single value expressions is not supported.')
            return cast(SeriesSubType, frame[key][self.name])

        if len(self.index) == 0:
            raise Exception('Not supported on Series without index. '
                            'Use .values[index] instead.')
        if len(self.index) > 1:
            raise NotImplementedError('Index only implemented for simple indexes. '
                                      'Use .values[index] instead')

        # Apply Boolean selection on index == key, help mypy a bit
        frame = cast(DataFrame, frame[list(frame.index.values())[0] == key])
        # limit to 1 row, will make all series SingleValueExpression, and get that series.
        return cast(SeriesSubType, frame[:1][self.name])

    def isnull(self) -> 'SeriesBoolean':
        """
        Evaluate for every row in this series whether the value is missing or NULL.

        .. note::
            Only NULL values in the Series in the underlying sql table will return True. numpy.nan is not
            checked for.

        See Also
        --------
        notnull
        """
        expression_str = f'{{}} is null'
        expression = NonAtomicExpression.construct(
            expression_str,
            self
        )
        from bach import SeriesBoolean
        return self.copy_override_type(SeriesBoolean).copy_override(expression=expression)

    def notnull(self) -> 'SeriesBoolean':
        """
        Evaluate for every row in this series whether the value is not missing or NULL.

        .. note::
          Only NULL values in the Series in the underlying sql table will return True. numpy.nan is not
          checked for.

        See Also
        --------
        isnull
        """
        expression_str = f'{{}} is not null'
        expression = NonAtomicExpression.construct(
            expression_str,
            self
        )
        from bach import SeriesBoolean
        return self.copy_override_type(SeriesBoolean).copy_override(expression=expression)

    def fillna(self: SeriesSubType, other: AllSupportedLiteralTypes) -> SeriesSubType:
        """
        Fill any NULL value with the given constant or other compatible Series

        In case a Series is given, the value from the same row is used to fill.

        :param other: The value to replace the NULL values with. Should be a supported
            type by the series, or a TypeError is raised. Can also be another Series

        .. note::
            Pandas replaces numpy.nan values, we can only replace NULL.

        .. note::
            You can replace None with None, have fun, forever!
        """
        return cast(
            SeriesSubType,
            self._binary_operation(
                other=other,
                operation='fillna',
                fmt_str='COALESCE({}, {})',
                other_dtypes=tuple([self.dtype]),
            )
        )

    def _binary_operation(
        self,
        other: Union[AllSupportedLiteralTypes, 'Series'],
        operation: str,
        fmt_str: str,
        other_dtypes: Tuple[str, ...] = (),
        dtype: Optional[Union[str, Mapping[str, Optional[str]]]] = None
    ) -> 'Series':
        """
        The standard way to perform a binary operation

        :param self: SeriesSubTypehe left hand side expression (lhs) in the operation
        :param other: The right hand side expression (rhs) in the operation
        :param operation: A user-readable representation of the operation
        :param fmt_str: An Expression.construct format string, accepting lhs and rhs as the only parameters,
            in that order.
        :param other_dtypes: The acceptable dtypes for the rhs expression
        :param dtype: The new dtype for the Series that results from this operation. Leave None for same
            as lhs, pass a string with the new explicit dtype, or pass a dict that maps rhs.dtype to the
            resulting dtype. If the dict does not contain the rhs.dtype, None is assumed, using the lhs
            dtype.
        """
        if len(other_dtypes) == 0:
            raise NotImplementedError(f'binary operation {operation} not supported '
                                      f'for {self.__class__} and {other.__class__}')

        other = value_to_series(base=self, value=other)
        self_modified, other = self._get_supported(operation, other_dtypes, other)
        expression = NonAtomicExpression.construct(fmt_str, self_modified, other)

        new_dtype: Optional[str]
        if dtype is None or isinstance(dtype, str):
            new_dtype = dtype
        else:  # dtype is Mapping[str, Optional[str]]
            if other.dtype not in dtype:
                new_dtype = None
            else:
                new_dtype = dtype[other.dtype]

        return self_modified.copy_override_dtype(dtype=new_dtype).copy_override(expression=expression)

    def _arithmetic_operation(
        self,
        other: Union[AllSupportedLiteralTypes, 'Series'],
        operation: str,
        fmt_str: str,
        other_dtypes: Tuple[str, ...] = (),
        dtype: Optional[Union[str, Mapping[str, Optional[str]]]] = None
    ) -> 'Series':
        """
        implement this in a subclass to have boilerplate support for all arithmetic functions
        defined below, but also call this method from specific arithmetic operation implementations
        without implementing it to get nice error messages in yield.

        :see: _binary_operation() for parameters
        """
        if len(other_dtypes) == 0:
            raise TypeError(f'arithmetic operation {operation} not supported for '
                            f'{self.__class__} and {other.__class__}')
        return self._binary_operation(other, operation, fmt_str, other_dtypes, dtype)

    def __add__(self, other: Union[AllSupportedLiteralTypes, 'Series']) -> 'Series':
        return self._arithmetic_operation(other, 'add', '{} + {}')

    def __sub__(self, other: Union[AllSupportedLiteralTypes, 'Series']) -> 'Series':
        return self._arithmetic_operation(other, 'sub', '{} - {}')

    def __truediv__(self, other: Union[AllSupportedLiteralTypes, 'Series']) -> 'Series':
        """ This case is not generically okay. subclasses should check that"""
        return self._arithmetic_operation(other, 'div', '{} / {}')

    def __floordiv__(self, other: Union[AllSupportedLiteralTypes, 'Series']) -> 'Series':
        return self._arithmetic_operation(other, 'floordiv', 'floor({} / {})', dtype='int64')

    def __mul__(self, other: Union[AllSupportedLiteralTypes, 'Series']) -> 'Series':
        return self._arithmetic_operation(other, 'mul', '{} * {}')

    def __mod__(self, other: Union[AllSupportedLiteralTypes, 'Series']) -> 'Series':
        # PG is picky in data types, so we solve it like this.
        # dividend - floor(dividend / divisor) * divisor';
        return self - self // other * other

    def __pow__(
        self,
        other: 'Series',
        modulo: Optional[Union[AllSupportedLiteralTypes, 'Series']] = None,
    ) -> 'Series':
        if modulo is not None:
            return (self.__pow__(other, None)).__mod__(modulo)
        return self._arithmetic_operation(other, 'pow', 'POWER({}, {})')

    def __lshift__(self, other: Union[AllSupportedLiteralTypes, 'Series']) -> 'Series':
        raise NotImplementedError()

    def __rshift__(self, other: Union[AllSupportedLiteralTypes, 'Series']) -> 'Series':
        raise NotImplementedError()

    # Boolean operations
    def __invert__(self) -> 'Series':
        raise NotImplementedError()

    def __and__(self, other) -> 'Series':
        raise NotImplementedError()

    def __xor__(self, other) -> 'Series':
        raise NotImplementedError()

    def __or__(self, other) -> 'Series':
        raise NotImplementedError()

    # Comparator operations
    def _comparator_operation(
        self,
        other: Union['Series', AllSupportedLiteralTypes],
        comparator: str,
        other_dtypes: Tuple[str, ...] = ()
    ) -> 'SeriesBoolean':
        if len(other_dtypes) == 0:
            raise TypeError(f'comparator {comparator} not supported for '
                            f'{self.__class__} and {other.__class__}')
        return cast('SeriesBoolean', self._binary_operation(
            other=other, operation=f"comparator '{comparator}'",
            fmt_str=f'{{}} {comparator} {{}}',
            other_dtypes=other_dtypes, dtype='bool'
        ))

    def __ne__(self, other: Union['Series', AllSupportedLiteralTypes]) -> 'SeriesBoolean':   # type: ignore
        return self._comparator_operation(other, "<>")

    def __eq__(self, other: Union['Series', AllSupportedLiteralTypes]) -> 'SeriesBoolean':   # type: ignore
        return self._comparator_operation(other, "=")

    def __lt__(self, other: Union['Series', AllSupportedLiteralTypes]) -> 'SeriesBoolean':
        return self._comparator_operation(other, "<")

    def __le__(self, other: Union['Series', AllSupportedLiteralTypes]) -> 'SeriesBoolean':
        return self._comparator_operation(other, "<=")

    def __ge__(self, other: Union['Series', AllSupportedLiteralTypes]) -> 'SeriesBoolean':
        return self._comparator_operation(other, ">=")

    def __gt__(self, other: Union['Series', AllSupportedLiteralTypes]) -> 'SeriesBoolean':
        return self._comparator_operation(other, ">")

    def apply_func(self, func: ColumnFunction, *args, **kwargs) -> List['Series']:
        """
        Apply the given functions to this Series.
        If multiple are given, a list of multiple new series will be returned.

        :param func: the function to look for on all series, either as a str, or callable,
                    or a list of such
        :param args: Positional arguments to pass through to the aggregation function
        :param kwargs: Keyword arguments to pass through to the aggregation function

        .. warning::
            You should probably not use this method directly.
        """
        if self.expression.has_multi_level_expressions:
            raise NotImplementedError('cannot apply functions to a series with multiple levels.')

        if isinstance(func, str) or callable(func):
            func = [func]
        if not isinstance(func, list):
            raise TypeError(f'Unsupported type for func: {type(func)}')
        if len(func) == 0:
            raise Exception('Nothing to do.')

        series = {}
        for fn in func:
            if isinstance(fn, str):
                series_name = f'{self.name}_{fn}'
                fn = cast(Callable, getattr(self, fn))
            elif callable(fn):
                series_name = f'{self._name}_{fn.__name__}'
            else:
                raise ValueError("func {fn} is not callable")

            # If the method is bound yet (__self__ set), we need to use the unbound function
            # to make sure call the method on the right series
            if hasattr(fn, '__self__'):
                fn = cast(Callable, fn.__func__)  # type: ignore[attr-defined]

            fn_applied_series = fn(self, *args, **kwargs)
            if series_name in series:
                raise ValueError(f'duplicate series target name {series_name}')
            series[series_name] = fn_applied_series.copy_override(name=series_name)

        return list(series.values())

    def aggregate(self,
                  func: ColumnFunction,
                  group_by: 'GroupBy' = None,
                  *args, **kwargs) -> DataFrameOrSeries:
        """
        Alias for :py:meth:`agg()`.
        """
        return self.agg(func, group_by, *args, **kwargs)

    def agg(self,
            func: ColumnFunction,
            group_by: 'GroupBy' = None,
            *args, **kwargs) -> DataFrameOrSeries:
        """
        Apply one or more aggregation functions to this Series.

        :param func: the aggregation function to look for on all series.
            See GroupBy.agg() for supported arguments
        :param group_by: the group_by to use, or aggregation over full base_node if None
        :param args: Positional arguments to pass through to the aggregation function
        :param kwargs: Keyword arguments to pass through to the aggregation function
        :return: Aggregated Series, or DataFrame if multiple series are returned
        """
        if group_by is None:
            from bach.partitioning import GroupBy
            group_by = GroupBy([])

        series = self.apply_func(func, group_by, *args, **kwargs)
        if len(series) == 1:
            return series[0]

        from bach.savepoints import Savepoints
        return DataFrame(engine=self.engine,
                         base_node=self.base_node,
                         index=group_by.index,
                         series={s.name: s for s in series},
                         group_by=group_by,
                         order_by=[],
                         savepoints=Savepoints())

    def _check_unwrap_groupby(
        self,
        wrapped: Optional[WrappedPartition],
        isin: Optional[Tuple[Type['GroupBy'], ...]] = None,
        notin: Optional[Tuple[Type['GroupBy'], ...]] = None,
    ) -> 'GroupBy':
        """
        1. If `wrapped` is a GroupBy, or if it contains one, use that.
        2. If it's None, check whether this Series has a group_by set and use that.
        3. If that still yields nothing, create a GroupBy([]) and use that.

        After that, perform some checks:
        - Make sure that the used GroupBy instance is of a type in the set `isin`, defaulting
          to make sure it's a GroupBy if `isin` is None
        - Make sure that it's instance type is not in `notin`

        Exceptions will be raised when check don't pass
        :returns: The potentially unwrapped GroupBy
        """
        from bach.partitioning import GroupBy
        isin = (GroupBy, ) if isin is None else isin
        notin = () if notin is None else notin

        if wrapped is None:
            if self._group_by:
                group_by = self._group_by
            else:
                # create an aggregation over the entire input
                group_by = GroupBy([])
        else:
            if isinstance(wrapped, DataFrame):
                unwrapped = wrapped.group_by
                if unwrapped is None:
                    unwrapped = GroupBy([])
            else:
                unwrapped = wrapped

            if self._group_by and self._group_by != unwrapped:
                raise ValueError("Series group_by not the same as given partition; I'm confused.")
            group_by = unwrapped

        if not isinstance(group_by, isin):
            raise ValueError(f'group_by {type(group_by)} not in {isin}')
        if isinstance(group_by, notin):
            raise ValueError(f'group_by {type(group_by)} not supported')
        return group_by

    def _derived_agg_func(
        self,
        partition: Optional[WrappedPartition],
        expression: Union[str, Expression],
        dtype: Optional[str] = None,
        skipna: bool = True,
        min_count: Optional[int] = None,
    ) -> 'Series':
        """
        Create a derived Series that aggregates underlying Series through the given expression.
        If no partition to aggregate on is given, and the Series does not have one set,
        it will create one that aggregates the entire series without any partitions.
        This allows for calls like:
          someseries.sum()

        Skipna will also be checked here as to make the callers life as simple as possible.
        :param partition: The Aggregator containing the GroupBy, or just the GroupBy
            to execute the expression within.
        :param expression: str or Expression of the aggregation function.
        :param dtype: Will be used for derived series if not None.
        :param skipna: skipna parameter for support check.
        :returns: The correctly typed derived Series, with either the current index in case of
            a Window function, or the GroupBy otherwise.
        """
        from bach.partitioning import Window

        if not skipna:
            raise NotImplementedError('Not skipping n/a is not supported')

        if self.expression.has_windowed_aggregate_function:
            raise ValueError(f'Cannot call an aggregation function on already windowed column '
                             f'`{self.name}` Try calling materialize() on the DataFrame'
                             f' this Series belongs to first.')

        if self.expression.has_aggregate_function:
            raise ValueError(f'Cannot call an aggregation function on already aggregated column '
                             f'`{self.name}` Try calling materialize() on the DataFrame'
                             f' this Series belongs to first.')

        if self.expression.has_multi_level_expressions:
            raise ValueError('Cannot call an aggregation function on a series containing multiple levels.')

        if isinstance(expression, str):
            expression = AggregateFunctionExpression.construct(f'{expression}({{}})', self)

        partition = self._check_unwrap_groupby(partition)

        if min_count is not None and min_count > 0:
            if isinstance(partition, Window):
                if partition.min_values != min_count:
                    raise NotImplementedError(
                        f'min_count conflicting with min_values in Window'
                        f'{min_count} != {partition.min_values}'
                    )
            else:
                expression = Expression.construct(
                    f'CASE WHEN {{}} >= {min_count} THEN {{}} ELSE NULL END',
                    self.count(partition, skipna=skipna), expression
                )
        derived_dtype = self.dtype if dtype is None else dtype

        if not isinstance(partition, Window):
            if self._group_by and self._group_by != partition:
                raise ValueError('passed partition does not match series partition. I\'m confused')

            # if the passed expression was not a str, make sure it's tagged correctly
            # we can't check the outer expression, because min_values logic above could have already wrapped
            # it.
            if not expression.has_aggregate_function:
                raise ValueError('Passed expression should contain an aggregation function')

            if partition.index == {}:
                # we're creating an aggregation on everything, this will yield one value
                expression = SingleValueExpression(expression)

            return self\
                .copy_override_dtype(dtype=derived_dtype)\
                .copy_override(
                    index=partition.index,
                    group_by=partition,
                    expression=expression,
                    order_by=[],
                )
        else:
            # The window expression already contains the full partition and sorting, no need
            # to keep that with this series, the expression can be used without any of those.
            return self\
                .copy_override_dtype(dtype=derived_dtype)\
                .copy_override(
                    group_by=None,
                    expression=partition.get_window_expression(expression),
                )

    def count(self, partition: WrappedPartition = None, skipna: bool = True) -> 'SeriesInt64':
        """
        Returns the amount of rows in each partition or for all values if none is given.

        :param partition: The partition or window to apply
        :param skipna: only ``skipna=True`` supported. This means NULL values are ignored.
        :returns: a new Series with the aggregation applied
        """
        # count is not constant because it depends on the number of rows in the selection.
        # See the comment in Expression.AggregationFunctionExpression
        return cast(
            'SeriesInt64', self._derived_agg_func(partition, 'count', 'int64', skipna=skipna)
        )

    def max(self: SeriesSubType, partition: WrappedPartition = None, skipna: bool = True) -> SeriesSubType:
        """
        Returns the maximum value in each partition or for all values if none is given.

        :param partition: The partition or window to apply
        :param skipna: only ``skipna=True`` supported. This means NULL values are ignored.
        :returns: a new Series with the aggregation applied
        """
        result = self._derived_agg_func(partition, 'max', skipna=skipna)
        return cast(SeriesSubType, result)

    def median(self: SeriesSubType, partition: WrappedPartition = None, skipna: bool = True) -> SeriesSubType:
        """
        Returns the median in each partition or for all values if none is given.

        :param partition: The partition or window to apply
        :param skipna: only ``skipna=True`` supported. This means NULL values are ignored.
        :returns: a new Series with the aggregation applied
        """
        result = self._derived_agg_func(
            partition=partition,
            expression=AggregateFunctionExpression.construct(
                f'percentile_disc(0.5) WITHIN GROUP (ORDER BY {{}})', self),
            skipna=skipna
        )
        return cast(SeriesSubType, result)

    def min(self: SeriesSubType, partition: WrappedPartition = None, skipna: bool = True) -> SeriesSubType:
        """
        Returns the minimum value in each partition or for all values if none is given.

        :param partition: The partition or window to apply
        :param skipna: only ``skipna=True`` supported. This means NULL values are ignored.
        :returns: a new Series with the aggregation applied
        """
        result = self._derived_agg_func(partition, 'min', skipna=skipna)
        return cast(SeriesSubType, result)

    def mode(self: SeriesSubType, partition: WrappedPartition = None, skipna: bool = True) -> SeriesSubType:
        """
        Returns the mode in each partition or for all values if none is given.

        :param partition: The partition or window to apply
        :param skipna: only ``skipna=True`` supported. This means NULL values are ignored.
        :returns: a new Series with the aggregation applied

        .. warning::
            The result of this function might be non-deterministic if there are multiple values with
            the same frequency.

        .. note::
            BigQuery has no support for aggregation function ``MODE``, therefore ``APPROX_TOP_COUNT``
            approximate aggregate function is used instead. Which means that an approximate result will
            be produced instead of exact results.

            For more information:
            https://cloud.google.com/bigquery/docs/reference/standard-sql/approximate_aggregate_functions#approx_top_count
        """
        agg_expr = f'mode() within group (order by {{}})'
        if is_bigquery(self.engine):
            # BigQuery has no aggregate function for mode, therefore we use
            # APPROX_TOP_COUNT which return an approximation of the exact result
            # https://cloud.google.com/bigquery/docs/reference/standard-sql/approximate_aggregate_functions
            agg_expr = f'approx_top_count({{}}, 1)[offset(0)].value'

        result = self._derived_agg_func(
            partition=partition,
            expression=AggregateFunctionExpression.construct(agg_expr, self),
            skipna=skipna
        )
        return cast(SeriesSubType, result)

    def nunique(self, partition: WrappedPartition = None, skipna: bool = True) -> 'SeriesInt64':
        """
        Returns the amount of unique values in each partition or for all values if none is given.

        :param partition: The partition or window to apply
        :param skipna: only ``skipna=True`` supported. This means NULL values are ignored.
        :returns: a new Series with the aggregation applied
        """
        from bach.partitioning import Window
        partition = self._check_unwrap_groupby(partition, notin=(Window, ))
        result = self._derived_agg_func(
            partition=partition, dtype='int64',
            expression=AggregateFunctionExpression.construct('count(distinct {})', self),
            skipna=skipna)

        return cast('SeriesInt64', result)

    def unique(self: SeriesSubType, partition: WrappedPartition = None, skipna: bool = True) -> SeriesSubType:
        """
        Return all unique values in this Series.

        :param partition: The partition or window to apply.
        :param skipna: If true, all NULL values are ignored.
        :returns: a new Series with the aggregation applied
        """
        if partition:
            raise ValueError('Can not use group_by in combination with unique(). Materialize() first.')

        df = self.to_frame().reset_index(drop=True)

        if skipna:
            df = df.dropna()
        df = df.materialize(distinct=True)

        df[f'{self.name}_unique'] = df[self.name]
        df = df.set_index(self.name)

        return cast(SeriesSubType, df[f'{self.name}_unique'])

    # Window functions applicable for all types of data, but only with a window
    # TODO more specific docs
    # TODO make group_by optional, but for that we need to use current series sorting
    def _check_window(
        self, agg_function: 'WindowFunction', window: Optional[WrappedWindow],
    ) -> 'Window':
        """
        Validate that the given partition or the stored group_by is a true Window or raise an exception
        """
        from bach.partitioning import Window
        checked_window = cast(Window, self._check_unwrap_groupby(window, isin=(Window, )))

        if not agg_function.supports_window_frame_clause(dialect=self.engine.dialect):
            # remove boundaries if the functions does not support window frame clause
            return checked_window.set_frame_clause(start_boundary=None, end_boundary=None)

        return checked_window

    def window_row_number(self, window: Optional[WrappedWindow] = None) -> 'SeriesInt64':
        """
        Returns the number of the current row within its window, counting from 1.
        """
        from bach.partitioning import WindowFunction
        window = self._check_window(WindowFunction.ROW_NUMBER, window)

        return cast(
            'SeriesInt64',
            self._derived_agg_func(window, Expression.construct('row_number()'), 'int64')
        )

    def window_rank(self, window: Optional[WrappedWindow] = None) -> 'Series':
        """
        Returns the rank of the current row, with gaps; that is, the row_number of the first row
        in its peer group.
        """
        from bach.partitioning import WindowFunction
        window = self._check_window(WindowFunction.RANK, window)

        return cast(
            'SeriesInt64',
            self._derived_agg_func(window, Expression.construct('rank()'), 'int64')
        )

    def window_dense_rank(self, window: Optional[WrappedWindow] = None) -> 'SeriesInt64':
        """
        Returns the rank of the current row, without gaps; this function effectively counts peer
        groups.
        """
        from bach.partitioning import WindowFunction
        window = self._check_window(WindowFunction.DENSE_RANK, window)

        return cast(
            'SeriesInt64',
            self._derived_agg_func(window, Expression.construct('dense_rank()'), 'int64')
        )

    def window_percent_rank(self, window: Optional[WrappedWindow] = None) -> 'SeriesFloat64':
        """
        Returns the relative rank of the current row, that is
        (rank - 1) / (total partition rows - 1).
        The value thus ranges from 0 to 1 inclusive.
        """
        from bach.partitioning import WindowFunction
        window = self._check_window(WindowFunction.PERCENT_RANK, window)

        return cast(
            'SeriesFloat64',
            self._derived_agg_func(window, Expression.construct('percent_rank()'), "double precision"),
        )

    def window_cume_dist(self, window: Optional[WrappedWindow] = None) -> 'SeriesFloat64':
        """
        Returns the cumulative distribution, that is
        (number of partition rows preceding or peers with current row) / (total partition rows).
        The value thus ranges from 1/N to 1.
        """
        from bach.partitioning import WindowFunction
        window = self._check_window(WindowFunction.CUME_DIST, window)

        return cast(
            'SeriesFloat64',
            self._derived_agg_func(window, Expression.construct('cume_dist()'), "double precision"),
        )

    def window_ntile(self, num_buckets: int = 1, window: Optional[WrappedWindow] = None) -> 'SeriesInt64':
        """
        Returns an integer ranging from 1 to the argument value,
        dividing the partition as equally as possible.
        """
        from bach.partitioning import WindowFunction
        window = self._check_window(WindowFunction.NTILE, window)

        return cast(
            'SeriesInt64',
            self._derived_agg_func(window, Expression.construct(f'ntile({num_buckets})'), "int64"),
        )

    def window_lag(
        self: SeriesSubType, offset: int = 1, default: Any = None, window: Optional[WrappedWindow] = None,
    ) -> SeriesSubType:
        """
        Returns value evaluated at the row that is offset rows before the current row within the window

        If there is no such row, instead returns default (which must be of the same type as value).
        Both offset and default are evaluated with respect to the current row.
        :param offset: The amount of rows to look back, default 1
        :param default: The value to return if no value is available, can be a constant value or Series.
        Defaults to None
        """
        from bach.partitioning import WindowFunction
        # TODO Lag, lead etc. could check whether the window is setup correctly to include that value
        window = self._check_window(WindowFunction.LAG, window)
        default_expr = self.value_to_expression(dialect=self.engine.dialect, value=default, dtype=self.dtype)
        result = self._derived_agg_func(
            window,
            Expression.construct(f'lag({{}}, {offset}, {{}})', self, default_expr),
            self.dtype
        )
        return cast(SeriesSubType, result)

    def window_lead(
        self: SeriesSubType,
        offset: int = 1,
        default: Optional[Any] = None,
        window: Optional[WrappedWindow] = None,
    ) -> SeriesSubType:
        """
        Returns value evaluated at the row that is offset rows after the current row within the window.

        If there is no such row, instead returns default (which must be of the same type as value).
        Both offset and default are evaluated with respect to the current row.
        :param offset: The amount of rows to look forward, default 1
        :param default: The value to return if no value is available, can be a constant value or Series.
        Defaults to None
        """
        from bach.partitioning import WindowFunction
        window = self._check_window(WindowFunction.LEAD, window)
        default_expr = self.value_to_expression(dialect=self.engine.dialect, value=default, dtype=self.dtype)
        result = self._derived_agg_func(
            window,
            Expression.construct(f'lead({{}}, {offset}, {{}})', self, default_expr),
            self.dtype
        )
        return cast(SeriesSubType, result)

    def window_first_value(self: SeriesSubType, window: Optional[WrappedWindow] = None) -> SeriesSubType:
        """
        Returns value evaluated at the row that is the first row of the window frame.
        """
        from bach.partitioning import WindowFunction
        window = self._check_window(WindowFunction.FIRST_VALUE, window)
        result = self._derived_agg_func(
            window,
            Expression.construct('first_value({})', self),
            self.dtype
        )
        return cast(SeriesSubType, result)

    def window_last_value(self: SeriesSubType, window: Optional[WrappedWindow] = None) -> SeriesSubType:
        """
        Returns value evaluated at the row that is the last row of the window frame.
        """
        from bach.partitioning import WindowFunction
        window = self._check_window(WindowFunction.LAST_VALUE, window)
        result = self._derived_agg_func(window, Expression.construct('last_value({})', self), self.dtype)

        return cast(SeriesSubType, result)

    def window_nth_value(
        self: SeriesSubType, n: int, window: Optional[WrappedWindow] = None,
    ) -> SeriesSubType:
        """
        Returns value evaluated at the row that is the n'th row of the window frame.
        (counting from 1); returns NULL if there is no such row.
        """
        from bach.partitioning import WindowFunction
        window = self._check_window(WindowFunction.NTH_VALUE, window)
        result = self._derived_agg_func(
            window,
            Expression.construct(f'nth_value({{}}, {n})', self),
            self.dtype
        )
        return cast(SeriesSubType, result)

    def append(
        self,
        other: Union['Series', List['Series']],
        ignore_index: bool = False,
    ) -> 'Series':
        """
        Append rows of other series to the caller series.

        :param other: objects to be added
        :param ignore_index: if true, drops indexes of all objects to be appended

        :return: a new series with all rows from appended other or self if other is empty.
        """
        from bach.operations.concat import SeriesConcatOperation
        if not other:
            return self

        other_series = other if isinstance(other, list) else [other]
        concatenated_series = SeriesConcatOperation(
            objects=[self] + other_series,
            ignore_index=ignore_index,
        )()
        return concatenated_series

    def describe(
        self,
        percentiles: Optional[Sequence[float]] = None,
        datetime_is_numeric: bool = False,
    ) -> 'Series':
        """
        Returns descriptive statistics, it will vary based on what is provided

        :param percentiles: list of percentiles to be calculated. Values must be between 0 and 1.
        :param datetime_is_numeric: not supported
        :returns: a new Series with the descriptive statistics
        """
        from bach.operations.describe import SeriesDescribeOperation
        return SeriesDescribeOperation(
            obj=self, datetime_is_numeric=datetime_is_numeric, percentiles=percentiles,
        )()

    def drop_duplicates(self: SeriesSubType, keep: Union[str, bool] = 'first') -> SeriesSubType:
        """
        Return a series with duplicated rows removed.

        :param keep: Supported values: "first", "last" and False. Determines which duplicates to keep:

            * `first`: drop all occurrences except the first one
            * `last`:  drop all occurrences except the last one
            * False: drops all duplicates

            If no value is provided, first occurrences will be kept by default.

        :return: a new series with dropped duplicates
        """
        df = self.to_frame().drop_duplicates(keep=keep)
        df = df.materialize()

        result = df.all_series[self.name]
        return cast(SeriesSubType, result)

    def dropna(self: SeriesSubType) -> SeriesSubType:
        """
        Removes rows with missing values.

        :return: a new series with dropped rows.
        """
        df = self.to_frame().dropna()
        assert isinstance(df, DataFrame)
        return cast(SeriesSubType, df.all_series[self.name])

    def value_counts(
        self,
        normalize: bool = False,
        sort: bool = True,
        ascending: bool = False,
        bins: Optional[int] = None,
        method: str = 'pandas',
    ) -> 'Series':
        """
        Returns a series containing counts per unique value

        :param normalize: returns proportions instead of frequencies
        :param sort: sorts result by frequencies
        :param ascending: sorts values in ascending order if true.
        :param bins: works only with numeric series, groups values into the request amount of bins
            and counts values based on each range.
        :param method: Method to use for calculating bin ranges.
            Supported values:

                - "pandas" (default): Performs bound adjustments based on Pandas implementation.

                - "bach": No bound adjustments are performed. Instead, first interval includes both
                  lower and upper bounds.

        :return: a series containing all counts per unique row.
        """
        from bach.series.series_numeric import SeriesAbstractNumeric
        if bins and not isinstance(self, SeriesAbstractNumeric):
            raise ValueError('Cannot calculate bins for non numeric series.')

        if not bins:
            return self.to_frame().value_counts(normalize=normalize, sort=sort, ascending=ascending)

        from bach.operations.cut import CutOperation, CutMethod
        if not any(method == valid_method.value for valid_method in CutMethod):
            raise ValueError(f'"{method}" is not a valid method.')

        assert isinstance(self, SeriesAbstractNumeric)
        bins_series = CutOperation(series=self, bins=bins, include_empty_bins=True, method=method)()

        bins_df = bins_series.to_frame()
        bins_w_values_df = bins_df[bins_series.index[self.name].notnull()]
        empty_bins_df = bins_df[bins_series.index[self.name].isnull()]

        # count only the bins that actually have value in the series
        # sort is not needed since final result is sorted after appending empty bins
        value_counts_result = bins_w_values_df.value_counts(normalize=normalize, sort=False)

        assert isinstance(empty_bins_df, DataFrame)
        empty_bins_df['value_counts'] = 0
        empty_bins_df = empty_bins_df.set_index(CutOperation.RANGE_SERIES_NAME)

        # append empty bins with count 0, final result must show those ranges
        result = value_counts_result.append(empty_bins_df.all_series['value_counts'])
        result = result.copy_override(name='value_counts')
        if sort:
            return result.sort_values(ascending=ascending)

        return result


def value_to_series(base: DataFrameOrSeries,
                    value: Union[AllSupportedLiteralTypes, Series],
                    name: str = None) -> Series:
    """
    INTERNAL: Take a value and return a Series representing a column with that value.

    If value is already a Series it is returned unchanged unless it has no base_node set, in case
    it's a subquery. We create a copy and hook it to our base node in that case, so we can work with it.
    If value is a constant then the right Series subclass is found for that type and instantiated
    with the constant value.
    :param base: Base series or DataFrame. In case a new Series object is created and returned, it will
        share its engine, index, and base_node with this one. Only applies if value is not a Series
    :param value: value for which to create a Series, or a Series
    :param name: optional name for the series object. Only applies if value is not a Series
    :return:
    """
    if isinstance(value, Series):
        return value
    name = '__const__' if name is None else name
    series_type = value_to_series_type(value)
    return series_type.from_value(base=base, value=value, name=name)


def variable_series(
    base: DataFrameOrSeries,
    value: Union[AllSupportedLiteralTypes, Series],
    name: str
) -> Series:
    """
    INTERNAL: Return a series with the same dtype as the value, but with a VariableToken instead of the
    value's literal in the series.expression.
    :param base: Base series or DataFrame. The new Series object will share its engine, index, and
        base_node with this one.
    :param value: constant value, used to determine the dtype of the series and the VariableToken in the
        series's expression.
    :param name: name of the variable
    """
    if isinstance(value, Series):
        return value
    series_type = value_to_series_type(value)
    variable_placeholder = Expression.variable(dtype=series_type.dtype, name=name)
    variable_expression = series_type.supported_literal_to_expression(
        dialect=base.engine.dialect,
        literal=variable_placeholder
    )
    result = series_type.get_class_instance(
        engine=base.engine,
        base_node=base.base_node,
        index=base.index,
        name='__variable__',
        expression=ConstValueExpression(variable_expression),
        group_by=None,
        order_by=[],
        instance_dtype=series_type.dtype  # TODO: make work for structural types too
    )
    return result
