.. _requirements:

Requirements
============

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
    On Mac OS, by default, containers are allocated 2 GB of RAM, which is not enough. You should follow `these instructions from the official Docker documentation <https://docs.docker.com/desktop/settings-and-maintenance/settings/#advanced>`__ to allocate at least 4-5 GB to the Docker daemon. If the deployment fails because of insufficient memory during database migrations, check the :ref:`relevant section in the troubleshooting guide <migrations_killed>`.


Virtual Environment (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To prevent conflicts with other Python packages and maintain a clean environment, it's recommended that Tutor should be installed within a Python virtual environment. This is especially important on fresh or shared systems where installing packages globally may require elevated privileges and can interfere with system-level Python dependencies:

.. code-block:: bash

   python3 -m venv env
   source env/bin/activate

For more details on virtual environments, refer to the official `Python documentation <https://docs.python.org/3/library/venv.html>`_.

Configuring DNS records
-----------------------

When running a server in production, it is necessary to define `DNS records <https://en.wikipedia.org/wiki/Domain_Name_System#Resource_records>`__ which will make it possible to access your Open edX platform by name in your browser. The precise procedure to create DNS records varies from one provider to the next and is beyond the scope of these docs. You should create a record of type A with a name equal to your LMS hostname (given by ``tutor config printvalue LMS_HOST``) and a value that indicates the IP address of your server. Applications other than the LMS, such as the studio, credentials, etc. typically reside in subdomains of the LMS. Thus, you should also create a CNAME record to point all subdomains of the LMS to the LMS_HOST.

For instance, to run an Open edX server at https://learn.mydomain.com on a server with IP address 1.1.1.1, you would need to configure the following DNS records::

    learn 1800 IN A 1.1.1.1
    *.learn 1800 IN CNAME learn.mydomain.com.
