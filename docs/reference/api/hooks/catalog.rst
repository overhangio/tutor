.. _hooks_catalog:

=============
Hooks catalog
=============

Tutor can be extended by making use of "hooks". Hooks are either "actions" or "filters". Here, we list all instances of actions and filters that are used across Tutor. Plugin developers can leverage these hooks to modify the behaviour of Tutor.

The underlying Python hook classes and API are documented :ref:`here <hooks_api>`.

.. autoclass:: tutor.hooks.Actions
    :members:

.. autoclass:: tutor.hooks.Filters
    :members:

.. autoclass:: tutor.hooks.Contexts
    :members:

Open edX hooks
--------------

.. automodule:: tutor.plugins.openedx.hooks
    :members:
