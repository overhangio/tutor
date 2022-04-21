.. _development:

Open edX development
====================

In addition to running Open edX in production, Tutor can be used for local development of Open edX. This means that it is possible to hack on Open edX without setting up a Virtual Machine. Essentially, this replaces the devstack provided by edX.


First-time setup
----------------

First, ensure you have already `installed Tutor <install.rst>`_ (for development against the named releases of Open edX) or `Tutor Nightly <nightly.rst>`_ (for development against Open edX's master branches).

Then, launch the developer platform setup process::

    tutor dev quickstart

This will perform several tasks for you. It will:

* stop any existing locally-running Tutor containers,

* disable HTTPS,

* set your ``LMS_HOST`` to `local.overhang.io <http://local.overhang.io>`_ (a convenience domain that simply `points at 127.0.0.1 <https://dnschecker.org/#A/local.overhang.io>`_),

* prompt for a platform details (with suitable defaults),

* build an ``openedx-dev`` image, which is based ``openedx`` production image but is `specialized for developer usage`_,

* start LMS, CMS, supporting services, and any plugged-in services,

* ensure databases are created and migrated, and

* run service initialization scripts, such as service user creation and Waffle configuration.

Once setup is complete, the platform will be running in the background:

* LMS will be accessible at `http://local.overhang.io:8000 <http://local.overhang.io:8000>`_.
* CMS will be accessible at `http://studio.local.overhang.io:8001 <http://studio.local.overhang.io:8001>`_.
* Plugged-in services should be accessible at their documented URLs.


Stopping the platform
---------------------

To bring down your platform's containers, simply run::

  tutor dev stop


Starting the platform back up
-----------------------------

Once you have used ``quickstart`` once, you can start the platform in the future with the lighter-weight ``start`` command, which brings up containers but does not perform any initialization tasks::

  tutor dev start     # Run platform in the same terminal ("attached")
  tutor dev start -d  # Or, run platform the in the background ("detached")

Nonetheless, ``quickstart`` is idempotent, so it is always safe to run it again in the future without risk to your data. In fact, you may find it useful to use this command as a one-stop-shop for pulling images, running migrations, initializing new plugins you have enabled, and/or executing any new initialization steps that may have been introduced since you set up Tutor::

  tutor dev quickstart --pullimages


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

    tutor dev run lms openedx-assets build --env=dev


.. _specialized for developer usage: 

Rebuilding the openedx-dev image
--------------------------------

The ``openedx-dev`` Docker image is based on the same ``openedx`` image used by ``tutor local ...`` to run LMS and CMS. However, it has a few differences to make it more convenient for developers:

- The user that runs inside the container has the same UID as the user on the host, to avoid permission problems inside mounted volumes (and in particular in the edx-platform repository).

- Additional Python and system requirements are installed for convenient debugging: `ipython <https://ipython.org/>`__, `ipdb <https://pypi.org/project/ipdb/>`__, vim, telnet.

- The edx-platform `development requirements <https://github.com/openedx/edx-platform/blob/open-release/maple.master/requirements/edx/development.in>`__ are installed.


If you are using a custom ``openedx`` image, then you will need to rebuild ``openedx-dev`` every time you modify ``openedx``. To so, run::

    tutor dev dc build lms


.. _bind_mounts:

Sharing directories with containers
-----------------------------------

It may sometimes be convenient to mount container directories on the host, for instance: for editing and debugging. Tutor provides different solutions to this problem.

.. _mount_option:

Bind-mount volumes with ``--mount``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``quickstart``, ``run``, ``init`` and ``start`` subcommands of ``tutor dev`` and ``tutor local`` support the ``-m/--mount`` option (see :option:`tutor dev start -m`) which can take two different forms. The first is explicit::

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

Bind-mount from the "volumes/" directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning:: Bind-mounting volumes with the ``bindmount`` command is no longer the default, recommended way of bind-mounting volumes from the host. Instead, see the :ref:`mount option <mount_option>`.

Tutor makes it easy to create a bind-mount from an existing container. First, copy the contents of a container directory with the ``bindmount`` command. For instance, to copy the virtual environment of the "lms" container::

    tutor dev bindmount lms /openedx/venv

This command recursively copies the contents of the ``/opendedx/venv`` directory to ``$(tutor config printroot)/volumes/venv``. The code of any Python dependency can then be edited -- for instance, you can then add a ``import ipdb; ipdb.set_trace()`` statement for step-by-step debugging, or implement a custom feature.

Then, bind-mount the directory back in the container with the ``--mount`` option::

		tutor dev start --mount=lms:$(tutor config printroot)/volumes/venv:/openedx/venv lms

.. note::
    The ``bindmount`` command and the ``--mount=...`` option syntax are available both for the ``tutor local`` and ``tutor dev`` commands.

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

.. _edx_platform_dev_env:

Setting up a development environment for edx-platform
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Following the instructions :ref:`above <bind_mounts>` on how to bind-mount directories from the host above, you may mount your own `edx-platform <https://github.com/openedx/edx-platform/>`__ fork in your containers by running::

    tutor dev start -d --mount=/path/to/edx-platform lms

But to achieve that, you will have to make sure that your fork works with Tutor.

First of all, you should make sure that you are working off the latest release tag (unless you are running the Tutor :ref:`nightly <nightly>` branch). See the :ref:`fork edx-platform section <edx_platform_fork>` for more information.

Then, you should run the following commands::

    # Run bash in the lms container
    tutor dev run --mount=/path/to/edx-platform lms bash

    # Compile local python requirements
    pip install --requirement requirements/edx/development.txt

    # Install nodejs packages in node_modules/
    npm install

    # Rebuild static assets
    openedx-assets build --env=dev

After running all these commands, your edx-platform repository will be ready for local development. To debug a local edx-platform repository, you can then add a ``import ipdb; ipdb.set_trace()`` breakpoint anywhere in your code and run::

    tutor dev start --mount=/path/to/edx-platform lms

If LMS isn't running, this will start it in your terminal. If an LMS container is already running background, this command will stop it, recreate it, and attach your terminal to it. Later, to detach your terminal without stopping the container, just hit ``Ctrl+z``.

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

    # Run tests on LMS
    export DJANGO_SETTINGS_MODULE=lms.envs.tutor.test
    pytest lms

    # Run tests on CMS
    export DJANGO_SETTINGS_MODULE=cms.envs.tutor.test
    pytest cms

.. note::
    Getting all edx-platform unit tests to pass on Tutor is currently a work-in-progress. Some unit tests are still failing. If you manage to fix some of these, please report your findings in the `Tutor forums <https://discuss.overhang.io>`__.
