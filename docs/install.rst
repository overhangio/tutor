.. _install:

Installing Tutor
================

.. _requirements:

Requirements
------------

* Supported OS: Tutor runs on any 64-bit, UNIX-based OS. It was also reported to work on Windows (with `WSL 2 <https://docs.microsoft.com/en-us/windows/wsl/install>`__).
* Architecture: Both AMD64 and ARM64 are supported.
* Required software:

    - `Docker <https://docs.docker.com/engine/installation/>`__: v24.0.5+ (with BuildKit 0.11+)
    - `Docker Compose <https://docs.docker.com/compose/install/>`__: v2.0.0+

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

When running a server in production, it is necessary to define `DNS records <https://en.wikipedia.org/wiki/Domain_Name_System#Resource_records>`__ which will make it possible to access your Open edX platform by name in your browser. The precise procedure to create DNS records varies from one provider to the next and is beyond the scope of these docs. You should create a record of type A with a name equal to your LMS hostname (given by ``tutor config printvalue LMS_HOST``) and a value that indicates the IP address of your server. Applications other than the LMS, such as the studio, ecommerce, etc. typically reside in subdomains of the LMS. Thus, you should also create a CNAME record to point all subdomains of the LMS to the LMS_HOST.

For instance, to run an Open edX server at https://learn.mydomain.com on a server with IP address 1.1.1.1, you would need to configure the following DNS records::

    learn 1800 IN A 1.1.1.1
    *.learn 1800 IN CNAME learn.mydomain.com.

.. _cloud_install:

Zero-click AWS installation
---------------------------

Tutor can be launched on Amazon Web Services very quickly with the `official Tutor AMI <https://aws.amazon.com/marketplace/pp/B07PV3TB8X>`__. Shell access is not required, as all configuration will happen through the Tutor web user interface. For detailed installation instructions, we recommend watching the following video:

.. youtube:: xtXP52qGphA

.. _upgrade:

Upgrading
---------

To upgrade your Open edX site or benefit from the latest features and bug fixes, you should simply upgrade Tutor. Start by backing up your data and reading the `release notes <https://docs.openedx.org/en/latest/community/release_notes/>`_ for the current release.

Next, upgrade the "tutor" package and its dependencies::

    pip install --upgrade "tutor[full]"

Then run the ``launch`` command again. Depending on your deployment target, run one of::

    tutor local launch # for local installations
    tutor dev launch   # for local development installations
    tutor k8s launch   # for Kubernetes installation

Upgrading with custom Docker images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you run :ref:`customised <configuration_customisation>` Docker images, you need to rebuild them before running ``launch``::

    tutor config save
    tutor images build all # specify here the images that you need to build
    tutor local launch

Upgrading to a new Open edX release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Major Open edX releases are published twice a year, in June and December, by the Open edX `Build/Test/Release working group <https://discuss.openedx.org/c/working-groups/build-test-release/30>`__. When a new Open edX release comes out, Tutor gets a major version bump (see :ref:`versioning`). Such an upgrade typically includes multiple breaking changes. Any upgrade is final because downgrading is not supported. Thus, when upgrading your platform from one major version to the next, it is strongly recommended to do the following:

1. Read the changes listed in the `CHANGELOG.md <https://github.com/overhangio/tutor/blob/master/CHANGELOG.md>`__ file. Breaking changes are identified by a "💥".
2. Perform a backup (see the :ref:`backup tutorial <backup_tutorial>`). On a local installation, this is typically done with::

    tutor local stop
    sudo rsync -avr "$(tutor config printroot)"/ /tmp/tutor-backup/

3. If you created custom plugins, make sure that they are compatible with the newer release.
4. Test the new release in a sandboxed environment.
5. If you are running edx-platform, or some other repository from a custom branch, then you should rebase (and test) your changes on top of the latest release tag (see :ref:`edx_platform_fork`).

The process for upgrading from one major release to the next works similarly to any other upgrade, with the ``launch`` command (see above). The single difference is that if the ``launch`` command detects that your tutor environment was generated with an older release, it will perform a few release-specific upgrade steps. These extra upgrade steps will be performed just once. But they will be ignored if you updated your local environment (for instance: with ``tutor config save``) before running ``launch``. This situation typically occurs if you need to re-build some Docker images (see above). In such a case, you should make use of the ``upgrade`` command. For instance, to upgrade a local installation from Redwood to Sumac and rebuild some Docker images, run::

    tutor config save
    tutor images build all # list the images that should be rebuilt here
    tutor local upgrade --from=redwood
    tutor local launch


Running older releases of Open edX
-------------------------------------

Instructions for installing the appropriate Tutor version for older Open edX releases. Each command ensures compatibility between Open edX and its corresponding Tutor version. For more details on versioning conventions in Tutor, see the :ref:`versioning` section.

+-------------------+---------------+--------------------------------------------+
| Open edX Release  | Tutor version | Installation command                       |
+===================+===============+============================================+
| Juniper           | v10           | pip install 'tutor[full]>=10.0.0,<11.0.0'  |
+-------------------+---------------+--------------------------------------------+
| Koa               | v11           | pip install 'tutor[full]>=11.0.0,<12.0.0'  |
+-------------------+---------------+--------------------------------------------+
| Lilac             | v12           | pip install 'tutor[full]>=12.0.0,<13.0.0'  |
+-------------------+---------------+--------------------------------------------+
| Maple             | v13           | pip install 'tutor[full]>=13.0.0,<14.0.0'  |
+-------------------+---------------+--------------------------------------------+
| Nutmeg            | v14           | pip install 'tutor[full]>=14.0.0,<15.0.0'  |
+-------------------+---------------+--------------------------------------------+
| Olive             | v15           | pip install 'tutor[full]>=15.0.0,<16.0.0'  |
+-------------------+---------------+--------------------------------------------+
| Palm              | v16           | pip install 'tutor[full]>=16.0.0,<17.0.0'  |
+-------------------+---------------+--------------------------------------------+
| Quince            | v17           | pip install 'tutor[full]>=17.0.0,<18.0.0'  |
+-------------------+---------------+--------------------------------------------+
| Redwood           | v18           | pip install 'tutor[full]>=18.0.0,<19.0.0'  |
+-------------------+---------------+--------------------------------------------+
| Sumac             | v19           | pip install 'tutor[full]>=19.0.0,<20.0.0'  |
+-------------------+---------------+--------------------------------------------+

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

It is fairly easy to completely uninstall Tutor and to delete the Open edX platforms that are running locally.

First of all, stop any locally-running platform and remove all Tutor containers::

    tutor local dc down --remove-orphans
    tutor dev dc down --remove-orphans

Then, delete all data associated with your Open edX platform::

    # WARNING: this step is irreversible
    sudo rm -rf "$(tutor config printroot)"

Finally, uninstall Tutor itself::

    # If you installed tutor from source
    pip uninstall tutor

    # If you downloaded the tutor binary
    sudo rm /usr/local/bin/tutor

    # Optionally, you may want to remove Tutor plugins installed.
    # You can get a list of the installed plugins:
    pip freeze | grep tutor
    # You can then remove them using the following command:
    pip uninstall <plugin-name>
