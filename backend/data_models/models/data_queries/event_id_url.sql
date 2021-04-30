{{ config(materialized='ephemeral') }}
select
    event_id,
    context ->> 'id' as url
from {{ ref('event_id_context_type') }}
where context_type = 'WebDocumentContext'
-- todo: make sure event_id is unique
