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

The open model hub is a toolkit that contains functions and models that can be applied on data collected with 
Objectiv’s Tracker. They can be combined to build advanced compound models with little effort. The open model 
hub is powered by Bach, our python-based modeling library.

:doc:`Learn more about the open model hub <open-model-hub/index>`

### The Bach modeling library

Bach is a python-based modeling library that enables you to use Pandas-like operations that run on your full 
dataset in the SQL database. Any dataframe or model built with Bach can be converted to an SQL statement with 
a single command.

:doc:`Learn more about the Objectiv Bach modeling libary <bach/index>`

## Get started

See how you can get up-and-running with your own notebook and data store in minutes.

:doc:`Learn how to get started <./get-started-in-your-notebook>`


.. toctree::
    :maxdepth: 7
    :hidden:

    Example notebooks <example-notebooks/index>
    Models <open-model-hub/models/index>
    Open model hub <open-model-hub/index>
    Bach <bach/index>
    Get started in your notebook <./get-started-in-your-notebook>
