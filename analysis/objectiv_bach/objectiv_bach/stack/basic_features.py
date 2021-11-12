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
  sd.session_id,
  sd.session_hit_number,
  sd.user_id,
  sd.global_contexts,
  sd.location_stack,
  sd.event_type,
  sd.stack_event_types,
  bm.feature,
  bm.feature_hash
FROM {{sessionized_data}} sd
JOIN {{feature_table}} bm USING (feature_hash)
'''
