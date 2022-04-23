.. _arm64:

==================================
Running Tutor on ARM-based systems
==================================

Tutor can be used on ARM64 systems, although support for that platform is currently experimental.

In any case, start by :ref:`installing <install>` Tutor and its dependencies (e.g. Docker) onto your system.

.. note:: For Open edX developers, if you want to use the :ref:`nightly <nightly>` version of Tutor to "run master", install Tutor using git and check out the ``nightly`` branch of Tutor at this point. See the :ref:`nightly documentation <nightly>` for details.

Then, follow one of the options in this tutorial:

The easy way: tutor-contrib-arm64
=================================

The easiest way to start using Tutor on ARM64 systems is through a community plugin which will automatically set the necessary configuration and which provides pre-built images.

To use the `tutor-contrib-arm64 plugin <https://github.com/open-craft/tutor-contrib-arm64>`_ to start using Tutor, run these commands::

    pip install git+https://github.com/open-craft/tutor-contrib-arm64
    tutor plugins enable arm64
    tutor local quickstart

That's it! You can now use the LMS at http://local.overhang.io/ and you're done with this tutorial.

The less easy way: building your own images
===========================================

If you want more flexibility than the plugin or its prebuilt images provide, you can build and run your own ARM64 images and change the database configuration yourself.

First, configure Tutor::

    tutor config save --interactive

Go through the configuration process, answering each question.

Then, build the "openedx" and "permissions" images::

    tutor images build openedx permissions

If you want to use Tutor as an Open edX development environment, you should also build the development images::

    tutor dev dc build lms

Change the database server
--------------------------

The version of MySQL that Open edX uses by default does not support the ARM architecture. You'll need to use a different database server/version, depending on which Open edX release you want to run.

For the **Maple** release of Open edX, we recommend using MariaDB, which should be largely compatible.

Configure Tutor to use MariaDB::

    tutor config save --set DOCKER_IMAGE_MYSQL=mariadb:10.4

.. warning::
    Note that using MariaDB is experimental and incompatibilities may exist, so this should only be used for local development - not for production instances.

For the **Nutmeg** release as well as **Tutor Nightly**, we recommend using MySQL 8::

    tutor config save --set DOCKER_IMAGE_MYSQL=mysql:8.0-oracle

If you aren't sure which of these applies, use MariaDB.

Finish setup and start Tutor
----------------------------

From this point on, use Tutor as normal. For example, start Open edX and run migrations with::

    tutor local init

Or for a development environment::

    tutor local stop
    tutor dev init
