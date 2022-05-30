"""
Copyright 2021 Objectiv B.V.
"""
from typing import TYPE_CHECKING
from bach.series import SeriesInt64

if TYPE_CHECKING:
    from bach.series import SeriesBoolean, Series


class Metrics:
    @staticmethod
    def _cm_prepare(y: 'SeriesBoolean', y_pred: 'SeriesBoolean') -> 'Series':
        df = y.copy_override(name='y').to_frame()
        df['y_pred'] = y_pred
        return df.value_counts()

    @classmethod
    def accuracy_score(cls, y: 'SeriesBoolean', y_pred: 'SeriesBoolean') -> float:
        """
        Returns the accuracy score from a series of true values compared to predicted values.

        :param y: Series with the true target variable.
        :param y_pred: Series with the predicted target variable.
        :returns: a single value with the proportion of correct predicted labels.

        .. note::
            This function queries the database.
        """
        cm = cls._cm_prepare(y, y_pred).to_frame().reset_index()

        if not isinstance(cm['value_counts'], SeriesInt64):
            raise TypeError(f"cm is of type {type(y)}, should be SeriesInt64")

        return (cm[cm.y == cm.y_pred]['value_counts'].sum() / cm['value_counts'].sum()).value
