"""
Copyright 2022 Objectiv B.V.
"""
from abc import abstractmethod

from sqlalchemy.engine import Dialect

from bach.dataframe import DataFrameOrSeries
import itertools
from collections import defaultdict
from typing import Tuple, Dict, Hashable, List, Set, Sequence, TypeVar, Generic

from bach.dataframe import DtypeNamePair
from bach import DataFrame, get_series_type_from_dtype, SeriesAbstractNumeric, Series
from bach.expression import Expression, join_expressions
from bach.sql_model import BachSqlModel, construct_references
from bach.utils import ResultSeries, get_result_series_dtype_mapping, get_merged_series_dtype
from sql_models.model import CustomSqlModelBuilder, Materialization

TDataFrameOrSeries = TypeVar('TDataFrameOrSeries', bound='DataFrameOrSeries')

DEFAULT_CONCAT_SERIES_DTYPE = 'string'


class ConcatOperation(Generic[TDataFrameOrSeries]):
    """
    Abstract class that specifies the list of objects to be concatenated.

    Child classes are in charge of specifying the correct type (DataFrame/Series) of all objects.
    All classes should implement:
     - _get_concatenated_object method: returns a single object with the correct instantiated type.
     - _join_series_expressions method: returns expression per object to be concatenated
     - _get_series method: returns the data series of the final concatenated object
    """
    objects: Sequence[TDataFrameOrSeries]
    ignore_index: bool

    def __init__(self, objects: Sequence[TDataFrameOrSeries], ignore_index: bool = False):
        self.objects = objects
        self.ignore_index = ignore_index

    def __call__(self, *args, **kwargs) -> TDataFrameOrSeries:
        """
        If only one object is provided for concatenation, it should just return a copy.
        Otherwise, child class _get_concatenated_object method is called.
        """
        if not len(self.objects):
            raise ValueError('no objects to concatenate.')

        if len(self.objects) == 1:
            index = {} if self.ignore_index else self.objects[0].index
            return self.objects[0].copy_override(index=index)  # type: ignore

        return self._get_concatenated_object()

    @property
    def dialect(self) -> Dialect:
        return self.objects[0].engine.dialect

    def _get_indexes(self) -> Dict[str, ResultSeries]:
        """
        gets the indexes of the final concatenated dataframe or series.
        All objects must have the same indexes, otherwise concatenation is not performed.
        """
        from bach.series import SeriesAbstractMultiLevel
        if self.ignore_index:
            return {}

        all_indexes = list(itertools.chain.from_iterable(obj.index.values() for obj in self.objects))
        merged_indexes = self._get_result_series(all_indexes)

        # all objects should have the same indexes
        for obj in self.objects:
            curr_obj_index = list(itertools.chain.from_iterable(
                [idx] if not isinstance(idx, SeriesAbstractMultiLevel) else list(idx.levels.values())
                for idx in obj.index.values()
            ))
            if set(merged_indexes.keys()) != {idx.name for idx in curr_obj_index}:
                raise ValueError('concatenation with different index levels is not supported yet.')

            if any(mi.dtype != oi.dtype for mi, oi in zip(merged_indexes.values(), curr_obj_index)):
                raise ValueError('concatenation with different index dtypes is not supported yet.')

        return merged_indexes

    def _get_result_series(self, series: List[Series]) -> Dict[str, ResultSeries]:
        """
        merges all shared series and defines final dtype
        """
        from bach.series import SeriesAbstractMultiLevel
        series_dtypes = defaultdict(set)
        for s in series:
            if not isinstance(s, SeriesAbstractMultiLevel):
                series_dtypes[s.name].add(s.dtype)
                continue

            for lvl in s.levels.values():
                series_dtypes[lvl.name].add(lvl.dtype)

        series_names = series_dtypes.keys()

        return {
            series_name: ResultSeries(
                name=series_name,
                expression=Expression.identifier(series_name),
                dtype=get_merged_series_dtype(series_dtypes[series_name]),
            )
            for series_name in series_names
        }

    def _get_model(
        self,
        objects: Sequence[TDataFrameOrSeries],
        variables: Dict['DtypeNamePair', Hashable],
    ) -> 'ConcatSqlModel':
        """
        returns a ConcatSqlModel which unifies all queries from all dataframes.
        """
        new_indexes = self._get_indexes()
        new_data_series = self._get_series()

        new_index_names = [rs.name for rs in new_indexes.values()]
        new_data_series_names = [rs.name for rs in new_data_series.values()]

        series_expressions = [self._join_series_expressions(df) for df in objects]

        return ConcatSqlModel.get_instance(
            dialect=self.dialect,
            columns=tuple(new_index_names + new_data_series_names),
            all_series_expressions=series_expressions,
            all_nodes=[df.base_node for df in objects],
            variables=variables,
        )

    @abstractmethod
    def _get_concatenated_object(self) -> TDataFrameOrSeries:
        """
        returns a single object based on the instantiated type from the child class
        """
        raise NotImplementedError()

    @abstractmethod
    def _join_series_expressions(self, obj: TDataFrameOrSeries) -> Expression:
        """
        return the column expression for the object subquery. For more information see implementation.
        """
        raise NotImplementedError()

    @abstractmethod
    def _get_series(self) -> Dict[str, ResultSeries]:
        """
        gets the data series of the final concatenated object
        """
        raise NotImplementedError()


