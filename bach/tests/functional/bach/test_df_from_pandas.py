"""
Copyright 2021 Objectiv B.V.
"""
import pytest
import sqlalchemy

from bach import DataFrame
from tests.conftest import DB_PG_TEST_URL
from tests.functional.bach.test_data_and_utils import get_pandas_df, TEST_DATA_CITIES, CITIES_COLUMNS, \
    assert_equals_data
import datetime
from uuid import UUID
import pandas as pd
import numpy as np

EXPECTED_COLUMNS = [
    '_index_skating_order', 'skating_order', 'city', 'municipality', 'inhabitants', 'founding'
]
EXPECTED_DATA = [
    [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285],
    [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456],
    [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268]
]

TEST_DATA_INJECTION = [
    [1, '{X}', "'test'", '"test"'],
    [2, '{{x}}', "{{test}}", "''test''\\''"]
]
COLUMNS_INJECTION = ['Index', 'X"x"', '{test}', '{te{}{{s}}t}']
# The expected data is what we put in, plus the index column, which equals the first column
EXPECTED_COLUMNS_INJECTION = [f'_index_{COLUMNS_INJECTION[0]}'] + COLUMNS_INJECTION
EXPECTED_DATA_INJECTION = [[row[0]] + row for row in TEST_DATA_INJECTION]

get_pandas_df(TEST_DATA_INJECTION, COLUMNS_INJECTION)

TYPES_DATA = [
    [1, 1.324, True, datetime.datetime(2021, 5, 3, 11, 28, 36, 388), 'Ljouwert', datetime.date(2021, 5, 3),
     ['Sûkerbôlle'], UUID('36ca4c0b-804d-48ff-809f-28cf9afd078a'), {'a': 'b'},
     datetime.timedelta(days=1, seconds=7583, microseconds=100), datetime.date(2021, 5, 3)],
    [2, 2.734, True, datetime.datetime(2021, 5, 4, 23, 28, 36, 388), 'Snits', datetime.date(2021, 5, 4),
     ['Dúmkes'], UUID('81a8ace2-273b-4b95-b6a6-0fba33858a22'), {'c': ['d', 'e']},
     datetime.timedelta(days=5, seconds=583, microseconds=100), ['Dúmkes']],
    [3, 3.52, False, datetime.datetime(2022, 5, 3, 14, 13, 13, 388), 'Drylts', datetime.date(2022, 5, 3),
     ['Grutte Pier Bier'], UUID('8a70b3d3-33ec-4300-859a-bb2efcf0b188'), {'f': 'g', 'h': 'i'},
     datetime.timedelta(days=4, seconds=8583, microseconds=100), ['Grutte Pier Bier']
     ]
]
TYPES_COLUMNS = ['int_column', 'float_column', 'bool_column', 'datetime_column',
                 'string_column', 'date_column', 'list_column', 'uuid_column',
                 'dict_column', 'timedelta_column', 'mixed_column']


def test_from_pandas_table():
    pdf = get_pandas_df(TEST_DATA_CITIES, CITIES_COLUMNS)
    engine = sqlalchemy.create_engine(DB_PG_TEST_URL)
    bt = DataFrame.from_pandas(
        engine=engine,
        df=pdf,
        convert_objects=True,
        name='test_from_pd_table',
        materialization='table',
        if_exists='replace'
    )
    assert_equals_data(bt, expected_columns=EXPECTED_COLUMNS, expected_data=EXPECTED_DATA)


def test_from_pandas_table_injection():
    pdf = get_pandas_df(TEST_DATA_INJECTION, COLUMNS_INJECTION)
    engine = sqlalchemy.create_engine(DB_PG_TEST_URL)
    bt = DataFrame.from_pandas(
        engine=engine,
        df=pdf,
        convert_objects=True,
        name='test_from_pd_{table}_"injection"',
        materialization='table',
        if_exists='replace'
    )
    assert_equals_data(bt, expected_columns=EXPECTED_COLUMNS_INJECTION, expected_data=EXPECTED_DATA_INJECTION)


def test_from_pandas_ephemeral_basic():
    pdf = get_pandas_df(TEST_DATA_CITIES, CITIES_COLUMNS)
    engine = sqlalchemy.create_engine(DB_PG_TEST_URL)
    bt = DataFrame.from_pandas(
        engine=engine,
        df=pdf,
        convert_objects=True,
        materialization='cte',
        name='ephemeral data'
    )
    assert_equals_data(bt, expected_columns=EXPECTED_COLUMNS, expected_data=EXPECTED_DATA)


def test_from_pandas_ephemeral_injection():
    pdf = get_pandas_df(TEST_DATA_INJECTION, COLUMNS_INJECTION)
    engine = sqlalchemy.create_engine(DB_PG_TEST_URL)
    bt = DataFrame.from_pandas(
        engine=engine,
        df=pdf,
        convert_objects=True,
        materialization='cte',
        name='ephemeral data'
    )
    assert_equals_data(bt, expected_columns=EXPECTED_COLUMNS_INJECTION, expected_data=EXPECTED_DATA_INJECTION)


