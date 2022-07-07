"""
Copyright 2022 Objectiv B.V.
"""


# Any import from modelhub initializes all the types, do not remove
from modelhub import __version__
import pytest
from tests_modelhub.data_and_utils.utils import get_objectiv_dataframe_test
from tests.functional.bach.test_data_and_utils import assert_equals_data


def test_retention_matrix(db_params):

    df, modelhub = get_objectiv_dataframe_test(db_params)
    event_type = 'ClickEvent'

    # yearly
    data = modelhub.aggregate.retention_matrix(df,
                                               time_period='yearly',
                                               event_type=event_type,
                                               percentage=False,
                                               display=False)

    assert_equals_data(
        data,
        expected_columns=['first_cohort', '_0'],
        expected_data=[
            ['2021', 4],
        ],
        use_to_pandas=True,
    )

    # monthly
    data = modelhub.aggregate.retention_matrix(df,
                                               time_period='monthly',
                                               event_type=event_type,
                                               percentage=False,
                                               display=False)

    # filling nan values with -999 in order to be able to do the check
    # (nan values are causing a trouble)
    data = data.fillna(value=-999)
    assert_equals_data(
        data,
        expected_columns=['first_cohort', '_0', '_1'],
        expected_data=[
            ['2021-11', 2, 1],
            ['2021-12', 2, -999],
        ],
        use_to_pandas=True,
    )

    # weekly
    data = modelhub.aggregate.retention_matrix(df,
                                               time_period='weekly',
                                               event_type=event_type,
                                               percentage=False,
                                               display=False)
    assert_equals_data(
        data,
        expected_columns=['first_cohort', '_0'],
        expected_data=[
            ['2021-11-29', 4],
        ],
        use_to_pandas=True,
    )

    # daily
    data = modelhub.aggregate.retention_matrix(df,
                                               time_period='daily',
                                               event_type=event_type,
                                               percentage=False,
                                               display=False)

    data = data.fillna(value=-999)
    assert_equals_data(
        data,
        expected_columns=['first_cohort', '_0', '_1'],
        expected_data=[
            ['2021-11-29', 1, 1],
            ['2021-11-30', 1, 1],
            ['2021-12-02', 1, -999],
            ['2021-12-03', 1, -999],
        ],
        use_to_pandas=True,
    )

    # not supported time_period
    with pytest.raises(ValueError, match='biweekly time_period is not available.'):
        modelhub.aggregate.retention_matrix(df,
                                            event_type=event_type,
                                            time_period='biweekly',
                                            display=False)

    # non-existing event type
    data = modelhub.aggregate.retention_matrix(df,
                                               event_type='some_event',
                                               display=False)

    assert list(data.index.keys()) == ['first_cohort']
    assert data.columns == []

    # all events
    data = modelhub.aggregate.retention_matrix(df,
                                               time_period='yearly',
                                               event_type=None,
                                               percentage=False,
                                               display=False)

    assert_equals_data(
        data,
        expected_columns=['first_cohort', '_0'],
        expected_data=[
            ['2021', 4],
        ],
        use_to_pandas=True,
    )

    # percentage
    data = modelhub.aggregate.retention_matrix(df,
                                              time_period='monthly',
                                              event_type=event_type,
                                              percentage=True,
                                              display=False)

    data = data.fillna(value=-999.0)
    assert_equals_data(
        data,
        expected_columns=['first_cohort', '_0', '_1'],
        expected_data=[
            ['2021-11', 100.0, 50.0],
            ['2021-12', 100.0, -999.0],
        ],
        use_to_pandas=True,
    )

    # start_date
    data = modelhub.aggregate.retention_matrix(df,
                                               time_period='daily',
                                               event_type=event_type,
                                               start_date='2021-11-30',
                                               percentage=False,
                                               display=False)

    data = data.fillna(value=-999)
    assert_equals_data(
        data,
        expected_columns=['first_cohort', '_0', '_1'],
        expected_data=[
            ['2021-11-30', 1, 1],
            ['2021-12-02', 1, -999],
            ['2021-12-03', 1, -999],
        ],
        use_to_pandas=True,
    )

    # end_date
    data = modelhub.aggregate.retention_matrix(df,
                                               time_period='daily',
                                               event_type=event_type,
                                               end_date='2021-12-02',
                                               percentage=False,
                                               display=False)

    assert_equals_data(
        data,
        expected_columns=['first_cohort', '_0', '_1'],
        expected_data=[
            ['2021-11-29', 1, 1],
            ['2021-11-30', 1, 1],
        ],
        use_to_pandas=True,
    )

    # start_date and end_date
    data = modelhub.aggregate.retention_matrix(df,
                                               time_period='daily',
                                               event_type=event_type,
                                               start_date='2021-11-30',
                                               end_date='2021-12-02',
                                               percentage=False,
                                               display=False)

    assert_equals_data(
        data,
        expected_columns=['first_cohort', '_0', '_1'],
        expected_data=[
            ['2021-11-30', 1, 1],
        ],
        use_to_pandas=True,
    )

    # wrong start_date
    with pytest.raises(ValueError, match="time data '2021-11' does not match format '%Y-%m-%d"):
        modelhub.aggregate.retention_matrix(df,
                                            time_period='daily',
                                            event_type=event_type,
                                            start_date='2021-11',
                                            percentage=False,
                                            display=False)

    # wrong end_date
    with pytest.raises(ValueError, match="time data '2021-11' does not match format '%Y-%m-%d"):
        modelhub.aggregate.retention_matrix(df,
                                            time_period='daily',
                                            event_type=event_type,
                                            end_date='2021-11',
                                            percentage=False,
                                            display=False)
