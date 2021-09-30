.. _local:

Local deployment
================

This method is for deploying Open edX locally on a single server, where docker images are orchestrated with `docker-compose <https://docs.docker.com/compose/overview/>`_.

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

But you may want to run commands one at a time: it's faster when you need to run only part of the local deployment process, and it helps you understand how your platform works. In the following we decompose the ``quickstart`` command.

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


Extra commands
--------------

.. _createuser:

Creating a new user with staff and admin rights
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You will most certainly need to create a user to administer the platform. Just run::

    tutor local createuser --staff --superuser yourusername user@email.com

You will asked to set the user password interactively.

.. _democourse:

Importing the demo course
~~~~~~~~~~~~~~~~~~~~~~~~~

After a fresh installation, your platform will not have a single course. To import the `Open edX demo course <https://github.com/edx/edx-demo-course>`_, run::

    tutor local importdemocourse

.. _settheme:

Setting a new theme
~~~~~~~~~~~~~~~~~~~

The default Open edX theme is rather bland, so Tutor makes it easy to switch to a different theme::

    tutor local settheme mytheme $(tutor config printvalue LMS_HOST) $(tutor config printvalue CMS_HOST)

Notice that we pass the hostnames of the LMS and the CMS to the ``settheme`` command: this is because in Open edX, themes are assigned per domain name.

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

.. _portainer:

Docker container web UI with `Portainer <https://portainer.io/>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Portainer is a web UI for managing docker containers. It lets you view your entire Open edX platform at a glace. Try it! It's really cool::

    docker run --rm \
        --volume=/var/run/docker.sock:/var/run/docker.sock \
        --volume=/tmp/portainer:/data \
        -p 9000:9000 \
        portainer/portainer:latest --bind=:9000

.. .. image:: https://portainer.io/images/screenshots/portainer.gif
    ..:alt: Portainer demo

You can then view the portainer UI at `http://localhost:9000 <http://localhost:9000>`_. You will be asked to define a password for the admin user. Then, select a "Local environment" to work on; hit "Connect" and select the "local" group to view all running containers.

Among many other things, you'll be able to view the logs for each container, which is really useful.

Guides
------

.. _web_proxy:

Running Open edX behind a web proxy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The containerized web server (`Caddy <https://caddyserver.com/>`__) needs to listen to ports 80 and 443 on the host in order to serve requests. If there is already a webserver running on the host, such as Apache or Nginx, the caddy container will not be able to start. Tutor supports running behind a web proxy. To do so, add the following configuration::

       tutor config save --set RUN_CADDY=false --set NGINX_HTTP_PORT=81

In this example, the nginx container port would be mapped to 81 instead of 80. You must then configure the web proxy on the host. As of v11.0.0, configuration files are no longer provided for automatic configuration of your web proxy. Basically, you should setup a reverse proxy to `localhost:NGINX_HTTP_PORT` from the following hosts: LMS_HOST, preview.LMS_HOST, CMS_HOST, as well as any additional host exposed by your plugins.

.. warning::
    In this setup, the Nginx HTTP port will be exposed to the world. Make sure to configure your server firewall to block unwanted connections to your server's `NGINX_HTTP_PORT`. Alternatively, you can configure the Nginx container to accept only local connections::

        tutor config save --set NGINX_HTTP_PORT=127.0.0.1:81

The same solution applies if you would like to enable https in Tutor, but with your own custom certificates instead of Let's Encrypt's. In that case, you should keep ``ENABLE_HTTPS=true``, disable Caddy (``RUN_CADDY=false``) and configure your own web proxy on the host (or elsewhere) to serve requests using your own certificates.

Running multiple Open edX platforms on a single server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With Tutor, it is easy to run multiple Open edX instances on a single server. To do so, the following configuration parameters must be different for all platforms:

- ``TUTOR_ROOT``: so that configuration, environment and data are not mixed up between platforms.
- ``LOCAL_PROJECT_NAME``: the various docker-compose projects cannot share the same name.
- ``NGINX_HTTP_PORT``: ports cannot be shared by two different containers.
- ``LMS_HOST``, ``CMS_HOST``: the different platforms must be accessible from different domain (or subdomain) names.

