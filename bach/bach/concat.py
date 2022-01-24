from abc import ABC
from dataclasses import dataclass
from typing import Tuple, Dict, Hashable, List, overload, Sequence, Set

from bach.dataframe import DtypeNamePair, DataFrameOrSeries
from bach import DataFrame, const_to_series, Series
from bach.expression import Expression, join_expressions
from bach.sql_model import BachSqlModel, construct_references, get_variable_values_sql, filter_variables
from bach.utils import ResultSeries, get_result_series_dtype_mapping
from sql_models.model import CustomSqlModelBuilder, Materialization


@dataclass
class ConcatOperation(ABC):
    objects: Sequence[DataFrameOrSeries]
    ignore_index: bool = False
    sort: bool = False

    def __call__(self, *args, **kwargs) -> DataFrameOrSeries:
        if not len(self.objects):
            raise ValueError('no objects to concatenate.')

        if len(self.objects) == 1:
            return self.objects[0].copy_override()
        return self._get_concatenated_object()

    def _get_concatenated_object(self) -> DataFrameOrSeries:
        raise NotImplementedError()

    def _get_model(
        self,
        objects: List[DataFrameOrSeries],
        variables: Dict['DtypeNamePair', Hashable],
    ) -> 'ConcatSqlModel':
        raise NotImplementedError()


class DataFrameConcatOperation(ConcatOperation):
    def _get_overridden_objects(self) -> List[DataFrame]:
        dfs: List[DataFrame] = []
        for obj in self.objects:
            if isinstance(obj, Series):
                raise Exception('Cannot concat Series to DataFrame')

            df = obj.copy_override()
            if self.ignore_index:
                df.reset_index(drop=True, inplace=True)

            dfs.append(self._fill_missing_series(df=df).materialize())

        return dfs

    def _fill_missing_series(self, df: DataFrame) -> DataFrame:
        df_cp = df.copy_override()
        new_indexes = self._get_indexes()
        new_data_series = self._get_series()

        def _fill_series(
            df_cp: DataFrame, result_series: Dict[str, ResultSeries],
        ) -> DataFrame:
            for idx, rc in result_series.items():
                if idx not in df_cp.all_series:
                    df_cp[idx] = const_to_series(base=df_cp, value=None, name=idx)
                    df_cp[idx] = df_cp[rc.name].astype(rc.dtype)
                elif df_cp.all_series[idx].dtype != rc.dtype:
                    df_cp.all_series[rc.name] = df_cp.all_series[rc.name].astype(rc.dtype)

            return df_cp

        df_cp = _fill_series(df_cp, new_indexes)
        df_cp = _fill_series(df_cp, new_data_series)
        return df_cp

    def _join_series_expressions(self, df: DataFrameOrSeries) -> Expression:
        if isinstance(df, Series):
            return df.expression

        new_indexes = self._get_indexes()
        new_data_series = self._get_series()

        def _add_expressions(
            result_series: Dict[str, ResultSeries], existing_series: List[str],
        ) -> List[Expression]:
            expressions = []
            for idx, rc in result_series.items():
                if idx not in existing_series:
                    expressions.append(Expression.construct('NULL as {}', Expression.identifier(rc.name)))
                else:
                    expressions.append(Expression.construct_expr_as_name(expr=rc.expression, name=rc.name))

            return expressions

        index_expressions = _add_expressions(new_indexes, df.index_columns)
        data_series_expressions = _add_expressions(new_data_series, df.data_columns)
        return join_expressions(index_expressions + data_series_expressions)

    def _get_indexes(self) -> Dict[str, ResultSeries]:
        if self.ignore_index:
            return {}

        new_indexes: Dict[str, ResultSeries] = {}
        for df in self.objects:
            if isinstance(df, Series):
                continue

            if not new_indexes:
                new_indexes = {
                    idx: ResultSeries(name=idx, expression=series.expression, dtype=series.dtype)
                    for idx, series in df.index.items()
                }
                continue

            if set(new_indexes.keys()) != set(df.index_columns):
                raise ValueError('concatenation with different index levels is not supported yet.')

        return new_indexes

    def _get_series(self) -> Dict[str, ResultSeries]:
        final_series = {
            series_name: ResultSeries(
                name=series_name,
                expression=df[series_name].expression,
                dtype=df[series_name].dtype,
            )
            for df in self.objects if isinstance(df, DataFrame)
            for series_name in df.data_columns
        }
        if self.sort:
            return {s: final_series[s] for s in sorted(final_series)}

        return final_series

    def _get_concatenated_object(self) -> DataFrameOrSeries:
        objects = self._get_overridden_objects()
        new_indexes = self._get_indexes()
        new_data_series = self._get_series()

        main_df: DataFrame = objects[0]
        variables = {}
        savepoints = main_df.savepoints
        for df in objects:
            variables.update(df.variables)
            savepoints.merge(df.savepoints)

        return main_df.copy_override(
            engine=main_df.engine,
            base_node=self._get_model(objects, variables),
            index_dtypes=get_result_series_dtype_mapping(list(new_indexes.values())),
            series_dtypes=get_result_series_dtype_mapping(list(new_data_series.values())),
            savepoints=savepoints,
            variables=variables,
        )

    def _get_model(
        self,
        objects: Sequence[DataFrameOrSeries],
        variables: Dict['DtypeNamePair', Hashable],
    ) -> 'ConcatSqlModel':
        new_indexes = self._get_indexes()
        new_data_series = self._get_series()

        new_index_names = [rs.name for rs in new_indexes.values()]
        new_data_series_names = [rs.name for rs in new_data_series.values()]

        series_expressions = [self._join_series_expressions(df=df) for df in objects]

        return ConcatSqlModel(
            series_names=tuple(new_index_names + new_data_series_names),
            all_series_expressions=series_expressions,
            all_nodes=[df.base_node for df in objects],
            variables=variables,  # type: ignore
        )


