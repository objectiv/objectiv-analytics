"""
Copyright 2021 Objectiv B.V.
"""
from sklearn.linear_model import LogisticRegression as LogisticRegression_sk  # type: ignore
from modelhub.metrics import Metrics
from typing import TYPE_CHECKING
from bach.series import SeriesBoolean

if TYPE_CHECKING:
    from bach.dataframe import DataFrame
    from bach.series import SeriesFloat64


class LogisticRegression:
    """
    A binary class logistic regression model that takes Bach data objects as input data.

    It is based on sklearn's LogisticRegression. All supported methods are run on the database using Bach
    directly, with the exeption of :py:meth:`fit`. For the `fit` method,
    data is extracted from the database before applying sklearn's fit method on the data.

    All parameters to instantiate sklearn's logistic regression are supported.

    For the full documentation, including a description of the parameters, of the Logistic Regression
    model see:
    https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
    """
    def __init__(self, *args, **kwargs):
        self._model = LogisticRegression_sk(*args, **kwargs)

    def __getattr__(self, item):
        sklearn_parameters = ['C', 'class_weight', 'dual', 'fit_intercept', 'intercept_scaling', 'l1_ratio',
                              'max_iter', 'multi_class', 'n_jobs', 'penalty', 'random_state', 'solver', 'tol',
                              'verbose', 'warm_start']
        sklearn_attributes = ['classes_', 'coef_', 'intercept_', 'n_features_in_', 'feature_names_in_',
                              'n_iter_']
        if item in sklearn_parameters + sklearn_attributes:
            return getattr(self._model, item)
        raise AttributeError(f"no attribute '{item}'")

    def __repr__(self):
        return self._model.__repr__()

    def _decision_function(self, X: 'DataFrame'):
        if len(X.data_columns) != len(self._model.coef_[0]):
            raise ValueError("incorrect number of columns in X")
        X_copy = X.copy()
        X_copy['confidence_score'] = self._model.intercept_[0]
        for column, coef in zip(X.data_columns, self._model.coef_[0]):
            X_copy['confidence_score'] = X_copy['confidence_score'] + X_copy[column] * coef

        return X_copy['confidence_score']

    def fit(self, X: 'DataFrame', y: 'SeriesBoolean'):
        """
        Fits a binary class logistic regression model.

        .. important::
            This method uses sklearns LogisticRegression.fit, meaning that the data in the database gets
            exported first before fitting the data.

        :param X: DataFrame with features.
        :param y: Series with the target variable.
        """

        if not isinstance(y, SeriesBoolean):
            raise TypeError(f"y is of type {type(y)}, should be SeriesBoolean")

        data = X.copy()
        data[y.name] = y
        pdf = data.to_pandas()
        X_p = pdf[X.data_columns]
        y_p = pdf[y.name]

        return self._model.fit(X_p, y_p)

    def predict(self, X: 'DataFrame') -> SeriesBoolean:
        """
        Predict the labels based on the fitted estimator.

        :param X: DataFrame with the same features as the training data set.
        """
        series = self.predict_proba(X) > .5
        return series.copy_override(name='labels')

    def predict_proba(self, X: 'DataFrame') -> 'SeriesFloat64':
        """
        Predict the probability of the 'True' label based on the fitted estimator.

        :param X: DataFrame with the same features as the training data set.
        """
        confidence_score = self._decision_function(X)
        probability = confidence_score.exp() / (confidence_score.exp() + 1.)
        return probability.copy_override(name='probability')

    def score(self, X: 'DataFrame', y: 'SeriesBoolean') -> float:
        """
        Returns the accuracy score from a series of true values compared to predicted values.

        :param X: DataFrame with the same features as the training data set.
        :param y: Series with the true target variable.
        :returns: a single value with the proportion of correct predicted labels.

        .. note::
            This function queries the database.
        """
        y_pred = self.predict(X)
        return Metrics.accuracy_score(y, y_pred)

    def set_params(self, **params):
        """
        Set parameters for the model. Use :py:meth:`get_params` to see the available parameters that can be
        set.
        """
        self._model.set_params(**params)

    def get_params(self) -> dict:
        """
        Return the parameters as a dictionary.
        """
        return self._model.get_params()
