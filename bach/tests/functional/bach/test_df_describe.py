"""
Copyright 2022 Objectiv B.V.
"""
import datetime

import numpy as np
import pandas as pd

from bach import DataFrame
from sql_models.util import is_bigquery
from tests.functional.bach.test_data_and_utils import (
    get_bt_with_test_data, assert_equals_data, get_df_with_test_data,
)
from unittest.mock import ANY


def test_df_categorical_describe(engine) -> None:
    df = get_df_with_test_data(engine)[['city', 'municipality']]
    result = df.describe()
    assert isinstance(result, DataFrame)
    assert_equals_data(
        result,
        expected_columns=[
            '__stat',
            'city',
            'municipality',
        ],
        expected_data=[
            ['count', '3', '3'],
            ['min', 'Drylts', 'Leeuwarden'],
            ['max', 'Snits', 'Súdwest-Fryslân'],
            ['nunique', '3', '2'],
            ['mode', ANY, 'Súdwest-Fryslân'],
        ],
    )


def test_df_numerical_describe(engine) -> None:
    df = get_df_with_test_data(engine)[['city', 'skating_order', 'inhabitants']]
    result = df.describe(percentiles=[0.5])
    assert isinstance(result, DataFrame)

    result = result.reset_index(drop=False).materialize()
    # mode for PG and BQ yield different results, because we cannot change sorting for APPROX_TOP_COUNT
    # have to exclude mode form
    result = result[result['__stat'] != 'mode']

    expected_df = pd.DataFrame(
        data=[
            ['count', 3., 3.],
            ['mean', 2., 43353.333],
            ['std', 1., 46009.9666],
            ['min', 1., 3055.],
            ['max', 3., 93485.],
            ['nunique', 3., 3.],
            ['0.5', 2., 33520.],
        ],
        columns=[
            '__stat',
            'skating_order',
            'inhabitants',
        ],
    )
    numerical_columns = expected_df.columns[1:]
    expected_df[numerical_columns] = expected_df[numerical_columns].round(2)

    np.testing.assert_equal(expected_df.to_numpy(), result.to_numpy())

    df2 = df.copy_override()
    df2['inhabitants'] = df['inhabitants'].astype('float64')

    result2 = df2.describe(include=['int64'], exclude=['float64'], percentiles=[0.5])
    result2 = result2.reset_index(drop=False).materialize()
    result2 = result2[result2['__stat'] != 'mode']

    np.testing.assert_equal(
        expected_df[['__stat', 'skating_order']].to_numpy(),
        result2.to_numpy(),
    )


def test_include_mixed() -> None:
    df = get_bt_with_test_data()
    df['inhabitants'] = df['inhabitants'].astype('float64')
    df['timedelta'] = datetime.timedelta(days=1)
    include_dtypes = ['string', 'float64', 'int64', 'timedelta']
    result = df.describe(include=include_dtypes)
    result = result.reset_index(drop=False)

    expected_df = pd.DataFrame(
        data=[
            ['count', 3., '3', '3', 3., 3., '3'],
            ['mean', 2., None, None, 43353.33, 1336.33, '1 day'],
            ['std', 1., None, None, 46009.97, 103.98, None],
            ['min', 1., 'Drylts', 'Leeuwarden', 3055., 1268., '1 day'],
            ['max', 3., 'Snits', 'Súdwest-Fryslân', 93485., 1456., '1 day'],
            ['nunique', 3., '3', '2', 3., 3., '1'],
            ['mode', 1., 'Drylts', 'Súdwest-Fryslân', 3055., 1268., '1 day'],
            ['0.25', 1.5, None, None, 18287.5, 1276.5, '1 day'],
            ['0.5', 2., None, None, 33520.,  1285., '1 day'],
            ['0.75', 2.5, None, None, 63502.5, 1370.5, '1 day'],
        ],
        columns=[
            '__stat', 'skating_order', 'city', 'municipality', 'inhabitants', 'founding', 'timedelta'
        ],
    )

    pd.testing.assert_frame_equal(result.to_pandas(), expected_df)


