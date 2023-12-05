.. _theming:

Changing the appearance of Open edX
===================================

Installing a custom theme
-------------------------

Comprehensive theming is enabled by default, but only the default theme is compiled. `Indigo <https://github.com/overhangio/indigo>`__ is a better, ready-to-run theme that you can start using today.

To compile your own theme, add it to the ``env/build/openedx/themes/`` folder::

    git clone https://github.com/me/myopenedxtheme.git \
      "$(tutor config printroot)/env/build/openedx/themes/myopenedxtheme"

The ``themes`` folder should have the following structure::

    openedx/themes/
        mycustomtheme1/
            cms/
                ...
            lms/
                ...
        mycustomtheme2/
            ...

Then you must rebuild the openedx Docker image::

    tutor images build openedx

Finally, you should enable your theme with the :ref:`settheme command <settheme>`.

.. _theme_development:

Developing a new theme
----------------------

With Tutor, it's pretty easy to develop your own themes. Start by placing your files inside the ``env/build/openedx/themes`` directory. For instance, you could start from the ``edx.org`` theme present inside the ``edx-platform`` repository::

    cp -r /path/to/edx-platform/themes/edx.org "$(tutor config printroot)/env/build/openedx/themes/"

.. warning::
    You should not create a soft link here. If you do, it will trigger a ``Theme not found in any of the themes dirs`` error. This is because soft links are not properly resolved from inside docker containers.

Then, run a local webserver::

    tutor dev start lms

The LMS can then be accessed at http://local.edly.io:8000. You will then have to :ref:`enable that theme <settheme>`::

    tutor dev do settheme mythemename

Watch the themes folders for changes (in a different terminal)::

    tutor dev run watchthemes

Make changes to some of the files inside the theme directory: the theme assets should be automatically recompiled and visible at http://local.edly.io:8000.
