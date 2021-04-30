{{ config(materialized='ephemeral') }}
with data as (
    select *
    from data
), id_context as (
    select data.event_id as event_id,
           ctxs.rn as context_number,
           ctxs.ctx as context
    from data
    left join lateral json_array_elements(data.value->'contexts') with ordinality as ctxs (ctx, rn) on true
), id_context_type_context as (
    select event_id                                              as event_id,
           context_number,
           json_array_elements_text(context -> '_context_types') as context_type,
           context                                               as context
    from id_context
)
select
    event_id,
    context_number,
    context_type,
    context
from id_context_type_context
order by event_id, context_number
