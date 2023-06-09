==========
Patches
==========

Patches are mechanisms that Tutor offers to plugin developers to modify the templates rendered to alter our environment. In many places, the Tutor templates include calls to ``{{ patch("patchname") }}``. Plugins can add content in these places with ``hooks.Filters.ENV_PATCHES.add_item``.

Example::

    from tutor import hooks

    hooks.Filters.ENV_PATCHES.add_item(
        (
            "openedx-lms-common-settings",
            "FEATURES['ALLOW_PUBLIC_ACCOUNT_CREATION'] = False"
        )
    )

This will add ``FEATURES['ALLOW_PUBLIC_ACCOUNT_CREATION'] = False`` to the lms common settings with a Python Tutor plugin.

.. note:: If you want a Package Tutor plugin, we recommend you to use the `overhangio/cookiecutter-tutor-plugin <https://github.com/overhangio/cookiecutter-tutor-plugin>`_ and add in the patches directory a file with the name of the patch, and inside the file add the content you want to add to the templates that use that patch.

You can find a list of all patches used across Tutor here:

.. toctree::
   :maxdepth: 1

   catalog