class DataFrameConcatOperation(ConcatOperation[DataFrame]):
    """
    In order to instantiate this class you should provide the following params:
    objects: a list of DataFrames to be concatenated (all DataFrames should have the same indexes)
    ignore_index: a boolean specifying if the resultant DataFrame must preserve the original indexes or not.
    sort: a boolean specifying the order of the data_columns in the result. If False, the order of series
    will be based on each object's position and data_columns value.

    returns a new DataFrame

    Example:
        DataFrameConcatOperation(objects=[df1, df2], ignore_index=True, sort=True)()
    """
    sort: bool

    def __init__(self, objects: Sequence[DataFrame], ignore_index: bool = False, sort: bool = False):
        self.sort = sort
        super().__init__(objects=objects, ignore_index=ignore_index)

    def _get_overridden_objects(self) -> List[DataFrame]:
        """
        generates a copy for each dataframe and prepares them for concatenation
        """
        dfs: List[DataFrame] = []
        for obj in self.objects:
            if isinstance(obj, Series):
                raise Exception('Cannot concat Series to DataFrame')

            df = obj.copy() if not self.ignore_index else obj.reset_index(drop=True)
            # need to materialize in order to avoid further problems
            if df.group_by:
                df = df.materialize()

            dfs.append(df)

        return dfs

    def _join_series_expressions(self, obj: DataFrame) -> Expression:
        """
        generates the column expression for the object subquery
        - if a column doesn't exist in the object's base_node, all values will be null
        - if the column exists but has a different dtype from the result, it will be casted
        """
        new_indexes = self._get_indexes()
        new_data_series = self._get_series()

        expressions = []

        all_result_series: Dict[str, ResultSeries] = {**new_indexes, **new_data_series}
        for idx, rc in all_result_series.items():
            if idx not in obj.all_series:
                expressions.append(Expression.construct('NULL as {}', Expression.identifier(rc.name)))
                continue

            has_diff_dtype = rc.dtype != obj.all_series[idx].dtype
            curr_series = obj.all_series[idx] if not has_diff_dtype else obj.all_series[idx].astype(rc.dtype)
            expressions.append(
                Expression.construct_expr_as_name(expr=curr_series.expression, name=rc.name)
            )

        return join_expressions(expressions)

    def _get_series(self) -> Dict[str, ResultSeries]:
        """
        gets the data series of the final concatenated dataframe
        """
        all_series = list(
            itertools.chain.from_iterable(df.data.values() for df in self.objects)
        )
        result_series = self._get_result_series(all_series)
        if not self.sort:
            return result_series

        return {s: result_series[s] for s in sorted(result_series)}

    def _get_concatenated_object(self) -> DataFrame:
        """
        prepares all dataframes for concatenation (all of them have the same columns)
        gets the resultant indexes and series for the final dataframe.

        returns a new dataframe with all the rows from the provided objects
        """
        objects = self._get_overridden_objects()
        new_indexes = self._get_indexes()
        new_data_series = self._get_series()

        main_df: DataFrame = objects[0]
        variables = {}
        savepoints = main_df.savepoints

        # variables are overridden based on the order of concatenation. This means that the initial dataframe
        # will have higher priority over the following dataframes
        for df in reversed(objects):
            variables.update(df.variables)
            savepoints.merge(df.savepoints)

        return main_df.copy_override(
            base_node=self._get_model(objects, variables),
            index_dtypes=get_result_series_dtype_mapping(list(new_indexes.values())),
            series_dtypes=get_result_series_dtype_mapping(list(new_data_series.values())),
            savepoints=savepoints,
            variables=variables,
        )


