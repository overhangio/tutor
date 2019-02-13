.. _install:

Installation
============

Requirements
------------

The only prerequisite for running this is a working docker install. Both docker and docker-compose are required. Follow the instructions from the official documentation:

- `Docker <https://docs.docker.com/engine/installation/>`_
- `Docker compose <https://docs.docker.com/compose/install/>`_

Note that the production web server container will bind to port 80 and 443, so if there a web server is running on the same server (Apache or Nginx, for instance), it should be stopped prior to running tutor. See the :ref:`troubleshooting <webserver>` section for a workaround.

With Tutor, Open edX can run on any platform that supports Docker, including Mac OS and Windows. Tutor was tested under various versions of Ubuntu and Mac OS.

At a minimum, the server running the containers should have 4 Gb of RAM. With less memory, the deployment procedure might crash during migrations (see the :ref:`troubleshooting <migrations_killed>` section) and the platform will be unbearably slow.

At least 9Gb of disk space is required.

Also, the host running the containers should be a 64 bit platform. (images are not built for i386 systems)

Direct binary downloads
-----------------------

The latest binaries can be downloaded from https://github.com/regisb/tutor/releases.

Installing from pip
-------------------

If, for some reason, you'd rather install from pypi instead of downloading a binary, run::

    pip install tutor-openedx

Installing from source
----------------------

::

    git clone https://github.com/regisb/tutor
    cd tutor
    python setup.py develop
