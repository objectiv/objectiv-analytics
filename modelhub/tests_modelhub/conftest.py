"""
Copyright 2022 Objectiv B.V.

### Fixtures
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> clean pytest conftest
There is some pytest 'magic' here that automatically fills out the db parameters for
test functions that require an engine.
By default such a test function will get a Postgres db parameters. But if --big-query or --all is
specified on the commandline, then it will (also) get a BigQuery db parameters. For specific
<<<<<<< HEAD
tests, it is possible to disable postgres or bigquery testing, see 'marks' section below.

=======
There is some pytest 'magic' here that automatically fills out the 'engine' and 'dialect' parameters for
test functions that have either of those.
By default such a test function will get a Postgres dialect or engine. But if --big-query or --all is
specified on the commandline, then it will (also) get a BigQuery dialect or engine. For specific
tests, it is possible to disable postgres or bigquery testing, see 'marks' section below.

Additionally we define a 'pg_engine' fixture here that always return a Postgres engine. This fixture should
not be used for new functions tho! After fully implementing BigQuery it will be removed.

>>>>>>> BasePipeline, ExtractedContextsPipeline, SessionizedDataPipeline
=======
tests, it is possible to disable postgres or bigquery testing, see 'marks' section below.

>>>>>>> clean pytest conftest
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

<<<<<<< HEAD
<<<<<<< HEAD
1 and 3 are the default for tests. These either get 'db_params' as fixture and run against all
databases. Category 2 are tests that test generic code that is not geared to a specific database.
Category 4 and 5 are for functionality that we explicitly not support on some databases.

Category 4, and 5 are the exception, these need to be marked with the `skip_postgres` or `skip_bigquery` marks.
=======
1 and 3 are the default for tests. These either get 'engine' or 'dialect' as fixture and run against all
databases. Category 2 are tests that test generic code that is not geared to a specific database.
Category 4 and 5 are for functionality that we explicitly not support on some databases.

Category 2, 4, and 5 are the exception, these need to be marked with the `db_independent`, `skip_postgres`,
or `skip_bigquery` marks.
>>>>>>> BasePipeline, ExtractedContextsPipeline, SessionizedDataPipeline
=======
1 and 3 are the default for tests. These either get 'db_params' as fixture and run against all
databases. Category 2 are tests that test generic code that is not geared to a specific database.
Category 4 and 5 are for functionality that we explicitly not support on some databases.

Category 4, and 5 are the exception, these need to be marked with the `skip_postgres` or `skip_bigquery` marks.
>>>>>>> clean pytest conftest
"""
import os
from enum import Enum
from typing import Dict, NamedTuple, Optional

import bach
import pytest
<<<<<<< HEAD
<<<<<<< HEAD
from _pytest.fixtures import SubRequest
=======
>>>>>>> BasePipeline, ExtractedContextsPipeline, SessionizedDataPipeline
=======
from _pytest.fixtures import SubRequest
>>>>>>> clean pytest conftest
from _pytest.main import Session
from _pytest.python import Metafunc
from _pytest.config.argparsing import Parser
from sql_models.constants import DBDialect
from sqlalchemy import create_engine
from tests_modelhub.data_and_utils.utils import setup_db

MARK_SKIP_POSTGRES = 'skip_postgres'
MARK_SKIP_BIGQUERY = 'skip_bigquery'


class DB(Enum):
    POSTGRES = 'postgres'
    BIGQUERY = 'bigquery'


class DBParams(NamedTuple):
    url: str
    credentials: Optional[str]
    table_name: str


@pytest.fixture(autouse=True, scope='session')
def setup_postgres_db(request: SubRequest) -> None:
    """
    Helper for creating postgres database used by all functional tests. Only created if it is required
    to run tests against Postgres.
    """
    if request.session.config.getoption("big_query"):
        return

    db_params = _get_postgres_db_params()
    engine = create_engine(url=db_params.url)
    setup_db(
        engine,
        table_name=db_params.table_name,
        columns={
            'event_id': bach.SeriesUuid.supported_db_dtype[DBDialect.POSTGRES],
            'day': bach.SeriesDate.supported_db_dtype[DBDialect.POSTGRES],
            'moment': bach.SeriesTimestamp.supported_db_dtype[DBDialect.POSTGRES],
            'cookie_id': bach.SeriesUuid.supported_db_dtype[DBDialect.POSTGRES],
            'value': bach.SeriesJson.supported_db_dtype[DBDialect.POSTGRES],
        },
    )


def pytest_addoption(parser: Parser):
    # Add options for parameterizing multi-database tests for testing either Postgres, Bigquery, or both.
    # The actual parameterizing happens in pytest_generate_tests(), based on the paramters that the user
    # provides

    # This function will automatically be called by pytest at the start of a test run, see:
    # https://docs.pytest.org/en/6.2.x/reference.html#initialization-hooks
    parser.addoption('--postgres', action='store_true', help='run the functional tests for Postgres')
    parser.addoption('--big-query', action='store_true', help='run the functional tests for BigQuery')
    parser.addoption('--all', action='store_true', help='run the functional tests for BigQuery')


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
        db_params.append(_get_postgres_db_params())

    if testing_bq and not skip_bigquery:
        db_params.append(_get_bigquery_db_params())

    if 'db_params' in metafunc.fixturenames:
        metafunc.parametrize("db_params", db_params)


def _get_postgres_db_params() -> DBParams:
    return DBParams(
        url=os.environ.get('OBJ_DB_PG_TEST_URL', 'postgresql://objectiv:@localhost:5432/objectiv'),
        credentials=None,
        table_name='objectiv_data',
    )


def _get_bigquery_db_params() -> DBParams:
    return DBParams(
        url=os.environ.get('OBJ_DB_BQ_TEST_URL', 'bigquery://objectiv-snowplow-test-2/modelhub_test'),
        credentials=os.environ.get(
            'OBJ_DB_BQ_CREDENTIALS_PATH',
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/.secrets/bach-big-query-testing.json'
        ),
        table_name='events',
    )