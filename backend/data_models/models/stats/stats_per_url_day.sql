--
-- Per url and day the number of unique users, sessions and events
--

--
--
-- TEST VAR: {{ var('test_variable') }} - Table {{ this }}
--
--
select
       eiu.url,
       sd.day,
       count(distinct sd.cookie_id) as users,
       count(distinct sd.session_id) as sessions,
       count(*) as events
from {{ ref('sessionized_data') }} as sd
inner join {{ ref('event_id_url') }} as eiu on eiu.event_id = sd.event_id
group by eiu.url, sd.day
