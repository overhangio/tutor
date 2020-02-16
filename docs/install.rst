.. _install:

Installation
============

Requirements
------------

The only prerequisite for running this is a working Docker installation. You'll need both the ``docker`` and ``docker-compose`` commands in your system ``$PATH``. Follow the instructions from the official documentation:

- `Docker <https://docs.docker.com/engine/installation/>`_: minimum supported version is 18.06.0.
- `Docker compose <https://docs.docker.com/compose/install/>`_

.. warning::
    Do not attempt to simply run ``apt-get install docker docker-compose`` on older Ubuntu platforms, such as 16.04 (Xenial), as you will get older versions of these utilities.

Note that the production web server container will bind to port 80 and 443, so if there a web server is running on the same server (Apache or Nginx, for instance), it should be stopped prior to running tutor. Check the section on :ref:`how to setup a web proxy <web_proxy>` for a workaround.

With Tutor, Open edX can run on any platform that supports Docker, including Mac OS and Windows. Tutor was tested under various versions of Ubuntu and Mac OS.

At a minimum, the server running the containers should have 4 Gb of RAM. With less memory, the deployment procedure might crash during migrations (see the :ref:`troubleshooting <migrations_killed>` section) and the platform will be unbearably slow.

At least 9Gb of disk space is required.

Also, the host running the containers should be a 64 bit platform. (images are not built for i386 systems)

Direct binary downloads
-----------------------

The latest binaries can be downloaded from https://github.com/overhangio/tutor/releases. From the command line:

.. include:: cli_download.rst

This is the simplest and recommended installation method for most people. Note however that you will not be able to use custom plugins with this pre-compiled binary. The only plugins you can use with this approach are those there are already bundled with the binary: `discovery <https://github.com/overhangio/tutor-discovery>`__, `ecommerce <https://github.com/overhangio/tutor-ecommerce>`__, `figures <https://github.com/overhangio/tutor-figures>`__, `minio <https://github.com/overhangio/tutor-minio>`__, `notes <https://github.com/overhangio/tutor-notes>`__, `xqueue <https://github.com/overhangio/tutor-xqueue>`__.

From source
-----------

If you would like to inspect the Tutor source code, you are most welcome to install Tutor from `Pypi <https://pypi.org/project/tutor-openedx/>`_ or directly from `the Github repository <https://github.com/overhangio/tutor>`_. You will need python >= 3.6 and the libyaml development headers. On Ubuntu, these requirements can be installed by running::

    sudo apt install python3 libyaml-dev

Installing from pypi::

    pip install tutor-openedx

Installing from a local clone of the repository::

    git clone https://github.com/overhangio/tutor
    cd tutor
    pip install -e .

.. _cloud_install:
  
Cloud deployment
----------------

Tutor can be launched on Amazon Web Services very quickly with the `official Tutor AMI <https://aws.amazon.com/marketplace/pp/B07PV3TB8X>`_. Shell access is not even required, as all configuration will happen through the Tutor web user interface.

.. _upgrade:

Upgrading
---------

To upgrade a running Open edX platform, just install the latest ``tutor`` version (using either methods above) and run the ``quickstart`` command again. If you have :ref:`customised <configuration_customisation>` your docker images, you will have to re-build them prior to running ``quickstart``.

.. _autocomplete:

Autocomplete
------------

Tutor is built on top of `Click <https://click.palletsprojects.com>`_, which is a great library for building command line interface (CLI) tools. As such, Tutor benefits from all Click features, including `auto-completion <https://click.palletsprojects.com/en/7.x/bashcomplete/>`_. After installing Tutor, auto-completion can be enabled by running::

    _TUTOR_COMPLETE=source tutor >> ~/.bashrc

If you are running zsh, run instead::

    _TUTOR_COMPLETE=source_zsh tutor >> ~/.zshrc

After opening a new shell, you can test auto-completion by typing::

    tutor <tab><tab>

.. include:: podman.rst
