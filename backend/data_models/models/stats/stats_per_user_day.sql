--
-- Per cookie_id the number of sessions and events
--
select
    cookie_id,
    day,
    count(distinct session_id) as sessions,
    count(*) as events
from {{ ref('sessionized_data') }}
group by cookie_id, day
