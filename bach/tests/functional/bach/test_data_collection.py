"""
Copyright 2021 Objectiv B.V.
"""
from bach.data_collection import DataCollection
from tests.functional.bach.test_data_and_utils import get_bt_with_test_data


def test_collection_to_sql_simple():
    df = get_bt_with_test_data()
    dc = DataCollection()

    df = dc.add(df, 'start')
    df['test'] = 1
    df = dc.add(df, 'step1')
    df = dc.get('start')
    df['test'] = 2
    df = dc.add(df, 'step2')

    result = dc.to_sql()
    print()
    for name, sql in result.items():
        print(f'name: {name}')
        print(f'sql: {sql}')
        print()
    assert len(result) == 3
    # TODO: execute queries, check results


def test_collection_to_sql_materialization():
    df = get_bt_with_test_data()
    dc = DataCollection()

    df = dc.add(df, 'start', materialization='table')

    df['test'] = 1
    df = dc.add(df, 'step1')
    df = dc.get('start')
    df['test'] = 2
    df = dc.add(df, 'step2')

    result = dc.to_sql()
    print()
    for name, sql in result.items():
        print(f'name: {name}')
        print(f'sql: {sql}')
        print()
    assert len(result) == 3
