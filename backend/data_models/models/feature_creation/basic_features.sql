SELECT
    cookie_id as user_id, -- TODO, we need to properly propagate a real user id
    *,
    concat_ws('___',
        location_stack0->>'_context_type',
        location_stack0->>'id',
        location_stack1->>'_context_type',
        location_stack1->>'id',
        location_stack2->>'_context_type',
        location_stack2->>'id',
        location_stack3->>'_context_type',
        location_stack3->>'id',
        location_stack4->>'_context_type',
        location_stack4->>'id',
        location_stack5->>'_context_type',
        location_stack5->>'id'
    ) as feature
FROM {{ ref('sessionized_data') }}
