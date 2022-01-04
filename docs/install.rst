.. _install:

Installing Tutor
================

.. _requirements:

Requirements
------------

* Supported OS: Tutor runs on any 64-bit, UNIX-based OS. It was also reported to work on Windows (with `WSL 2 <https://docs.microsoft.com/en-us/windows/wsl/install>`__).
* Architecture: support for ARM64 is a work-in-progress. See `this issue <https://github.com/overhangio/tutor/issues/510>`__.
* Required software:

    - `Docker <https://docs.docker.com/engine/installation/>`__: v18.06.0+
    - `Docker Compose <https://docs.docker.com/compose/install/>`__: v1.22.0+

.. warning::
    Do not attempt to simply run ``apt-get install docker docker-compose`` on older Ubuntu platforms, such as 16.04 (Xenial), as you will get older versions of these utilities.

* Ports 80 and 443 should be open. If other web services run on these ports, check the tutorial on :ref:`how to setup a web proxy <web_proxy>`.
* Hardware:

    - Minimum configuration: 4 GB RAM, 2 CPU, 8 GB disk space
    - Recommended configuration: 8 GB RAM, 4 CPU, 25 GB disk space

.. note::
    On Mac OS, by default, containers are allocated 2 GB of RAM, which is not enough. You should follow `these instructions from the official Docker documentation <https://docs.docker.com/docker-for-mac/#advanced>`__ to allocate at least 4-5 GB to the Docker daemon. If the deployment fails because of insufficient memory during database migrations, check the :ref:`relevant section in the troubleshooting guide <migrations_killed>`.

Download
--------

Choose **one** of the installation methods below. If you install Tutor in different ways, you will end up with multiple ``tutor`` executables, which is going to be very confusing. At any time, you can check the path to your ``tutor`` executable by running ``which tutor``.

Python package
~~~~~~~~~~~~~~

.. include:: download/pip.rst

Check the "tutor" package on Pypi: https://pypi.org/project/tutor. You will need Python >= 3.6 with pip and the libyaml development headers. On Ubuntu, these requirements can be installed by running::

    sudo apt install python3 python3-pip libyaml-dev

.. _install_binary:

Binary release
~~~~~~~~~~~~~~

The latest binaries can be downloaded from https://github.com/overhangio/tutor/releases. From the command line:

.. include:: download/binary.rst

This is the simplest and recommended installation method for most people who do not have Python 3 on their machine. Note however that **you will not be able to use custom plugins** with this pre-compiled binary. The only plugins you can use with this approach are those that are already bundled with the binary: see the :ref:`existing plugins <existing_plugins>`.

.. _install_source:

Installing from source
~~~~~~~~~~~~~~~~~~~~~~

To inspect the Tutor source code, install Tutor from `the Github repository <https://github.com/overhangio/tutor>`__::

    git clone https://github.com/overhangio/tutor
    cd tutor
    pip install -e .

Configuring DNS records
-----------------------

When running a server in production, it is necessary to define `DNS records <https://en.wikipedia.org/wiki/Domain_Name_System#Resource_records>`__ which will make it possible to access your Open edX platform by name in your browser. The precise procedure to create DNS records vary from one provider to the next and is beyond the scope of these docs. You should create a record of type A with a name equal to your LMS hostname (given by ``tutor config printvalue LMS_HOST``) and a value that indicates the IP address of your server. Applications other than the LMS, such as the studio, ecommerce, etc. typically reside in subdomains of the LMS. Thus, you should also create a CNAME record to point all subdomains of the LMS to the LMS_HOST.

For instance, the demo Open edX server that runs at https://demo.openedx.overhang.io has the following DNS records::

    demo.openedx 1800 IN A 172.105.89.208
    *.demo.openedx 1800 IN CNAME demo.openedx.overhang.io.

.. _cloud_install:

Zero-click AWS installation
---------------------------

Tutor can be launched on Amazon Web Services very quickly with the `official Tutor AMI <https://aws.amazon.com/marketplace/pp/B07PV3TB8X>`__. Shell access is not required, as all configuration will happen through the Tutor web user interface. For detailed installation instructions, we recommend watching the following video:

.. youtube:: xtXP52qGphA

.. _upgrade:

Upgrading
---------

With Tutor, it is very easy to upgrade to a more recent Open edX or Tutor release. Just install the latest ``tutor`` version (using either methods above) and run the ``quickstart`` command again. If you have :ref:`customised <configuration_customisation>` your docker images, you will have to re-build them prior to running ``quickstart``.

``quickstart`` should take care of automatically running the upgrade process. If for some reason you need to *manually* upgrade from an Open edX release to the next, you should run ``tutor local upgrade``. For instance, to upgrade from Lilac to Maple, run::

    tutor local upgrade --from=lilac

.. _autocomplete:

Shell autocompletion
--------------------

Tutor is built on top of `Click <https://click.palletsprojects.com>`_, which is a great library for building command line interface (CLI) tools. As such, Tutor benefits from all Click features, including `auto-completion <https://click.palletsprojects.com/en/8.x/bashcomplete/>`_. After installing Tutor, auto-completion can be enabled in bash by running::

    _TUTOR_COMPLETE=bash_source tutor >> ~/.bashrc

If you are running zsh, run instead::

    _TUTOR_COMPLETE=zsh_source tutor >> ~/.zshrc

After opening a new shell, you can test auto-completion by typing::

    tutor <tab><tab>

Uninstallation
--------------

It is fairly easy to completely uninstall Tutor and to delete the Open edX platforms that is running locally.

First of all, stop any locally-running platform::

    tutor local stop
    tutor dev stop

Then, delete all data associated to your Open edX platform::

    # WARNING: this step is irreversible
    sudo rm -rf "$(tutor config printroot)"

Finally, uninstall Tutor itself::

    # If you installed tutor from source
    pip uninstall tutor

    # If you downloaded the tutor binary
    sudo rm /usr/local/bin/tutor
