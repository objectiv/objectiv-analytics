"""
Copyright 2021 Objectiv B.V.
"""
import time
from typing import Callable, Any

from objectiv_backend.common.config import get_config_postgres
from objectiv_backend.common.db import get_db_connection


def worker_main(function: Callable[[Any], int], loop: bool) -> int:
    """
    Run the function once, or in a loop.
    Will print the last part of the function's name and information about the function's execution time.

    If running in a loop it will sleep a second between invocations if the function returns 0.
    :param function: function that will be called. Should take a `connection` as arguments. The connection
        is a db_connection as delivered by get_db_connection()
    :param loop: whether to call the function once (False) or in an endless loop (True)
    :return number of processed events, if loop is False
    """
    pg_config = get_config_postgres()
    if pg_config is None:
        raise Exception('Missing Postgres configuration')
    connection = get_db_connection(pg_config)
    name = function.__name__.split('_')[-1]
    print(f'{name} worker')
    while True:
        start = time.time()
        event_count = function(connection)
        end = time.time()
        print(f'Processing time: {(end - start):.5} s')
        if not loop:
            return event_count
        if event_count == 0:
            time.sleep(1)
