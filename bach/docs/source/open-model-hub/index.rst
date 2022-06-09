.. _open_model_hub:

.. currentmodule:: modelhub

.. frontmatterposition:: 2
.. frontmatterslug:: /modeling/open-model-hub/

==============
Open model hub
==============
The open model hub is a toolkit that contains functions and models that can be applied on data collected with 
Objectiv’s Tracker. There are three types of functions/models: 
1. Helper functions. These helper functions simplify manipulating and analyzing the data. 
2. Aggregation models. These models consist of a combination of Bach instructions that run some of the more common data analyses or product analytics metrics. 
3. Machine learning models.

All models are open-source, free to use, and can be combined to build advanced compound models with little effort. The open model hub is powered by :ref:`Bach <bach>`: Objectiv's data modeling library. 

If you want to use the open model hub, install the package from PyPI as follows:

.. code-block:: console

    pip install objectiv-modelhub


See the :ref:`example notebooks <example_notebooks>` section to get started immediately. 

View the list of available models :ref:`here <models>` or check out the full
:ref:`open model hub API reference <open_model_hub_api_reference>`. 

More information on setting up a development environment for the open model hub and how to configure Metabase 
is in the `readme <https://github.com/objectiv/objectiv-analytics/tree/main/modelhub>`_.

The open model hub is powered by :ref:`Bach <bach>`: Objectiv's data modeling library. With Bach, you can 
compose models with familiar Pandas-like dataframe operations in your notebook. It uses a SQL abstraction 
layer that enables models to run on the full dataset, and you can output models to SQL with a single command. 
Head over to the :ref:`Bach <bach>` section to learn all about it.

.. toctree::
    :maxdepth: 7
    :hidden:
    
    version-check
    API reference <api-reference/index>
