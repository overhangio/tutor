Requirements
============

The only prerequisite for running this is a working docker install. You will need both docker and docker-compose. Follow the instructions from the official documentation:

- `Docker <https://docs.docker.com/engine/installation/>`_
- `Docker compose <https://docs.docker.com/compose/install/>`_

Note that the production web server container will bind to port 80, so if you already have a web server running (Apache or Nginx, for instance), you should stop it.

You should be able to run Open edX on any platform that supports Docker and Python, including Mac OS and Windows. For now, only Ubuntu 16.04 was tested but we have no reason to believe the install would not work on a different OS.

At a minimum, the server running the containers should have 4 Gb of RAM; otherwise, the deployment procedure will crash during migrations (see the :ref:`troubleshooting` section).

Also, the host running the containers should be a 64 bit platform. (images are not built for i386 systems)
