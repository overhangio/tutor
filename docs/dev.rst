.. _development:

Open edX development
====================

In addition to running Open edX in production, Tutor can be used for local development of Open edX. This means it is possible to hack on Open edX without setting up a Virtual Machine. Essentially, this replaces the devstack provided by edX.

The following commands assume you have previously launched a :ref:`local <local>` Open edX platform. If you have not done so already, you should run::

    tutor local quickstart

You should setup real host names for the LMS and the CMS (i.e: not "localhost"). It is not necessary to configure the DNS records for local development: in other words, it doesn't matter that the chosen domain names exist or not for your platform, as the LMS and the CMS will be accessed on ``localhost``. You should *not* activate HTTPS certificates, which will not work locally.

Once the local platform has been configured, you should stop it so that it does not interfere with the development environment::

    tutor local stop

Finally, you should build the ``openedx-dev`` docker image::

    tutor images build openedx-dev

This ``openedx-dev`` development image differs from the ``openedx`` production image:

- The user that runs inside the container has the same UID as the user on the host, in order to avoid permission problems inside mounted volumes (and in particular in the edx-platform repository).
- Additional python and system requirements are installed for convenient debugging: `ipython <https://ipython.org/>`__, `ipdb <https://pypi.org/project/ipdb/>`__, vim, telnet.
- The edx-platform `development requirements <https://github.com/edx/edx-platform/blob/open-release/ironwood.2/requirements/edx/development.in>`__ are installed.

Since the ``openedx-dev`` is based upon the ``openedx`` docker image, it should be re-built every time the ``openedx`` docker image is modified.

Run a local development webserver
---------------------------------

::

    tutor dev runserver lms # Access the lms at http://localhost:8000
    tutor dev runserver cms # Access the cms at http://localhost:8001

Running arbitrary commands
--------------------------

To run any command inside one of the containers, run ``tutor dev run [OPTIONS] SERVICE [COMMAND] [ARGS]...``. For instance, to open a bash shell in the LMS or CMS containers::

    tutor dev run lms bash
    tutor dev run cms bash

To open a python shell in the LMS or CMS, run::

    tutor dev run lms ./manage.py lms shell
    tutor dev run cms ./manage.py cms shell

You can then import edx-platform and django modules and execute python code.

To collect assets, you can use the standard ``update_assets`` Open edX command with the right settings::

    tutor dev run lms paver update_assets --settings=tutor.development
    tutor dev run cms paver update_assets --settings=tutor.development

Point to a local edx-platform
-----------------------------

If you have one, you can point to a local version of `edx-platform <https://github.com/edx/edx-platform/>`_ on your host machine. To do so, pass a ``-P/--edx-platform-path`` option to the commands. For instance::

    tutor dev run --edx-platform-path=/path/to/edx-platform lms bash

If you don't want to rewrite this option every time, you can instead define the environment variable::

    export TUTOR_EDX_PLATFORM_PATH=/path/to/edx-platform

All development commands will then automatically mount your local repo.

**Note:** containers are built on the Ironwood release. If you are working on a different version of Open edX, you will have to rebuild the ``openedx`` docker images with the version. See the :ref:`fork edx-platform section <edx_platform_fork>`.

Prepare the edx-platform repo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to run a fork of edx-platform, dependencies need to be properly installed and assets compiled in that repo. To do so, run::

    export TUTOR_EDX_PLATFORM_PATH=/path/to/edx-platform
    tutor dev run lms pip install --requirement requirements/edx/development.txt
    tutor dev run lms python setup.py install
    tutor dev run lms paver update_assets --settings=tutor.development

Debug edx-platform
~~~~~~~~~~~~~~~~~~

To debug a local edx-platform repository, add a ``import ipdb; ipdb.set_trace()`` breakpoint anywhere in your code and run::

    tutor dev runserver lms --edx-platform-path=/path/to/edx-platform

Customised themes
-----------------

With Tutor, it's pretty easy to develop your own themes. Start by placing your files inside the ``env/build/openedx/themes`` directory. For instance, you could start from the ``edx.org`` theme present inside the ``edx-platform`` repository::

    cp -r /path/to/edx-platform/themes/edx.org "$(tutor config printroot)/env/build/openedx/themes/"

**Note:** Soft link doen't work here, may cause a theme not found error

Then, run a local webserver::

    tutor dev runserver lms

The LMS can then be accessed at http://localhost:8000.

Then, follow the `Open edX documentation to apply your themes <https://edx.readthedocs.io/projects/edx-installing-configuring-and-running/en/latest/configuration/changing_appearance/theming/enable_themes.html#apply-a-theme-to-a-site>`_. You will not have to modify the ``lms.env.json``/``cms.env.json`` files; just follow the instructions to add a site theme in http://localhost:8000/admin (starting from step 3).

Watch the themes folders for changes (in a different terminal)::

    tutor dev run watchthemes

Make changes to some of the files inside the theme directory: the theme assets should be automatically recompiled and visible at http://localhost:8000.

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
