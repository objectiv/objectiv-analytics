import json
from datetime import datetime, timezone
from typing import Dict, Any
from uuid import UUID

from bach import DataFrame
from sql_models.util import is_postgres, is_bigquery
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from tests.functional.bach.test_data_and_utils import get_bt, run_query

from modelhub import ModelHub
from tests_modelhub.data_and_utils.data_json_real import TEST_DATA_JSON_REAL, JSON_COLUMNS_REAL
from tests_modelhub.data_and_utils.data_objectiv import TEST_DATA_OBJECTIV


def _convert_moment_to_utc_time(moment: str) -> int:
    dt = datetime.fromisoformat(moment)
    dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1e3)


def get_bt_with_json_data_real() -> DataFrame:
    bt = get_bt(TEST_DATA_JSON_REAL, JSON_COLUMNS_REAL, True)
    bt['global_contexts'] = bt.global_contexts.astype('json')
    bt['location_stack'] = bt.location_stack.astype('json')
    return bt


def get_objectiv_dataframe_test(db_params=None, time_aggregation=None):
    if not db_params:
        # by default use PG (this should be removed after modelhub is able to work with all bach engines)
        import os
        db_url = os.environ.get('OBJ_DB_PG_TEST_URL', 'postgresql://objectiv:@localhost:5432/objectiv')
        credentials = None
        table_name = 'objectiv_data'
    else:
        db_url = db_params.url
        credentials = db_params.credentials
        table_name = db_params.table_name

    kwargs = {}
    if time_aggregation:
        kwargs = {'time_aggregation': time_aggregation}
    modelhub = ModelHub(**kwargs)

    return modelhub.get_objectiv_dataframe(
        db_url=db_url,
        table_name=table_name,
        bq_credentials_path=credentials,
    ), modelhub


def get_parsed_objectiv_data(engine):
    parsed_data = []
    for event_data in TEST_DATA_OBJECTIV:
        event_id, day, moment, cookie_id, value = event_data
        value = json.loads(value)
        # BQ uses time from taxonomy json for getting moment and day
        # therefore time value MUST be the same as moment
        if is_bigquery(engine):
            value['time'] = _convert_moment_to_utc_time(moment)

        parsed_data.append(
            {
                'event_id': UUID(event_id),
                'day': datetime.strptime(day, '%Y-%m-%d').date(),
                'moment': datetime.fromisoformat(moment),
                'cookie_id': UUID(cookie_id),
                'value': value
            }
        )

    return parsed_data


def create_engine_from_db_params(db_params) -> Engine:
    if db_params.credentials:
        engine = create_engine(url=db_params.url, credentials_path=db_params.credentials)
    else:
        engine = create_engine(url=db_params.url)

    return engine


def setup_db(engine: Engine, table_name: str, columns: Dict[str, Any]):
    _prep_db_table(engine, table_name=table_name, columns=columns)
    _insert_records_in_db(engine, table_name=table_name, columns=columns)


def _prep_db_table(engine, table_name: str, columns: Dict[str, Any]):
    if is_postgres(engine):
        column_stmt = ','.join(f'{col_name} {db_type}' for col_name, db_type in columns.items())
        sql = f"""
            drop table if exists {table_name};
            create table {table_name} ({column_stmt});
            alter table {table_name}
                owner to objectiv
        """
    else:
        raise Exception()
    run_query(engine, sql)


def _insert_records_in_db(engine, table_name: str, columns: Dict[str, Any]):
    from tests_modelhub.data_and_utils.data_objectiv import TEST_DATA_OBJECTIV

    column_stmt = ','.join(columns.keys())
    records = []
    if is_postgres(engine):
        for record in TEST_DATA_OBJECTIV:
            formatted_values = [f"'{record[col_index]}'" for col_index, _ in enumerate(columns)]
            records.append(f"({','.join(formatted_values)})")
    else:
        raise Exception()

    values_stmt = ','.join(records)
    sql = f'insert into {table_name} ({column_stmt}) values {values_stmt}'
    run_query(engine, sql)