class SeriesConcatOperation(ConcatOperation[Series]):
    """
    In order to instantiate this class you should provide the following params:
    objects: a list of Series to be concatenated (all Series should have the same indexes)
    ignore_index: a boolean specifying if the resultant Series must preserve the original indexes or not.

    returns a new Series

    Example:
        SeriesConcatOperation(objects=[s1, s2], ignore_index=True)()
    """
    def _get_overridden_objects(self) -> List[Series]:
        """
        creates new copies for each series to be concatenated
        """
        series: List[Series] = []
        for obj in self.objects:
            if isinstance(obj, DataFrame):
                raise Exception('Cannot concat DataFrame to Series')

            df = obj.to_frame()
            if df.group_by:
                df = df.materialize()
            series.append(df.all_series[obj.name])

        return series

    def _get_series(self) -> Dict[str, ResultSeries]:
        """
        gets the final data series result
        """
        dtypes: Set[str] = set(series.dtype for series in self.objects)

        main_series = self.objects[0].copy_override_dtype(dtype=get_merged_series_dtype(dtypes))
        return self._get_result_series([main_series])

    def _join_series_expressions(self, obj: Series) -> Expression:
        """
        generates the column expression for the object subquery
        """
        result_series = list(self._get_series().values())[0]

        series_expression = Expression.construct_expr_as_name(
            expr=obj.astype(result_series.dtype).expression,
            name=result_series.name,
        )

        if self.ignore_index:
            return series_expression

        index_expressions = [idx.expression for idx in self._get_indexes().values()]
        return join_expressions(index_expressions + [series_expression])

    def _get_concatenated_object(self) -> Series:
        """
        returns a series that contains all rows from all provided objects.
        """
        objects = self._get_overridden_objects()
        main_series: Series = objects[0]
        final_result_series: ResultSeries = list(self._get_series().values())[0]

        series_cls = get_series_type_from_dtype(final_result_series.dtype)
        node = self._get_model(objects, variables={})
        index = {
            idx_name: idx.copy_override(base_node=node)
            for idx_name, idx in main_series.index.items()
        }
        return series_cls(
            engine=main_series.engine,
            base_node=node,
            name=final_result_series.name,
            expression=Expression.column_reference(final_result_series.name),
            index={} if self.ignore_index else index,
            group_by=None,
            order_by=[],
            instance_dtype=series_cls.dtype  # TODO: make this work for structural types too
        )


class ConcatSqlModel(BachSqlModel):
    @classmethod
    def get_instance(
        cls,
        *,
        dialect: Dialect,
        columns: Tuple[str, ...],
        all_series_expressions: List[Expression],
        all_nodes: List[BachSqlModel],
        variables: Dict['DtypeNamePair', Hashable],
    ) -> 'ConcatSqlModel':
        name = 'concat_sql'
        base_sql = 'select {serie_expr} from {node}'
        sql = ' union all '.join(
            base_sql.format(serie_expr=col_expr.to_sql(dialect), node=f"{{{{node_{idx}}}}}")
            for idx, col_expr in enumerate(all_series_expressions)
        )

        references = construct_references(
            base_references={f'node_{idx}': node for idx, node in enumerate(all_nodes)},
            expressions=all_series_expressions
        )

        return ConcatSqlModel(
            model_spec=CustomSqlModelBuilder(sql=sql, name=name),
            placeholders=cls._get_placeholders(dialect, variables, all_series_expressions),
            references=references,
            materialization=Materialization.CTE,
            materialization_name=None,
            column_expressions={c: Expression.column_reference(c) for c in columns},
        )
