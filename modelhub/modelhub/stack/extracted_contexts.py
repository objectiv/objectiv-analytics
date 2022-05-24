"""
Copyright 2021 Objectiv B.V.
"""
import operator
from functools import reduce

import bach
from typing import  Optional

from sql_models.model import CustomSqlModelBuilder
from sql_models.util import quote_identifier, is_bigquery
from sqlalchemy.engine import Engine

from modelhub.stack.util import (
    ObjectivSupportedColumns, get_supported_dtypes_per_objectiv_column, check_objectiv_dataframe
)
from modelhub.stack.base_pipeline import BaseDataPipeline


class ExtractedContextsPipeline(BaseDataPipeline):
    TAXONOMY_COLUMN = 'value'

    # Expected structure of taxonomy JSON
    TAXONOMY_STRUCTURE_DTYPE = {
        '_type': bach.SeriesString.dtype,
        '_types': bach.SeriesJson.dtype,
        'global_contexts': bach.SeriesJson.dtype,
        'location_stack': bach.SeriesJson.dtype,
    }

    DATE_FILTER_COLUMN = ObjectivSupportedColumns.DAY.value

    # default structure that will be considered for all engines, define otherwise in child class
    required_columns_x_dtypes = {
        'event_id': bach.SeriesUuid.dtype,
        'day': bach.SeriesDate.dtype,
        'moment': bach.SeriesTimestamp.dtype,
        'cookie_id': bach.SeriesUuid.dtype,
        TAXONOMY_COLUMN: bach.SeriesJson.dtype,
    }

    # mapping for column and supported columns by objectiv
    context_column_aliases = {
        'cookie_id': ObjectivSupportedColumns.USER_ID,
        '_type': ObjectivSupportedColumns.EVENT_TYPE,
        '_types': ObjectivSupportedColumns.STACK_EVENT_TYPES,
    }

    def __init__(self, engine: Engine, table_name: str):
        super().__init__(engine, table_name)

        # check if table has all required columns for pipeline
        dtypes = bach.from_database.get_dtypes_from_table(
            engine=self._engine,
            table_name=self._table_name,
        )
        self._validate_data_columns(current_columns=list(dtypes.keys()))

    def _get_pipeline_result(self, **kwargs) -> bach.DataFrame:
        context_df = bach.DataFrame.from_table(
            table_name=self._table_name,
            engine=self._engine,
            index=[],
            all_dtypes=self.required_columns_x_dtypes,
        )
        context_df = self._apply_date_filter(context_df=context_df, **kwargs)
        context_df = self._process_base_data(context_df)
        context_df = self._apply_aliases(context_df)
        context_df = self._convert_dtypes(context_df)

        final_columns = list(ObjectivSupportedColumns.get_extracted_context_columns())
        context_df = context_df[final_columns]

        return context_df.materialize(node_name='context_data')

    def _process_base_data(self, df: bach.DataFrame) -> bach.DataFrame:
        df_cp = df.copy()

        # extract columns from taxonomy json
        taxonomy_series = df[self.TAXONOMY_COLUMN].copy_override_type(bach.SeriesJson)
        for key, dtype in self.TAXONOMY_STRUCTURE_DTYPE.items():
            taxonomy_col = taxonomy_series.json.get_value(key, as_str=True)
            taxonomy_col = taxonomy_col.copy_override(name=key)
            df_cp[key] = taxonomy_col

        return df_cp

    def _convert_dtypes(self, df: bach.DataFrame) -> bach.DataFrame:
        df_cp = df.copy()
        objectiv_dtypes = get_supported_dtypes_per_objectiv_column()
        for col in ObjectivSupportedColumns.get_extracted_context_columns():
            if col not in df_cp.data:
                continue

            df_cp[col] = df_cp[col].astype(objectiv_dtypes[col])

        return df_cp

    @classmethod
    def validate_pipeline_result(cls, result: bach.DataFrame) -> None:
        check_objectiv_dataframe(
            result,
            columns_to_check=list(ObjectivSupportedColumns.get_extracted_context_columns()),
            check_dtypes=True,
        )

    def _apply_date_filter(
        self,
        context_df: bach.DataFrame,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs,
    ) -> bach.DataFrame:
        context_df_cp = context_df.copy()

        if not start_date and not end_date:
            return context_df_cp

        date_filters = []
        if start_date:
            date_filters.append(context_df_cp[self.DATE_FILTER_COLUMN] >= start_date)
        if end_date:
            date_filters.append(context_df_cp[self.DATE_FILTER_COLUMN] <= end_date)

        return context_df_cp[reduce(operator.and_, date_filters)]

    def _apply_aliases(self, context_df: bach.DataFrame) -> bach.DataFrame:
        columns_to_rename = {
            col_name: alias.value
            for col_name, alias in self.context_column_aliases.items()
            if col_name in context_df.data
        }
        if not columns_to_rename:
            return context_df

        return context_df.rename(columns=columns_to_rename)


