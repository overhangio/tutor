.. _development:

Open edX development
====================

In addition to running Open edX in production, Tutor can be used for local development of Open edX. This means that it is possible to hack on Open edX without setting up a Virtual Machine. Essentially, this replaces the devstack provided by edX.

The following commands assume you have previously launched a :ref:`local <local>` Open edX platform. If you have not done so already, you should run::

    tutor local quickstart

In order to run the platform in development mode, you **must** answer no ("n") to the question "Are you configuring a production platform". 

Note that the local.overhang.io `domain <https://dnschecker.org/#A/local.overhang.io>`__ and its `subdomains <https://dnschecker.org/#CNAME/studio.local.overhang.io>`__ all point to 127.0.0.1. This is just a domain name that was setup to conveniently access a locally running Open edX platform.

Once the local platform has been configured, you should stop it so that it does not interfere with the development environment::

    tutor local stop

Finally, you should build the ``openedx-dev`` docker image::

    tutor images build openedx-dev

This ``openedx-dev`` development image differs from the ``openedx`` production image:

- The user that runs inside the container has the same UID as the user on the host, in order to avoid permission problems inside mounted volumes (and in particular in the edx-platform repository).
- Additional python and system requirements are installed for convenient debugging: `ipython <https://ipython.org/>`__, `ipdb <https://pypi.org/project/ipdb/>`__, vim, telnet.
- The edx-platform `development requirements <https://github.com/edx/edx-platform/blob/open-release/juniper.2/requirements/edx/development.in>`__ are installed.

Since the ``openedx-dev`` is based upon the ``openedx`` docker image, it should be re-built every time the ``openedx`` docker image is modified.

Run a local development webserver
---------------------------------

::

    tutor dev runserver lms # Access the lms at http://local.overhang.io:8000
    tutor dev runserver cms # Access the cms at http://studio.local.overhang.io:8001

Running arbitrary commands
--------------------------

To run any command inside one of the containers, run ``tutor dev run [OPTIONS] SERVICE [COMMAND] [ARGS]...``. For instance, to open a bash shell in the LMS or CMS containers::

    tutor dev run lms bash
    tutor dev run cms bash

To open a python shell in the LMS or CMS, run::

    tutor dev run lms ./manage.py lms shell
    tutor dev run cms ./manage.py cms shell

You can then import edx-platform and django modules and execute python code.

To collect assets, you can use the ``openedx-assets`` command that ships with Tutor::

    tutor dev run lms openedx-assets --env=dev

Point to a local edx-platform
-----------------------------

If you have one, you can point to a local version of `edx-platform <https://github.com/edx/edx-platform/>`_ on your host machine. To do so, pass a ``-v/--volume`` option to the ``run`` and runserver commands. For instance::

    tutor dev run -v /path/to/edx-platform:/openedx/edx-platform lms bash

If you don't want to rewrite this option every time, you can define a command alias::

    alias tutor-dev-run-lms="tutor dev run -v /path/to/edx-platform:/openedx/edx-platform lms"

For technical reasons, the ``-v`` option is only supported for the ``run`` and ``runserver`` commands. With these commands, only one service is started. But there are cases where you may want to launch and debug a complete Open edX platform with ``tutor dev start`` and mount a custom edx-platform fork. For instance, this might be needed when testing the interaction between multiple services. To do so, you should create a ``docker-compose.override.yml`` file that will specify a custom volume to be used with all ``dev`` commands::
    
    vim "$(tutor config printroot)/env/dev/docker-compose.override.yml"

Then, add the following content::
    
    version: "3.7"
    services:
      lms:
        volumes:
          - /path/to/edx-platform/:/openedx/edx-platform
      cms:
        volumes:
          - /path/to/edx-platform/:/openedx/edx-platform
      lms-worker:
        volumes:
          - /path/to/edx-platform/:/openedx/edx-platform
      cms-worker:
        volumes:
          - /path/to/edx-platform/:/openedx/edx-platform

This override file will be loaded when running any ``tutor dev ..`` command. The edx-platform repo mounted at the specified path will be automaticall mounted inside all LMS and CMS containers. With this file, you should no longer specify the ``-v`` option from the command line with the ``run`` or ``runserver`` commands.

