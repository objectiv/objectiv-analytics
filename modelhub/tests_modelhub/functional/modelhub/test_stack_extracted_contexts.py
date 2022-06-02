"""
Copyright 2022 Objectiv B.V.
"""
import datetime
import json

import bach
import pandas as pd
from sql_models.util import is_bigquery
from tests.functional.bach.test_data_and_utils import assert_equals_data

from modelhub import ExtractedContextsPipeline, get_extracted_contexts_df
from tests_modelhub.data_and_utils.utils import create_engine_from_db_params, get_parsed_objectiv_data

_EXPECTED_CONTEXT_COLUMNS = [
    'event_id',
    'day',
    'moment',
    'user_id',
    'global_contexts',
    'location_stack',
    'event_type',
    'stack_event_types',
]


def _get_parsed_test_data_pandas_df(engine) -> pd.DataFrame:
    parsed_data = get_parsed_objectiv_data(engine)
    if not is_bigquery(engine):
        return pd.DataFrame(parsed_data)

    bq_data = []
    for event in parsed_data:
        taxonomy_data = [
            {
                '_type': event['value']['_type'],
                '_types': json.dumps(event['value']['_types']),
                'global_contexts': json.dumps(event['value']['global_contexts']),
                'location_stack': json.dumps(event['value']['location_stack']),
                'time': event['value']['time'],
                'event_id': str(event['event_id']),
                'cookie_id': str(event['cookie_id']),
            }
        ]
        bq_data.append({'contexts_io_objectiv_taxonomy_1_0_0': taxonomy_data})

    return pd.DataFrame(bq_data)


def get_expected_context_pandas_df(engine) -> pd.DataFrame:
    pdf = pd.DataFrame(get_parsed_objectiv_data(engine))
    context_pdf = pdf['value'].apply(pd.Series)

    context_pdf['event_id'] = pdf['event_id']
    context_pdf['day'] = pdf['day']
    context_pdf['moment'] = pdf['moment']
    context_pdf['user_id'] = pdf['cookie_id']
    context_pdf = context_pdf.rename(
        columns={
            '_type': 'event_type',
            '_types': 'stack_event_types',
        }
    )

    return context_pdf[_EXPECTED_CONTEXT_COLUMNS]


def _get_extracted_contexts_pipeline(db_params) -> ExtractedContextsPipeline:
    engine = create_engine_from_db_params(db_params)
    return ExtractedContextsPipeline(engine=engine, table_name=db_params.table_name)


def test_get_pipeline_result(db_params) -> None:
    context_pipeline = _get_extracted_contexts_pipeline(db_params)
    engine = context_pipeline._engine

    result = context_pipeline().sort_values(by='event_id').to_pandas()
    expected = get_expected_context_pandas_df(engine)
    pd.testing.assert_frame_equal(expected, result)


def test_get_initial_data(db_params) -> None:
    context_pipeline = _get_extracted_contexts_pipeline(db_params)
    engine = context_pipeline._engine
    expected = _get_parsed_test_data_pandas_df(engine)
    result = context_pipeline._get_initial_data()

    if not is_bigquery(engine):
        assert set(result.data_columns) == set(expected.columns)
        sorted_columns = sorted(result.data_columns)
        result = result[sorted_columns].sort_values(by='event_id')
        assert_equals_data(
            result,
            expected_columns=sorted_columns,
            expected_data=expected[sorted_columns].to_numpy().tolist(),
            use_to_pandas=True,
        )
        return

    taxonomy_column = 'contexts_io_objectiv_taxonomy_1_0_0'
    assert taxonomy_column in result.data
    assert isinstance(result[taxonomy_column], bach.SeriesList)

    # need to sort the rows since order is non-deterministic
    result['event_id'] = result[taxonomy_column].elements[0].elements['event_id']
    result = result.sort_values(by='event_id')
    result = result[[taxonomy_column]]

    assert_equals_data(
        result,
        expected_columns=[taxonomy_column],
        expected_data=expected.to_numpy().tolist(),
    )


def test_process_taxonomy_data(db_params) -> None:
    context_pipeline = _get_extracted_contexts_pipeline(db_params)
    engine = context_pipeline._engine

    df = context_pipeline._get_initial_data()
    result = context_pipeline._process_taxonomy_data(df).reset_index(drop=True)

    expected_series = [
        'user_id', 'event_type', 'stack_event_types', 'location_stack', 'global_contexts', 'event_id', 'day', 'moment',
    ]
    if is_bigquery(engine):
        # day and moment are parsed after processing base data
        expected_series = expected_series[:-2]

    for expected_s in expected_series:
        assert expected_s in result.data

    result = result.sort_values(by='event_id')[expected_series]
    expected = get_expected_context_pandas_df(engine)[expected_series]

    pd.testing.assert_frame_equal(
        expected,
        result.to_pandas(),
        check_index_type=False,
    )


def test_apply_extra_processing(db_params) -> None:
    context_pipeline = _get_extracted_contexts_pipeline(db_params)
    engine = context_pipeline._engine

    df = context_pipeline._get_initial_data()
    df = context_pipeline._process_taxonomy_data(df)
    result = context_pipeline._apply_extra_processing(df)

    if not is_bigquery(engine):
        assert df == result
        return None

    assert 'day' not in df.data
    assert 'day' in result.data

    assert 'moment' not in df.data
    assert 'moment' in result.data

    expected_data = get_expected_context_pandas_df(engine)[['day', 'moment']].values.tolist()
    assert_equals_data(
        result.sort_values(by='event_id')[['day', 'moment']],
        expected_columns=['day', 'moment'],
        expected_data=expected_data,
        use_to_pandas=True,
    )


def test_apply_date_filter(db_params) -> None:
    context_pipeline = _get_extracted_contexts_pipeline(db_params)
    engine = context_pipeline._engine

    pdf = get_expected_context_pandas_df(engine)[['event_id', 'day']]
    if is_bigquery(engine):
        pdf['event_id'] = pdf['event_id'].astype(str)

    df = bach.DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    df = df.reset_index(drop=True)

    result = context_pipeline._apply_date_filter(df)
    assert df == result

    start_date = '2021-12-01'
    result = context_pipeline._apply_date_filter(df, start_date=start_date).sort_values(by='event_id')
    start_mask = pdf['day'] >= datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    expected = pdf[start_mask].reset_index(drop=True)

    pd.testing.assert_frame_equal(expected, result.to_pandas(), check_index_type=False)

    end_date = '2021-12-02'
    result = context_pipeline._apply_date_filter(df, end_date=end_date).sort_values(by='event_id')
    end_mask = pdf['day'] <= datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    expected = pdf[end_mask].reset_index(drop=True)

    pd.testing.assert_frame_equal(expected, result.to_pandas(), check_index_type=False)

    result = context_pipeline._apply_date_filter(
        df, start_date=start_date, end_date=end_date,
    ).sort_values(by='event_id')
    expected = pdf[start_mask & end_mask].reset_index(drop=True)

    pd.testing.assert_frame_equal(expected, result.to_pandas(), check_index_type=False)


def test_get_extracted_contexts_df(db_params) -> None:
    engine = create_engine_from_db_params(db_params)

    result = get_extracted_contexts_df(engine=engine, table_name=db_params.table_name)
    result = result.sort_index()
    expected = get_expected_context_pandas_df(engine).set_index('event_id')
    pd.testing.assert_frame_equal(expected, result.to_pandas())

    result = get_extracted_contexts_df(engine=engine, table_name=db_params.table_name, set_index=False)
    assert 'event_id' not in result.index
    assert 'event_id' in result.data

