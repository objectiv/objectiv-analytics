.. _open_model_hub:

.. currentmodule:: modelhub

.. frontmatterposition:: 3
.. frontmatterslug:: /modeling/open-model-hub/

==============
Open model hub
==============
The open model hub is a toolkit with functions and models that can run directly on a full dataset collected 
with Objectiv's Tracker SDKs. All models are open-source, free to use, and can easily be combined to build 
advanced compound models.

How to use the open model hub
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Three types of functions/models are provided: 
1. :doc:`Helper functions <./models/helper-functions/index>`: simplify manipulating and analyzing the data. 
2. :doc:`Aggregation models <./models/aggregation/index>`: enable running some of the more common data 
analyses and product analytics metrics. 
3. :doc:`Machine learning models <./models/machine-learning/index>`.

Modeling behavior of users and groups is enabled through configurable 
:doc:`Identity Resolution <./identity-resolution>`.

See how to :doc:`get started in your notebook <../get-started-in-your-notebook>` and the 
:doc:`example notebooks <../example-notebooks/index>`, and install the model hub package directly from PyPI:

.. code-block:: console

    pip install objectiv-modelhub


Powered by Bach
~~~~~~~~~~~~~~~
The open model hub is powered by :ref:`Bach <bach>`: Objectiv's data modeling library. With Bach, you can 
compose models with familiar Pandas-like dataframe operations that use an SQL abstraction layer to run on the 
full dataset. Models can be output to SQL with one command.


.. toctree::
    :maxdepth: 7
    :hidden:
    
    identity-resolution
    Models <models/index>
    API reference <api-reference/index>
    version-check
