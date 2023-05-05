.. _theme_development:

Open edX theme development 
--------------------------

With Tutor, it's pretty easy to develop your own themes. Start by placing your files inside the ``env/build/openedx/themes`` directory. For instance, you could start from the ``edx.org`` theme present inside the ``edx-platform`` repository::

    cp -r /path/to/edx-platform/themes/edx.org "$(tutor config printroot)/env/build/openedx/themes/"

.. warning::
    You should not create a soft link here. If you do, it will trigger a ``Theme not found in any of the themes dirs`` error. This is because soft links are not properly resolved from inside docker containers.

Then, run a local webserver::

    tutor dev start lms

The LMS can then be accessed at http://local.overhang.io:8000. You will then have to :ref:`enable that theme <settheme>`::

    tutor dev do settheme mythemename

Watch the themes folders for changes (in a different terminal)::

    tutor dev run watchthemes

Make changes to some of the files inside the theme directory: the theme assets should be automatically recompiled and visible at http://local.overhang.io:8000.