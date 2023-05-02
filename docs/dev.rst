.. _development:

Open edX development
====================

In addition to running Open edX in production, Tutor can be used for local development of Open edX. This means that it is possible to hack on Open edX without setting up a Virtual Machine. Essentially, this replaces the devstack provided by edX.

.. _edx_platform_dev_env:

First-time setup
----------------

Firstly, either :ref:`install Tutor <install>` (for development against the named releases of Open edX) or :ref:`install Tutor Nightly <nightly>` (for development against Open edX's master branches).

Then, optionally, tell Tutor to use a local fork of edx-platform.::

    tutor config save --append MOUNTS=./edx-platform

Then, launch the developer platform setup process::

    tutor images build openedx-dev
    tutor dev launch

This will perform several tasks. It will:

* build the "openedx-dev" Docker image, which is based on the "openedx" production image but is `specialized for developer usage`_ (eventually with your fork),
* stop any existing locally-running Tutor containers,
* disable HTTPS,
* set ``LMS_HOST`` to `local.overhang.io <http://local.overhang.io>`_ (a convenience domain that simply `points at 127.0.0.1 <https://dnschecker.org/#A/local.overhang.io>`_),
* prompt for a platform details (with suitable defaults),
* build an ``openedx-dev`` image,
* start LMS, CMS, supporting services, and any plugged-in services,
* ensure databases are created and migrated, and
* run service initialization scripts, such as service user creation and Waffle configuration.

Additionally, when a local clone of edx-platform is bind-mounted, it will:

* re-run setup.py,
* clean-reinstall Node modules, and
* regenerate static assets.

Once setup is complete, the platform will be running in the background:

* LMS will be accessible at `http://local.overhang.io:8000 <http://local.overhang.io:8000>`_.
* CMS will be accessible at `http://studio.local.overhang.io:8001 <http://studio.local.overhang.io:8001>`_.
* Plugged-in services should be accessible at their documented URLs.

Now, use the ``tutor dev ...`` command-line interface to manage the development environment. Some common commands are described below.

.. note::

  If you've added your edx-platform to the ``MOUNTS`` setting, you can remove at any time by running::

    tutor config save --remove MOUNTS=./edx-platform

  At any time, check your configuration by running::

    tutor config printvalue MOUNTS

  Read more about bind-mounts :ref:`below <bind_mounts>`.

Stopping the platform
---------------------

To bring down the platform's containers, simply run::

  tutor dev stop

Starting the platform back up
-----------------------------

Once first-time setup has been performed with ``launch``, the platform can be started going forward with the lighter-weight ``start -d`` command, which brings up containers *detached* (that is: in the background), but does not perform any initialization tasks::

  tutor dev start -d

Or, to start with platform with containers *attached* (that is: in the foreground, the current terminal), omit the ``-d`` flag::

  tutor dev start

When running containers attached, stop the platform with ``Ctrl+c``, or switch to detached mode using ``Ctrl+z``.

Finally, the platform can also be started back up with ``launch``. It will take longer than ``start``, but it will ensure that config is applied, databases are provisioned & migrated, plugins are fully initialized, and (if applicable) the bind-mounted edx-platform is set up. Notably, ``launch`` is idempotent, so it is always safe to run it again without risk to data. Including the ``--pullimages`` flag will also ensure that container images are up-to-date::

  tutor dev launch --pullimages

Debugging with breakpoints
--------------------------

To debug a local edx-platform repository, add a `python breakpoint <https://docs.python.org/3/library/functions.html#breakpoint>`__ with ``breakpoint()`` anywhere in the code. Then, attach to the applicable service's container by running ``start`` (without ``-d``) followed by the service's name::

  # Debugging LMS:
  tutor dev start lms

  # Or, debugging CMS:
  tutor dev start cms

Running arbitrary commands
--------------------------

To run any command inside one of the containers, run ``tutor dev run [OPTIONS] SERVICE [COMMAND] [ARGS]...``. For instance, to open a bash shell in the LMS or CMS containers::

    tutor dev run lms bash
    tutor dev run cms bash

To open a python shell in the LMS or CMS, run::

    tutor dev run lms ./manage.py lms shell
    tutor dev run cms ./manage.py cms shell

You can then import edx-platform and django modules and execute python code.

To rebuild assets, you can use the ``openedx-assets`` command that ships with Tutor::

    tutor dev run lms openedx-assets build --env=dev


.. _specialized for developer usage:

Rebuilding the openedx-dev image
--------------------------------

The ``openedx-dev`` Docker image is based on the same ``openedx`` image used by ``tutor local ...`` to run LMS and CMS. However, it has a few differences to make it more convenient for developers:

- The user that runs inside the container has the same UID as the user on the host, to avoid permission problems inside mounted volumes (and in particular in the edx-platform repository).
- Additional Python and system requirements are installed for convenient debugging: `ipython <https://ipython.org/>`__, `ipdb <https://pypi.org/project/ipdb/>`__, vim, telnet.
- The edx-platform `development requirements <https://github.com/openedx/edx-platform/blob/open-release/palm.master/requirements/edx/development.in>`__ are installed.


If you are using a custom ``openedx`` image, then you will need to rebuild ``openedx-dev`` every time you modify ``openedx``. To so, run::

    tutor images build openedx-dev

Alternatively, the image will be automatically rebuilt every time you run::

    tutor dev launch


.. _bind_mounts:

Sharing directories with containers
-----------------------------------

It may sometimes be convenient to mount container directories on the host, for instance: for editing and debugging. Tutor provides different solutions to this problem.

.. _persistent_mounts:

Persistent bind-mounted volumes with ``MOUNTS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``MOUNTS`` is a Tutor setting to bind-mount host directories both at build time and run time:

- At build time: plugins can automatically add certain directories listed in this setting to the `Docker build context <https://docs.docker.com/engine/reference/commandline/buildx_build/#build-context>`__. This makes it possible to transparently build a Docker image using a locally checked-out repository.
- At run time: host directories will be bind-mounted in running containers, using either an automatic or a manual configuration.

After some values have been added to the ``MOUNTS`` setting, all ``tutor dev`` and ``tutor local`` commands will make use of these bind-mount volumes.

Values added to ``MOUNTS`` can take one of two forms. The first is explicit::

    tutor config save --append MOUNTS=lms:/path/to/edx-platform:/openedx/edx-platform

The second is implicit::

    tutor config save --append MOUNTS=/path/to/edx-platform

With the explicit form, the setting means "bind-mount the host folder /path/to/edx-platform to /openedx/edx-platform in the lms container at run time".

If you use the explicit format, you will quickly realise that you usually want to bind-mount folders in multiple containers at a time. For instance, you will want to bind-mount the edx-platform repository in the "cms" container, but also the "lms-worker" and "cms-worker" containers. To do that, write instead::

    # each service is added to a coma-separated list
    tutor config save --append MOUNTS=lms,cms,lms-worker,cms-worker:/path/to/edx-platform:/openedx/edx-platform

This command line is a bit cumbersome. In addition, with this explicit form, the edx-platform repository will *not* be added to the build context at build time. But Tutor can be smart about bind-mounting folders to the right containers in the right place when you use the implicit form of the ``MOUNTS`` setting. For instance, the following implicit form can be used instead of the explicit form above::

    tutor config save --append MOUNTS=/path/to/edx-platform

With this implicit form, the edx-platform repo will be bind-mounted in the containers at run time, just like with the explicit form. But in addition, the edx-platform will also automatically be added to the Docker image at build time.

So, when should you *not* be using the implicit form? That would be when Tutor does not know where to bind-mount your host folders. For instance, if you wanted to bind-mount your edx-platform virtual environment located in ``~/venvs/edx-platform``, you should not write ``--append MOUNTS=~/venvs/edx-platform``, because that folder would be mounted in a way that would override the edx-platform repository in the container. Instead, you should write::

    tutor config save --append MOUNTS=lms:~/venvs/edx-platform:/openedx/venv

.. note:: Remember to setup your edx-platform repository for development! See :ref:`edx_platform_dev_env`.

Copy files from containers to the local filesystem
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes, you may want to modify some of the files inside a container for which you don't have a copy on the host. A typical example is when you want to troubleshoot a Python dependency that is installed inside the application virtual environment. In such cases, you want to first copy the contents of the virtual environment from the container to the local filesystem. To that end, Tutor provides the ``tutor dev copyfrom`` command. First, copy the contents of the container folder to the local filesystem::

    tutor dev copyfrom lms /openedx/venv ~

Then, bind-mount that folder back in the container with the ``MOUNTS`` setting (described :ref:`above <persistent_mounts>`)::

    tutor config save --append MOUNTS=lms:~/venv:/openedx/venv

You can then edit the files in ``~/venv`` on your local filesystem and see the changes live in your "lms" container.

Manual bind-mount to any directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning:: Manually bind-mounting volumes with the ``--volume`` option makes it difficult to simultaneously bind-mount to multiple containers. Also, the ``--volume`` options are not compatible with ``start`` commands. For an alternative, see the :ref:`persistent mounts <persistent_mounts>`.

The above solution may not work for you if you already have an existing directory, outside of the "volumes/" directory, which you would like mounted in one of your containers. For instance, you may want to mount your copy of the `edx-platform <https://github.com/openedx/edx-platform/>`__ repository. In such cases, you can simply use the ``-v/--volume`` `Docker option <https://docs.docker.com/storage/volumes/#choose-the--v-or---mount-flag>`__::

    tutor dev run --volume=/path/to/edx-platform:/openedx/edx-platform lms bash

Override docker-compose volumes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adding items to the ``MOUNTS`` setting effectively adds new bind-mount volumes to the ``docker-compose.yml`` files. But you might want to have more control over your volumes, such as adding read-only options, or customising other fields of the different services. To address these issues, you can create a ``docker-compose.override.yml`` file that will specify custom volumes to be used with all ``dev`` commands::

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

This override file will be loaded when running any ``tutor dev ..`` command. The edx-platform repo mounted at the specified path will be automatically mounted inside all LMS and CMS containers.

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
