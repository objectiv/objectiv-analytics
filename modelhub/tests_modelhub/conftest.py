"""
Copyright 2022 Objectiv B.V.

### Fixtures
There is some pytest 'magic' here that automatically fills out the 'engine' and 'dialect' parameters for
test functions that have either of those.
By default such a test function will get a Postgres dialect or engine. But if --big-query or --all is
specified on the commandline, then it will (also) get a BigQuery dialect or engine. For specific
tests, it is possible to disable postgres or bigquery testing, see 'marks' section below.

Additionally we define a 'pg_engine' fixture here that always return a Postgres engine. This fixture should
not be used for new functions tho! After fully implementing BigQuery it will be removed.

### Marks and Test Categorization
A lot of functionality needs to be tested for multiple databases. The 'engine' and 'dialects' fixtures
mentioned above help with that. Additionally we have some marks (`@pytest.mark.<type>`) to make it explicit
which databases we expect tests to run against.

We broadly want 5 categories of tests:
* unit-test: These don't interact with a database
  * unit-tests that are tested with multiple database dialects (1)
  * unit-tests that are database-dialect independent (2)
* functional-tests: These interact with a database
  *  functional-tests that run against all supported databases (3)
  *  functional-tests that run against all supported databases except Postgres (4)
  *  functional-tests that run against all supported databases except BigQuery (5)

1 and 3 are the default for tests. These either get 'engine' or 'dialect' as fixture and run against all
databases. Category 2 are tests that test generic code that is not geared to a specific database.
Category 4 and 5 are for functionality that we explicitly not support on some databases.

Category 2, 4, and 5 are the exception, these need to be marked with the `db_independent`, `skip_postgres`,
or `skip_bigquery` marks.
"""
import os
from enum import Enum
from typing import Dict

import pytest
from _pytest.main import Session
from _pytest.python import Metafunc, Function
from _pytest.config.argparsing import Parser
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from tests_modelhub.functional.modelhub.logistic_regression_test_utils import TestLR


DB_PG_TEST_URL = os.environ.get('OBJ_DB_PG_TEST_URL', 'postgresql://objectiv:@localhost:5432/objectiv')
DB_BQ_TEST_URL = os.environ.get('OBJ_DB_BQ_TEST_URL', 'bigquery://objectiv-snowplow-test-2/bach_test')
DB_BQ_CREDENTIALS_PATH = os.environ.get(
    'OBJ_DB_BQ_CREDENTIALS_PATH',
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/.secrets/bach-big-query-testing.json'
)


MARK_DB_INDEPENDENT = 'db_independent'
MARK_SKIP_POSTGRES = 'skip_postgres'
MARK_SKIP_BIGQUERY = 'skip_bigquery'


TestLR.__test__ = False


class DB(Enum):
    POSTGRES = 'postgres'
    BIGQUERY = 'bigquery'


_ENGINE_CACHE: Dict[DB, Engine] = {}


@pytest.fixture()
def pg_engine() -> Engine:
    # TODO: port all tests that use this to be multi-database. Or explicitly mark them as skip-bigquery
    return _ENGINE_CACHE[DB.POSTGRES]


def pytest_addoption(parser: Parser):
    # Add options for parameterizing multi-database tests for testing either Postgres, Bigquery, or both.
    # The actual parameterizing happens in pytest_generate_tests(), based on the paramters that the user
    # provides

    # This function will automatically be called by pytest at the start of a test run, see:
    # https://docs.pytest.org/en/6.2.x/reference.html#initialization-hooks
    parser.addoption('--postgres', action='store_true', help='run the functional tests for Postgres')
    parser.addoption('--big-query', action='store_true', help='run the functional tests for BigQuery')
    parser.addoption('--all', action='store_true', help='run the functional tests for BigQuery')


def pytest_sessionstart(session: Session):
    # Initialize _ENGINE_CACHE per pytest-xdist worker session based on current pytest running config.
    # This way we avoid the creation of a new engine per test, as this is quite inefficient and might
    # cause failures due to multiple clients trying to connect to db server.

    # For more information, please see:
    # https://pytest-xdist.readthedocs.io/en/latest/distribution.html
    # https://docs.pytest.org/en/6.2.x/reference.html#pytest.hookspec.pytest_sessionstart

    if session.config.getoption("all"):
        _ENGINE_CACHE[DB.POSTGRES] = _get_postgres_engine()
        _ENGINE_CACHE[DB.BIGQUERY] = _get_bigquery_engine()
    elif session.config.getoption("big_query"):
        _ENGINE_CACHE[DB.BIGQUERY] = _get_bigquery_engine()
    else:  # default option, don't even check if --postgres is set
        _ENGINE_CACHE[DB.POSTGRES] = _get_postgres_engine()


def pytest_generate_tests(metafunc: Metafunc):
    # Paramaterize the 'engine' and 'dialect' parameters of tests based on the options specified by the
    # user (see pytest_addoption() for options).

    # This function will automatically be called by pytest while it is creating the list of tests to run,
    # see: https://docs.pytest.org/en/6.2.x/reference.html#collection-hooks
    markers = list(metafunc.definition.iter_markers())
    skip_postgres = any(mark.name == MARK_SKIP_POSTGRES for mark in markers)
    skip_bigquery = any(mark.name == MARK_SKIP_BIGQUERY for mark in markers)

    engines = []
    for name, engine_dialect in _ENGINE_CACHE.items():
        if name == DB.POSTGRES and skip_postgres:
            continue
        if name == DB.BIGQUERY and skip_bigquery:
            continue
        engines.append(engine_dialect)

    if 'dialect' in metafunc.fixturenames:
        dialects = [engine.dialect for engine in engines]
        metafunc.parametrize("dialect", dialects)
    if 'engine' in metafunc.fixturenames:
        metafunc.parametrize("engine", engines)


def pytest_runtest_setup(item: Function):
    # Here we check that tests that are marked as `db_independent`, that they do not have a `dialect` or
    # `engine` parameter.

    # This function will automatically be called by pytest before running a specific test function. See:
    # https://docs.pytest.org/en/6.2.x/reference.html#test-running-runtest-hooks
    fixture_names = item.fixturenames
    markers = list(item.iter_markers())
    is_db_independent_test = any(mark.name == MARK_DB_INDEPENDENT for mark in markers)
    is_multi_db_test = 'dialect' in fixture_names or 'engine' in fixture_names
    if is_db_independent_test and is_multi_db_test:
        raise Exception('Test has both the `db_independent` mark as well as either the `dialect` or '
                        '`engine` parameter. Test can not be both database independent and multi-database.')


def _get_postgres_engine() -> Engine:
    return create_engine(DB_PG_TEST_URL)


def _get_bigquery_engine() -> Engine:
    return create_engine(DB_BQ_TEST_URL, credentials_path=DB_BQ_CREDENTIALS_PATH)
