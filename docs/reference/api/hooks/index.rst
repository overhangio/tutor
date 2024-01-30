.. _hooks_api:

=========
Hooks API
=========

Types
=====

This is the Python documentation of the two types of hooks (actions and filters) as well as the contexts system which is used to instrument them. Understanding how Tutor hooks work is useful to create plugins that modify the behaviour of Tutor. However, plugin developers should almost certainly not import these hook types directly. Instead, use the reference :ref:`hooks catalog <hooks_catalog>`.

.. toctree::
   :maxdepth: 1

   actions
   filters
   contexts

Utilities
=========

Functions
---------

.. autofunction:: tutor.core.hooks::clear_all
.. autofunction:: tutor.hooks::lru_cache

Priorities
----------

.. automodule:: tutor.core.hooks.priorities
   :members: HIGH, DEFAULT, LOW
