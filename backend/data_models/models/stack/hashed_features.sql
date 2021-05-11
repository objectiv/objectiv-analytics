WITH selected_stacks AS
(
SELECT   event_id,
         Array_to_string(Array_agg(Cast(x AS TEXT)),',') AS stack_selection,
         Array_to_json(Array_agg(Row_to_json(x))) as selected_stack_location
FROM     {{ ref('extracted_contexts') }},
         json_to_recordset(location_stack) AS x(_context_type text,id text)
GROUP BY event_id
ORDER BY event_id
)
SELECT *,
       md5(concat(stack_selection,event)) as feature_hash
FROM {{ ref('extracted_contexts') }}
JOIN selected_stacks USING (event_id)