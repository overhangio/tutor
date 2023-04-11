.. _arm64:

Running Tutor on ARM-based systems
==================================

Tutor can be used on ARM64 systems, although no official ARM64 docker images are available. If you want to get started quickly, there is `an unofficial  community-maintained ARM64 plugin <https://github.com/open-craft/tutor-contrib-arm64>`_ which will set the required settings for you and which includes unofficial docker images. If you prefer not to use an unofficial plugin, you can follow this tutorial.

.. note:: There are generally two ways to run Tutor on an ARM system - using emulation (via qemu or Rosetta 2) to run x86_64 images or running native ARM images. Since emulation can be noticeably slower (typically 20-100% slower depending on the emulation method), this tutorial aims to use native images where possible.


Building the images
-------------------

Although there are no official ARM64 images, Tutor makes it easy to build the images yourself.

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

The version of MySQL that Open edX uses by default (5.7) does not support the ARM architecture. You need to tell Tutor to use MySQL 8.0, which does support the ARM architecture and which has been supported by Open edX since the "Nutmeg" release.

Configure Tutor to use MySQL 8::

    tutor config save --set DOCKER_IMAGE_MYSQL=docker.io/mysql:8.0

(If you need to run an older release of Open edX on ARM64, you can try using `mariadb:10.4` although it's not officially supported nor recommended for production.)

Finish setup and start Tutor
----------------------------

From this point on, use Tutor as normal. For example, start Open edX and run migrations with::

    tutor local start -d
    tutor local do init

Or for a development environment::

    tutor dev start -d
    tutor dev do init
