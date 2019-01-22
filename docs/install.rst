.. _install:

Installation
============

Requirements
------------

The only prerequisite for running this is a working docker install. Both docker and docker-compose are required. Follow the instructions from the official documentation:

- `Docker <https://docs.docker.com/engine/installation/>`_
- `Docker compose <https://docs.docker.com/compose/install/>`_

Note that the production web server container will bind to port 80, so if you already have a web server running (Apache or Nginx, for instance), you should stop it.

You should be able to run Open edX on any platform that supports Docker, including Mac OS and Windows. Tutor was tested under various versions of Ubuntu and Mac OS.

At a minimum, the server running the containers should have 4 Gb of RAM. With less memory, the Open edX , the deployment procedure might crash during migrations (see the :ref:`troubleshooting` section) and the platform will be unbearably slow.

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
