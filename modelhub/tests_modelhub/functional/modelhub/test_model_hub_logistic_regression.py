"""
Copyright 2021 Objectiv B.V.
"""

# Any import from modelhub initializes all the types, do not remove


import pytest
from tests_modelhub.data_and_utils.utils import get_objectiv_dataframe_test
from tests_modelhub.functional.modelhub.logistic_regression_test_utils import TestLR


def test_fitted_model(db_params):
    bt, modelhub = get_objectiv_dataframe_test(db_params)
    bt['ts'] = bt['moment'].dt.strftime('%m%d%H%m').astype(dtype=int)
    bt['session'] = bt['session_hit_number'] * 100
    bt['target'] = bt.session_hit_number > 1

    test_lr = TestLR(X=bt[['ts', 'session_hit_number']],
                     y=bt['target'])

    test_lr.test_fitted_model()


@pytest.mark.parametrize("method_name,X,y", [
    ('predict', True, False),
    ('predict_proba', True, False),
    ('score', True, True),
])
def test_model_methods(db_params, method_name, X, y):
    bt, modelhub = get_objectiv_dataframe_test(db_params)
    bt['ts'] = bt['moment'].dt.strftime('%m%d%H%m').astype(dtype=int)
    bt['session'] = bt['session_hit_number'] * 100
    bt['target'] = bt.session_hit_number > 1

    test_lr = TestLR(X=bt[['ts', 'session_hit_number', 'session']],
                     y=bt['target'])

    test_lr.test_method(method_name=method_name, X=X, y=y)
