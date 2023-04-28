.. _filters:

=======
Filters
=======

Filters are one of the two types of hooks (the other being :ref:`actions`) that can be used to extend Tutor. Filters allow one to modify the application behavior by transforming data. Each filter has a name, and callback functions can be attached to it. When a filter is applied, these callback functions are called in sequence; the result of each callback function is passed as the first argument to the next callback function. The result of the final callback function is returned to the application as the filter's output.

.. autoclass:: tutor.core.hooks.Filter
    :members:

.. The following are only to ensure that the docs build without warnings
.. class:: tutor.core.hooks.filters.T1
.. class:: tutor.core.hooks.filters.T2
.. class:: tutor.core.hooks.filters.L
