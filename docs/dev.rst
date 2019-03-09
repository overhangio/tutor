.. _development:

Using Tutor for Open edX development
====================================

In addition to running Open edX in production, you can use the docker containers for local development. This means you can hack on Open edX without setting up a Virtual Machine. Essentially, this replaces the devstack provided by edX.

Run a local development webserver
---------------------------------

::

    tutor dev runserver lms # Access the lms at http://localhost:8000
    tutor dev runserver cms # Access the cms at http://localhost:8001

Open a bash shell
-----------------

::

    tutor dev shell lms
    tutor dev shell cms

Point to a local edx-platform
-----------------------------

If you have one, you can point to a local version of `edx-platform <https://github.com/edx/edx-platform/>`_ on your host machine. To do so, pass a ``-P/--edx-platform-path`` option to the commands. For instance::

    tutor dev shell lms --edx-platform-path=/path/to/edx-platform

If you don't want to rewrite this option every time, you can instead define the environment variable::

    export TUTOR_EDX_PLATFORM_PATH=/path/to/edx-platform

All development commands will then automatically mount your local repo.

**Note:** containers are built on the Hawthorn release. If you are working on a different version of Open edX, you will have to rebuild the ``openedx`` docker images with the version. See the ":ref:`fork edx-platform <edx_platform_fork>`.

Prepare the edx-platform repo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to run a fork of edx-platform, dependencies need to be properly installed and assets compiled in that repo. To do so, run::

    export TUTOR_EDX_PLATFORM_PATH=/path/to/edx-platform
    tutor dev run lms npm install
    tutor dev run lms pip install --requirement requirements/edx/development.txt
    tutor dev run lms python setup.py install
    tutor dev run lms openedx-assets build

Debug edx-platform
~~~~~~~~~~~~~~~~~~

To debug a local edx-platform repository, add a ``import pdb; pdb.set_trace()`` breakpoint anywhere in your code and run::

    tutor dev runserver lms --edx-platform-path=/path/to/edx-platform

Customised themes
-----------------

With Tutor, it's pretty easy to develop your own themes. Start by placing your files inside the ``env/build/openedx/themes`` directory. For instance, you could start from the ``edx.org`` theme present inside the ``edx-platform`` repository::

    cp -r /path/to/edx-platform/themes/edx.org $(tutor config printroot)/env/build/openedx/themes/

Then, run a local webserver::

    tutor dev runserver lms

The LMS can then be accessed at http://localhost:8000.

Then, follow the `Open edX documentation to apply your themes <https://edx.readthedocs.io/projects/edx-installing-configuring-and-running/en/latest/configuration/changing_appearance/theming/enable_themes.html#apply-a-theme-to-a-site>`_. You will not have to modify the ``lms.env.json``/``cms.env.json`` files; just follow the instructions to add a site theme in http://localhost:8000/admin (starting from step 3).

Watch the themes folders for changes (in a different terminal)::

    tutor dev watchthemes

Make changes to some of the files inside the theme directory: the theme assets should be automatically recompiled and visible at http://localhost:8000.

Assets management
-----------------

Assets building and collecting is made more difficult by the fact that development settings are `incorrectly loaded in Hawthorn <https://github.com/edx/edx-platform/pull/18430/files>`_. This should be fixed in the next Open edX release. Meanwhile, do not run ``paver update_assets`` while in development mode. When working locally on a theme, build assets by running in the container::

    openedx-assets build

Alternatively, run from the host::
    
    tutor dev run lms openedx-assets build

This command will take quite some time to run. You can speed up this process by running only part of the full build. Run ``openedx-assets -h`` for more information.

Running python commands
-----------------------

These commands will open a python shell in the lms or the cms::

    tutor dev run lms python
    tutor dev run cms python

You can then import edx-platform and django modules and execute python code.

Custom edx-platform settings
----------------------------

By default, tutor settings files are mounted inside the docker images at ``/openedx/edx-platform/lms/envs/tutor/`` and ``/openedx/edx-platform/cms/envs/tutor/``. In the various ``dev`` commands, the default ``edx-platform`` settings module is set to ``tutor.development`` and you don't have to do anything to set up these settings.

If, for some reason, you want to use different settings, you will need to pass the ``-S/--edx-platform-settings`` option to each command. Alternatively, you can define the ``TUTOR_EDX_PLATFORM_SETTINGS`` environment variable.

For instance, let's assume you have created the ``/path/to/edx-platform/lms/envs/mysettings.py`` and ``/path/to/edx-platform/cms/envs/mysettings.py`` modules. These settings should be pretty similar to the following files::

    $(tutor config printroot)/env/apps/openedx/tutor/lms/development.py
    $(tutor config printroot)/env/apps/openedx/tutor/cms/development.py

Alternatively, the ``mysettings.py`` files can import the tutor development settings::

    # Beginning of mysettings.py
    from .tutor.development import *

You should then specify the settings to use on the host::

    export TUTOR_EDX_PLATFORM_SETTINGS=mysettings

From then on, all ``dev`` commands will use the ``mysettings`` module. For instance::

    tutor dev runserver lms --edx-platform-path=/path/to/edx-platform
