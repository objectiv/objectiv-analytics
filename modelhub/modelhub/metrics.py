"""
Copyright 2021 Objectiv B.V.
"""
# todo: assumes classes are True and False


class Metrics:
    @staticmethod
    def _cm_prepare(y, y_pred):
        df = y.copy_override(name='y').to_frame()
        df['y_pred'] = y_pred
        return df.value_counts()

    @classmethod
    def get_confusion_matrix(cls, y, y_pred):
        confusion_matrix = cls._cm_prepare(y, y_pred)
        return confusion_matrix.to_pandas().unstack()

    @classmethod
    def _precision_recall(cls,
                          y,
                          y_pred,
                          return_class_true: bool = True,
                          return_precision=True):
        """
        :param return_class_true: get precision for the 'True' class.
        """
        confusion_matrix = cls.get_confusion_matrix(y, y_pred)
        precision = confusion_matrix / confusion_matrix.sum()
        recall = confusion_matrix / confusion_matrix.sum(axis=1)

        return_data = recall
        if return_precision:
            return_data = precision

        if return_class_true in return_data.columns:
            return return_data.loc[return_class_true, return_class_true]

    @classmethod
    def get_precision(cls, y, y_pred, return_class_true: bool = True):
        return cls._precision_recall(y, y_pred, return_class_true=return_class_true, return_precision=True)

    @classmethod
    def get_recall(cls, y, y_pred, return_class_true: bool = True):
        return cls._precision_recall(y, y_pred, return_class_true=return_class_true, return_precision=False)

    @staticmethod
    def get_f1_score(precision, recall):
        return 2 * (precision * recall) / (precision + recall)

    @classmethod
    def accuracy_score(cls,
                       y,
                       y_pred):
        """
        Assumes classes are True and False

        """
        cm = cls._cm_prepare(y, y_pred).to_frame().reset_index()
        return (cm[cm.y == cm.y_pred]['value_counts'].sum() / cm['value_counts'].sum()).value

    @classmethod
    def get_classification_report(cls, y, y_pred, output_dict: bool = False):
        report = '              precision    recall  f1-score\n\n'
        report_dict = {}
        for return_class_true in [False, True]:
            precision = cls.get_precision(y, y_pred, return_class_true=return_class_true)

            recall = cls.get_recall(y, y_pred, return_class_true=return_class_true)
            f1 = cls.get_f1_score(precision, recall)
            report_dict[str(return_class_true)] = {'precision': precision, 'recall': recall, 'f1': f1}
            report += f"{return_class_true}: {precision}  {recall}  {f1} \n"

        macro_avg_f1 = (report_dict['False']['f1'] + report_dict['True']['f1']) / 2
        report_dict['macro_avg'] = {'f1': macro_avg_f1}
        report += f"\nmacro avg:                           {macro_avg_f1} \n"

        # weighted_avg_f1 = (report_dict[False]['f1'] * len(y[y == 0]) + report_dict[True]['f1'] * len(
        #     y[y == 1])) / len(y)
        # report_dict['weighted_avg'] = {'f1': weighted_avg_f1}
        # report += f"weighted avg:                           {weighted_avg_f1} \n"

        if output_dict:
            return report_dict
        return report
