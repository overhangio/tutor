.. _local:

Local deployment
================

This method is for deploying Open edX locally on a single server, where docker images are orchestrated with `docker-compose <https://docs.docker.com/compose/overview/>`_.

.. note::
    As of v16.0.0, Tutor now uses the ``docker compose`` subcommand instead of the separate ``docker-compose`` command.

.. _tutor_root:

In the following, environment and data files will be generated in a user-specific project folder which will be referred to as the "**project root**". On Linux, the default project root is ``~/.local/share/tutor``. An alternative project root can be defined by passing the ``--root=...`` option to the ``tutor`` command, or defining the ``TUTOR_ROOT=...`` environment variable::

    tutor --root=/path/to/tutorroot run ...
    # Or equivalently:
    export TUTOR_ROOT=/path/to/tutorroot
    tutor run ...

Main commands
-------------

All available commands can be listed by running::

    tutor local --help

All-in-one command
~~~~~~~~~~~~~~~~~~

A fully-functional platform can be configured and run in one command::

    tutor local launch

But you may want to run commands one at a time: it's faster when you need to run only part of the local deployment process, and it helps you understand how your platform works. In the following, we decompose the ``launch`` command.

Configuration
~~~~~~~~~~~~~

::

    tutor config save --interactive

This is the only non-automatic step in the installation process. You will be asked various questions about your Open edX platform and appropriate configuration files will be generated. If you would like to automate this step then you should run ``tutor config save --interactive`` once. This will generate a ``config.yml`` file in the **project root**. This file contains all the configuration values for your platform, such as randomly generated passwords, domain names, etc. The location of the **project root** can be found by running ``tutor config printroot``. See :ref:`section above <tutor_root>`.

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

    tutor local do init

This command should be run just once. It will initialise all applications in a running platform. In particular, this will create the required databases tables and apply database migrations for all applications.

If initialisation is stopped with a ``Killed`` message, this certainly means the docker containers don't have enough RAM. See the :ref:`troubleshooting` section.

Logging
~~~~~~~

By default, logs from all containers are forwarded to the `default Docker logging driver <https://docs.docker.com/config/containers/logging/configure/>`_: this means that logs are printed to the standard output when running in non-daemon mode (``tutor local start``). In daemon mode, logs can still be accessed with ``tutor local logs`` commands (see :ref:`logging <logging>`).

In addition, all LMS and CMS logs are persisted to disk by default in the following files::

    $(tutor config printroot)/data/lms/logs/all.log
    $(tutor config printroot)/data/cms/logs/all.log

Finally, tracking logs that store `user events <https://docs.openedx.org/en/latest/developers/references/internal_data_formats/tracking_logs/index.html>`_ are persisted in the following files::

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

    tutor local do createuser --staff --superuser yourusername user@email.com

You will be asked to set the user password interactively.

.. _democourse:

Importing the demo course
~~~~~~~~~~~~~~~~~~~~~~~~~

After a fresh installation, your platform will not have a single course. To import the `Open edX demo course <https://github.com/openedx/edx-demo-course>`_, run::

    tutor local do importdemocourse

.. _settheme:

Setting a new theme
~~~~~~~~~~~~~~~~~~~

The default Open edX theme is rather bland, so Tutor makes it easy to switch to a different theme::

    tutor local do settheme mytheme

Out of the box, only the default "open-edx" theme is available. We also developed `Indigo, a beautiful, customizable theme <https://github.com/overhangio/indigo>`__ which is easy to install with Tutor.

Changing the mysql charset and collation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: This command has been tested only for users upgrading from Quince. While it is expected to work for users on earlier releases, please use it with caution as it has not been tested with those versions.

The database's charset and collation might not support specific characters or emojis. Tutor will function normally without this change unless specific characters are used in the instance.

.. warning:: This change is potentially irreversible. It is recommended to make a backup of the MySQL database. See the :ref:`database dump instructions <database_dumps>` to create a DB dump.

