.. _quickstart:

Quickstart
==========

::

    git clone https://github.com/regisb/tutor
    cd tutor/
    make local

**That's it?**

Yes :) This is what happens when you run ``make all``:

1. You answer a few questions about the configuration of your Open edX platform and your :ref:`selected options <options>`
2. Configuration files are generated.
3. Docker images are downloaded.
4. Docker containers are provisioned.
5. A full, production-ready platform is run with docker-compose.

The whole procedure should require less than 10 minutes, on a server with a good bandwidth. Note that your host environment will not be affected in any way, since everything runs inside docker containers. Root access is not even necessary.
