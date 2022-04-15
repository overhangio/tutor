.. _filters:

=======
Filters
=======

Filters are one of the two types of hooks (the other being :ref:`actions`) that can be used to extend Tutor. Filters allow one to modify the application behavior by transforming data. Each filter has a name, and callback functions can be attached to it. When a filter is applied, these callback functions are called in sequence; the result of each callback function is passed as the first argument to the next callback function. The result of the final callback function is returned to the application as the filter's output.

.. autofunction:: tutor.hooks.filters::get
.. autofunction:: tutor.hooks.filters::get_template
.. autofunction:: tutor.hooks.filters::add
.. autofunction:: tutor.hooks.filters::add_item
.. autofunction:: tutor.hooks.filters::add_items
.. autofunction:: tutor.hooks.filters::apply
.. autofunction:: tutor.hooks.filters::iterate
.. autofunction:: tutor.hooks.filters::clear
.. autofunction:: tutor.hooks.filters::clear_all

.. autoclass:: tutor.hooks.filters.Filter
.. autoclass:: tutor.hooks.filters.FilterTemplate
