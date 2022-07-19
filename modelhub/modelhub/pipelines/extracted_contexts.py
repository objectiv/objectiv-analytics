"""
Copyright 2021 Objectiv B.V.
"""
import operator
from functools import reduce

import bach
from typing import Optional, Any, Mapping, Dict, NamedTuple

from bach.types import StructuredDtype
from sql_models.constants import DBDialect
from sql_models.util import is_bigquery, is_postgres
from sqlalchemy.engine import Engine

from modelhub.util import (
    ObjectivSupportedColumns, get_supported_dtypes_per_objectiv_column, check_objectiv_dataframe
)
from modelhub.pipelines.base_pipeline import BaseDataPipeline


class TaxonomyColumnDefinition(NamedTuple):
    name: str
    dtype: Any


_DEFAULT_TAXONOMY_DTYPE_PER_FIELD = {
    '_type': bach.SeriesString.dtype,
    '_types': bach.SeriesJson.dtype,
    'global_contexts': bach.SeriesJson.dtype,
    'location_stack': bach.SeriesJson.dtype,
    'time': bach.SeriesInt64.dtype,
}

_PG_TAXONOMY_COLUMN = TaxonomyColumnDefinition(name='value', dtype=bach.SeriesJson.dtype)

_BQ_TAXONOMY_COLUMN = TaxonomyColumnDefinition(
    name='contexts_io_objectiv_taxonomy_1_0_0',  # change only when version is updated
    dtype=[
        {
            **_DEFAULT_TAXONOMY_DTYPE_PER_FIELD,
            'cookie_id': bach.SeriesUuid.dtype,
            'event_id': bach.SeriesUuid.dtype,
        },
    ],
)


def _get_taxonomy_column_definition(engine: Engine) -> TaxonomyColumnDefinition:
    """
    Returns the definition of the Objectiv taxonomy column per supported engine
    """
    if is_postgres(engine):
        return _PG_TAXONOMY_COLUMN

    if is_bigquery(engine):
        return _BQ_TAXONOMY_COLUMN

    raise Exception('define taxonomy definition for engine')


