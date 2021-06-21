"""
Tool that connects to the database and creates the needed tables as defined in create_table.sql
If a duplicate-table error is encounterd, then the script will assume that the databse is already
initialized correctly and exit successfully.

This assumes that the user and database already exist.

Copyright 2021 Objectiv B.V.
"""
import argparse
import os
import sys
from time import sleep

import psycopg2

from objectiv_backend.common.config import get_config_postgres
from objectiv_backend.common.db import get_db_connection

_MAX_RETRIES = 5
_POSTGRES_DUPLICATE_TABLE_ERROR = '42P07'


def get_sql() -> str:
    """ get content of ../../create_tables.sql as string """
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, '../../create_tables.sql')
    with open(filename) as f:
        return f.read()


def get_connection_with_retries(retry: bool):
    """ Connect to database. If retry set will attempt multiple times"""
    pg_config = get_config_postgres()
    if pg_config is None:
        raise Exception('Missing Postgres configuration')

    retries = 0
    while True:
        try:
            return get_db_connection(pg_config)
        except psycopg2.OperationalError as error:
            if not retry or retries == _MAX_RETRIES:
                raise Exception("Could not connect to database") from error
            retries += 1
            print(f'Cannot connect to database. Retrying again in {retries} second(s)')
            sleep(retries)


def main():
    parser = argparse.ArgumentParser(description='Create tables in Postgres DB')
    parser.add_argument('--no-retries', dest='retry', default=True, action='store_false',
                        help="By default we'll try to connect multiple times before giving up; thus"
                             "giving the database time to start up if run at start up. If set won't retry")
    parser.add_argument('--print', dest='print', default=False, action='store_true',
                        help="Instead of running sql to setup schema, print it to stdout")
    args = parser.parse_args(sys.argv[1:])
    sql = get_sql()

    if args.print:
        print(sql)
        exit(0)

    connection = get_connection_with_retries(args.retry)
    with connection.cursor() as cursor:
        try:
            cursor.execute(sql)
            print('Succesfully initialized database.')
        except psycopg2.Error as error:
            if error.pgcode == _POSTGRES_DUPLICATE_TABLE_ERROR:
                print('Got "duplicate table error", assuming database is already initialized')
                exit(0)
            raise


if __name__ == '__main__':
    main()
