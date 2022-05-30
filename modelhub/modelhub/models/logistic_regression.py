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


class LogisticRegression(LogisticRegression_sk):
    def _decision_function(self, X):
        if len(X.data_columns) != len(self.coef_[0]):
            raise ValueError("incorrect number of columns in X")
        X_copy = X.copy()
        X_copy['confidence_score'] = self.intercept_[0]
        for column, coef in zip(X.data_columns, self.coef_[0]):
            X_copy['confidence_score'] = X_copy['confidence_score'] + X_copy[column] * coef

        return X_copy['confidence_score']

    def fit(self, X: 'DataFrame', y: 'SeriesBoolean'):
        """
        Fits a binary class logistic regression model. This method uses sklearns LogisticRegression.fit,
        meaning that the data in the database gets exported first before fitting the data.

        :param X: DataFrame with features.
        :param y: Series with the target variable.
        """

        if not isinstance(y, SeriesBoolean):
            raise TypeError(f"y is of type {type(y)}, should be SeriesBoolean")

        X_p = X.to_pandas()
        y_p = y.to_pandas()

        return super().fit(X_p, y_p)

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

    def predict_log_proba(self, X):
        """
        INTERNAL: Not implemented
        """
        raise NotImplementedError

    def densify(self):
        """
        INTERNAL: Not implemented
        """
        raise NotImplementedError

    def sparsify(self):
        """
        INTERNAL: Not implemented
        """
        raise NotImplementedError