**Note:** containers are built on the Juniper release. If you are working on a different version of Open edX, you will have to rebuild the ``openedx`` docker images with the version. See the :ref:`fork edx-platform section <edx_platform_fork>`.

Prepare the edx-platform repo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to run a fork of edx-platform, dependencies need to be properly installed and assets compiled in that repo. To do so, run::

    tutor dev run -v /path/to/edx-platform:/openedx/edx-platform lms bash
    pip install --requirement requirements/edx/development.txt
    python setup.py install
    openedx-assets build --env=dev

Debug edx-platform
~~~~~~~~~~~~~~~~~~

To debug a local edx-platform repository, add a ``import ipdb; ipdb.set_trace()`` breakpoint anywhere in your code and run::

    tutor dev runserver -v /path/to/edx-platform:/openedx/edx-platform lms

XBlock and edx-platform plugin development
------------------------------------------

In some cases you will have to develop features for packages that are pip-installed next to edx-platform. This is quite easy with Tutor. Just add your packages to the ``$(tutor config printroot)/env/build/openedx/requirements/private.txt`` file. To avoid re-building the openedx Docker image at every change, you should add your package in editable mode. For instance::

    echo "-e ./mypackage" >> "$(tutor config printroot)/env/build/openedx/requirements/private.txt"

The ``requirements`` folder should have the following content::

    env/build/openedx/requirements/
        private.txt
        mypackage/
            setup.py
            ...

You will have to re-build the openedx Docker image once::

    tutor images build openedx

You should then run the development server as usual, with ``runserver``. Every change made to the ``mypackage`` folder will be picked up and the development server will be automatically reloaded.

.. _theming:

Customised themes
-----------------

With Tutor, it's pretty easy to develop your own themes. Start by placing your files inside the ``env/build/openedx/themes`` directory. For instance, you could start from the ``edx.org`` theme present inside the ``edx-platform`` repository::

    cp -r /path/to/edx-platform/themes/edx.org "$(tutor config printroot)/env/build/openedx/themes/"

.. warning::
    You should not create a soft link here. If you do, it will trigger a ``Theme not found in any of the themes dirs`` error. This is because soft links are not properly resolved from inside docker containers.

Then, run a local webserver::

    tutor dev runserver lms

The LMS can then be accessed at http://local.overhang.io:8000. You will then have to :ref:`enable that theme <settheme>` for the development domain names::
    
    tutor dev settheme mythemename local.overhang.io:8000 studio.local.overhang.io:8001

Re-build development docker image (and compile assets)::
    
    tutor images build openedx-dev

Watch the themes folders for changes (in a different terminal)::

    tutor dev run watchthemes

Make changes to some of the files inside the theme directory: the theme assets should be automatically recompiled and visible at http://local.overhang.io:8000.

Custom edx-platform settings
----------------------------

By default, tutor settings files are mounted inside the docker images at ``/openedx/edx-platform/lms/envs/tutor/`` and ``/openedx/edx-platform/cms/envs/tutor/``. In the various ``dev`` commands, the default ``edx-platform`` settings module is set to ``tutor.development`` and you don't have to do anything to set up these settings.

If, for some reason, you want to use different settings, you will need to pass the ``-e SETTINGS=mycustomsettings`` option to each command. Alternatively, you can define the ``TUTOR_EDX_PLATFORM_SETTINGS`` environment variable.

For instance, let's assume you have created the ``/path/to/edx-platform/lms/envs/mysettings.py`` and ``/path/to/edx-platform/cms/envs/mysettings.py`` modules. These settings should be pretty similar to the following files::

    $(tutor config printroot)/env/apps/openedx/tutor/lms/development.py
    $(tutor config printroot)/env/apps/openedx/tutor/cms/development.py

Alternatively, the ``mysettings.py`` files can import the tutor development settings::

    # Beginning of mysettings.py
    from .tutor.development import *

You should then specify the settings to use on the host::

    export TUTOR_EDX_PLATFORM_SETTINGS=mysettings

From then on, all ``dev`` commands will use the ``mysettings`` module. For instance::

    tutor dev runserver -v /path/to/edx-platform:/openedx/edx-platform lms
