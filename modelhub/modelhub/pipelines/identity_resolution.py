"""
Copyright 2022 Objectiv B.V.
"""
from typing import Dict, Optional

import bach
from modelhub.pipelines.base_pipeline import BaseDataPipeline
from modelhub.util import (
    ObjectivSupportedColumns, get_supported_dtypes_per_objectiv_column, check_objectiv_dataframe
)


class IdentityResolutionPipeline(BaseDataPipeline):
    """
    Pipeline in charge of resolving user identities based on `IdentityContext`.
    This pipeline is dependent on the result from ExtractedContextsPipeline, therefore it expects that
    the result from the latter is generated correctly.


    The steps followed in this pipeline are the following:
        1. _validate_extracted_context_df: Validates if provided DataFrame contains
            user_id, global_contexts and moment series.
        2. _extract_identities_from_global_contexts: Creates new identity (user id) id
            and name values from the first IdentityContext value found for the event
            under the global_contexts series json. Returns a DataFrame considering the last
            registered identity for each user_id. If no identity was found, user_id is not considered.
        3. _resolve_original_user_ids: Replaces original user_ids with the ones extracted from previous step,
            only if an identity was found for it.
        4. _convert_dtypes: Will convert all required identity series to their correct dtype

    If user anonymization is required, call classmethod `anonymize_user_ids_without_identity`. The
        provided dataframe MUST have  `identity_user_id` series.

    Final bach DataFrame will be later validated, it must include:
        - 'identity_user_id', 'user_id', 'global_contexts', 'moment' series.
    """

    IDENTITY_FORMAT = "({}) || '|' || ({})"

    def __init__(self, identity_id: Optional[str] = None):
        self._identity_id = identity_id

    def _get_pipeline_result(
        self,
        extracted_contexts_df: Optional[bach.DataFrame] = None,
        **kwargs,
    ) -> bach.DataFrame:
        """
        Contains steps for solving identities for user_ids in provided dataframe.
        :param extracted_contexts_df: bach DataFrame containing `user_id`, `global_contexts`
            and `moment` series.
        :param identity_id: Identity id to be used for filtering IdentityContexts. If no value is provided,
            all IdentityContexts will be considered.

        returns a bach DataFrame
            - user_id original series dtype will be changed to string
            - identity_user_id series and all series from provided extracted_contexts_df.

        .. note::
            If user has no identity, original value will remain. If anonymization is required, please call
            IdentityResolutionPipeline.anonymize_user_ids_without_identity(df).
        """
        if not extracted_contexts_df:
            raise ValueError(f'{self.__class__.__name__} requires dataframe with extracted contexts.')

        context_df = extracted_contexts_df.copy()

        self._validate_extracted_context_df(context_df)

        context_df[ObjectivSupportedColumns.USER_ID.value] = (
            context_df[ObjectivSupportedColumns.USER_ID.value].astype(bach.SeriesString.dtype)
        )
        identity_context_df = self._extract_identities_from_global_contexts(context_df)

        context_df = self._resolve_original_user_ids(context_df, identity_context_df)
        return self._convert_dtypes(df=context_df)

    @classmethod
    def validate_pipeline_result(cls, result: bach.DataFrame) -> None:
        """
        Checks if we are returning required Objectiv series with respective dtype.
        """
        check_objectiv_dataframe(
            df=result,
            columns_to_check=['identity_user_id', 'user_id', 'global_contexts', 'moment'],
            check_dtypes=True,
            infer_identity_resolution=True,
        )

    @classmethod
    def anonymize_user_ids_without_identity(cls, df: bach.DataFrame) -> bach.DataFrame:
        """
        If user_id has no identity, then it will be anonymized by replacing original value with NULL.
        """
        resolved_user_id_series_name = ObjectivSupportedColumns.IDENTITY_USER_ID.value
        if resolved_user_id_series_name not in df.data_columns:
            raise Exception(
                (
                    f'Cannot anonymize user ids if {resolved_user_id_series_name} series '
                    'is not present in DataFrame data columns.'
                )
            )

        df = df.copy()
        has_no_identity = df[resolved_user_id_series_name].isnull()
        df.loc[has_no_identity, ObjectivSupportedColumns.USER_ID.value] = None
        return df

    @property
    def result_series_dtypes(self) -> Dict[str, str]:
        return {
            ObjectivSupportedColumns.USER_ID.value: bach.SeriesString.dtype,
            ObjectivSupportedColumns.IDENTITY_USER_ID.value: bach.SeriesString.dtype,
        }

    def _validate_extracted_context_df(self, df: bach.DataFrame) -> None:
        # make sure the context_df has AT LEAST the following series
        supported_dtypes = get_supported_dtypes_per_objectiv_column(
            with_identity_resolution=False,
        )
        expected_context_columns = [
            ObjectivSupportedColumns.USER_ID.value,
            ObjectivSupportedColumns.GLOBAL_CONTEXTS.value,
            ObjectivSupportedColumns.MOMENT.value,
        ]

        self._validate_data_dtypes(
            expected_dtypes={col: supported_dtypes[col] for col in expected_context_columns},
            current_dtypes=df.dtypes,
        )

    def _extract_identities_from_global_contexts(self, df: bach.DataFrame) -> bach.DataFrame:
        """
        Generates a dataframe containing the last encountered unique identity per user_id.
        This is performed by:
            1. Extract the first IdentityContext where `id` value matches the provided identity_id param value
                from the event's global_contexts. If `self._identity_id` is None, then the
                first IdentityContext found will be used instead.
            2. Drop rows where events have no IdentityContext
            3. Create the new user id based on the IdentityContext's id and name.
                Follows the following format:
                {id}|{name}
            4. Consider only the last identity from the user's last event
        returns a bach DataFrame with two series: user_id and identity_user_id.
            user-id is the user_id series from the provided `df` DataFrame
            identity_user_id is the new user_id in the format {id}|{name}
        """
        global_context_series = (
            df[ObjectivSupportedColumns.GLOBAL_CONTEXTS.value]
            .copy_override_type(bach.SeriesJson)
        )

        user_id_series_name = ObjectivSupportedColumns.USER_ID.value
        moment_series_name = ObjectivSupportedColumns.MOMENT.value

        identity_context_df = df[[user_id_series_name, moment_series_name]]

        # Extract first identity context for the event
        identity_slice_filter = {'_type': 'IdentityContext'}
        if self._identity_id is not None:
            identity_slice_filter['id'] = self._identity_id

        gc_array_slice = slice(identity_slice_filter, None)
        identity_context_df['identity_context_series'] = global_context_series.json[gc_array_slice].json[0]

        # drop events that have no identity
        identity_context_df = identity_context_df.dropna(subset=['identity_context_series'])

        # extract id and name values for the identity and create new user id
        identity_context_series = (
            identity_context_df['identity_context_series'].copy_override_type(bach.SeriesJson)
        )
        resolved_expr = bach.expression.Expression.construct(
            self.IDENTITY_FORMAT,
            identity_context_series.json.get_value('value', as_str=True),
            identity_context_series.json.get_value('id', as_str=True),
        )

        identity_user_id_series_name = ObjectivSupportedColumns.IDENTITY_USER_ID.value
        identity_context_df[identity_user_id_series_name] = (
            identity_context_df[user_id_series_name].copy_override(expression=resolved_expr)
        )

        identity_context_df = identity_context_df.materialize(node_name='extracted_id_and_name')

        # keep the last registered identity for the user
        identity_context_df = identity_context_df.drop_duplicates(
            subset=[user_id_series_name], keep='last', sort_by=moment_series_name, ascending=True,
        )
        return identity_context_df[[user_id_series_name, identity_user_id_series_name]]

    def _resolve_original_user_ids(
        self, df_to_resolve: bach.DataFrame, identity_context_df: bach.DataFrame,
    ) -> bach.DataFrame:
        """
        Replaces values from original user_id series with the extracted identities
        iff the identity is not NULL, otherwise original value is kept.
        Returns a DataFrame with updated user_ids and a new series for identity_user_id.
        """
        user_id_series_name = ObjectivSupportedColumns.USER_ID.value
        identity_user_id_series_name = ObjectivSupportedColumns.IDENTITY_USER_ID.value

        df_to_resolve = df_to_resolve.merge(
            identity_context_df, on=[user_id_series_name], how='left',
        )

        # replace user_ids with respective identity
        has_identity = df_to_resolve[identity_user_id_series_name].notnull()
        df_to_resolve.loc[has_identity, user_id_series_name] = (
            df_to_resolve[identity_user_id_series_name]
        )

        return df_to_resolve
