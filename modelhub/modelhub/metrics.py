"""
Copyright 2021 Objectiv B.V.
"""


class Metrics:
    @staticmethod
    def _cm_prepare(y, y_pred):
        df = y.copy_override(name='y').to_frame()
        df['y_pred'] = y_pred
        return df.value_counts()

    @classmethod
    def accuracy_score(cls,
                       y,
                       y_pred):
        """
        Assumes classes are True and False

        """
        cm = cls._cm_prepare(y, y_pred).to_frame().reset_index()
        return (cm[cm.y == cm.y_pred]['value_counts'].sum() / cm['value_counts'].sum()).value
