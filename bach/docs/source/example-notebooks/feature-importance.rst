.. _feature_importance:

.. frontmatterposition:: 7

.. currentmodule:: bach

===========================
Modeling feature importance
===========================

In this example we will demo how the model hub provides a toolkit for modeling the importance of features
on achieving a conversion goal. The features in this model can be any interactions with your product's
content.

This model is currently in development. The draft pr is found `here
<https://github.com/objectiv/objectiv-analytics/pull/662/>`_. This example page is based on the data that
comes with our quickstart. To already try it out you have to use the model hub version in that branch. It
is easiest to set up a development environment as detailed in the `readme
<https://github.com/objectiv/objectiv-analytics/tree/main/modelhub#setup-development-environment>`_.

First we have to install the open model hub and instantiate the Objectiv DataFrame object; see
:doc:`getting started in your notebook <../get-started-in-your-notebook>`.

The feature importance model from the open model hub creates a Bach data set that can be used for the model
as well as the model that returns the results. The model includes tools to assess the accuracy of your
model as well.

First we have to define the conversion goal that we are predicting as well as the features that we want to
use as predictors.

.. code-block:: python

    # define which events to use as conversion events
    modelhub.add_conversion_event(location_stack=df.location_stack.json[{'id': 'modeling', '_type': 'RootLocationContext'}:],
                                  event_type='PressEvent',
                                  name='use_modeling')
    # the features that we use for predicting
    df['root'] = df.location_stack.ls.get_from_context_with_type_series(type='RootLocationContext', key='id')

In our example, the conversion goal is reaching the modeling section. We want to obtain the impact of
pressing in individual sections (root location) on our website. For demonstration purposes these
are appropriate features because of the limited amount of root locations in this data set. We assume there
is as causal relation between the number of clicks of a user per root location and conversion.
Make sure to think of this assumption when using this model on your own data.

We estimate conversion by the number of presses in each root location on our site per user using a logistic
regression model. The coefficients of this regression can be interpreted as the contribution to conversion
(direction and magnitude).

Now the data set and untrained model can be instantiated.

.. code-block:: python

    X_temp, y_temp, model = modelhub.agg.feature_importance(
        data=df[df.event_type=='PressEvent'],
        name='use_modeling',
        feature_column='root'
    )

This let's you adjust the data set further or use the model as is. `y_temp` is a BooleanSeries that
indicates conversion per user. `X_temp` is a DataFrame with the number
of presses per `user_id`. For users that converted in the selected data, only usage from _before_
reaching conversion is counted. The `model` is the
toolkit that can be used to assess the feature importance on our conversion goal.

In this example we first review the data set with Bach before using it for the actual model training (hence
the `_temp` suffix). We create a single DataFrame that has all the features, the target and a sum of all
features.

.. code-block:: python

    data_set_temp = X_temp.copy()
    # we save the columns that are in our data set, these will be used later.
    columns = X_temp.data_columns
    data_set_temp['is_converted'] = y_temp
    data_set_temp['total_press'] = modelhub.map.sum_feature_rows(X_temp)

Reviewing the data set
----------------------
For a logistic regression several assumptions, such as sample size, no influential outliers and linear
relation between the features and the logit of the goal should be fulfilled. We will look at our data to
get the best possible data set for our model.

.. code-block:: python

    data_set_temp.describe().head()

We have 543 samples in our data. The description of our data set learns us that the mean is quite low for
most features and the standard deviation as well. This indicates that the feature usage is not distributed
very well.

.. code-block:: python

    print(data_set_temp.is_converted.value_counts().head())
    (data_set_temp.is_converted.value_counts()/data_set_temp.is_converted.count()).head()

The data set is not balanced in terms of users that did or did not reach conversion: 74 converted users (13
.6%). While this is not necessarily a problem, it influences the metric we choose to look at for model
performance. The model that we instantiated already accommodates for this.

We can also plot histograms with Bach of the features so we can inspect the distributions more closely.

.. code-block:: python

    figure, axis = plt.subplots(len(columns), 2, figsize=(15,30))

    for idx, name in enumerate(columns):
        data_set_temp[data_set_temp.is_converted==True][[name]].plot.hist(bins=20, title='Converted', ax=axis[idx][0])
        data_set_temp[data_set_temp.is_converted==False][[name]].plot.hist(bins=20, title='Not converted', ax=axis[idx][1])
    plt.tight_layout()

We see that some features are not useful at all ('join-slack' and 'privacy'), so we will remove them. Moreover
we think that users that clicking only once in any of the root locations will not provide us with any
explantory behavior for the goal.

Those users might, for instance, be users that wanted to go to our modeling section, and this was the
quickest way to get there with the results Google provided them. In that case, the intent of the user
(something of which we can never be 100% sure), was going to the modeling section. The _features_ did not
convince them.

By filtering like this, it is more likely that the used features on our website did, or did not convince a
user to check out the modeling section of our docs. This is exactly what we are after. An additional
advantage is that the distribution of feature usage will most likely get more favorable after removing
1-press-users.

.. code-block:: python

    # remove useless features.
    data_set_temp = data_set_temp.drop(columns=['privacy', 'join-slack'])
    # we update the columns that are still in our data set.
    columns = [x for x in data_set_temp.data_columns if x in X_temp.data_columns]
    # only use users with at least more than 1 press.
    data_set_temp = data_set_temp[data_set_temp.total_press>1]

If we now rerun the code above to review the data set we find that the data set is more balanced (16.5%
converted), although it is a bit small now (406 samples). The distributions as shown by describing the data
set and the histograms look indeed better for our model now. We will use this data set to create our X and
y data set that we will use in the model.

.. code-block:: python

    X = data_set_temp[columns]
    y = data_set_temp.is_converted

Train and evaluate the model
----------------------------
As mentioned above, the model is based on logistic regression. Logistic regression seems sensible as it is
used for classification, but also has relatively easy to interpret coefficients for the features. The
feature importance model uses the AUC to assess the performance. This is because we are more interested in
the coefficients than the actual predicted labels, and also because this metric can handle imbalanced data
sets. The feature importance model by default trains a logistic regression model three times on the entire
data set split in three folds. This way we can not only calculate the AUC on one test after training the
model. But also see whether the coefficients for the model are relatively stable when trained on different
data. After fitting the model, the results (the average coefficients of the three models) as well as the
performance of the three models can be retrieved with `model` methods.

.. code-block:: python

    # train the model
    model.fit(X, y, seed=.4)
    model.results()

The mean of the coefficients are returned together with the standard deviation. The lower the standard
deviation, the more stable the coefficients in the various runs. Our results show that 'about' has most
negative impact on conversion, while 'tracking', 'blog' and 'taxonomy' most positive.

.. code-block:: python

    model.auc()

The average AUC of our models is 0.69. This is better than a baseline model (0.5 AUC). However, it also
means that it is not a perfect model and therefore the chosen features alone can't predict
conversion completely.
Among others, some things that might improve further models are a larger data set, other explanatory
variables (i.e. more detailed locations instead of only root locations), and more information on the users
(i.e. user referrer as a proxy for user intent).

This concludes the demonstration of our upcoming feature importance model in the model hub. The pr for
this model is `here
<https://github.com/objectiv/objectiv-analytics/pull/662/>`_.

For an overview of all currently available models, check out the :ref:`models <models>`.
