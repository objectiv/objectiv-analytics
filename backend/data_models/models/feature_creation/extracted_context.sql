WITH extracted_contexts AS (
    SELECT *,
            value->>'event' AS event,
            JSON_EXTRACT_PATH(value, 'global_contexts') AS global_contexts,
            JSON_EXTRACT_PATH(value, 'location_stack') AS location_stack,
            JSON_EXTRACT_PATH(value, 'time') AS time,
            JSON_EXTRACT_PATH(value, 'events') AS events
    FROM data)
(SELECT *,
        location_stack->0 AS location_stack0,
        location_stack->1 AS location_stack1,
        location_stack->2 AS location_stack2,
        location_stack->3 AS location_stack3,
        location_stack->4 AS location_stack4,
        location_stack->5 AS location_stack5
FROM extracted_contexts)
