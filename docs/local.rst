.. _local:

Local deployment
================

This method is for deploying Open edX locally on a single server. Docker images are orchestrated with `docker-compose <https://docs.docker.com/compose/overview/>`_.

The following commands should be run inside the ``deploy/local`` folder::

    cd deploy/local

You can use these commands individually instead of running the full installation with ``make all``.

Configure
---------

::

    make configure

This is the only non-automatic step in the install process. You will be asked various questions about your Open edX platform and appropriate configuration files will be generated. If you would like to automate this step then you should run ``make configure`` interactively once. After that, you will have a ``config.json`` file at the root of the repository.

If you want to run a fully automated install, upload the ``config.json`` file to wherever you want to run Open edX, and then run ``make configure SILENT=1`` instead of ``make configure``. All values from ``config.json`` will be automatically loaded.

Download docker images
----------------------

::

    make update

You will need to download the docker images from `Docker Hub <https://hub.docker.com/r/regis/openedx/>`_. Depending on your bandwidth, this might take a long time. Minor image updates will be incremental, and thus much faster.

Database creation, migrations and collection of static assets
-------------------------------------------------------------

::

    make databases

This command should be run just once. It will create the required databases tables and apply database migrations for all applications.


If migrations are stopped with a ``Killed`` message, this certainly means the docker containers don't have enough RAM. See the :ref:`troubleshooting` section.

Collecting static assets
------------------------

::

    make assets

This command also needs to be run just once. It will make sure that static assets, such as images, stylesheets and Javascript dependencies, can be served by the nginx container.

Running Open edX
----------------

::

    make run

This will launch the various docker containers required for your Open edX platform. The LMS and the Studio will then be reachable at the domain name you specified during the configuration step. You can also access them at http://localhost and http://studio.localhost.

To stop the running containers, just hit Ctrl+C.

In production, you will probably want to daemonize the services. Instead of ``make run``, run::

    make daemonize

And then, to stop all services::

    make stop

Creating a new user with staff and admin rights
-----------------------------------------------

You will most certainly need to create a user to administer the platform. Just run::

    make create-staff-user USERNAME=yourusername EMAIL=user@email.com

You will asked to set the user password interactively.

Importing the demo course
-------------------------

On a fresh install, your platform will not have a single course. To import the `Open edX demo course <https://github.com/edx/edx-demo-course>`, run::

    make import-demo-course

Updating the course search index
--------------------------------

The course search index can be updated with::

    make reindex-courses

Run this command periodically to ensure that course search results are always up-to-date.

Additional commands
-------------------

All available commands can be listed by running::

    make help
