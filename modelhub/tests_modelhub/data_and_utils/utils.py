import os
from typing import Dict, Any

from bach import DataFrame
from sql_models.util import is_postgres
from sqlalchemy.engine import Engine
from tests.functional.bach.test_data_and_utils import get_bt, run_query

from modelhub import ModelHub
from tests_modelhub.data_and_utils.data_json_real import TEST_DATA_JSON_REAL, JSON_COLUMNS_REAL

PG_DB_URL = os.environ.get('OBJ_DB_PG_TEST_URL', 'postgresql://objectiv:@localhost:5432/objectiv')
PG_TABLE_NAME = 'objectiv_data'


def get_bt_with_json_data_real() -> DataFrame:
    bt = get_bt(TEST_DATA_JSON_REAL, JSON_COLUMNS_REAL, True)
    bt['global_contexts'] = bt.global_contexts.astype('json')
    bt['location_stack'] = bt.location_stack.astype('json')
    return bt


def get_objectiv_dataframe_test(time_aggregation=None):
    kwargs = {}
    if time_aggregation:
        kwargs = {'time_aggregation': time_aggregation}
    modelhub = ModelHub(**kwargs)

    return modelhub.get_objectiv_dataframe(
        db_url=PG_DB_URL,
        table_name=PG_TABLE_NAME,
    ), modelhub


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
