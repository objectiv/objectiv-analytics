begin;

create table queue_entry (
    event_id uuid not null,
    insert_order bigserial,
    value json not null
);

create table queue_finalize (
    event_id uuid not null,
    insert_order bigserial,
    value json not null
);

create table data (
    event_id uuid not null,
    day date not null, -- This is for query convenience; a possible sharding key? We might well put an index on this badboy
    moment timestamp not null,
    cookie_id uuid not null,
    value json not null,
    primary key(event_id)
);

create index on data(day);

create type failure_reason as enum('failed validation', 'duplicate');

create table nok_data (
    -- perhaps we want to add a field here that states the reason why the data is not ok?
    event_id uuid not null,
    day date not null, -- This is for query convenience; a possible sharding key? We might well put an index on this badboy
    moment timestamp not null,
    cookie_id uuid not null,
    value json not null,
    reason failure_reason default 'failed validation'
);


create view data_with_sessions as
with session_starts as (
    select
        cookie_id as cookie_id,
        event_id as event_id,
        coalesce(
            -- TODO: session is now 5 seconds, change this.
            extract(epoch from (moment - lag(moment, 1) over (partition by cookie_id order by moment, event_id))) > 5,
            true
        ) as is_start_of_session,
        moment as moment
    from data
),
session_id_and_start as (
    select
            -- We need a unique identifier for the session. We use event_id, as that gives us a unique id
            -- per session. The event_ids are all unique, and an event can only belong to one
            -- session, and thus we can use the event_id as a unique session_id.
           event_id as session_id,
           cookie_id,
           event_id as event_id,
           moment as moment
    from session_starts
    where is_start_of_session
)
select
        s.session_id as session_id,
        row_number() over (partition by s.session_id order by d.moment, d.event_id asc) as session_hit_number,
        d.*
from data as d
inner join session_id_and_start as s on s.cookie_id = d.cookie_id and s.moment <= d.moment
where not exists (
    select *
    from session_id_and_start as s2
    where
      -- a session start for the same cookie
          s2.cookie_id = d.cookie_id
      and s2.moment <= d.moment
      -- and that session is closer to pq.moment than the selected session s
      and s2.moment > s.moment
)
order by session_id, moment
;


-- used by collector to write incoming events
create role obj_collector_role noinherit;
grant select, update, insert on queue_entry to obj_collector_role;
-- we also add the "worker" permissions here, to make sure
-- the synchronous mode properly works
grant select, insert on data, nok_data to obj_collector_role;

-- used by worker to read/write queues
-- update priv is needed because of the `select for update` queries
create role obj_worker_role noinherit;
grant select, update, delete on queue_entry to obj_worker_role;
grant select, update, insert, delete on queue_finalize to obj_worker_role;
grant insert on data, nok_data to obj_worker_role;

-- used by for example notebook to query session data
create role obj_reader_role noinherit;
grant select on data, data_with_sessions to obj_reader_role;


commit;