class ExtractedContextsPipeline(BaseDataPipeline):
    """
    Pipeline in charge of extracting Objectiv context columns from event data source.
    Based on the provided engine, it will perform the proper transformations for generating a bach DataFrame
    that contains all expected series to be used by Modelhub.

    The steps followed in this pipeline are the following:
        1. _get_initial_data: Gets the initial bach DataFrame containing all required context columns
            based on the engine.
        2. _process_taxonomy_data: Will extract required fields from taxonomy json, it will use
            _DEFAULT_TAXONOMY_DTYPE_PER_FIELD by default. If engine requires other fields,
            it should be specified to the pipeline.
        3. _apply_extra_processing: Applies extra processing if required, this is mainly based on the engine.
            For example, for BigQuery, the pipeline will generate moment and day series from `time` series
            extracted from the taxonomy.
        4. _convert_dtypes: Will convert all required context series to their correct dtype
        5. _apply_date_filter: Applies start_date and end_date filter, if required.

    Final bach DataFrame will be later validated, it must include:
        - all context series defined in ObjectivSupportedColumns
        - correct dtypes for context series
    """
    DATE_FILTER_COLUMN = ObjectivSupportedColumns.DAY.value

    # extra columns that are needed to be fetched, taxonomy column provided for the engine
    # is ALWAYS selected
    required_context_columns_per_dialect: Dict[DBDialect, Dict[str, StructuredDtype]] = {
        DBDialect.POSTGRES: {
            'event_id': bach.SeriesUuid.dtype,
            'day': bach.SeriesDate.dtype,
            'moment': bach.SeriesTimestamp.dtype,
            'cookie_id': bach.SeriesUuid.dtype,
        },
        DBDialect.BIGQUERY: {
            'collector_tstamp': bach.SeriesTimestamp.dtype,
        },
    }

    def __init__(self, engine: Engine, table_name: str):
        super().__init__()
        self._engine = engine
        self._table_name = table_name
        self._taxonomy_column = _get_taxonomy_column_definition(engine)

        # check if table has all required columns for pipeline
        dtypes = bach.from_database.get_dtypes_from_table(
            engine=self._engine,
            table_name=self._table_name,
        )
        self._validate_data_dtypes(
            expected_dtypes=dict(self._get_base_dtypes()),
            current_dtypes=dtypes,
        )

    def _get_pipeline_result(self, **kwargs) -> bach.DataFrame:
        """
        Calls all operations performed to the initial data and returns a bach DataFrame with the expected
        context series
        """
        context_df = self._get_initial_data()
        context_df = self._process_taxonomy_data(context_df)
        context_df = self._apply_extra_processing(context_df)

        context_df = self._convert_dtypes(df=context_df)
        context_df = self._apply_date_filter(df=context_df, **kwargs)

        context_columns = ObjectivSupportedColumns.get_extracted_context_columns()
        context_df = context_df[context_columns]
        return context_df.materialize(node_name='context_data')

    @property
    def result_series_dtypes(self) -> Dict[str, str]:
        context_columns = ObjectivSupportedColumns.get_extracted_context_columns()
        supported_dtypes = get_supported_dtypes_per_objectiv_column(with_identity_resolution=False)
        return {
            col: dtype for col, dtype in supported_dtypes.items()
            if col in context_columns
        }

    def _get_base_dtypes(self) -> Mapping[str, StructuredDtype]:
        """
        Returns mapping of series names and dtypes expected from initial data
        """
        db_dialect = DBDialect.from_engine(self._engine)
        return {
            self._taxonomy_column.name: self._taxonomy_column.dtype,
            **self.required_context_columns_per_dialect[db_dialect],
        }

    def _get_initial_data(self) -> bach.DataFrame:
        return bach.DataFrame.from_table(
            table_name=self._table_name,
            engine=self._engine,
            index=[],
            all_dtypes=self._get_base_dtypes(),
        )

    def _process_taxonomy_data(self, df: bach.DataFrame) -> bach.DataFrame:
        """
        Extracts all needed values from the taxonomy json/dict and creates a new Series for each.
        Fields are dependent on the engine's taxonomy definition, therefore the new generated series might be
        different per engine.

        Returns a bach DataFrame containing each extracted field as series
        """
        df_cp = df.copy()
        taxonomy_series = df_cp[self._taxonomy_column.name]
        dtypes = _DEFAULT_TAXONOMY_DTYPE_PER_FIELD

        if is_bigquery(df.engine):
            # taxonomy column is a list, we just need to get the first value (LIST IS ALWAYS A SINGLE EVENT)
            taxonomy_series = taxonomy_series.elements[0]

            # same definition as _DEFAULT_TAXONOMY_DTYPE_PER_FIELD with some extra fields
            dtypes = self._taxonomy_column.dtype[0]

        for key, dtype in dtypes.items():
            # parsing element to string and then to dtype will avoid
            # conflicts between casting compatibility
            if isinstance(taxonomy_series, bach.SeriesJson):
                taxonomy_col = taxonomy_series.json.get_value(key, as_str=True)
            else:
                # taxonomy_series is dtype='dict' for BQ. Therefore, we need to explicitly
                # cast the resultant element as string
                taxonomy_col = taxonomy_series.elements[key].astype('string')

            taxonomy_col = taxonomy_col.astype(dtype).copy_override(name=key)
            df_cp[key] = taxonomy_col

        # rename series to objectiv supported
        df_cp = df_cp.rename(
            columns={
                'cookie_id': ObjectivSupportedColumns.USER_ID.value,
                '_type': ObjectivSupportedColumns.EVENT_TYPE.value,
                '_types': ObjectivSupportedColumns.STACK_EVENT_TYPES.value,
            },
        )

        return df_cp

    def _apply_extra_processing(self, df: bach.DataFrame) -> bach.DataFrame:
        """
        Applies more operations to the dataframe (if needed).

        Returns a bach DataFrame
        """
        df_cp = df.copy()
        if is_postgres(self._engine):
            return df_cp

        # remove taxonomy column, no longer needed
        df_cp = df_cp.drop(columns=[self._taxonomy_column.name])

        # this materialization is to generate a readable query
        df_cp = df_cp.materialize(node_name='bq_extra_processing')

        # Remove duplicated event_ids
        # Unfortunately, some events might share an event ID due to
        # browser pre-cachers or scraping bots sending the same event multiple time. Although,
        # legitimate clients might try to send the same events multiple times,
        # in an attempt to make sure that events do not get lost in case of connection problems
        # and/or app reloads. We can easily recognize these events as they'll have non-unique event-ids.
        # In all cases we are only interested in the first event. On postgres we achieve this by having a
        # primary key index on event-id. On BigQuery such indexes are not possible. Instead, we here filter
        # out duplicate event-ids, keeping the first event
        # based on the time the collector sends it to snowplow.
        df_cp = df_cp.drop_duplicates(subset=['event_id'], sort_by=['collector_tstamp'], keep='first')

        # BQ data source has no moment and day columns, therefore we need to generate them
        # based on the time value from the taxonomy column
        df_cp['moment'] = df_cp['time'].copy_override(
            expression=bach.expression.Expression.construct(f'TIMESTAMP_MILLIS({{}})', df_cp['time']),
        )
        df_cp['moment'] = df_cp['moment'].copy_override_type(bach.SeriesTimestamp)
        df_cp['day'] = df_cp['moment'].astype('date')

        return df_cp

    @classmethod
    def validate_pipeline_result(cls, result: bach.DataFrame) -> None:
        """
        Checks if we are returning ALL expected context series with proper dtype.
        """
        check_objectiv_dataframe(
            result,
            columns_to_check=ObjectivSupportedColumns.get_extracted_context_columns(),
            check_dtypes=True,
            infer_identity_resolution=False,
        )

    def _apply_date_filter(
        self,
        df: bach.DataFrame,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs,
    ) -> bach.DataFrame:
        """
        Filters dataframe by a date range.

        returns bach DataFrame
        """
        df_cp = df.copy()

        if not start_date and not end_date:
            return df_cp

        date_filters = []
        if start_date:
            date_filters.append(df_cp[self.DATE_FILTER_COLUMN] >= start_date)
        if end_date:
            date_filters.append(df_cp[self.DATE_FILTER_COLUMN] <= end_date)

        return df_cp[reduce(operator.and_, date_filters)]
