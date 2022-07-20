"""
Copyright 2022 Objectiv B.V.
"""
import operator
from abc import ABC, abstractmethod
from copy import copy
from functools import reduce
from typing import Union, List, Optional, Dict, Any, cast, TypeVar, Tuple, Type, TYPE_CHECKING

from bach import DataFrameOrSeries, SortColumn
from bach.series.series import Series
from bach.series.series_numeric import SeriesAbstractNumeric, SeriesFloat64, SeriesInt64
from bach.series.series_string import SeriesString


import pandas
from sqlalchemy.engine import Engine, Dialect
from bach.expression import Expression, MultiLevelExpression
from bach.series.series import ToPandasInfo
from bach.sql_model import BachSqlModel
from bach.types import AllSupportedLiteralTypes, get_series_type_from_dtype, StructuredDtype
from sql_models.constants import DBDialect, NotSet, not_set
from sql_models.util import DatabaseNotSupportedException, is_postgres, is_bigquery

T = TypeVar('T', bound='SeriesAbstractMultiLevel')

if TYPE_CHECKING:
    from bach.partitioning import GroupBy
    from bach.series import SeriesBoolean
    from bach.dataframe import DataFrame


class SeriesAbstractMultiLevel(Series, ABC):
    """
    A Series that represent the base multi-level types. Works as a data structure containing multiple series
    of different dtypes (based on the structure defined by the child class).

    Each level is treated as an individual series till user calls the following methods:
        * `SeriesAbstractMultiLevel.to_pandas`
        * `SeriesAbstractMultiLevel.to_numpy`
        * `SeriesAbstractMultiLevel.view_sql`

    Each child class must be in charge of:
        * having each level as a property (ensuring immutability)
        * a column expression representing the final structure to be built.

    ** Operations **
        Adapts all supported methods by Series class. Currently, aggregations are not supported.
    """
    def copy_override(
        self: T,
        *,
        engine: Optional[Engine] = None,
        base_node: Optional[BachSqlModel] = None,
        index: Optional[Dict[str, 'Series']] = None,
        name: Optional[str] = None,
        expression: Optional['Expression'] = None,
        group_by: Optional[Union['GroupBy', NotSet]] = not_set,
        instance_dtype: Optional[StructuredDtype] = None,
        order_by: Optional[List[SortColumn]] = None,
        **kwargs,
    ) -> T:
        """
        INTERNAL: Copy this instance into a new one, with the given overrides

        SeriesAbstractMultiLevel only provides current levels if not present in extra arguments
        """
        extra_params = copy(self.levels)
        extra_params.update(kwargs)
        return cast(T, super().copy_override(
            engine=engine,
            base_node=base_node,
            index=index,
            name=name,
            expression=expression,
            group_by=group_by,
            instance_dtype=instance_dtype,
            order_by=order_by,
            **extra_params
        ))

    @classmethod
    def get_class_instance(
        cls,
        engine: Engine,
        base_node: BachSqlModel,
        index: Dict[str, 'Series'],
        name: str,
        expression: Expression,
        group_by: Optional['GroupBy'],
        order_by: Optional[List[SortColumn]],
        instance_dtype: StructuredDtype,
        **kwargs
    ):
        """
        INTERNAL: Create an instance of this class.

        Creates a new instance for each level series.
        """
        base_params = {
            'engine': engine,
            'base_node': base_node,
            'group_by': group_by,
            'index': index,
            'order_by': order_by,
        }

        default_level_dtypes = cls.get_supported_level_dtypes()

        # check if all level are provided in kwargs and each of them is a series instance
        levels_are_provided = all(
            level in kwargs and isinstance(kwargs[level], Series)
            for level in default_level_dtypes.keys()
        )

        if not levels_are_provided:
            # if levels are not provided, search for them in base node
            # this can only happen when instantiating a new DataFrame, if df is containing a multilevel series
            # then levels MUST be in the base node.
            missing_references = [
                f'_{name}_{level_name}' for level_name in default_level_dtypes.keys()
                if f'_{name}_{level_name}' not in base_node.columns
            ]
            if missing_references:
                raise ValueError(
                    f'base node must include all referenced columns {missing_references} '
                    f'for the "{cls.__name__}" instance.'
                )

        sub_levels = {}
        for level_name in default_level_dtypes.keys():
            if levels_are_provided:
                # caller should be responsible for providing correct column references
                level_base = kwargs[level_name]
                dtype = level_base.dtype
                expr = level_base.expression
            else:
                dtype = default_level_dtypes[level_name][0]
                expr = Expression.column_reference(f'_{name}_{level_name}')

            sub_levels[level_name] = get_series_type_from_dtype(dtype).get_class_instance(
                name=f'_{name}_{level_name}',
                expression=expr,
                instance_dtype=dtype,
                **base_params
            )

        return cls(
            engine=engine,
            base_node=base_node,
            index=index,
            name=name,
            expression=expression,
            group_by=group_by,
            order_by=order_by,
            instance_dtype=instance_dtype,
            **sub_levels
        )

    @property
    def levels(self) -> Dict[str, Series]:
        """returns mapping between level name and series"""
        return {
            attr: getattr(self, attr) for attr in self.get_supported_level_dtypes().keys()
        }

    @property
    def expression(self) -> Expression:
        """ INTERNAL: Get the MultiLevelExpression composed by all levels' expression"""
        return MultiLevelExpression([level.expression for level in self.levels.values()])

    @property
    def level_expressions(self) -> List[Expression]:
        """ INTERNAL: Returns a list with each level expression"""
        return [level.expression for level in self.levels.values()]

    @abstractmethod
    def get_column_expression(self, table_alias: str = None) -> Expression:
        """
        INTERNAL: Child class must be in charge of providing the correct expression that represents the type.
        """
        raise NotImplementedError()

    @classmethod
    def get_supported_level_dtypes(cls) -> Dict[str, Tuple[str, ...]]:
        """returns mapping of supported dtypes per level"""
        raise NotImplementedError()

    @classmethod
    def from_value(
        cls: Type[T],
        base: DataFrameOrSeries,
        value: Any,
        name: str,
        dtype: Optional[StructuredDtype] = None
    ) -> T:
        """
        Create an instance of this class, that represents a column with the given value.
        The returned Series will be similar to the Series given as base. In case a DataFrame is given,
        it can be used immediately with that frame.
        :param base:    The DataFrame or Series that the internal parameters are taken from
        :param value:   None or a mapping between each level and constant. All levels must be present.
        :param name:    The name that it will be known by (only for representation)
        """
        if dtype is None:
            dtype = cls.dtype
        if (
            value is not None
            and (
                not isinstance(value, dict)
                or not all(level in value for level in cls.get_supported_level_dtypes().keys())
            )
        ):
            raise ValueError(f'value should contain mapping for each {cls.__name__} level')

        from bach.series.series import value_to_series

        if value is not None:
            levels = {
                level_name: value_to_series(base=base, value=level_value)
                for level_name, level_value in value.items()
            }
        else:
            levels = {
                level_name: value_to_series(base=base, value=None).astype(dtypes[0])
                for level_name, dtypes in cls.get_supported_level_dtypes().items()
            }
        result = cls.get_class_instance(
            engine=base.engine,
            base_node=base.base_node,
            index=base.index,
            name=name,
            expression=Expression.construct(''),
            group_by=None,
            order_by=[],
            instance_dtype=dtype,
            **levels
        )

        return result

    @classmethod
    def dtype_to_expression(cls, dialect: Dialect, source_dtype: str, expression: Expression) -> Expression:
        raise NotImplementedError()

    @classmethod
    def supported_literal_to_expression(cls, dialect: Dialect, literal: Expression) -> Expression:
        raise NotImplementedError()

    @classmethod
    def supported_value_to_literal(cls, dialect: Dialect, value: Any, dtype: StructuredDtype) -> Expression:
        raise NotImplementedError()

    def astype(self, dtype: Union[str, Type]) -> 'Series':
        raise NotImplementedError(f'{self.__class__.__name__} cannot be casted to other types.')

    def equals(self, other: Any, recursion: str = None) -> bool:
        """
        Checks if all levels between both multi-level series are the same.

        For more information look at :py:meth:`bach.Series.equals()`
        """
        if not isinstance(other, self.__class__):
            return False

        same_levels = all(
            self.levels[level_name].equals(other.levels[level_name], recursion)
            for level_name in self.levels.keys()
        )
        return same_levels and super().equals(other, recursion)

    def isnull(self) -> 'SeriesBoolean':
        """
        Checks if all levels are null.

        For more information look at :py:meth:`bach.Series.isnull()`
        """
        all_series = [lvl.isnull() for lvl in self.levels.values()]
        return reduce(operator.and_, all_series)

    def notnull(self) -> 'SeriesBoolean':
        """
        Checks if all levels are not null.

        For more information look at :py:meth:`bach.Series.notnull()`
        """
        all_series = [lvl.notnull() for lvl in self.levels.values()]
        return reduce(operator.and_, all_series)

    def fillna(self, other: AllSupportedLiteralTypes):
        """
        Fill any NULL value of any or all levels.
        For more information look at :py:meth:`bach.Series.fillna()`

        ..note:
            "other" should be a dict object containing at least one level to be filled.
        """
        if (
            not isinstance(other, dict)
            or not all(level in self.levels for level in other.keys())
        ):
            raise ValueError(
                f'"other" should contain mapping for at least one of {self.__class__.__name__} levels'
            )

        self_cp = self.copy()
        for level_name, value in other.items():
            setattr(self_cp, f'_{level_name}', self.levels[level_name].fillna(value))

        return self_cp

    def append(
        self,
        other: Union['Series', List['Series']],
        ignore_index: bool = False,
    ) -> 'Series':
        """
        Append rows of other multi-level series to the caller series.
        For more information look at :py:meth:`bach.Series.append()`

        ..note:
            All elements to be appended must be the same multi-level dtype as the caller.
        """
        if not other:
            return self

        levels_df_to_append = []
        for series in other if isinstance(other, list) else [other]:
            if not isinstance(series, self.__class__):
                raise ValueError(f'can only append "{self.dtype}" series to {self.name}')

            level_df = series.copy_override(name=self.name).flatten()
            levels_df_to_append.append(level_df)

        appended_df = self.flatten().append(levels_df_to_append)
        return self.from_value(
            base=appended_df,
            value={
                level_name: appended_df[f'_{self.name}_{level_name}'] for level_name in self.levels.keys()
            },
            name=self.name,
            dtype=self.dtype
        )

    def flatten(self) -> 'DataFrame':
        """
        Converts the multi-level series into a DataFrame,
        where each level is a series of the resultant DataFrame.
        """
        from bach.dataframe import DataFrame
        from bach.savepoints import Savepoints
        return DataFrame(
            engine=self.engine,
            base_node=self.base_node,
            index=self.index,
            series={level.name: level for level in self.levels.values()},
            group_by=self.group_by,
            order_by=[],
            savepoints=Savepoints(),
            variables={},
        )

    def _parse_level_value(self, level_name: str, value: Union[AllSupportedLiteralTypes, Series]) -> 'Series':
        """
        INTERNAL: validates that the level value is supported by the caller.
        """
        supported_dtypes = self.get_supported_level_dtypes()
        if level_name not in supported_dtypes:
            raise ValueError(f'{level_name} is not a supported level in {self.__class__.__name__}.')

        from bach.series.series import value_to_series
        level = value_to_series(base=self, value=value)

        if not any(
            isinstance(level, get_series_type_from_dtype(dtype)) for dtype in supported_dtypes[level_name]
        ):
            raise ValueError(f'"{level_name}" level should be any of {supported_dtypes[level_name]} dtypes.')

        # level should have same attributes as parent
        return level.copy_override(
            name=f'_{self.name}_{level_name}',
            engine=self.engine,
            base_node=self.base_node,
            index=self.index,
            group_by=self.group_by,
            order_by=self.order_by,
        )