In addition, a web proxy must be setup on the host, as described :ref:`above <web_proxy>`.

Loading different production settings for ``edx-platform``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default settings module loaded by ``edx-platform`` is ``tutor.production``. The folders ``$(tutor config printroot)/env/apps/openedx/settings/lms`` and ``$(tutor config printroot)/env/apps/openedx/settings/cms`` are mounted as ``edx-platform/lms/envs/tutor`` and ``edx-platform/cms/envs/tutor`` inside the docker containers. Thus, to use your own settings, you must do two things:

1. Copy your settings files for the lms and the cms to ``$(tutor config printroot)/env/apps/openedx/settings/lms/mysettings.py`` and ``$(tutor config printroot)/env/apps/openedx/settings/cms/mysettings.py``.
2. Load your settings by adding ``TUTOR_EDX_PLATFORM_SETTINGS=tutor.mysettings`` to ``$(tutor config printroot)/env/local/.env``.

Of course, your settings should be compatible with the docker installation. You can get some inspiration from the ``production.py`` settings modules generated by Tutor, or just import it as a base by adding ``from .production import *`` at the top of ``mysettings.py``.

Upgrading from earlier versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Upgrading from v3+
******************

Just upgrade Tutor using your :ref:`favorite installation method <install>` and run quickstart again::

    tutor local quickstart

Upgrading from v1 or v2
***********************

Versions 1 and 2 of Tutor were organized differently: they relied on many different ``Makefile`` and ``make`` commands instead of a single ``tutor`` executable. To migrate from an earlier version, you should first stop your platform::

    make stop

Then, install Tutor using one of the :ref:`installation methods <install>`. Then, create the Tutor project root and move your data::

    mkdir -p "$(tutor config printroot)"
    mv config.json data/ "$(tutor config printroot)"

Finally, launch your platform with::

    tutor local quickstart

Backups/Migrating to a different server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With Tutor, all data are stored in a single folder. This means that it's extremely easy to migrate an existing platform to a different server. For instance, it's possible to configure a platform locally on a laptop, and then move this platform to a production server.

1. Make sure `tutor` is installed on both servers with the same version.
2. Stop any running platform on server 1::

    tutor local stop

3. Transfer the configuration, environment and platform data from server 1 to server 2::

    rsync -avr "$(tutor config printroot)/" username@server2:/tmp/tutor/

4. On server 2, move the data to the right location::

    mv /tmp/tutor "$(tutor config printroot)"

5. Start the instance with::

    tutor local start -d

Making database dumps
~~~~~~~~~~~~~~~~~~~~~

To dump all data from the MySQL and Mongodb databases used on the platform, run the following commands::

    tutor local exec -e MYSQL_ROOT_PASSWORD="$(tutor config printvalue MYSQL_ROOT_PASSWORD)" mysql \
        sh -c 'mysqldump --all-databases --password=$MYSQL_ROOT_PASSWORD > /var/lib/mysql/dump.sql'
    tutor local exec mongodb mongodump --out=/data/db/dump.mongodb

The ``dump.sql`` and ``dump.mongodb`` files will be located in ``$(tutor config printroot)/data/mysql`` and ``$(tutor config printroot)/data/mongodb``.

Customizing the deployed services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You might want to customize the docker-compose services listed in ``$(tutor config printroot)/env/local/docker-compose.yml``. To do so, you should create a ``docker-compose.override.yml`` file in that same folder::

    vim $(tutor config printroot)/env/local/docker-compose.override.yml

The values in this file will override the values from ``docker-compose.yml`` and ``docker-compose.prod.yml``, as explained in the `docker-compose documentation <https://docs.docker.com/compose/extends/#adding-and-overriding-configuration>`__.

Similarly, the job service configuration can be overridden by creating a ``docker-compose.jobs.override.yml`` file in that same folder.
