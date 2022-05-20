.. _modeling:

.. frontmatterposition:: 1
.. frontmattersidebartitle:: Introduction

======================
Modeling with Objectiv
======================

Objectiv's modeling toolkit enables you to quickly build advanced data models and run in-depth analyses. 
This is the combined result of three components:

1. The open analytics taxonomy.
1. The open model hub.
1. The Bach modeling library.

### The open analytics taxonomy

Objectiv's tracker validates all collected data against the open analytics taxonomy to ensure it is ready to 
model on without any cleaning or transformation. 

`Learn more about the open analytics taxonomy </docs/taxonomy/>`_

### The open model hub

The open model hub consists of pre-built models and operations that you can combine to build advanced 
compound models with little effort. The open model hub is powered by Bach, our python-based modeling library.

:ref:`Learn more about the open model hub <open_model_hub>`

### The Bach modeling library

Bach is a python-based modeling library that enables you to use Pandas-like operations that run on your full 
dataset in the SQL database. Any dataframe or model built with Bach can be converted to an SQL statement with 
a single command.

:ref:`Learn more about the Objectiv Bach modeling libary <bach>`

### Example notebooks

To see how all components work together, there are several example notebooks that show how you can analyze 
and model data using the open analytics taxonomy, the open model hub, and the Bach modeling library.

:ref:`See the example notebooks <example_notebooks>`


.. toctree::
    :maxdepth: 7
    :hidden:

    Example notebooks <example-notebooks/index>
    Models <open-model-hub/models/index>
    Open model hub <open-model-hub/index>
    Bach <bach/index>