To change the charset and collation of all the tables in the openedx database, run::

    tutor local do convert-mysql-utf8mb4-charset

Alternatively, to change the charset and collation of certain tables or to exclude certain tables, the ``--include`` or ``--exclude`` options can be used. These options take comma separated names of tables/apps with no space in-between. To upgrade the ``courseware_studentmodule`` and ``courseware_studentmodulehistory`` tables, run::

    tutor local do convert-mysql-utf8mb4-charset --include=courseware_studentmodule,courseware_studentmodulehistory

Tutor performs pattern matching from the start of the table name so just the name of the app is enough to include/exclude all the tables under that app. To upgrade all the tables in the database except the ones under the student and wiki apps, run::

    tutor local do convert-mysql-utf8mb4-charset --exclude=student,wiki

In the above command, all the tables whose name starts with either student or wiki will be excluded from the upgrade process.

By default, only the tables in the openedx database are changed. For upgrading tables in any additional databases used by plugins, the ``--database`` option can be used to upgrade them. To upgrade all the tables in the discovery database, run::

    tutor local do convert-mysql-utf8mb4-charset --database=discovery

.. _update_mysql_authentication_plugin:

Updating the authentication plugin of MySQL users
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As of MySQL v8.4.0, the ``mysql_native_password`` authentication plugin has been deprecated. Users created with this authentication plugin should ideally be updated to use the latest ``caching_sha2_password`` authentication plugin.

Tutor makes it easy do so with this handy command::

    tutor local do update-mysql-authentication-plugin USERNAME

The password will not be required for official plugins that have database users as tutor can infer it from the config. If the password cannot be found by tutor, you will be prompted to enter the password interactively. Alternatively, the password can also be provided as an option::

    tutor local do update-mysql-authentication-plugin USERNAME --password=PASSWORD

.. warning:: Since we are generating a new password hash, whatever password is entered here will be considered as the new password for the user. Please make similar changes to any connection strings to avoid database connection issues.

To update the database users for a vanilla tutor installation::

    tutor local do update-mysql-authentication-plugin $(tutor config printvalue OPENEDX_MYSQL_USERNAME)
    tutor local do update-mysql-authentication-plugin $(tutor config printvalue MYSQL_ROOT_USERNAME)


Running arbitrary ``manage.py`` commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any ``./manage.py`` command provided by Open edX can be run in a local platform deployed with Tutor. For instance, to delete a course, run::

    tutor local run cms ./manage.py cms delete_course <your_course_id>

To update the course search index, run::

    # Run this command periodically to ensure that course search results are always up-to-date.
    tutor local run cms ./manage.py cms reindex_course --all --setup

Reloading Open edX settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~

After modifying Open edX settings, for instance when running ``tutor config save``, you will want to restart the web processes of the LMS and the CMS to take into account those new settings. It is possible to simply restart the whole platform (with ``tutor local reboot``) or just a single service (``tutor local restart lms``) but that is overkill. A quicker alternative is to restart just the web server process running inside the containers. This can be done by updating a file in the granian's "--reload-paths" config. The "openedx" Docker image comes with a convenient script that does just that. To run it, execute::

    tutor local exec lms reload-granian


Customizing the deployed services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You might want to customise the docker-compose services listed in ``$(tutor config printroot)/env/local/docker-compose.yml``. To do so, you should create a ``docker-compose.override.yml`` file in that same folder::

    vim $(tutor config printroot)/env/local/docker-compose.override.yml

The values in this file will override the values from ``docker-compose.yml`` as explained in the `docker-compose documentation <https://docs.docker.com/compose/extends/#adding-and-overriding-configuration>`__.

Services defined in ``docker-compose.prod.yml`` can be overriden in a ``docker-compose.prod.override.yml`` file in that same folder.

Similarly, the job service configuration can be overridden by creating a ``docker-compose.jobs.override.yml`` file in that same folder.
