.. _open_model_hub_version_check:

.. currentmodule:: modelhub

.. frontmatterposition:: 5

=============
Version check
=============

The Objectiv :ref:`ModelHub <modelhub_reference_modelhub>` package comes with a built-in version checker. 
During import, it automatically checks if the loaded version is the most recent version.

**Why?**

We are adding new models and taxonomy operations at a high pace, so the goal of this version check is to 
notify you when new models & taxonomy operations are available to use. 

**How?**

An HTTP request to https://version-check.objectiv.io is sent on package import. A Python warning
message is issued in case a new version is available. 


**What data is being sent?**

Your current version of objectiv-modelhub and objectiv-bach. No cookies, IPs or any other PII is being sent.

**Disable the version check**

Disable the check by setting the environment variable `OBJECTIV_VERSION_CHECK_DISABLE` to `true` prior to 
importing objectiv-modelhub.

**Source code**

For more detailed information, check the source code in 
`__init__.py <https://github.com/objectiv/objectiv-analytics/blob/main/modelhub/modelhub/__init__.py>`_
