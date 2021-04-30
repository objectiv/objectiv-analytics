with session_starts as (
    select
        cookie_id as cookie_id,
        event_id as event_id,
        coalesce(
            extract(
                epoch from (moment - lag(moment, 1) over (partition by cookie_id order by moment, event_id))
            ) > {{ var('session_gap_seconds') }},
            true
        ) as is_start_of_session,
        moment as moment
    from data
),
session_id_and_start as (
    select
           -- TODO: do something smart so this can scale.
           -- currently we always have to query all data. We want to have consistent session_ids, but don't
           -- want to calculate them from scratch every time.
           -- uuid_generate_v1() as session_id,
           row_number() over (order by moment asc) as session_id,
           cookie_id,
           event_id,
           moment as moment
    from session_starts
    where is_start_of_session
)
select
        s.session_id as session_id,
        row_number() over (partition by s.session_id order by d.moment, d.event_id asc) as session_hit_number,
        d.*
from data as d
inner join session_id_and_start as s on s.cookie_id = d.cookie_id and s.moment <= d.moment
where not exists (
    select *
    from session_id_and_start as s2
    where
      -- a session start for the same cookie
          s2.cookie_id = d.cookie_id
      and s2.moment <= d.moment
      -- and that session is closer to pq.moment than the selected session s
      and s2.moment > s.moment
)
order by session_id, moment