class SeriesNumericInterval(SeriesAbstractMultiLevel):
    """
    Multi-Level Series representing a structure for numeric intervals. This is due that not all supported
    databases have a type that emulates a similar behavior as pandas.Interval dtype.

    For each supported database, structure is composed by 3 levels:
        * `lower`: a numerical value representing the lowest edge of the interval
        * `upper`: a numerical value representing the upper edge of the interval
        * `bounds`: a string value representing the boundary type of the interval:
            Supported values are: '[]', '[)' and '()', if value is not supported,
            then '()' will be used as default when parsing results into `pandas.DataFrame`

    DB representation per engine:
        * postgres: NUMRANGE type will be built as a result.
            For more information: https://www.postgresql.org/docs/current/rangetypes.html
        * bigquery: BigQuery has no direct type that handles ranges, therefore a STRUCT type column is used as
            a final representation.
    """
    dtype = 'numeric_interval'
    dtype_aliases = (pandas.Interval, 'numrange')
    supported_db_dtype = {
        DBDialect.POSTGRES: 'numrange',
        DBDialect.BIGQUERY: 'STRUCT<lower FLOAT64, upper FLOAT64, bounds STRING(2)>'
    }

    supported_value_types = (pandas.Interval, dict)

    def __init__(
        self,
        *,
        lower: Union['SeriesAbstractNumeric', float, int],
        upper: Union['SeriesAbstractNumeric', float, int],
        bounds: Union['SeriesString', str],
        **kwargs,
    ) -> None:
        # multi-level series should have an empty expression
        kwargs['expression'] = Expression.construct('')
        super().__init__(**kwargs)

        self._lower = cast(SeriesAbstractNumeric, self._parse_level_value(level_name='lower', value=lower))
        self._upper = cast(SeriesAbstractNumeric, self._parse_level_value(level_name='upper', value=upper))
        self._bounds = cast(SeriesString, self._parse_level_value(level_name='bounds', value=bounds))

    @property
    def lower(self) -> 'SeriesAbstractNumeric':
        return self._lower

    @property
    def upper(self) -> 'SeriesAbstractNumeric':
        return self._upper

    @property
    def bounds(self) -> 'SeriesString':
        return self._bounds

    @classmethod
    def get_supported_level_dtypes(cls) -> Dict[str, Tuple[str, ...]]:
        return {
            'lower': (SeriesFloat64.dtype, SeriesInt64.dtype),
            'upper': (SeriesFloat64.dtype, SeriesInt64.dtype),
            'bounds': (SeriesString.dtype, ),
        }

    def to_pandas_info(self) -> Optional[ToPandasInfo]:
        if is_postgres(self.engine):
            return ToPandasInfo(dtype='object', function=self._parse_numeric_interval_value_postgres)
        if is_bigquery(self.engine):
            return ToPandasInfo(dtype='object', function=self._parse_numeric_interval_value_bigquery)
        return None

    def get_column_expression(self, table_alias: str = None) -> Expression:
        # construct final column based on levels
        if is_postgres(self.engine):
            # casting is needed since numrange does not support float64
            base_expr_stmt = f'numrange(cast({{}} as numeric), cast({{}} as numeric), {{}})'

        elif is_bigquery(self.engine):
            # BigQuery has no proper datatype for numeric intervals,
            # therefore we should represent it as a struct
            base_expr_stmt = f'struct({{}} as lower, {{}} as upper, {{}} as bounds)'
        else:
            raise DatabaseNotSupportedException(self.engine)

        # should return null when all levels are null
        expr = Expression.construct(
            f'CASE WHEN {{}} THEN {base_expr_stmt} ELSE NULL END',
            self.notnull(),
            self.lower,
            self.upper,
            self.bounds,
        )
        return Expression.construct_expr_as_name(expr, self.name)

    @staticmethod
    def _parse_numeric_interval_value_postgres(value) -> Optional[pandas.Interval]:
        """
        Helper function that converts Postgres NUMRANGE values into a pandas.Interval object.
        """
        if value is None:
            return value

        if value.lower_inc and value.upper_inc:
            closed = 'both'
        elif value.lower_inc:
            closed = 'left'
        else:
            closed = 'right'
        return pandas.Interval(float(value.lower), float(value.upper), closed=closed)

    @staticmethod
    def _parse_numeric_interval_value_bigquery(value) -> Optional[pandas.Interval]:
        """
        Helper function that converts BigQuery STRUCT values into a pandas.Interval object.
        """
        if value is None:
            return value

        # expects a dict with interval information
        expected_keys = ['lower', 'upper', 'bounds']
        if not isinstance(value, dict) or not all(k in value for k in expected_keys):
            raise ValueError(f'{value} has not the expected structure.')

        if value['bounds'] == '[]':
            closed = 'both'
        elif value['bounds'] == '[)':
            closed = 'left'
        else:
            closed = 'right'
        return pandas.Interval(float(value['lower']), float(value['upper']), closed=closed)
