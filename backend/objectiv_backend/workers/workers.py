"""
Copyright 2021 Objectiv B.V.
"""
import argparse
import sys
import time

from objectiv_backend.common.config import WORKER_SLEEP_SECONDS
from objectiv_backend.workers.util import worker_main
from objectiv_backend.workers.worker_entry import main_entry
from objectiv_backend.workers.worker_finalize import main_finalize


def call_all(loop: bool):
    while True:
        event_count = worker_main(function=main_entry, loop=False)
        event_count += worker_main(function=main_finalize, loop=False)
        if not loop:
            break
        if event_count == 0:
            # sleeping a short random time is nice for catching concurrency problems
            # time.sleep(0.2 * random.random())
            time.sleep(WORKER_SLEEP_SECONDS)


def main():
    parser = argparse.ArgumentParser(prog='worker')
    parser.add_argument('type',
                        choices=['all', 'entry', 'finalize'],
                        default='all',
                        type=str)
    parser.add_argument('--loop', action='store_true')
    args = parser.parse_args(sys.argv[1:])
    if args.type == 'all':
        return call_all(args.loop)
    if args.type == 'entry':
        return worker_main(function=main_entry, loop=args.loop)
    if args.type == 'finalize':
        return worker_main(function=main_finalize, loop=args.loop)


if __name__ == '__main__':
    main()
