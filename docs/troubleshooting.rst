.. _troubleshooting:

Troubleshooting
===============

"Cannot start service nginx: driver failed programming external connectivity"
-----------------------------------------------------------------------------

The containerized Nginx needs to listen to ports 80 and 443 on the host. If there is already a webserver, such as Apache or Nginx, running on the host, the nginx container will not be able to start. There are two solutions:

1. Stop Apache or Nginx on the host::

       sudo systemctl stop apache2
       sudo systemctl stop nginx

However, you might now want to do that if you need a webserver for running non-Open edX related applications. In such cases...

2. Run the nginx container on different ports: you can create a ``.env`` file in the ``openedx-docker`` directory in which you indicate different ports. For instance::

       cat .env
       NGINX_HTTP_PORT=81
       NGINX_HTTPS_PORT=444

In this example, the nginx container ports would be mapped to 81 and 444, instead of 80 and 443.

You should note that with the latter solution, it is your responsibility to configure the webserver on the host as a proxy to the nginx container. See `this <https://github.com/regisb/openedx-docker/issues/69#issuecomment-425916825>`_ for http, and `this <https://github.com/regisb/openedx-docker/issues/90#issuecomment-437687294>`_ for https.

Help! The Docker containers are eating all my RAM/CPU/CHEESE
------------------------------------------------------------

You can identify which containers are consuming most resources by running::

    docker stats

"Running migrations... Killed!"
-------------------------------

The LMS and CMS containers require at least 4 GB RAM, in particular to run the Open edX SQL migrations. On Docker for Mac, by default, containers are allocated at most 2 GB of RAM. On Mac OS, if the ``make all`` command dies after displaying "Running migrations", you most probably need to increase the allocated RAM. Follow `these instructions from the official Docker documentation <https://docs.docker.com/docker-for-mac/#advanced>`_.


``Build failed running pavelib.servers.lms: Subprocess return code: 1``
-----------------------------------------------------------------------

::

    python manage.py lms --settings=development print_setting STATIC_ROOT 2>/dev/null
    ...
    Build failed running pavelib.servers.lms: Subprocess return code: 1`"

This might occur when you run a ``paver`` command. ``/dev/null`` eats the actual error, so you will have to run the command manually. Run ``make lms`` (or ``make cms``) to open a bash session and then::

    python manage.py lms --settings=development print_setting STATIC_ROOT

Of course, you should replace `development` with your own settings. The error produced should help you better understand what is happening.

``ValueError: Unable to configure handler 'local'``
---------------------------------------------------

::

    ValueError: Unable to configure handler 'local': [Errno 2] No such file or directory

This will occur if you try to run a development environment without patching the LOGGING configuration, as indicated in the `development_` section. Maybe you correctly patched the development settings, but they are not taken into account? For instance, you might have correctly defined the ``EDX_PLATFORM_SETTINGS`` environment variable, but ``paver`` uses the ``devstack`` settings (which does not patch the ``LOGGING`` variable). This is because calling ``paver lms --settings=development`` or ``paver cms --settings=development`` ignores the ``--settings`` argument. Yes, it might be considered an edx-platform bug... Instead, you should run the ``update_assets`` and ``runserver`` commands, as explained above.

"``TypeError: get_logger_config() got an unexpected keyword argument 'debug'``"
-------------------------------------------------------------------------------

This might occur when you try to run the latest version of ``edx-platform``, and not a version close to ``hawthorn.master``. It is no longer necessary to patch the ``LOGGING`` configuration in the latest ``edx-platform`` releases, as indicated in the `development_` section, so you should remove the call to ``get_logger_config`` altogether from your development settings.

The chosen default language does not display properly
-----------------------------------------------------

By default, Open edX comes with a `limited set <https://github.com/edx/edx-platform/blob/master/conf/locale/config.yaml>` of translation/localization files. To complement these languages, we add locales from the `openedx-i18n project <https://github.com/openedx/openedx-i18n/blob/master/edx-platform/locale/config-extra.yaml>`_. But not all supported locales are downloaded. In some cases, the chosen default language will not display properly because if was not packaged in either edx-platform or openedx-i18n. If you feel like your language should be packaged, please `open an issue on the openedx-i18n project <https://github.com/openedx/openedx-i18n/issues>`_.
