.. _quickstart:

Quickstart
==========

1. `Download <https://github.com/regisb/tutor/releases>`_ the latest stable release of Tutor, uncompress the file and place the ``tutor`` executable in your path. From the command line::

       sudo curl -L "https://github.com/regisb/tutor/releases/download/latest/tutor-$(uname -s)_$(uname -m)" -o /usr/local/bin/tutor
       sudo chmod +x /usr/local/bin/tutor

2. Run ``tutor local quickstart``
3. You're done!

**That's it?**

Yes :) This is what happens when you run ``tutor local quickstart``:

1. You answer a few questions about the :ref:`configuration` of your Open edX platform.
2. Configuration files are generated from templates.
3. Docker images are downloaded.
4. Docker containers are provisioned.
5. A full, production-ready platform is run with docker-compose.

The whole procedure should require less than 10 minutes, on a server with a good bandwidth. Note that your host environment will not be affected in any way, since everything runs inside docker containers. Root access is not even necessary.
