SELECT user_id, COUNT(DISTINCT session_id) >= {{ var('frequency', 3) }} as achieved
FROM {{ ref('sessionized_data')}}
GROUP BY user_id