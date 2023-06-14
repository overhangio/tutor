.. _actions:

=======
Actions
=======

Actions are one of the two types of hooks (the other being :ref:`filters`) that can be used to extend Tutor. Each action represents an event that can occur during the application life cycle. Each action has a name, and callback functions can be attached to it. When an action is triggered, these callback functions are called in sequence. Each callback function can trigger side effects, independently from one another.

.. autoclass:: tutor.core.hooks.Action
    :members:

.. The following are only to ensure that the docs build without warnings
.. class:: tutor.core.hooks.actions.T
.. class:: tutor.types.Config
