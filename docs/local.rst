.. _local:

Local deployment
================

This method is for deploying Open edX locally on a single server, where docker images are orchestrated with `docker-compose <https://docs.docker.com/compose/overview/>`_.

.. _tutor_root:

In the following, environment and data files will be generated in a user-specific project folder which will be referred to as the "**project root**". On Linux, the default project root is ``~/.local/share/tutor``. An alternative project root can be defined by passing the ``--root=...`` option to the ``tutor`` command, or defining the ``TUTOR_ROOT=...`` environment variable::

    tutor --root=/path/to/tutorroot run ...
    # Or equivalently:
    export TUTOR_ROOT=/path/to/tutorroot
    tutor run ...

.. note::
    As of v10.0.0, a locally-running Open edX platform can no longer be accessed from http://localhost or http://studio.localhost. Instead, when running ``tutor local quickstart``, you must now decide whether you are running a platform that will be used in production. If not, the platform will be automatically be bound to http://local.overhang.io and http://studio.local.overhang.io, which are domain names that point to 127.0.0.1 (localhost). This change was made to facilitate internal communication between Docker containers.

Main commands
-------------

All available commands can be listed by running::

    tutor local help

All-in-one command
~~~~~~~~~~~~~~~~~~

A fully-functional platform can be configured and run in one command::

    tutor local quickstart

But you may want to run commands one at a time: it's faster when you need to run only part of the local deployment process, and it helps you understand how your platform works. In the following, we decompose the ``quickstart`` command.

Configuration
~~~~~~~~~~~~~

::

    tutor config save --interactive

This is the only non-automatic step in the installation process. You will be asked various questions about your Open edX platform and appropriate configuration files will be generated. If you would like to automate this step then you should run ``tutor config save --interactive`` once. After that, there will be a ``config.yml`` file at the root of the project folder: this file contains all the configuration values for your platform, such as randomly generated passwords, domain names, etc.

If you want to run a fully automated installation, upload the ``config.yml`` file to wherever you want to run Open edX. You can then entirely skip the configuration step.

Update docker images
~~~~~~~~~~~~~~~~~~~~

::

    tutor local dc pull

This downloads the latest version of the Docker images from `Docker Hub <https://hub.docker.com/r/overhangio/openedx/>`_. Depending on your bandwidth, this might take a long time. Minor image updates will be incremental, and thus much faster.

Running Open edX
~~~~~~~~~~~~~~~~

::

    tutor local start

This will launch the various docker containers required for your Open edX platform. The LMS and the Studio will then be reachable at the domain name you specified during the configuration step.

To stop the running containers, just hit Ctrl+C.

In production, you will probably want to daemonize the services. To do so, run::

    tutor local start --detach

And then, to stop all services::

    tutor local stop

Service initialisation
~~~~~~~~~~~~~~~~~~~~~~

::

    tutor local init

This command should be run just once. It will initialise all applications in a running platform. In particular, this will create the required databases tables and apply database migrations for all applications.

If initialisation is stopped with a ``Killed`` message, this certainly means the docker containers don't have enough RAM. See the :ref:`troubleshooting` section.

Logging
~~~~~~~

By default, logs from all containers are forwarded to the `default Docker logging driver <https://docs.docker.com/config/containers/logging/configure/>`_: this means that logs are printed to the standard output when running in non-daemon mode (``tutor local start``). In daemon mode, logs can still be accessed with ``tutor local logs`` commands (see :ref:`logging <logging>`).

In addition, all LMS and CMS logs are persisted to disk by default in the following files::

    $(tutor config printroot)/data/lms/logs/all.log
    $(tutor config printroot)/data/cms/logs/all.log

Finally, tracking logs that store `user events <https://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/index.html>`_ are persisted in the following files::

    $(tutor config printroot)/data/lms/logs/tracking.log
    $(tutor config printroot)/data/cms/logs/tracking.log

Status
~~~~~~

You can view your platform's containers::

    tutor local status

Notice the **State** column in the output. It will tell you whether each container is starting, restarting, running (``Up``), cleanly stopped (``Exit 0``), or stopped on error (``Exit N``, where N ≠ 0).

Common tasks
------------

.. _createuser:

Creating a new user with staff and admin rights
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You will most certainly need to create a user to administer the platform. Just run::

    tutor local createuser --staff --superuser yourusername user@email.com

You will be asked to set the user password interactively.

.. _democourse:

Importing the demo course
~~~~~~~~~~~~~~~~~~~~~~~~~

After a fresh installation, your platform will not have a single course. To import the `Open edX demo course <https://github.com/openedx/edx-demo-course>`_, run::

    tutor local importdemocourse

.. _settheme:

Setting a new theme
~~~~~~~~~~~~~~~~~~~

The default Open edX theme is rather bland, so Tutor makes it easy to switch to a different theme::

    tutor local settheme mytheme

Out of the box, only the default "open-edx" theme is available. We also developed `Indigo, a beautiful, customizable theme <https://github.com/overhangio/indigo>`__ which is easy to install with Tutor.

Running arbitrary ``manage.py`` commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any ``./manage.py`` command provided by Open edX can be run in a local platform deployed with Tutor. For instance, to delete a course, run::

    tutor local run cms ./manage.py cms delete_course <your_course_id>

To update the course search index, run::

    # Run this command periodically to ensure that course search results are always up-to-date.
    tutor local run cms ./manage.py cms reindex_course --all --setup

Reloading Open edX settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~

After modifying Open edX settings, for instance when running ``tutor config save``, you will want to restart the web processes of the LMS and the CMS to take into account those new settings. It is possible to simply restart the whole platform (with ``tutor local reboot``) or just a single service (``tutor local restart lms``) but that is overkill. A quicker alternative is to send the HUP signal to the uwsgi processes running inside the containers. The "openedx" Docker image comes with a convenient script that does just that. To run it, execute::

    tutor local exec lms reload-uwsgi


Customizing the deployed services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You might want to customise the docker-compose services listed in ``$(tutor config printroot)/env/local/docker-compose.yml``. To do so, you should create a ``docker-compose.override.yml`` file in that same folder::

    vim $(tutor config printroot)/env/local/docker-compose.override.yml

The values in this file will override the values from ``docker-compose.yml`` and ``docker-compose.prod.yml``, as explained in the `docker-compose documentation <https://docs.docker.com/compose/extends/#adding-and-overriding-configuration>`__.

Similarly, the job service configuration can be overridden by creating a ``docker-compose.jobs.override.yml`` file in that same folder.
