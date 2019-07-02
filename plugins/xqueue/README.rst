Xqueue external grading system plugin for `Tutor <https://docs.tutor.overhang.io>`_
===================================================================================

This is a plugin for `Tutor <https://docs.tutor.overhang.io>`_ that provides the Xqueue external grading system for Open edX platforms. If you don't know what it is, you probably don't need it.

Installation
------------

The plugin is currently bundled with the `binary releases of Tutor <https://github.com/overhangio/tutor/releases>`_. If you have installed Tutor from source, you will have to install this plugin from source, too::
  
    pip install tutor-xqueue

Then, to enable this plugin, run::
  
    tutor plugins enable xqueue

Configuration
-------------

- ``XQUEUE_AUTH_PASSWORD`` (default: ``"{{ 8|random_string }}"``)
- ``XQUEUE_MYSQL_PASSWORD`` (default: ``"{{ 8|random_string }}"``)
- ``XQUEUE_SECRET_KEY`` (default: ``"{{ 24|random_string }}"``)
- ``XQUEUE_DOCKER_IMAGE`` (default: ``"overhangio/openedx-xqueue:{{ TUTOR_VERSION }}"``)
- ``XQUEUE_AUTH_USERNAME`` (default: ``"lms"``)
- ``XQUEUE_MYSQL_DATABASE`` (default: ``"xqueue"``
- ``XQUEUE_MYSQL_USERNAME`` (default: ``"xqueue"``)

These values can be modified with ``tutor config save --set PARAM_NAME=VALUE`` commands.
