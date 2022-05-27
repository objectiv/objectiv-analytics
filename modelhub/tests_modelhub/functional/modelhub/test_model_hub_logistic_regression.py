"""
Copyright 2021 Objectiv B.V.
"""

# Any import from modelhub initializes all the types, do not remove


import pytest
from tests.functional.bach.test_data_and_utils import get_df_with_test_data
from tests_modelhub.functional.modelhub.logistic_regression_test_utils import TestLR


def test_fitted_model(engine):
    bt = get_df_with_test_data(engine=engine, full_data_set=True)
    bt['target'] = bt.municipality == 'Súdwest-Fryslân'

    test_lr = TestLR(X=bt[['skating_order', 'inhabitants', 'founding']],
                     y=bt['target'])

    test_lr.test_fitted_model()


@pytest.mark.parametrize("method_name,X,y", [
    ('decision_function', True, False),
    ('predict', True, False),
    ('predict_proba', True, False),
    ('score', True, True),
])
def test_model_methods(engine, method_name, X, y):
    bt = get_df_with_test_data(engine=engine, full_data_set=True)
    bt['target'] = bt.municipality == 'Súdwest-Fryslân'

    test_lr = TestLR(X=bt[['skating_order', 'inhabitants', 'founding']],
                     y=bt['target'])

    test_lr.test_method(method_name=method_name,
                        X=X,
                        y=y)
