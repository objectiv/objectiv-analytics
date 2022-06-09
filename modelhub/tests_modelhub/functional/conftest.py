"""
Copyright 2022 Objectiv B.V.

In this module we setup the database for functional tests.
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
    # use same logic as tests_modelhub.conftest.pytest_generate_tests()
    testing_pg = not request.session.config.getoption("big_query")
    if not testing_pg:
        return

    if worker_id == 'master':
        # This is the simple case: we are running with a single worker
        _real_setup_postgres_db()
        return

    # We are running with multiple workers. Make sure only one worker calls _real_setup_postgres_db()
    # Use a FileLock, as advised by the pytest-xdist docs [1]
    # [1] https://pypi.org/project/pytest-xdist/#making-session-scoped-fixtures-execute-only-once
    # Basic idea is that we'll use a lock file to make sure only one process at a time is in the critical
    # section. Besides setting up the database in the critical section, we'll also create a file on disk to
    # indicate to the other processes that the database has been setup already.

    root_tmp_dir = tmp_path_factory.getbasetemp().parent  # get the temp directory shared by all workers
    is_done_path: Path = root_tmp_dir / "setup_database_is_done.txt"
    lock_path: Path = root_tmp_dir / "setup_database.lock"

    # Try to get lock, but give up after 10 seconds. If another process is still busy setting up the database
    # after 10 seconds, then something is likely wrong. Better to fail than to wait forever.
    lock = FileLock(str(lock_path), timeout=10)
    with lock:
        if not is_done_path.is_file():
            # We got the lock, but the file does not yet exist, so we are the first process
            _real_setup_postgres_db()
            is_done_path.write_text('done')
        # else case: We got the lock, but the is_done_path file already exists, indicating we don't have to
        # do anything.


def _real_setup_postgres_db():
    db_params = get_postgres_db_params()
    setup_db(engine=create_engine(url=db_params.url), table_name=db_params.table_name)