class BigQueryExtractedContextsPipeline(ExtractedContextsPipeline):
    # change when version is updated
    TAXONOMY_COLUMN = 'contexts_io_objectiv_taxonomy_1_0_0'
    # Expected structure of taxonomy JSON
    TAXONOMY_STRUCTURE_DTYPE = {
        **ExtractedContextsPipeline.TAXONOMY_STRUCTURE_DTYPE,
        'cookie_id': bach.SeriesUuid.dtype,
        'event_id': bach.SeriesUuid.dtype,
        'time': bach.SeriesTimestamp.dtype,
    }

    DATE_FILTER_COLUMN = 'load_tstamp'

    # constant used for referring to unnested taxonomy column
    UNNESTED_TAXONOMY_COLUMN = 'taxonomy'

    required_columns_x_dtypes = {
        DATE_FILTER_COLUMN: bach.SeriesDate.dtype,
        TAXONOMY_COLUMN: [TAXONOMY_STRUCTURE_DTYPE],  # expect list of taxonomy per registry
    }

    # mapping for column and supported columns by objectiv
    context_column_aliases = {
        **ExtractedContextsPipeline.context_column_aliases,
        DATE_FILTER_COLUMN: ObjectivSupportedColumns.DAY,
        'time': ObjectivSupportedColumns.MOMENT,
    }

    def _process_base_data(self, context_df: bach.DataFrame) -> bach.DataFrame:
        dialect = self._engine.dialect

        # TODO: Replace this when bach supports UNNEST for SeriesList
        context_dtypes = self.required_columns_x_dtypes
        taxonomy_columns_dtypes = context_dtypes[self.TAXONOMY_COLUMN][0]
        other_columns_dtypes = {
            col: dtype for col, dtype in context_dtypes.items() if col != self.TAXONOMY_COLUMN
        }

        all_dtypes = {**taxonomy_columns_dtypes, **other_columns_dtypes}

        column_exprs = []
        for col in all_dtypes.keys():
            if col not in taxonomy_columns_dtypes:
                expr = bach.expression.Expression.column_reference(col)
            else:
                # reference to the unnested column and add alias
                table_ref = bach.expression.Expression.table_column_reference(
                    table_name=self.UNNESTED_TAXONOMY_COLUMN, field_name=col,
                )
                expr = bach.expression.Expression.construct_expr_as_name(expr=table_ref, name=col)

            column_exprs.append(expr)

        column_stmt = bach.expression.join_expressions(column_exprs).to_sql(dialect)

        sql = (
            f'SELECT {column_stmt} '
            f'from {{{{context_node}}}} '
            f'cross join unnest({quote_identifier(dialect, self.TAXONOMY_COLUMN)}) '
            f'as {quote_identifier(dialect, self.UNNESTED_TAXONOMY_COLUMN)}'

        )

        model_builder = CustomSqlModelBuilder(sql=sql, name='unnested_taxonomy')
        df = bach.DataFrame.from_model(
            engine=self._engine,
            model=model_builder(context_node=context_df.base_node),
            index=[],
            all_dtypes={
                **taxonomy_columns_dtypes,
                **other_columns_dtypes,
            },
        )

        # time column contains integer values, we need to convert it into a timestamp
        df['time'] = df['time'].copy_override(
            expression=bach.expression.Expression.construct(f'TIMESTAMP_MILLIS({{}})', df['time']),
        )
        return df


def get_extracted_contexts_df(
    engine: Engine, table_name: str, set_index=True, **kwargs
) -> bach.DataFrame:
    if is_bigquery(engine):
        pipeline = BigQueryExtractedContextsPipeline(engine=engine, table_name=table_name)
    else:
        pipeline = ExtractedContextsPipeline(engine=engine, table_name=table_name)

    result = pipeline(**kwargs)
    if set_index:
        indexes = list(ObjectivSupportedColumns.get_index_columns())
        result = result.set_index(keys=indexes)

    return result
