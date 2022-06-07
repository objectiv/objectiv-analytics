.. _example_logistic_regression:

.. frontmatterposition:: 1

.. currentmodule:: bach

===================
Logistic Regression
===================

The open model hub supports logistic regression on Bach data objects. A logistic regression model can be fitted, values can be predicted and results can be tested directly on the full data set in the database. Note that for fitting the model data is extracted from the database under the hood.

This example is also available in a `notebook
<https://github.com/objectiv/objectiv-analytics/blob/main/notebooks/modelhub-logistic-regression.ipynb>`_
to run on your own data or use our
`quickstart
<https://objectiv.io/docs/home/quickstart-guide/>`_ to try it out with demo data in 5 minutes.

At first we have to install the open model hub and instantiate the Objectiv DataFrame object. See
:ref:`getting_started_with_objectiv` for more info on this.

Creating a feature set
----------------------
We create a data set that counts the number of clicks per user in each section of our website. We obtain
the main sections by extracting the `root location
<https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext/>`_ from the location
stack. It is similar data set to the one used in the `'Bach and sklearn'
<https://objectiv.io/docs/modeling/example-notebooks/machine-learning/>`_ example. Note that this is a small
and simple data set used just for demonstration purposes of the logistic regression functionality, and not so much the model results itself.

For the ins and outs on feature engineering see our :ref:`feature engineering example
<example_feature_engineering>`.

.. code-block:: python

    # extract the root location from the location stack
    df['root'] = df.location_stack.ls.get_from_context_with_type_series(type='RootLocationContext', key='id')
    # only look at press events and count the root locations
    features = df[(df.event_type=='PressEvent')].groupby('user_id').root.value_counts()
    # unstack the series, to create a DataFrame with the number of clicks per root location as columns
    features_unstacked = features.unstack(fill_value=0)

Sample the data
~~~~~~~~~~~~~~~
We take a 10% sample of the full data that we will use to train the model on. This limits data processing and speeds up the fitting procedure.

After the model is fitted, it can be used to predict the labels for the _entire_ data set.

.. code-block:: python

    features_set_sample = features_unstacked.get_sample('test_lr_sample', sample_percentage=10, overwrite=True, seed=42)

Using a logistic regression we will predict whether a user clicked in the modeling section or not. We will predict this by the number of clicks in any of the other sections. `X` is a Bach DataFrame that contains the explanatory variables. `y` is a Bach SeriesBoolean with the labels we want to predict.

.. code-block:: python

    y_column = 'modeling'
    y = features_set_sample[y_column] > 0
    X = features_set_sample.drop(columns=[y_column])

Instantiating the logistic regression model
-------------------------------------------
We can instantiate the logistic regression model from the model hub. Since the model is based on sklearn's
version of LogisticRegression, it can be instantiated with any parameters that sklearn's LogisticRegression
`supports
<https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html>`_. In our
example we instantiate it with `fit_intercept=False`

.. code-block:: python

    lr = modelhub.get_logistic_regression(fit_intercept=False)

Fitting the model
-----------------
The `fit` method fits a model to the passed data. This method extracts the data from the database under the hood.

.. code-block:: python

    lr.fit(X, y)

Accuracy and predicting
-----------------------
All following operations are carried out directly on the database. Therefore, they can be exported to SQL statements so it can be used in for example your BI tooling.

.. code-block:: python

    lr.score(X, y)

The model has the same attributes as the Logistic Regression model from sklearn.

.. code-block:: python

    # show the coefficients of the fitted model
    lr.coef_

Create columns for the predicted values and labels in the sampled data set. Labels `True` if the probability is over .5.

.. code-block:: python

    features_set_sample['predicted_values'] = lr.predict_proba(X)
    features_set_sample['predicted_labels'] = lr.predict(X)

    # show the sampled data set, including predictions
    features_set_sample.head()

Unsample and view the SQL
-------------------------
The data can be unsampled and viewed as an SQL statement. `features_set_full` and the SQL statement for this DataFrame are for the full unsampled data set including the predicted values.

.. code-block:: python

    features_set_full = features_set_sample.get_unsampled()

Get the sql statement for the _full_ data set including the predicted values.

.. code-block:: python

    print(features_set_full.view_sql())

This demonstrates the core functionality of the Logistic Regression model in the open model hub. Stay tuned for more metrics for assessing the fit of the model, as well as simplifying splitting the data into training and testing data sets.