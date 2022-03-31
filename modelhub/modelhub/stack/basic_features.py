"""
Copyright 2021 Objectiv B.V.
"""
from sql_models.model import SqlModelBuilder


class BasicFeatures(SqlModelBuilder):

    @property
    def sql(self):
        return '''
SELECT
  sd.event_id,
  sd.day,
  sd.moment,
  sd.user_id,
  sd.session_id,
  sd.session_hit_number,
  sd.global_contexts,
  sd.location_stack,
  sd.event_type,
  sd.stack_event_types
FROM {{sessionized_data}} sd
'''
