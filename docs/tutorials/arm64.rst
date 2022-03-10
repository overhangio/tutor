.. _arm64:

Running Tutor on ARM-based systems
==================================

Tutor can be used on ARM64 systems, although support for that platform is currently experimental.

There are generally two ways to run Tutor on am ARM system - using qemu to run x86_64 images using emulation or running native ARM images. Since emulation can be quite slow, this Tutorial will focus on using native images where possible.

There are currently no official ARM64 images provided for Tutor, but Tutor makes it easy to build them yourself.

Building the images
-------------------

Start by :ref:`installing <install>` Tutor and its dependencies (e.g. Docker) onto your system.

.. note:: For Open edX developers, if you want to use the :ref:`nightly <nightly>` version of Tutor to "run master", install Tutor using git and check out the ``nightly`` branch of Tutor at this point. See the :ref:`nightly documentation <nightly>` for details.

Next, configure Tutor::

    tutor config save --interactive

Go through the configuration process, answering each question.

Then, build the "openedx" and "permissions" images::

    tutor images build openedx permissions

If you want to use Tutor as an Open edX development environment, you should also build the development images::

    tutor dev dc build lms

Change the database server
--------------------------

The version of MySQL that Open edX uses by default does not support the ARM architecture. Our current recommendation is to use MariaDB instead, which should be largely compatible.

.. warning::
    Note that using MariaDB is experimental and incompatibilites may exist, so this should only be used for local development - not for production instances.

Configure Tutor to use MariaDB::

    tutor config save --set DOCKER_IMAGE_MYSQL=mariadb:10.4

Finish setup and start Tutor
----------------------------

From this point on, use Tutor as normal. For example, start Open edX and run migrations with::

    tutor local start -d
    tutor local init

Or for a development environment::

    tutor local stop
    tutor dev start -d
    tutor dev init

Using with tutor-mfe
--------------------

You may wish to use `tutor-mfe <https://github.com/overhangio/tutor-mfe>`_ to run the Open edX microfrontends. If so, be aware that there is a known issue with ``tutor-mfe`` on ARM systems. See `this GitHub issue <https://github.com/overhangio/tutor-mfe/issues/31>`_ for details and known workarounds.
