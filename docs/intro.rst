.. _intro:

Introduction
============

`Open edX <http://open.edx.org/>`_ is a thriving open source project, backed by a great community, for running an online learning platform at scale. Historically, it's always been :ref:`difficult <native>` to install Open edX. The goal of Tutor is to solve this issue.

Tutor simplifies the deployment of Open edX by:

1. Separating the configuration logic from the deployment platforms.
2. Running application processes in cleanly separated `docker containers <https://www.docker.com/resources/what-container>`_.

Because Docker containers are becoming an industry-wide standard, that means that with Tutor it becomes possible to run Open edX anywhere: for now, Tutor supports deploying on a local server, with `docker-compose <https://docs.docker.com/compose/overview/>`_, and in a large cluster, with `Kubernetes <http://kubernetes.io/>`_. But in the future, Tutor may support other deployment platforms.

.. include:: ../README.rst
    :start-after: _whats_tutor_start:
    :end-before: _whats_tutor_end:

How does Tutor work?
--------------------

You can experiment with Tutor very quickly: start by `installing <install>`_ Tutor. Then run::
  
    tutor config save --interactive

This command does two things:

1. Generate a ``config.yml`` configuration file: this file contains core :ref:`configuration parameters <configuration>` for your Open edX platforms, such as passwords and feature flags.
2. Generate an ``env/`` folder, which we call the Tutor "environment", and which contains all the files that are necessary to run an Open edX platform: these are mostly Open edX configuration files.

All these files are stored in a single folder, called the Tutor project root. On Linux, this folder is in ``~/.local/share/tutor`` and on Mac OS it is ``~/Library/Application Support/tutor``.

The values from ``config.yml`` are used to generate the environment files in ``env/``. As a consequence, **every time the values from** ``config.yml`` **are modified, the environment must be regenerated**. This can be done with::
    
    tutor config save
    
Another consequence is that **any manual change made to a file in** ``env/`` **will be overwritten by** ``tutor config save`` **commands**. Consider yourself warned ;-)

Running Open edX
----------------

Now that you have generated a configuration and environment, you probably want to run Open edX.

- The most simple and popular use case is to `run Open edX locally, on a single server <local>`_, with docker-compose.
- If you have a running cluster, you can use Tutor to `deploy Open edX on Kubernetes <k8s>`_.
- Are you an Open edX developer? You can use Tutor for `hacking into the internals of edx-platform <development>`_.

Bells and whistles
------------------

For more advanced usage of Tutor, take a look at the :ref:`configuration and customisation <configuration_customisation>` and the :ref:`extra <extra>` sections