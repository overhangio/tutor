.. _installation:
.. _install:

Installation
============

Download
--------

Choose **one** of the installation methods below. If you install Tutor in different ways, you will end up with multiple ``tutor`` executables, which is going to be very confusing. At any time, you can check the path to your ``tutor`` executable by running ``which tutor``.

Python package
~~~~~~~~~~~~~~

.. include:: download/pip.rst

Check the "tutor" package on Pypi: https://pypi.org/project/tutor. You will need Python >= 3.9 with pip and the ``libyaml`` development headers. On Ubuntu, these requirements can be installed by running::

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

.. _cloud_install:

Zero-click AWS installation
---------------------------

Tutor can be launched on Amazon Web Services very quickly with the `official Tutor AMI <https://aws.amazon.com/marketplace/pp/B07PV3TB8X>`__. Shell access is not required, as all configuration will happen through the Tutor web user interface. For detailed installation instructions, we recommend watching the following video:

.. youtube:: xtXP52qGphA


Running older releases of Open edX
-------------------------------------

Instructions for installing the appropriate Tutor version for older Open edX releases. Each command ensures compatibility between Open edX and its corresponding Tutor version. For more details on versioning conventions in Tutor, see the :ref:`versioning` section.

+-------------------+---------------+--------------------------------------------+
| Open edX Release  | Tutor version | Installation command                       |
+===================+===============+============================================+
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
| Teak              | v20           | pip install 'tutor[full]>=20.0.0,<21.0.0'  |
+-------------------+---------------+--------------------------------------------+
| Ulmo              | v21           | pip install 'tutor[full]>=21.0.0,<22.0.0'  |
+-------------------+---------------+--------------------------------------------+
