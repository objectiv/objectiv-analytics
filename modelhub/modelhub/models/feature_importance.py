"""
Copyright 2021 Objectiv B.V.
"""
import bach
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, auc  # type: ignore
from modelhub.metrics import Metrics
from modelhub.models import LogisticRegression


class FeatureImportance:
    def __init__(self):
        self._result_dict = {}

    def get_full_results(self):
        return self._result_dict

    def _set_seed(self, data: bach.DataFrame, seed: float):
        if not -1 <= seed <= 1:
            raise ValueError("seed should be between -1 and 1")

        from sql_models.model import SqlModelBuilder

        class SetSeed(SqlModelBuilder):
            @property
            def sql(self):
                _SQL = \
                    f'''
                    with old_base_node{{{{id}}}} as (SELECT * FROM {{{{base_node}}}})

                    SELECT *
                    FROM old_base_node{{{{id}}}}, (select setseed({seed})) as _seed
                    '''
                return _SQL

        seed_model = SetSeed()
        new_base_node_model = seed_model.build(base_node=data.base_node)

        new_base_node = bach.sql_model.BachSqlModel.from_sql_model(
            sql_model=new_base_node_model,
            column_expressions=data.base_node.column_expressions,
        )

        df_with_seed = data.copy_override_base_node(base_node=new_base_node)
        return df_with_seed

    def _split_data_set_stratified(self, X, y, folds, seed):

        data_set = X.copy()
        # todo test y.name not in data X (should not be anyway)
        data_set[y.name] = y

        data_set = data_set.sort_index().materialize()
        data_set = self._set_seed(data_set, seed)
        data_set['_ordering'] = 0.1
        data_set['_ordering'] = data_set['_ordering'].get_random_number()

        from bach.partitioning import WindowFrameBoundary, WindowFrameMode
        window = data_set.sort_values('_ordering').groupby(y.name).window(
            mode=WindowFrameMode.ROWS,
            start_boundary=WindowFrameBoundary.PRECEDING,
            start_value=None,
            end_boundary=WindowFrameBoundary.FOLLOWING,
            end_value=None)
        data_set['_part'] = window[X.data_columns[0]].window_ntile(folds)
        data_set = data_set.materialize()

        return data_set

    def _get_stratified_folds(self, X, y, folds, seed):
        data = self._split_data_set_stratified(X=X, y=y, folds=folds, seed=seed)
        for fold in range(folds):
            train = data[data['_part'] != fold + 1]
            test = data[data['_part'] == fold + 1]
            X_train = train[X.data_columns]
            X_test = test[X.data_columns]
            y_train = train[y.name]
            y_test = test[y.name]

            yield X_train, X_test, y_train, y_test

    def fit(self, X, y, folds=3, seed=None, print_report=False, **kwargs):
        if seed is None:
            seed = np.random.random()
        self._results_dict = {}

        coef = pd.DataFrame(columns=X.data_columns)
        i = 1

        for X_train, X_test, y_train, y_test in self._get_stratified_folds(X, y, folds=folds,
                                                                           seed=seed):
            report = f"fold {i}\n"
            report += "==============================\n"

            lr = LogisticRegression(**kwargs)
            lr.fit(X_train, y_train)

            report += f"score: {lr.score(X_test, y_test)}\n"

            cr = Metrics.get_classification_report(y_test,
                                                   lr.predict(X_test),
                                                   output_dict=True)

            x_results = X_test.copy()
            x_results['is_converted'] = y_test
            x_results['yhat'] = lr.predict(X_test)

            proba = lr.predict_proba(X_test).to_pandas()
            fpr, tpr, thresholds = roc_curve(y_test.to_pandas(), proba)

            report += f"\npredicted converted correct:" \
                      f"{x_results[(x_results['yhat']) & (x_results['is_converted'])].yhat.count().value}\n"""
            report += f"recall: {cr['True']['recall']}\n"
            report += f"precision: {cr['True']['precision']}\n"
            report += f"roc auc: {auc(fpr, tpr)}\n"

            coef_fold = pd.DataFrame(lr.coef_, columns=X.data_columns)

            coef = pd.concat([coef, coef_fold])

            self._result_dict[f'fold {i}'] = {'classification_report': cr,
                                              'auc': auc(fpr, tpr),
                                              'coef': coef_fold,
                                              'fitted_model': lr}

            i += 1
            report += "==============================\n\n"
            if print_report:
                print(report)
        self._result_dict['coef'] = coef

        feature = pd.DataFrame([coef.mean(), coef.std()], index=['mean', 'std']).T.sort_values(
            'mean')

        self._results_dict['seed'] = seed
        self._result_dict['feature_importance'] = feature
        self._result_dict['auc_mean'] = np.mean([y['auc'] for x, y in self._result_dict.items() if x[:4] ==
                                                 'fold'])

    def auc(self):
        return self._result_dict['auc_mean']

    def results(self, full=False):
        if full:
            return self._result_dict['coef']
        return self._result_dict['feature_importance']
