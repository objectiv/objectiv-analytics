.. _open_model_hub_identity_resolution:

.. currentmodule:: modelhub

.. frontmatterposition:: 2

===================
Identity Resolution
===================

The open model hub package provides configurable Identity Resolution to help you track users across different 
sessions and devices with very little effort. By default every event belongs to a session, and every session 
belongs to a user. However, this can easily be reconfigured to suit your application's user identity needs, 
e.g. using internal IDs for logged-in users.

How to use Identity Resolution
------------------------------
Identity Resolution should be configured 
:py:meth:`on creating the Objectiv DataFrame <ModelHub.get_objectiv_dataframe>`:

* By default cookie-based user identities are used; in this case, no need to specify anything.
* For more specific resolution, use the `identity_resolution` and (optionally) the 
  `anonymize_unidentified_users` parameters in the 
  :py:meth:`get_objectiv_dataframe <ModelHub.get_objectiv_dataframe>` call.


.. caution:: 
    We recommend not to track raw Personal Identifiable Information (PII). A simple way around that is to 
    hash the source data, and set the method in the `id` field accordingly, e.g. `md5(some_data)`.


How does it work?
-----------------
Sessions are normally assigned to users that are identified by a cookie. In case the cookie isn't available 
(e.g. deleted, user is on a different device, etc.), or not sufficient (e.g. because the user should be 
linked to an internal ID), the tracker needs some help. It should then be instructed to track the user 
identity explicitly, for example with a unique hash that identifies them persistently across devices when 
they log in. 

An identity is tracked through an 
`IdentityContext <https://objectiv.io/docs/taxonomy/reference/global-contexts/IdentityContext>`_ and contains 
two fields:
1. The `id` field, storing the identification method;
2. The `value` field, containing the actual identifier, e.g. a unique User ID or email address.

See the `Tracking section <https://objectiv.io/docs/tracking/>`_ on how to configure the SDK for your 
platform to track this IdentityContext.

The method in the `id` field can then be used to configure model hub (in the 
:py:meth:`get_objectiv_dataframe <ModelHub.get_objectiv_dataframe>` call) to use all matching IdentityContexts 
for identity resolution. This triggers the following flow:
1. All cookie-based users get resolved to the last identity available for that user (filtered for the given 
method);
2. Sessions are assigned to the new identity, with any parallel sessions (e.g. same user logged in on 
multiple devices) remaining intact;
3. Sessions for users that do not have a new identity are either left alone, or they can be fully anonymized. 
This behavior can be specified in the :py:meth:`get_objectiv_dataframe <ModelHub.get_objectiv_dataframe>` 
call.
