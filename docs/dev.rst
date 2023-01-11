.. _development:

Open edX development
====================

In addition to running Open edX in production, Tutor can be used for local development of Open edX. This means that it is possible to hack on Open edX without setting up a Virtual Machine. Essentially, this replaces the devstack provided by edX.

.. _edx_platform_dev_env:

First-time setup
----------------

First, ensure you have already :ref:`installed Tutor <install>` (for development against the named releases of Open edX) or :ref:`Tutor Nightly <nightly>` (for development against Open edX's master branches).

Then, run one of the following in order to launch the developer platform setup process::

    # To use the edx-platform repository that is built into the image:
    tutor dev launch

    # To bind-mount and run your local clone of edx-platform,
    # where './edx-platform' should be replaced with your local edx-platform's path:
    tutor dev launch --mount=./edx-platform

This will perform several tasks for you. It will:

* stop any existing locally-running Tutor containers,

* disable HTTPS,

* set your ``LMS_HOST`` to `local.overhang.io <http://local.overhang.io>`_ (a convenience domain that simply `points at 127.0.0.1 <https://dnschecker.org/#A/local.overhang.io>`_),

* prompt for a platform details (with suitable defaults),

* build an ``openedx-dev`` image, which is based ``openedx`` production image but is `specialized for developer usage`_,

* start LMS, CMS, supporting services, and any plugged-in services,

* ensure databases are created and migrated, and

* run service initialization scripts, such as service user creation and Waffle configuration.

Additionally, if you chose to bind-mount your local clone of edx-platform, it will:

* re-run setup.py,

* clean-reinstall Node modules, and

* regenerate static assets.

Once setup is complete, the platform will be running in the background:

* LMS will be accessible at `http://local.overhang.io:8000 <http://local.overhang.io:8000>`_.
* CMS will be accessible at `http://studio.local.overhang.io:8001 <http://studio.local.overhang.io:8001>`_.
* Plugged-in services should be accessible at their documented URLs.

Now, you can use the ``tutor dev ...`` command-line interface to manage your development environment. Some common commands are described below.

.. note::

  Wherever you see ``[--mount=./edx-platform]``, either:

  * omit it, if you are using the edx-platform repository built into the image, or
  * substitute it with ``--mount=<path/to/your/edx-platform>``.

  You can :ref:`read more about bind-mounts below <bind_mounts>`.

Stopping the platform
---------------------

To bring down your platform's containers, simply run::

  tutor dev stop

Starting the platform back up
-----------------------------

Once you have used ``launch`` once, you can start the platform in the future with the lighter-weight ``start -d`` command, which brings up containers *detached* (that is: in the background), but does not perform any initialization tasks::

  tutor dev start -d [--mount=./edx-platform]

If you prefer to run containers *attached* (that is: in the foreground, your current terminal), you can omit the ``-d`` flag::

  tutor dev start [--mount=./edx-platform]

When running containers attached, you can stop the platform with ``Ctrl+c``, or switch to detached mode using ``Ctrl+z``.

Finally, you can always start your platform with ``launch``, even if you have already run it in the past. It will take longer, but it will ensure that your config is applied, your database is provisioned, your plugins are fully initialized, and (if mounted) your local edx-platform is set up. If you include the ``--pullimages`` flag it will also ensure that your container images are up-to-date as well::

  tutor dev launch [--mount=./edx-platform] --pullimages

Debugging with breakpoints
--------------------------

To debug a local edx-platform repository, you can add a `python breakpoint <https://docs.python.org/3/library/functions.html#breakpoint>`__ with ``breakpoint()`` anywhere in your code. Then, attach to the applicable service's container by running ``start`` (without ``-d``) followed by the service's name:

  # Debugging LMS:
  tutor dev start [--mount=./edx-platform] lms

  # Or, debugging CMS:
  tutor dev start [--mount=./edx-platform] cms

Running arbitrary commands
--------------------------

To run any command inside one of the containers, run ``tutor dev run [OPTIONS] SERVICE [COMMAND] [ARGS]...``. For instance, to open a bash shell in the LMS or CMS containers::

    tutor dev run [--mount=./edx-platform] lms bash
    tutor dev run [--mount=./edx-platform] cms bash

To open a python shell in the LMS or CMS, run::

    tutor dev run [--mount=./edx-platform] lms ./manage.py lms shell
    tutor dev run [--mount=./edx-platform] cms ./manage.py cms shell

You can then import edx-platform and django modules and execute python code.

To rebuild assets, you can use the ``openedx-assets`` command that ships with Tutor::

    tutor dev run [--mount=./edx-platform] lms openedx-assets build --env=dev


.. _specialized for developer usage: 

Rebuilding the openedx-dev image
--------------------------------

The ``openedx-dev`` Docker image is based on the same ``openedx`` image used by ``tutor local ...`` to run LMS and CMS. However, it has a few differences to make it more convenient for developers:

- The user that runs inside the container has the same UID as the user on the host, to avoid permission problems inside mounted volumes (and in particular in the edx-platform repository).

- Additional Python and system requirements are installed for convenient debugging: `ipython <https://ipython.org/>`__, `ipdb <https://pypi.org/project/ipdb/>`__, vim, telnet.

- The edx-platform `development requirements <https://github.com/openedx/edx-platform/blob/open-release/olive.master/requirements/edx/development.in>`__ are installed.


If you are using a custom ``openedx`` image, then you will need to rebuild ``openedx-dev`` every time you modify ``openedx``. To so, run::

    tutor dev dc build lms


.. _bind_mounts:

Sharing directories with containers
-----------------------------------

It may sometimes be convenient to mount container directories on the host, for instance: for editing and debugging. Tutor provides different solutions to this problem.

.. _mount_option:

Bind-mount volumes with ``--mount``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``launch``, ``run``, ``init`` and ``start`` subcommands of ``tutor dev`` and ``tutor local`` support the ``-m/--mount`` option (see :option:`tutor dev start -m`) which can take two different forms. The first is explicit::

    tutor dev start --mount=lms:/path/to/edx-platform:/openedx/edx-platform lms

And the second is implicit::

    tutor dev start --mount=/path/to/edx-platform lms

With the explicit form, the ``--mount`` option means "bind-mount the host folder /path/to/edx-platform to /openedx/edx-platform in the lms container".

If you use the explicit format, you will quickly realise that you usually want to bind-mount folders in multiple containers at a time. For instance, you will want to bind-mount the edx-platform repository in the "cms" container. To do that, write instead::

    tutor dev start --mount=lms,cms:/path/to/edx-platform:/openedx/edx-platform lms

This command line can become cumbersome and inconvenient to work with. But Tutor can be smart about bind-mounting folders to the right containers in the right place when you use the implicit form of the ``--mount`` option. For instance, the following commands are equivalent::

    # Explicit form
    tutor dev start --mount=lms,lms-worker,lms-job,cms,cms-worker,cms-job:/path/to/edx-platform:/openedx/edx-platform lms
    # Implicit form
    tutor dev start --mount=/path/to/edx-platform lms

So, when should you *not* be using the implicit form? That would be when Tutor does not know where to bind-mount your host folders. For instance, if you wanted to bind-mount your edx-platform virtual environment located in ``~/venvs/edx-platform``, you should not write ``--mount=~/venvs/edx-platform``, because that folder would be mounted in a way that would override the edx-platform repository in the container. Instead, you should write::

    tutor dev start --mount=lms:~/venvs/edx-platform:/openedx/venv lms

.. note:: Remember to setup your edx-platform repository for development! See :ref:`edx_platform_dev_env`.

Copy files from containers to the local filesystem
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes, you may want to modify some of the files inside a container for which you don't have a copy on the host. A typical example is when you want to troubleshoot a Python dependency that is installed inside the application virtual environment. In such cases, you want to first copy the contents of the virtual environment from the container to the local filesystem. To that end, Tutor provides the ``tutor dev copyfrom`` command. First, copy the contents of the container folder to the local filesystem::

    tutor dev copyfrom lms /openedx/venv ~

Then, bind-mount that folder back in the container with the ``--mount`` option (described :ref:`above <mount_option>`)::

    tutor dev start --mount lms:~/venv:/openedx/venv lms

You can then edit the files in ``~/venv`` on your local filesystem and see the changes live in your container.

Manual bind-mount to any directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning:: Manually bind-mounting volumes with the ``--volume`` option makes it difficult to simultaneously bind-mount to multiple containers. Also, the ``--volume`` options are not compatible with ``start`` commands. For an alternative, see the :ref:`mount option <mount_option>`.

The above solution may not work for you if you already have an existing directory, outside of the "volumes/" directory, which you would like mounted in one of your containers. For instance, you may want to mount your copy of the `edx-platform <https://github.com/openedx/edx-platform/>`__ repository. In such cases, you can simply use the ``-v/--volume`` `Docker option <https://docs.docker.com/storage/volumes/#choose-the--v-or---mount-flag>`__::

    tutor dev run --volume=/path/to/edx-platform:/openedx/edx-platform lms bash

Override docker-compose volumes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The above solutions require that you explicitly pass the ``-m/--mount`` options to every ``run``, ``start`` or ``init`` command, which may be inconvenient. To address these issues, you can create a ``docker-compose.override.yml`` file that will specify custom volumes to be used with all ``dev`` commands::

    vim "$(tutor config printroot)/env/dev/docker-compose.override.yml"

You are then free to bind-mount any directory to any container. For instance, to mount your own edx-platform fork::

    version: "3.7"
    services:
      lms:
        volumes:
          - /path/to/edx-platform:/openedx/edx-platform
      cms:
        volumes:
          - /path/to/edx-platform:/openedx/edx-platform
      lms-worker:
        volumes:
          - /path/to/edx-platform:/openedx/edx-platform
      cms-worker:
        volumes:
          - /path/to/edx-platform:/openedx/edx-platform

This override file will be loaded when running any ``tutor dev ..`` command. The edx-platform repo mounted at the specified path will be automatically mounted inside all LMS and CMS containers. With this file, you should no longer specify the ``-m/--mount`` option from the command line.

.. note::
    The ``tutor local`` commands load the ``docker-compose.override.yml`` file from the ``$(tutor config printroot)/env/local/docker-compose.override.yml`` directory. One-time jobs from initialisation commands load the ``local/docker-compose.jobs.override.yml`` and ``dev/docker-compose.jobs.override.yml``.

Common tasks
------------

XBlock and edx-platform plugin development
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In some cases, you will have to develop features for packages that are pip-installed next to the edx-platform. This is quite easy with Tutor. Just add your packages to the ``$(tutor config printroot)/env/build/openedx/requirements/private.txt`` file. To avoid re-building the openedx Docker image at every change, you should add your package in editable mode. For instance::

    echo "-e ./mypackage" >> "$(tutor config printroot)/env/build/openedx/requirements/private.txt"

The ``requirements`` folder should have the following content::

    env/build/openedx/requirements/
        private.txt
        mypackage/
            setup.py
            ...

You will have to re-build the openedx Docker image once::

    tutor images build openedx

You should then run the development server as usual, with ``start``. Every change made to the ``mypackage`` folder will be picked up and the development server will be automatically reloaded.

Running edx-platform unit tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's possible to run the full set of unit tests that ship with `edx-platform <https://github.com/openedx/edx-platform/>`__. To do so, run a shell in the LMS development container::

    tutor dev run lms bash

Then, run unit tests with ``pytest`` commands::

    # Run tests on common apps
    unset DJANGO_SETTINGS_MODULE
    unset SERVICE_VARIANT
    export EDXAPP_TEST_MONGO_HOST=mongodb
    pytest common
    pytest openedx
    pytest xmodule

    # Run tests on LMS
    export DJANGO_SETTINGS_MODULE=lms.envs.tutor.test
    pytest lms

    # Run tests on CMS
    export DJANGO_SETTINGS_MODULE=cms.envs.tutor.test
    pytest cms

.. note::
    Getting all edx-platform unit tests to pass on Tutor is currently a work-in-progress. Some unit tests are still failing. If you manage to fix some of these, please report your findings in the `Open edX forum <https://discuss.openedx.org/tag/tutor>`__.
