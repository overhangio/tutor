Step-by-step install
====================

Configure
---------

::

    make configure

This is the only non-automatic step in the install process. You will be asked various questions about your Open edX platform and appropriate configuration files will be generated. If you would like to automate this step then you should run ``make configure`` interactively once. After that, you will have a ``config.json`` file at the root of the repository. Just upload it to wherever you want to run Open edX and then run ``make configure SILENT=1`` instead of ``make configure``. All values from ``config.json`` will be automatically loaded.

Download
--------

::

    make update

You will need to download the docker images from `Docker Hub <https://hub.docker.com/r/regis/openedx/>`_. Depending on your bandwidth, this might take a long time. Minor image updates will be incremental, and thus much faster.

Database creation, migrations and collection of static assets
-------------------------------------------------------------

::

    make databases
    make assets

These commands should be run just once. They will create the required databases tables, apply database migrations and make sure that static assets, such as images, stylesheets and Javascript dependencies, can be served by the nginx container.

If migrations are stopped with a ``Killed`` message, this certainly means the docker containers don't have enough RAM. See the :ref:`troubleshooting` section.

Running Open edX
----------------

::

    make run

This will launch the various docker containers required for your Open edX platform. The LMS and the Studio will then be reachable at the domain name you specified during the configuration step. You can also access them at http://localhost and http://studio.localhost.

Additional commands
-------------------

All available commands can be listed by running::

    make help

Creating a new user with staff and admin rights
-----------------------------------------------

You will most certainly need to create a user to administer the platform. Just run::

    make create-staff-user USERNAME=yourusername EMAIL=user@email.com

You will asked to set the user password interactively.

Importing the demo course
-------------------------

On a fresh install, your platform will not have a single course. To import the `Open edX demo course <https://github.com/edx/edx-demo-course>`, run::

    make import-demo-course

Daemonizing
-----------

In production, you will probably want to daemonize the services. Instead of ``make run``, run::

    make daemonize

And then, to stop all services::

    make stop

Updating the course search index
--------------------------------

The course search index can be updated with::

    make reindex-courses

Run this command periodically to ensure that course search results are always up-to-date.

Logging
-------

To view the logs from all containers use the `docker-compose logs <https://docs.docker.com/compose/reference/logs/>`_ command::

    docker-compose logs -f

To view the logs from just one container, for instance the web server::

    docker-compose logs -f nginx

The last commands produce the logs since the creation of the containers, which can be a lot. Similar to a ``tail -f``, you can run::

    docker-compose logs --tail=0 -f

Debugging
---------

Open a bash shell in the lms or the cms::

    make lms
    make cms

Open a python shell in the lms or the cms::

    make lms-python
    make cms-python
