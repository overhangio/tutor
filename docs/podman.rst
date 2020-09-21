Running Tutor with Podman
-------------------------

You have the option of running Tutor with `Podman <https://podman.io/>`__, instead of the native Docker tools. This has some practical advantages: it does not require a running Docker daemon, and it enables you to run and build Docker images without depending on any system component running ``root``. As such, it is particularly useful for building Tutor images from CI pipelines.

The ``podman`` CLI aims to be fully compatible with the ``docker`` CLI, and ``podman-compose`` is meant to be a fully-compatible alias of ``docker-compose``. This means that you should be able to use together with Tutor, without making any changes to Tutor itself.

.. warning::
   Since this was written, it was discovered that there are major compatibility issues between ``podman-compose`` and ``docker-compose``. Thus, podman cannot be considered a drop-in replacement of Docker in the context of Tutor -- at least for running Open edX locally.

.. warning::
   You should not attempt to run Tutor with Podman on a system that already has native ``docker`` installed. If you want to switch to ``podman`` using the aliases described here, you should uninstall (or at least stop) the native Docker daemon first.


Enabling Podman
~~~~~~~~~~~~~~~

Podman is supported on a variety of development platforms, see the `installation instructions <https://podman.io/getting-started/installation>`_ for details.

Once you have installed Podman and its dependencies on the platform of your choice, you'll need to make sure that its ``podman`` binary, usually installed as ``/usr/bin/podman``, is aliased to ``docker``, and is included as such in your system ``$PATH``. On some CentOS and Fedora releases you can install a package named ``podman-docker`` to do this for you, but on other platforms you'll need to take of this yourself.

- If ``$HOME/bin`` is in your ``$PATH``, you can create a symbolic link there::

    ln -s $(which podman) $HOME/bin/docker

- If you want to instead make ``docker`` a system-wide alias for ``podman``, you can create your symlink in ``/usr/local/bin``, an action that normally requires ``root`` privileges::

    sudo ln -s $(which podman) /usr/local/bin/docker


Enabling podman-compose
~~~~~~~~~~~~~~~~~~~~~~~

``podman-compose`` is available as a package from PyPI, and can thus be installed with ``pip``. See `its README <https://github.com/containers/podman-compose/blob/devel/README.md>`_ for installation instructions. Note that if you have installed Tutor in its own virtualenv, you'll need to run ``pip install podman-compose`` in that same virtualenv.

Once installed, you'll again need to create a symbolic link that aliases ``docker-compose`` to ``podman-compose``.

- If you run Tutor and ``podman-compose`` in a virtualenv, create the symlink in that virtualenv's ``bin`` directory: activate the virtualenv, then run::

    ln -s $(which podman-compose) $(dirname $(which podman-compose))/docker-compose

- If you do not, create the symlink in ``/usr/local/bin``, using ``root`` privileges::

    sudo ln -s $(which podman-compose) /usr/local/bin/docker-compose


Verifying your environment
~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you have configured your symbolic links as described, you should be able to run ``docker version`` and ``docker-compose --help`` and their output should agree, respectively, with ``podman version`` and ``podman-compose --help``.

After that, you should be able to use ``tutor local``, ``tutor build``, and other commands as if you had installed the native Docker tools.
