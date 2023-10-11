.. _quickstart:

Quickstart (1-click install)
----------------------------

1. Install the latest stable release of Tutor from pip:

.. include:: download/pip.rst

Or `download <https://github.com/overhangio/tutor/releases>`_ the pre-compiled binary and place the ``tutor`` executable in your path:

.. include:: download/binary.rst

2. Run ``tutor local launch``
3. You're done!

**That's it?**

Yes :) This is what happens when you run ``tutor local launch``:

1. You answer a few questions about the :ref:`configuration` of your Open edX platform.
2. Configuration files are generated from templates.
3. Docker images are downloaded.
4. Docker containers are provisioned.
5. A full, production-ready Open edX platform (`Quince <https://edx.readthedocs.io/projects/edx-installing-configuring-and-running/en/open-release-quince.master/platform_releases/quince.html>`__ release) is run with docker-compose.

The whole procedure should require less than 10 minutes, on a server with good bandwidth. Note that your host environment will not be affected in any way, since everything runs inside docker containers. Root access is not even necessary.

There's a lot more to Tutor than that! To learn more about what you can do with Tutor and Open edX, check out the :ref:`whatnext` section. If the launch installation method above somehow didn't work for you, check out the :ref:`troubleshooting` guide.
