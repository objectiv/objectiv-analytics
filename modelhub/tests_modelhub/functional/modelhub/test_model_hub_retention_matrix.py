"""
Copyright 2022 Objectiv B.V.
"""


# Any import from modelhub initializes all the types, do not remove
from modelhub import __version__
import pytest
from tests_modelhub.data_and_utils.utils import get_objectiv_dataframe_test
from tests.functional.bach.test_data_and_utils import assert_equals_data


def test_retention_rate():

    df, modelhub = get_objectiv_dataframe_test()
    event_type = 'ClickEvent'

    # yearly
    data = modelhub.map.retention_matrix(df,
                                         time_period='yearly',
                                         event_type=event_type,
                                         percentage=False,
                                         display=False)

    assert_equals_data(
        data,
        expected_columns=['first_cohort', '0'],
        expected_data=[
            ['2021', 4],
        ],
        use_to_pandas=True,
    )

    # monthly
    data = modelhub.map.retention_matrix(df,
                                         time_period='monthly',
                                         event_type=event_type,
                                         percentage=False,
                                         display=False)

    # filling nan values with -999 in order to be able to do the check
    # (nan values are causing a trouble)
    data = data.fillna(value=-999)
    assert_equals_data(
        data,
        expected_columns=['first_cohort', '0', '1'],
        expected_data=[
            ['2021-11', 2, 1],
            ['2021-12', 2, -999],
        ],
        use_to_pandas=True,
    )

    # daily
    data = modelhub.map.retention_matrix(df,
                                         time_period='daily',
                                         event_type=event_type,
                                         percentage=False,
                                         display=False)

    data = data.fillna(value=-999)
    assert_equals_data(
        data,
        expected_columns=['first_cohort', '0', '1'],
        expected_data=[
            ['2021-11-29', 1, 1],
            ['2021-11-30', 1, 1],
            ['2021-12-02', 1, -999],
            ['2021-12-03', 1, -999],
        ],
        use_to_pandas=True,
    )

    # not supported time_period
    with pytest.raises(ValueError, match='weekly time_period is not available.'):
        modelhub.map.retention_matrix(df,
                                      event_type=event_type,
                                      time_period='weekly',
                                      display=False)

    # non-existing event type
    data = modelhub.map.retention_matrix(df,
                                         event_type='some_event',
                                         display=False)

    assert list(data.index.keys()) == ['first_cohort']
    assert data.columns == []

    # percentage
    data = modelhub.map.retention_matrix(df,
                                         time_period='monthly',
                                         event_type=event_type,
                                         percentage=True,
                                         display=False)

    data = data.fillna(value=-999.0)
    assert_equals_data(
        data,
        expected_columns=['first_cohort', '0', '1'],
        expected_data=[
            ['2021-11', 1.0, 0.5],
            ['2021-12', 1.0, -999.0],
        ],
        use_to_pandas=True,
    )
