"""
Copyright 2021 Objectiv B.V.
"""

# Any import from modelhub initializes all the types, do not remove



from typing import Iterable
import bach
from sklearn.linear_model import LogisticRegression
from modelhub import ModelHub
import numpy as np


class TestLR:
    """
    Tests if model used on Bach gives the same outcome as model used on sklearn.
    Note that it only works for solvers that provide consistent outcomes.
    """

    def __init__(self, X: bach.DataFrame, y: bach.Series, **kwargs):
        """
        :param X: the independent variables.
        :param y: the target variable.
        :param **kwargs: any parameters that sklearn's LogisticRegression takes for instantiating the model.
            These parameters are used also for the model hub version of Logistic Regression.
        """

        self.X = X
        self.y = y

        data = X.copy()
        data[y.name] = y
        pdf = data.to_pandas()

        self.X_p = pdf[X.data_columns]
        self.y_p = pdf[y.name]

        modelhub = ModelHub()

        self.sklearn_lr = LogisticRegression(**kwargs)
        self.modelhub_lr = modelhub.get_logistic_regression(**kwargs)

        self.sklearn_lr.fit(self.X_p, self.y_p)
        self.modelhub_lr.fit(self.X, self.y)

    def test_fitted_model(self):
        for key, value in self.sklearn_lr.__dict__.items():
            modelhub_value = getattr(self.modelhub_lr, key)
            print(f'testing {key}')
            print(f'modelhub value: {modelhub_value}\nsklearn value : {value}\n')
            result = modelhub_value == value
            if isinstance(result, Iterable):
                result = result.all()
            assert result

    def test_method(self, method_name, X=False, y=False, **kwargs):
        """
        tests if modelhub outcome of method is the same as sklearn.
        """

        if method_name not in ['decision_function',
                               'predict',
                               'predict_proba',
                               'score']:
            raise NotImplementedError(f"method {method_name} not supported")

        sklearn_args = tuple()
        modelhub_args = tuple()

        if X:
            # need sorting for the comparison
            sklearn_args = (self.X_p.sort_index(),)
            modelhub_args = (self.X.sort_index(),)
            if y:
                # for now, we only calculate score, sorting is not needed
                sklearn_args = (self.X_p, self.y_p)
                modelhub_args = (self.X, self.y)

        sklearn_method = getattr(self.sklearn_lr, method_name)
        modelhub_method = getattr(self.modelhub_lr, method_name)
        sklearn_data = sklearn_method(*sklearn_args, **kwargs)
        modelhub_data = modelhub_method(*modelhub_args, **kwargs)

        if method_name == 'predict_proba':
            # extract the probabilities from sklearn's predicted probabilities for the True class only:
            sklearn_data = sklearn_data[:, np.where(self.sklearn_lr.classes_)[0][0]]

        if method_name == 'score':
            equals = np.isclose(sklearn_data, modelhub_data)
        else:
            modelhub_data = modelhub_data.sort_index().to_numpy()
            equals = np.isclose(sklearn_data, modelhub_data).all()

        assert equals, f"modelhub_data: {modelhub_data} != sklearn_data: {sklearn_data}"

        print(f"test ok")
        print(f'modelhub value: {modelhub_data}\nsklearn value : {sklearn_data}\n')

