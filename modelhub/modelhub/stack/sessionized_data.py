"""
Copyright 2021 Objectiv B.V.
"""
from sql_models.model import SqlModelBuilder


class SessionizedData(SqlModelBuilder):

    @property
    def sql(self):
        return _SQL


_SQL = \
    '''
    with session_starts_{{id}} as (
        select
            *,
            case when coalesce(
                extract(
                    epoch from (moment - lag(moment, 1)
                        over (partition by user_id order by moment, event_id))
                ) > {session_gap_seconds},
                true
            ) then true end as is_start_of_session
        from {{extracted_contexts}}
    ),
    session_id_and_start_{{id}} as (
        select
            *,
            -- generates a session_start_id for each is_start_of_session
            case
                when is_start_of_session then
                    row_number() over (partition by is_start_of_session order by moment, event_id)
            end as session_start_id,
            -- generates a unique number for each session, but not in the right order.
            count(is_start_of_session) over (order by user_id, moment, event_id) as is_one_session
        from session_starts_{{id}}
    )
    select
        *,
        -- populates the correct session_id for all rows with the same value for is_one_session
        first_value(
            session_start_id
        ) over (
            partition by is_one_session order by moment, event_id
        ) as session_id,
        row_number() over (partition by is_one_session order by moment, event_id) as session_hit_number
    from session_id_and_start_{{id}}
    '''
