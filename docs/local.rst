.. _local:

Local deployment
================

This method is for deploying Open edX locally on a single server, where docker images are orchestrated with `docker-compose <https://docs.docker.com/compose/overview/>`_.

In the following, environment and data files will be generated in a user-specific project folder which will be referred to as the "**project root**". On Linux, the default project root is ``~/.local/share/tutor``. An alternative project root can be defined by passing the ``--root=...`` option to most commands, or define the ``TUTOR_ROOT=...`` environment variable.

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

    tutor local pullimages

This downloads the latest version of the docker images from `Docker Hub <https://hub.docker.com/r/overhangio/openedx/>`_. Depending on your bandwidth, this might take a long time. Minor image updates will be incremental, and thus much faster.

Running Open edX
~~~~~~~~~~~~~~~~

::

    tutor local start

This will launch the various docker containers required for your Open edX platform. The LMS and the Studio will then be reachable at the domain name you specified during the configuration step. You can also access them at http://localhost and http://studio.localhost.

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

Creating a new user with staff and admin rights
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You will most certainly need to create a user to administer the platform. Just run::

    tutor local createuser --staff --superuser yourusername user@email.com

You will asked to set the user password interactively.

Importing the demo course
~~~~~~~~~~~~~~~~~~~~~~~~~

After a fresh installation, your platform will not have a single course. To import the `Open edX demo course <https://github.com/edx/edx-demo-course>`_, run::

    tutor local importdemocourse

Running arbitrary ``manage.py`` commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any ``./manage.py`` command provided by Open edX can be run in a local platform deployed with Tutor. For instance, to delete a course, run::
    
    tutor local run cms ./manage.py cms delete_course <your_course_id>

To update the course search index, run::

    # Run this command periodically to ensure that course search results are always up-to-date.
    tutor local run cms ./manage.py cms reindex_course --all --setup

.. _portainer:

Docker container web UI with `Portainer <https://portainer.io/>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Portainer is a web UI for managing docker containers. It lets you view your entire Open edX platform at a glace. Try it! It's really cool::

    tutor local portainer

.. .. image:: https://portainer.io/images/screenshots/portainer.gif
    ..:alt: Portainer demo

After launching your platfom, the web UI will be available at `http://localhost:9000 <http://localhost:9000>`_. You will be asked to define a password for the admin user. Then, select a "Local environment" to work on; hit "Connect" and select the "local" group to view all running containers.

Among many other things, you'll be able to view the logs for each container, which is really useful.

Recipes
-------

.. _web_proxy:

Running Open edX behind a web proxy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The containerized web server (nginx) needs to listen to ports 80 and 443 on the host. If there is already a webserver running on the host, such as Apache or Nginx, the nginx container will not be able to start. Tutor supports running behind a web proxy. To do so, add the following configuration::

       tutor config save --set WEB_PROXY=true --set NGINX_HTTP_PORT=81 --set NGINX_HTTPS_PORT=444

In this example, the nginx container ports would be mapped to 81 and 444, instead of 80 and 443. You must then configure the web proxy on the host. Basic configuration files are provided by Tutor which can be used directly by your web proxy.

For nginx::

    sudo ln -s "$(tutor config printroot)/env/local/proxy/nginx/openedx.conf" /etc/nginx/sites-enabled/
    sudo systemctl reload nginx

For apache::

    sudo a2enmod proxy
    sudo a2enmod proxy_http
    sudo ln -s "$(tutor config printroot)/env/local/proxy/apache2/openedx.conf" /etc/apache2/sites-enabled/
    sudo systemctl reload apache2

If you have configured your platform to use SSL/TLS certificates for HTTPS access, the generation and renewal of certificates will not be managed by Tutor: you are supposed to take care of it yourself. Suggestions for generating and renewing these certificates with `Let's Encrypt <https://letsencrypt.org/>`_ are given by::

    tutor local https create
    tutor local https renew

Running multiple Open edX platforms on a single server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With Tutor, it is easy to run multiple Open edX instances on a single server. To do so, the following configuration parameters must be different for all platforms:

- ``TUTOR_ROOT``: so that configuration, environment and data are not mixed up between platforms.
- ``LOCAL_PROJECT_NAME``: the various docker-compose projects cannot share the same name.
- ``NGINX_HTTP_PORT``, ``NGINX_HTTPS_PORT``: ports cannot be shared by two different containers.
- ``LMS_HOST``, ``CMS_HOST``: the different platforms must be accessible from different domain (or subdomain) names.

In addition, a web proxy must be setup on the host, as described :ref:`above <web_proxy>`.

As an example, here is how to launch two different platforms, with nginx running as a web proxy::

    # platform 1
    export TUTOR_ROOT=~/openedx/site1
    tutor config save --interactive --set WEB_PROXY=true --set LOCAL_PROJECT_NAME=tutor_site1 --set NGINX_HTTP_PORT=81 --set NGINX_HTTPS_PORT=481
    tutor local quickstart
    sudo ln -s "$(tutor config printroot)/env/local/proxy/nginx/openedx.conf" /etc/nginx/sites-enabled/site1.conf

    # platform 2
    export TUTOR_ROOT=~/openedx/site2
    tutor config save --interactive --set WEB_PROXY=true --set LOCAL_PROJECT_NAME=tutor_site2 --set NGINX_HTTP_PORT=82 --set NGINX_HTTPS_PORT=482
    tutor local quickstart
    sudo ln -s "$(tutor config printroot)/env/local/proxy/nginx/openedx.conf" /etc/nginx/sites-enabled/site2.conf

You should then have two different platforms, completely isolated from one another, running on the same server.

Loading different production settings for ``edx-platform``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default settings module loaded by ``edx-platform`` is ``tutor.production``. The folders ``$(tutor config printroot)/env/apps/openedx/settings/lms`` and ``$(tutor config printroot)/env/apps/openedx/settings/cms`` are mounted as ``edx-platform/lms/envs/tutor`` and ``edx-platform/cms/envs/tutor`` inside the docker containers. Thus, to use your own settings, you must do two things:

1. Copy your settings files for the lms and the cms to ``$(tutor config printroot)/env/apps/openedx/settings/lms/mysettings.py`` and ``$(tutor config printroot)/env/apps/openedx/settings/cms/mysettings.py``.
2. Load your settings by adding ``EDX_PLATFORM_SETTINGS=tutor.mysettings`` to ``$(tutor config printroot)/env/local/.env``.

Of course, your settings should be compatible with the docker installation. You can get some inspiration from the ``production.py`` settings modules generated by Tutor, or just import it as a base by adding ``from .production import *`` at the top of ``mysettings.py``.


Upgrading from earlier versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Versions 1 and 2 of Tutor were organized differently: they relied on many different ``Makefile`` and ``make`` commands instead of a single ``tutor`` executable. To migrate from an earlier version, you should first stop your platform::

    make stop

Then, create the Tutor project root and move your data::

    mkdir -p "$(tutor config printroot)"
    mv config.json data/ "$(tutor config printroot)"

`Download <https://github.com/overhangio/tutor/releases>`_ the latest stable release of Tutor, uncompress the file and place the ``tutor`` executable in your path.

Finally, start your platform again::

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
    
    