def test_from_pandas_non_happy_path():
    pdf = get_pandas_df(TEST_DATA_CITIES, CITIES_COLUMNS)
    engine = sqlalchemy.create_engine(DB_PG_TEST_URL)
    with pytest.raises(TypeError):
        # if convert_objects is false, we'll get an error, because pdf's dtype for 'city' and 'municipality'
        # is 'object
        DataFrame.from_pandas(
            engine=engine,
            df=pdf,
            convert_objects=False,
            name='test_from_pd_table_convert_objects_false',
            materialization='table',
            if_exists='replace'
        )
    # Create the same table twice. This will fail if if_exists='fail'
    # Might fail on either the first or second try. As we don't clean up between tests.
    with pytest.raises(ValueError, match="Table 'test_from_pd_table' already exists"):
        DataFrame.from_pandas(
            engine=engine,
            df=pdf,
            convert_objects=True,
            name='test_from_pd_table',
            materialization='table',
        )
        DataFrame.from_pandas(
            engine=engine,
            df=pdf,
            convert_objects=True,
            name='test_from_pd_table',
            materialization='table',
        )


@pytest.mark.parametrize("materialization", ['cte', 'table'])
def test_from_pandas_index(materialization: str):
    # test multilevel index
    pdf = get_pandas_df(TEST_DATA_CITIES, CITIES_COLUMNS).set_index(['skating_order', 'city'])
    engine = sqlalchemy.create_engine(DB_PG_TEST_URL)
    bt = DataFrame.from_pandas(
        engine=engine,
        df=pdf,
        convert_objects=True,
        name='test_from_pd_table',
        materialization=materialization,
        if_exists='replace'
    )

    assert_equals_data(
        bt,
        expected_columns=['_index_skating_order',
                          '_index_city',
                          'municipality',
                          'inhabitants',
                          'founding'],
        expected_data=[x[1:] for x in EXPECTED_DATA])

    # test nameless index
    pdf.reset_index(inplace=True)
    engine = sqlalchemy.create_engine(DB_PG_TEST_URL)
    bt = DataFrame.from_pandas(
        engine=engine,
        df=pdf,
        convert_objects=True,
        name='test_from_pd_table',
        materialization=materialization,
        if_exists='replace'
    )

    assert_equals_data(
        bt,
        expected_columns=['_index_0',
                          'skating_order',
                          'city',
                          'municipality',
                          'inhabitants',
                          'founding'],
        expected_data=[[idx] + x[1:] for idx, x in enumerate(EXPECTED_DATA)])


@pytest.mark.parametrize("materialization", ['cte', 'table'])
def test_from_pandas_types(materialization: str):
    pdf = pd.DataFrame.from_records(TYPES_DATA, columns=TYPES_COLUMNS)
    pdf.set_index(pdf.columns[0], drop=True, inplace=True)
    engine = sqlalchemy.create_engine(DB_PG_TEST_URL)
    df = DataFrame.from_pandas(
        engine=engine,
        df=pdf.loc[:, :'string_column'],
        convert_objects=True,
        name='test_from_pd_table',
        materialization=materialization,
        if_exists='replace'
    )

    assert df.index_dtypes == {'_index_int_column': 'int64'}
    assert df.dtypes == {'float_column': 'float64', 'bool_column': 'bool',
                         'datetime_column': 'timestamp', 'string_column': 'string'}

    assert_equals_data(
        df,
        expected_columns=[
            '_index_int_column',
            'float_column',
            'bool_column',
            'datetime_column',
            'string_column'
        ],
        expected_data=[x[:5] for x in TYPES_DATA]
    )

    pdf = pd.DataFrame.from_records(TYPES_DATA, columns=TYPES_COLUMNS)
    pdf.set_index(pdf.columns[0], drop=False, inplace=True)
    pdf['int32_column'] = pdf.int_column.astype(np.int32)
    df = DataFrame.from_pandas(
        engine=engine,
        df=pdf[['int32_column']],
        convert_objects=True,
        name='test_from_pd_table',
        materialization=materialization,
        if_exists='replace'
    )

    assert df.index_dtypes == {'_index_int_column': 'int64'}
    assert df.dtypes == {'int32_column': 'int64'}

    assert_equals_data(
        df,
        expected_columns=[
            '_index_int_column',
            'int32_column'
        ],
        expected_data=[[x[0], x[0]] for x in TYPES_DATA]
    )


def test_from_pandas_types_cte():
    pdf = pd.DataFrame.from_records(TYPES_DATA, columns=TYPES_COLUMNS)
    pdf.set_index(pdf.columns[0], drop=True, inplace=True)
    engine = sqlalchemy.create_engine(DB_PG_TEST_URL)
    df = DataFrame.from_pandas(
        engine=engine,
        df=pdf.loc[:, :'timedelta_column'],
        convert_objects=True,
        materialization='cte'
    )

    assert df.index_dtypes == {'_index_int_column': 'int64'}
    assert df.dtypes == {'float_column': 'float64',
                         'bool_column': 'bool',
                         'datetime_column': 'timestamp',
                         'string_column': 'string',
                         'date_column': 'date',
                         'list_column': 'jsonb',
                         'uuid_column': 'uuid',
                         'dict_column': 'jsonb',
                         'timedelta_column': 'timedelta'}

    assert_equals_data(
        df,
        expected_columns=['_index_int_column',
                          'float_column',
                          'bool_column',
                          'datetime_column',
                          'string_column',
                          'date_column',
                          'list_column',
                          'uuid_column',
                          'dict_column',
                          'timedelta_column'],
        expected_data=[x[:10] for x in TYPES_DATA]
    )

    with pytest.raises(TypeError, match="unsupported dtype for"):
        DataFrame.from_pandas(
            engine=engine,
            df=pdf.loc[:, :'timedelta_column'],
            convert_objects=True,
            name='test_from_pd_table',
            materialization='table',
            if_exists='replace'
        )

    with pytest.raises(TypeError, match="multiple types found in column"):
        DataFrame.from_pandas(
            engine=engine,
            df=pdf.loc[:, :'mixed_column'],
            convert_objects=True,
            materialization='cte'
        )
