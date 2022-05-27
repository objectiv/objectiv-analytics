"""
Copyright 2021 Objectiv B.V.
"""
from sklearn.linear_model import LogisticRegression as LogisticRegression_sk  # type: ignore
from modelhub.metrics import Metrics


class LogisticRegression(LogisticRegression_sk):
    def decision_function(self, X):
        if len(X.data_columns) != len(self.coef_[0]):
            raise ValueError("incorrect number of columns in X")
        X_copy = X.copy()
        X_copy['confidence_score'] = self.intercept_[0]
        for column, coef in zip(X.data_columns, self.coef_[0]):
            X_copy['confidence_score'] = X_copy['confidence_score'] + X_copy[column] * coef
        return X_copy['confidence_score']

    def fit(self, X, y, *args, **kwargs):
        X_p = X.to_pandas()
        y_p = y.to_pandas()
        return super().fit(X_p, y_p, *args, **kwargs)

    def predict(self, X):
        series = self.predict_proba(X) > .5
        return series.copy_override(name='labels')

    def predict_proba(self, X):
        confidence_score = self.decision_function(X)
        probability = confidence_score.exp() / (confidence_score.exp() + 1.)
        return probability.copy_override(name='probability')

    def score(self, X, y):
        y_pred = self.predict(X)
        return Metrics.accuracy_score(y, y_pred)

    def predict_log_proba(self, X):
        raise NotImplementedError

    def densify(self):
        raise NotImplementedError

    def sparsify(self):
        raise NotImplementedError
