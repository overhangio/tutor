.. _installation:

Installation
============

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

.. _cloud_install:

Zero-click AWS installation
---------------------------

Tutor can be launched on Amazon Web Services very quickly with the `official Tutor AMI <https://aws.amazon.com/marketplace/pp/B07PV3TB8X>`__. Shell access is not required, as all configuration will happen through the Tutor web user interface. For detailed installation instructions, we recommend watching the following video:

.. youtube:: xtXP52qGphA