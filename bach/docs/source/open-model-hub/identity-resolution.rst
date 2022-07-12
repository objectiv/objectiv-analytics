.. _open_model_hub_identity_resolution:

.. currentmodule:: modelhub

.. frontmatterposition:: 5

===================
Identity Resolution
===================

The Objectiv :ref:`ModelHub <modelhub_reference_modelhub>` package comes with configurable session-based identity resolution. This will help you track users across different sessions and devices with very little effort. Out of the box, every event belongs to a session, and every sessions belongs to a user. Modelhub allows you to make this more intelligent with very little effort.


**How does it work?**
Sessions are normally assigned to users that are identified by a cookie. In case it is not available because a user is on a different device, or not sufficient because the user needs to be correlated to an internal id, the tracker needs some help. It needs to be instructed to track the user identity explicitely, for example by tracking a unique hash that identifies the user persistently across devices whenever this user logs in. 
An identity is tracked through an IdentityContext (LINK) and contains two fields:
- The `id` field, where the identification method is stored
- The `value` field, that contains the actual identifier

The method in the `id` field can be used to configure modelhub to use all matching IdentityContexts for identity resolution. This triggers the following flow
1. All cookie based users get resolved to the last identity available for that user (filtered for the given method)
2. Sessions are assigned to the new identity; parallel sessions are allowed and remain intact.
3. Sessions for users that do not have a new identity are either left alone, or they can be fully anonymised.

**How to use**
Identity resolution needs to be setup upon creating the objectiv dataframe. To get the default cookie based user identities, nothing has to be specified. To enable more specific resolution, it only requires the addition of the `identity_resolution` parameter to the get_objectiv_dataframe call. Please have a look at the API reference(LINK) for more details and to find out how to configure anonymisation.  

**Recommendations**
We recommend tracking identities in a responsible way. Therefore, it is not adviced to track raw PII. A simple way around that is to hash the source data, and set the method in the `id` field accordingly, e.g.: `md5(some_data)`.

