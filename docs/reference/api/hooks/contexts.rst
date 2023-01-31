.. _contexts:

========
Contexts
========

Contexts are a feature of the hook-based extension system in Tutor, which allows us to keep track of which components of the code created which callbacks. Contexts are very much an internal concept that most plugin developers should not have to worry about.

.. autoclass:: tutor.core.hooks.Context
.. autofunction:: tutor.core.hooks.contexts::enter
