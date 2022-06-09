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
from pathlib import Path

from filelock import FileLock
import pytest
from _pytest.fixtures import SubRequest
from _pytest.tmpdir import TempPathFactory
from sqlalchemy import create_engine

from tests_modelhub.conftest import get_postgres_db_params
from tests_modelhub.data_and_utils.utils import setup_db


@pytest.fixture(autouse=True, scope='session')
def setup_postgres_db(request: SubRequest, tmp_path_factory: TempPathFactory, worker_id: str) -> None:
    """
    Helper for creating postgres database used by all functional tests. Only created if it is required
    to run tests against Postgres.
    When running in a scenario with multiple test processes, this will use a filelock to ensure the database
    get created only once.
    """
    if not request.session.config.getoption("all") and not request.session.config.getoption("postgres"):
        return

    if worker_id == 'master':
        # This is the simple case: we are running with a single worker
        _real_setup_postgres_db()
        return

    # We are running with multiple workers. Make sure only one worker calls _actually_setup_postgres_db()
    # Use a FileLock, as advised by the pytest-xdist docs [1]
    # [1] https://pypi.org/project/pytest-xdist/#making-session-scoped-fixtures-execute-only-once
    # Basic idea is that we'll use a lock file to make sure only one process at a time is in the critical
    # section. Besides setting up the database in the critical section, we'll also create a file on disk to
    # indicate to the other processes that the database has been setup already.

    root_tmp_dir = tmp_path_factory.getbasetemp().parent  # get the temp directory shared by all workers
    is_done_path: Path = root_tmp_dir / "setup_database_is_done.txt"
    lock_path: Path = root_tmp_dir / "setup_database.lcok"
    lock = FileLock(str(lock_path))
    with lock:
        if not is_done_path.is_file():
            # We got the lock, but the file does not yet exist, so we are the first process
            _real_setup_postgres_db()
            is_done_path.write_text('done')
            print("\n\nDB CREATED\n\n")
        else:
            print("\n\nDB READY\n\n")
        # else case: We got the lock, but the is_done_path file already exists, indicating we don't have to
        # do anything.


def _real_setup_postgres_db():
    db_params = get_postgres_db_params()
    setup_db(engine=create_engine(url=db_params.url), table_name=db_params.table_name)