class SeriesConcatOperation(ConcatOperation):
    def _get_overridden_objects(self) -> List[Series]:
        series = []
        for obj in self.objects:
            if isinstance(obj, DataFrame):
                raise Exception('Cannot concat DataFrame to Series')
            series.append(obj)
        return series

    def _get_concatenated_object(self) -> DataFrameOrSeries:
        objects = self._get_overridden_objects()
        main_series: Series = objects[0]
        all_names = []
        dtypes: Set[str] = set()
        for series in objects:
            all_names.append(series.name)
            dtypes.update(series.dtype)

        final_dtype = 'string' if len(dtypes) > 1 else dtypes.pop()
        final_name = '_'.join(all_names)

        return main_series.copy_override(
            engine=main_series.engine,
            base_node=self._get_model(objects, variables={}),
            name=final_name,
            dtype=final_dtype,
        )

    def _get_model(
        self,
        objects: Sequence[DataFrameOrSeries],
        variables: Dict['DtypeNamePair', Hashable],
    ) -> 'ConcatSqlModel':
        series_expressions = [obj.expression for obj in objects]

        return ConcatSqlModel(
            series_names=tuple('concatenated_series'),
            all_series_expressions=series_expressions,
            all_nodes=[series.base_node for series in objects],
            variables=variables,  # type: ignore
        )


class ConcatSqlModel(BachSqlModel):
    def __init__(
        self,
        *,
        series_names: Tuple[str, ...],
        all_series_expressions: List[Expression],
        all_nodes: List[BachSqlModel],
        variables: Dict['DtypeNamePair', Hashable],
    ) -> None:
        name = 'concat_sql'
        base_sql = 'select {serie_expr} from {node}'
        sql = ' union all '.join(
            base_sql.format(serie_expr=col_expr.to_sql(), node=f"{{{{node_{idx}}}}}")
            for idx, (col_expr, node) in enumerate(zip(all_series_expressions, all_nodes))
        )

        references = construct_references(
            base_references={f'node_{idx}': node for idx, node in enumerate(all_nodes)},
            expressions=all_series_expressions
        )

        super().__init__(
            model_spec=CustomSqlModelBuilder(sql=sql, name=name),
            properties=self._get_properties(variables, all_series_expressions),
            references=references,
            materialization=Materialization.CTE,
            materialization_name=None,
            columns=series_names
        )

    @classmethod
    def _get_properties(
        cls,
        variables: Dict['DtypeNamePair', Hashable],
        expressions: List[Expression],
    ) -> Dict[str, str]:
        filtered_variables = filter_variables(variables, expressions)
        return get_variable_values_sql(filtered_variables)
