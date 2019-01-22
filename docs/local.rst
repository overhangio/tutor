.. _local:

Local deployment
================

This method is for deploying Open edX locally on a single server, where docker images are orchestrated with `docker-compose <https://docs.docker.com/compose/overview/>`_.

In the following, environment and data files will be generated in a user-specific project folder which will be referred to as the "**project root**". On Linux, the default project root is ``~/.local/share/tutor``. An alternative project root can be defined by passing the ``--root=...`` option to most commands, or define the ``TUTOR_ROOT=...`` environment variable.

All-in-one command
------------------

A fully-functional platform can be configured and run in one command::

    tutor local quickstart
    
But you may want to run commands one at a time: it's faster when you need to run only part of the local deployment process, and it helps you understand how your platform works. In the following we decompose the ``quickstart`` command.

Configuration
-------------

::

    tutor config interactive

This is the only non-automatic step in the install process. You will be asked various questions about your Open edX platform and appropriate configuration files will be generated. If you would like to automate this step then you should run ``tutor config interactive`` once. After that, there will be a ``config.yml`` file at the root of the project folder: this file contains all the configuration values for your platform, such as randomly generated passwords, domain names, etc.

If you want to run a fully automated install, upload the ``config.yml`` file to wherever you want to run Open edX. You can then entirely skip the configuration step.

Environment files generation
----------------------------

::

    tutor local env

This command generates environment files, such as the ``*.env.json``, ``*.auth.json`` files, the ``docker-compose.yml`` file, etc. They are generated from templates and the configuration values stored in ``config.yml``. The generated files are placed in the ``env/local`` subfolder of the project root. You may modify and delete those files at will, since they can be easily re-generated with the same ``tutor local env`` command.

Update docker images
--------------------

::

    tutor local pullimages

This downloads the latest version of the docker images from `Docker Hub <https://hub.docker.com/r/regis/openedx/>`_. Depending on your bandwidth, this might take a long time. Minor image updates will be incremental, and thus much faster.

Database management
-------------------

::

    tutor local databases

This command should be run just once. It will create the required databases tables and apply database migrations for all applications.

If migrations are stopped with a ``Killed`` message, this certainly means the docker containers don't have enough RAM. See the :ref:`troubleshooting` section.

Running Open edX
----------------

::

    tutor local start

This will launch the various docker containers required for your Open edX platform. The LMS and the Studio will then be reachable at the domain name you specified during the configuration step. You can also access them at http://localhost and http://studio.localhost.

To stop the running containers, just hit Ctrl+C.

In production, you will probably want to daemonize the services. To do so, run::

    tutor local start --detach

And then, to stop all services::

    tutor local stop

Creating a new user with staff and admin rights
-----------------------------------------------

You will most certainly need to create a user to administer the platform. Just run::

    tutor createuser --staff --superuser yourusername user@email.com

You will asked to set the user password interactively.

Importing the demo course
-------------------------

On a fresh install, your platform will not have a single course. To import the `Open edX demo course <https://github.com/edx/edx-demo-course>`_, run::

    tutor local importdemocourse

Updating the course search index
--------------------------------

The course search index can be updated with::

    tutor local indexcourses

Run this command periodically to ensure that course search results are always up-to-date.

.. _portainer:

Docker container web UI with `Portainer <https://portainer.io/>`__
------------------------------------------------------------------

Portainer is a web UI for managing docker containers. It lets you view your entire Open edX platform at a glace. Try it! It's really cool::

    tutor local portainer

.. .. image:: https://portainer.io/images/screenshots/portainer.gif
    ..:alt: Portainer demo

After launching your platfom, the web UI will be available at `http://localhost:9000 <http://localhost:9000>`_. You will be asked to define a password for the admin user. Then, select a "Local environment" to work on; hit "Connect" and select the "local" group to view all running containers.

Among many other things, you'll be able to view the logs for each container, which is really useful.

Loading different production settings for ``edx-platform``
----------------------------------------------------------

The default settings module loaded by ``edx-platform`` is ``tutor.production``. The folders ``tutor/deploy/env/openedx/settings/lms`` and ``tutor/deploy/env/openedx/settings/cms`` are mounted as ``edx-platform/lms/envs/tutor`` and ``edx-platform/cms/envs/tutor`` inside the docker containers. Thus, to use your own settings, you must do two things:

1. Copy your settings files for the lms and the cms to ``tutor/deploy/env/openedx/settings/lms/mysettings.py`` and ``tutor/deploy/env/openedx/settings/cms/mysettings.py``.
2. Load your settings by adding ``EDX_PLATFORM_SETTINGS=tutor.mysettings`` to ``tutor/deploy/local/.env``.

Of course, your settings should be compatible with the docker install. You can get some inspiration from the ``production.py`` settings modules generated by Tutor.

Additional commands
-------------------

All available commands can be listed by running::

    tutor local help

Upgrading from earlier versions
-------------------------------

Versions 1 and 2 of Tutor were organized differently: they relied on many different ``Makefile`` and ``make`` commands instead of a single ``tutor`` executable. To migrate from an earlier version, you should first stop your platform::

    make stop

Then, create the Tutor project root and move your data::

    mkdir -p $(tutor config printroot)
    mv config.json data/ $(tutor config printroot)

`Download <https://github.com/regisb/tutor/releases>`_ the latest stable release of Tutor, uncompress the file and place the ``tutor`` executable in your path.

Finally, start your platform again::

    tutor local quickstart
