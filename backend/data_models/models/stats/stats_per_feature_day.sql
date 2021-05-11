--
-- Per feature and day the number of unique users, sessions and events
--
select
       f.feature_pretty_name,
       sd.day,
       count(distinct sd.user_id) as users,
       count(distinct sd.session_id) as sessions,
       count(*) as events
from {{ ref('sessionized_data') }} as sd
inner join {{ ref( var("feature_table") | as_text ) }} as f using (feature_hash)
group by f.feature_pretty_name, sd.day
