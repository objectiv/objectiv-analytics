"""
Copyright 2021 Objectiv B.V.
"""
from sql_models.model import SqlModelBuilder


class ExtractedContexts(SqlModelBuilder):

    @property
    def sql(self):
        return _SQL


_SQL = \
    '''
    SELECT event_id,
            day,
            moment,
            cookie_id AS user_id,
            CAST(JSON_EXTRACT_PATH(value, 'global_contexts') AS jsonb) AS global_contexts,
            CAST(JSON_EXTRACT_PATH(value, 'location_stack') AS jsonb) AS location_stack,
            value->>'_type' AS event_type,
            CAST(JSON_EXTRACT_PATH(value, '_types') AS jsonb) AS stack_event_types
     FROM {table_name}
     {date_range}
     '''
