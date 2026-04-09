Running Tutor with Podman
-------------------------

`Podman <https://podman.io/>`_ is a fully featured container engine that is daemonless. It provides a Docker CLI comparable command line that makes it pretty easy for people transitioning over from Docker.

Simply put, this means that you can do something like: ``alias docker=podman`` and everything will run and behave pretty much as expected.

As of podman v3.0.0, podman now officially supports ``docker-compose`` via a shim service. This means that you now have the option of running Tutor with Podman, instead of the native Docker tools.

This has some practical advantages: it does not require a running Docker daemon, and it enables you to run and build Docker images without depending on any system component running as ``root``.

.. warning::
   You should not attempt to run Tutor with Podman on a system that already has native ``docker`` installed. If you want to switch to ``podman`` using the aliases described here, you should uninstall (or at least stop) the native Docker daemon first.


Enabling Podman
~~~~~~~~~~~~~~~

Podman is supported on a variety of development platforms, see the `installation instructions <https://podman.io/getting-started/installation>`_ for details.

Once you have installed Podman and its dependencies on the platform of your choice, you'll need to make sure that the ``podman`` binary, usually installed as ``/usr/bin/podman``, is aliased to ``docker``.

On some CentOS and Fedora releases, you can install a package named ``podman-docker`` to do this for you, but on other platforms, you'll need to take of this yourself.

- To alias ``podman`` to ``docker``, you can simply run this command::

    $ alias docker=podman

.. note::
   Running this command only makes a temporary alias. For a more permanent alias, you should place that command in your ``bashrc`` or equivalent file.

Getting docker-compose to work with Podman
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To allow ``podman`` to work with ``docker-compose``, you'll need to enable a podman socket which pretends to be ``docker``.

For rootless containers, this requires you to start the ``podman.service`` as a regular user and set the ``DOCKER_HOST`` environment variable. This can be done as follows::

  # To start the podman service
  $ systemctl --user start podman.service

  # To set the DOCKER_HOST environment variable
  $ export DOCKER_HOST="unix://$XDG_RUNTIME_DIR/podman/podman.sock"

If you are running in rootless mode, ``tutor local`` expects a web proxy to be running on port ``80`` or port ``443``. For instructions on how to configure a web proxy, view `this tutorial <https://docs.tutor.edly.io/tutorials/proxy.html>`_.

.. note::
   As with the previous ``alias`` command, if you'd like to make the ``DOCKER_HOST`` variable permanent, you should put the entire export command in your ``bashrc`` or equivalent file.

Fixing SELinux Errors
~~~~~~~~~~~~~~~~~~~~~

.. warning::
   Disabling ``SELinux`` or setting it to *permissive mode* on your system is **highly discouraged and will render your system vulnerable.**

If your system has ``SELinux`` working in enforcing mode, chances are that the SELinux context of the tutor root directory won't be set correctly. This will cause read issues because containers will not be able read files from volumes due to a context mismatch.

Errors stemming from this will look as follows in the ``sealert`` program::

  "SELinux is preventing caddy from read access on the file Caddyfile."
  "SELinux is preventing celery from read access on the directory cms."
  "SELinux is preventing mysqld from add_name access on the directory is_writable."

You can verify the context mismatch by running::

  $ ls -lZ $(tutor config printroot)

You'll most likely see something that looks like this::

  -rw-r--r--. 1 tutor tutor unconfined_u:object_r:data_home_t:s0 2145 Jan  6 20:13 config.yml
  drwxr-xr-x. 2 tutor tutor unconfined_u:object_r:data_home_t:s0    6 Jan  6 20:14 data
  drwxr-xr-x. 8 tutor tutor unconfined_u:object_r:data_home_t:s0  121 Jan  6 20:14 env

We're interested in the ``unconfined_u:object_r:data_home_t:s0`` part of that output.

Notice how the third part of that says ``data_home_t``?

That's the context type. For tutor to work, we need that part to be set to ``container_file_t``.

This can be done as follows::

  # Set the SELinux type of the tutor root directory and all of it's subdirectories to `container_file_t`
  $ sudo semanage fcontext -a -t container_file_t "$(tutor config printroot)(/.*)?"

  # Apply the newly set security context to the directories
  $ sudo restorecon -RF $(tutor config printroot)

Running these two commands in a sequence should fix the SELinux errors.

Verifying your environment
~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you've set everything up as described, you should be able to run ``docker version`` and ``docker-compose --help`` and get a valid output.

After that, you should be able to use ``tutor local``, and other commands as if you had installed the native Docker tools.
