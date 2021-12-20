drop database if exists metabase;
create database metabase;
\c metabase

create role metabase with password 'metabase' login noinherit;
grant all  on database metabase to metabase;

\c objectiv
grant select on table objectiv.public.data to metabase;
grant temporary on database objectiv to metabase;