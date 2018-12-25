.. _development:

Open edX development
====================

In addition to running Open edX in production, you can use the docker containers for local development. This means you can hack on Open edX without setting up a Virtual Machine. Essentially, this replaces the devstack provided by edX.

To begin with, define development settings::

    export EDX_PLATFORM_SETTINGS=tutor.development

Run a local webserver
---------------------

::

    make lms-runserver
    make cms-runserver

Open a bash shell
-----------------

::

    make lms
    make cms

Debug edx-platform
------------------

If you have one, you can point to a local version of `edx-platform <https://github.com/edx/edx-platform/>`_ on your host machine::

    export EDX_PLATFORM_PATH=/path/to/your/edx-platform

Note that you should use an absolute path here, not a relative path (e.g: ``/path/to/edx-platform`` and not ``../edx-platform``).

All development commands will then automatically mount your local repo. For instance, you can add a ``import pdb; pdb.set_trace()`` breakpoint anywhere in your code and run::

    make lms-runserver

Note: containers are built on the Hawthorn release. If you are working on a different version of Open edX, you will have to rebuild the images with the right ``EDX_PLATFORM_VERSION`` argument. You may also want to change the ``EDX_PLATFORM_REPOSITORY`` argument to point to your own fork of edx-platform.

With a customised edx-platform repo, you must be careful to have settings that are compatible with the docker environment. You are encouraged to copy the ``tutor.development`` settings files to our own repo:

    cp -r config/openedx/tutor/lms/ /path/to/edx-platform/lms/envs/tutor
    cp -r config/openedx/tutor/cms/ /path/to/edx-platform/cms/envs/tutor

You can then run your platform with the ``tutor.development`` settings.

Develop customised themes
-------------------------

Run a local webserver::

    make lms-runserver

Watch the themes folders for changes::

    make watch-themes

Make changes to ``openedx/themes/yourtheme``: the theme assets should be automatically recompiled and visible at http://localhost:8000.

Assets management
-----------------

Assets building and collecting is made more difficult by the fact that development settings are `incorrectly loaded in Hawthorn <https://github.com/edx/edx-platform/pull/18430/files>`_. This should be fixed in the next Open edX release. Meanwhile, do not run ``paver update_assets`` while in development mode. When working locally on a theme, build assets by running in the container::

    openedx-assets build

This command will take quite some time to run. You can speed up this process by running only part of the full build. Run ``openedx-assets -h`` for more information.
