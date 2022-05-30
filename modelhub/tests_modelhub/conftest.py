import bach
import pytest
from sql_models.constants import DBDialect
from sqlalchemy import create_engine

from tests_modelhub.data_and_utils.utils import PG_DB_URL, setup_db, PG_TABLE_NAME


@pytest.fixture(autouse=True, scope='session')
def setup_postgres_db() -> None:
    """
    Helper for creating postgres database used by all functional tests.
    """
    engine = create_engine(url=PG_DB_URL)
    setup_db(
        engine,
        table_name=PG_TABLE_NAME,
        columns={
            'event_id': bach.SeriesUuid.supported_db_dtype[DBDialect.POSTGRES],
            'day': bach.SeriesDate.supported_db_dtype[DBDialect.POSTGRES],
            'moment': bach.SeriesTimestamp.supported_db_dtype[DBDialect.POSTGRES],
            'cookie_id': bach.SeriesUuid.supported_db_dtype[DBDialect.POSTGRES],
            'value': bach.SeriesJsonPostgres.supported_db_dtype[DBDialect.POSTGRES],
        },
    )
