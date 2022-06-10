"""
Copyright 2022 Objectiv B.V.
### Fixtures
There is some pytest 'magic' here that automatically fills out the db parameters for
test functions that require an engine.
By default such a test function will get a Postgres db parameters. But if --big-query or --all is
specified on the commandline, then it will (also) get a BigQuery db parameters. For specific
tests, it is possible to disable postgres or bigquery testing, see 'marks' section below.
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
1 and 3 are the default for tests. These either get 'db_params' as fixture and run against all
databases. Category 2 are tests that test generic code that is not geared to a specific database.
Category 4 and 5 are for functionality that we explicitly not support on some databases.
Category 4, and 5 are the exception, these need to be marked with the `skip_postgres` or `skip_bigquery` marks.
"""
import os

from _pytest.python import Metafunc
from _pytest.config.argparsing import Parser
from tests_modelhub.data_and_utils.utils import DBParams


DB_PG_TEST_URL = os.environ.get('OBJ_DB_PG_TEST_URL', 'postgresql://objectiv:@localhost:5432/objectiv')
DB_BQ_TEST_URL = os.environ.get('OBJ_DB_BQ_TEST_URL', 'bigquery://objectiv-snowplow-test-2/modelhub_test')
DB_BQ_CREDENTIALS_PATH = os.environ.get(
    'OBJ_DB_BQ_CREDENTIALS_PATH',
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/.secrets/bach-big-query-testing.json'
)


MARK_SKIP_POSTGRES = 'skip_postgres'
MARK_SKIP_BIGQUERY = 'skip_bigquery'


def pytest_addoption(parser: Parser):
    # Add options for parameterizing multi-database tests for testing either Postgres, Bigquery, or both.
    # The actual parameterizing happens in pytest_generate_tests(), based on the paramters that the user
    # provides

    # This function will automatically be called by pytest at the start of a test run, see:
    # https://docs.pytest.org/en/6.2.x/reference.html#initialization-hooks
    parser.addoption('--postgres', action='store_true', help='run the functional tests for Postgres')
    parser.addoption('--big-query', action='store_true', help='run the functional tests for BigQuery')
    parser.addoption('--all', action='store_true', help='run the functional tests for all databases.')


def pytest_generate_tests(metafunc: Metafunc):
    # Paramaterize the 'db_params' parameters of tests based on the options specified by the
    # user (see pytest_addoption() for options).

    # This function will automatically be called by pytest while it is creating the list of tests to run,
    # see: https://docs.pytest.org/en/6.2.x/reference.html#collection-hooks
    markers = list(metafunc.definition.iter_markers())
    skip_postgres = any(mark.name == MARK_SKIP_POSTGRES for mark in markers)
    skip_bigquery = any(mark.name == MARK_SKIP_BIGQUERY for mark in markers)
    db_params = []

    testing_pg = not metafunc.config.getoption("big_query")
    testing_bq = metafunc.config.getoption("all") or metafunc.config.getoption("big_query")

    if testing_pg and not skip_postgres:
        db_params.append(get_postgres_db_params())

    if testing_bq and not skip_bigquery:
        db_params.append(_get_bigquery_db_params())

    if 'db_params' in metafunc.fixturenames:
        metafunc.parametrize("db_params", db_params)


def get_postgres_db_params() -> DBParams:
    """
    Get Postgres DBParams. Never call this function from a test, always use the 'db_params' fixture.
    """
    return DBParams(
        url=DB_PG_TEST_URL,
        credentials=None,
        table_name='objectiv_data',
    )


def _get_bigquery_db_params() -> DBParams:
    return DBParams(
        url=DB_BQ_TEST_URL,
        credentials=DB_BQ_CREDENTIALS_PATH,
        table_name='events',
    )
