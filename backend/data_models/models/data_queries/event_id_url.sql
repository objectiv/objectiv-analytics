{{ config(materialized='ephemeral') }}
--
--
-- TEST VAR: {{ var('test_variable') }} - Table {{ this }}
--
--
select
    event_id,
    context ->> 'id' as url
from {{ ref('event_id_context_type') }}
where context_type = 'WebDocumentContext'
-- todo: make sure event_id is unique
