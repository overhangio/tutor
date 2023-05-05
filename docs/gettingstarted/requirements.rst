.. _requirements:

Requirements
============

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

Configuring DNS records
-----------------------

When running a server in production, it is necessary to define `DNS records <https://en.wikipedia.org/wiki/Domain_Name_System#Resource_records>`__ which will make it possible to access your Open edX platform by name in your browser. The precise procedure to create DNS records varies from one provider to the next and is beyond the scope of these docs. You should create a record of type A with a name equal to your LMS hostname (given by ``tutor config printvalue LMS_HOST``) and a value that indicates the IP address of your server. Applications other than the LMS, such as the studio, ecommerce, etc. typically reside in subdomains of the LMS. Thus, you should also create a CNAME record to point all subdomains of the LMS to the LMS_HOST.

For instance, the demo Open edX server that runs at https://demo.openedx.overhang.io has the following DNS records::

    demo.openedx 1800 IN A 172.105.89.208
    *.demo.openedx 1800 IN CNAME demo.openedx.overhang.io.
