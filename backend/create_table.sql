begin;

create table public.queue_entry (
    event_id uuid not null,
    insert_order bigserial,
    value json not null,
    primary key(event_id)
);

create table public.queue_enrichment (
    event_id uuid not null,
    insert_order bigserial,
    value json not null,
    primary key(event_id)
);

create table public.queue_finalize (
    event_id uuid not null,
    insert_order bigserial,
    value json not null,
    primary key(event_id)
);

create table public.data (
    event_id uuid not null,
    day date not null, -- This is for query convenience; a possible sharding key? We might well put an index on this badboy
    moment timestamp not null,
    cookie_id uuid not null,
    value json not null,
    primary key(event_id)
);

create index on data(day);

create table public.nok_data (
    -- perhaps we want to add a field here that states the reason why the data is not ok?
    event_id uuid not null,
    day date not null, -- This is for query convenience; a possible sharding key? We might well put an index on this badboy
    moment timestamp not null,
    cookie_id uuid not null,
    value json not null,
    primary key(event_id)
);

-- used by collector to write incoming events
create role obj_collector_role noinherit;
grant select,update,insert on public.queue_entry to obj_collector_role;

-- used by worker to read/write queues
-- update priv is needed because of the `select for update` queries
create role obj_worker_role noinherit;
grant select,update,delete on public.queue_entry to obj_worker_role;
grant select,update,insert,delete on public.queue_enrichment, public.queue_finalize to obj_worker_role;
grant insert on public.data to obj_worker_role;

-- used by for example notebook to query session data
create role obj_reader_role noinherit;

commit;
