.. _install:

Install Tutor
=============

.. _requirements:

Requirements
------------

* Supported OS: Tutor runs on any 64-bit, UNIX-based system. It was also reported to work on Windows.
* Required software:

    - `Docker <https://docs.docker.com/engine/installation/>`__: v18.06.0+
    - `Docker Compose <https://docs.docker.com/compose/install/>`__: v1.22.0+

.. warning::
    Do not attempt to simply run ``apt-get install docker docker-compose`` on older Ubuntu platforms, such as 16.04 (Xenial), as you will get older versions of these utilities.

* Ports 80 and 443 should be open. If other web services run on these ports, check the section on :ref:`how to setup a web proxy <web_proxy>`.
* Hardware:

    - Minimum configuration: 4 Gb RAM, 2 CPU, 8 Gb disk space
    - Recommended configuration: 8 Gb RAM, 4 CPU, 25 Gb disk space

.. note::
    On Mac OS, by default, containers are allocated 2 GB of RAM, which is not enough. You should follow `these instructions from the official Docker documentation <https://docs.docker.com/docker-for-mac/#advanced>`__ to allocate at least 4-5 Gb to the Docker daemon. If the deployment fails because of insufficient memory during database migrations, check the :ref:`relevant section in the troubleshooting guide <migrations_killed>`.

.. _install_binary:

Direct binary download
----------------------

The latest binaries can be downloaded from https://github.com/overhangio/tutor/releases. From the command line:

.. include:: cli_download.rst

This is the simplest and recommended installation method for most people. Note however that you will not be able to use custom plugins with this pre-compiled binary. The only plugins you can use with this approach are those that are already bundled with the binary: see the :ref:`existing plugins <existing_plugins>`.

.. _install_source:

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
  
Zero-click AWS installation
---------------------------

Tutor can be launched on Amazon Web Services very quickly with the `official Tutor AMI <https://aws.amazon.com/marketplace/pp/B07PV3TB8X>`__. Shell access is not required, as all configuration will happen through the Tutor web user interface. For detailed installation instructions, we recommend watching the following video:

.. youtube:: xtXP52qGphA

.. _upgrade:

Upgrading
---------

With Tutor, it is very easy to upgrade to a more recent Open edX or Tutor release. Just install the latest ``tutor`` version (using either methods above) and run the ``quickstart`` command again. If you have :ref:`customised <configuration_customisation>` your docker images, you will have to re-build them prior to running ``quickstart``.

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