def test_describe_datetime(engine) -> None:
    pdf = pd.DataFrame(
        data=[
            [np.datetime64("2000-01-01")], [np.datetime64("2010-01-01")], [np.datetime64("2010-01-01")],
        ],
        columns=['column'],
    )
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)

    result = df.describe()
    result = result.reset_index(drop=False)
    tz = '+00' if is_bigquery(engine) else ''
    expected_df = pd.DataFrame(
        data=[
            ['count', '3'],
            ['min', f'2000-01-01 00:00:00{tz}'],
            ['max', f'2010-01-01 00:00:00{tz}'],
            ['nunique', '2'],
            ['mode', f'2010-01-01 00:00:00{tz}'],
        ],
        columns=['__stat', 'column'],
    )
    pd.testing.assert_frame_equal(expected_df, result.to_pandas())


def test_describe_date(engine) -> None:
    pdf = pd.DataFrame(
        data=[
            [np.datetime64("2000-01-01")], [np.datetime64("2010-01-01")], [np.datetime64("2010-01-01")],
        ],
        columns=['column'],
    )
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    df['column'] = df['column'].astype('date')

    result = df.describe()
    result = result.reset_index(drop=False)

    expected_df = pd.DataFrame(
        data=[
            ['count', '3'],
            ['min', '2000-01-01'],
            ['max', '2010-01-01'],
            ['nunique', '2'],
            ['mode', '2010-01-01'],
        ],
        columns=['__stat', 'column'],
    )
    pd.testing.assert_frame_equal(expected_df, result.to_pandas())


def test_describe_time(engine) -> None:
    pdf = pd.DataFrame(
        data=[
            ["11:00:01"], ["11:00:01"], ["13:37:00"],
        ],
        columns=['column'],
    )
    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    df['column'] = df['column'].astype('time')

    result = df.describe()
    result = result.reset_index(drop=False)

    expected_df = pd.DataFrame(
        data=[
            ['count', '3'],
            ['min', '11:00:01'],
            ['max', '13:37:00'],
            ['nunique', '2'],
            ['mode', '11:00:01'],
        ],
        columns=['__stat', 'column'],
    )
    pd.testing.assert_frame_equal(expected_df, result.to_pandas())


def test_describe_boolean(pg_engine) -> None:
    pdf = pd.DataFrame(
        data=[
            [True], [False], [True],
        ],
        columns=['column'],
    )
    df = DataFrame.from_pandas(engine=pg_engine, df=pdf, convert_objects=True)

    result = df.describe()
    result = result.reset_index(drop=False)

    expected_df = pd.DataFrame(
        data=[
            ['count', '3'],
            ['min', 'false'],
            ['max', 'true'],
            ['nunique', '2'],
            ['mode', 'true'],
        ],
        columns=['__stat', 'column'],
    )
    pd.testing.assert_frame_equal(expected_df, result.to_pandas())


def test_describe_json(pg_engine) -> None:
    pdf = pd.DataFrame(
        data=[
            ['"a string"'],
            ['"other string"'],
            ['{"key": "value", "another key": "value"}'],
            ['"a string"'],
        ],
        columns=['column'],
    )
    df = DataFrame.from_pandas(engine=pg_engine, df=pdf, convert_objects=True)
    df['column'] = df['column'].astype('json')

    result = df.describe()
    result = result.reset_index(drop=False)

    expected_df = pd.DataFrame(
        data=[
            ['count', '4'],
            ['nunique', '3'],
            ['mode', '"a string"'],
        ],
        columns=['__stat', 'column'],
    )
    pd.testing.assert_frame_equal(expected_df, result.to_pandas())


def test_describe_uuid(pg_engine) -> None:
    pdf = pd.DataFrame(
        data=[
            ['0022c7dd-074b-4a44-a7cb-b7716b668264'],
            ['0022c7dd-074b-4a44-a7cb-b7716b668265'],
            ['0022c7dd-074b-4a44-a7cb-b7716b668266'],
        ],
        columns=['column'],
    )
    df = DataFrame.from_pandas(engine=pg_engine, df=pdf, convert_objects=True)
    df['column'] = df['column'].astype('uuid')
    result = df.describe()
    result = result.reset_index(drop=False)

    expected_df = pd.DataFrame(
        data=[
            ['count', '3'],
            ['nunique', '3'],
            ['mode', '0022c7dd-074b-4a44-a7cb-b7716b668264'],
        ],
        columns=['__stat', 'column'],
    )
    pd.testing.assert_frame_equal(expected_df, result.to_pandas())
