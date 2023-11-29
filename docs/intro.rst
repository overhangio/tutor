.. _intro:

Concepts
========

What is Open edX?
-----------------

`Open edX <http://open.edx.org/>`_ is a thriving open source project, backed by a great community, for running an online learning platform at scale. Open edX comes with an LMS (Learning Management System) where students access course contents, a CMS (Content Management System) that course staff uses to design courses, and a few other components to provide more services to students, course staff, and platform administrators.

Should I use Open edX?
----------------------

Open edX competitors include `Moodle <https://moodle.org/>`__, `Instructure's Canvas <https://www.instructure.com/>`__, `Blackboard's Open LMS <https://www.blackboard.com>`__, as well as a slew of hosted, closed source alternatives. Open edX is the only online learning system that satisfies all following properties:

* Open source software to avoid vendor lock-in
* Scales well in all directions (number of users and courses)
* Multiple extension points for comprehensive customization
* Modern, intuitive user interface to keep students engaged

Open edX is a safe bet: it is backed by edX.org, a US-based non-profit that is committed to open source and which runs Open edX to service its millions of learners. With Open edX you can be sure that the features you need will be available. If it's good enough for Harvard, the MIT, or the French government, then it will probably also work for you.

Should I self-host Open edX or rely on a hosting provider?
----------------------------------------------------------

Third-party Open edX providers can provide you with custom, closed-source features that they developed internally. However, their pricing is usually per-seat: that makes it difficult to predict how much running Open edX will actually cost you if you don't know in advance how many students will connect to your platform. And once you start scaling up and adding many students, running the platform will become very expensive.

On the other hand, running Open edX on your own servers will help you keep your costs under control. Because you own your servers and data, you will always be able to migrate your platform, either to a different cloud provider or an Open edX service provider. This is the true power of the open source.

Should I use Tutor?
-------------------

Running software on-premises is cheaper only if your management costs don't go through the roof. You do not want to hire a full-time devops team just for managing your online learning platform. This is why we created Tutor: to make it easy to run a state-of-the-art online learning platform without breaking the bank. Historically, it's always been difficult to install Open edX with native installation scripts. For instance, there are no official instructions for upgrading an existing Open edX platform: the `recommended approach <https://docs.bitnami.com/azure/apps/edx/administration/upgrade/>`__ is to backup all data, trash the server, and create a new one. As a consequence, people tend not to upgrade their platform and keep running on deprecated releases. Tutor makes it possible even for non-technical users to launch, manage and upgrade Open edX at any scale. Should you choose at some point that Tutor is not the right solution for you, you always have an escape route: because Tutor is open source software, you can easily dump your data and switch to a different installation method. But we are confident you will not do that 😉

To learn more about Tutor, watch this 7-minute lightning talk that was made at the 2019 Open edX conference in San Diego, CA (with `slides <https://regisb.github.io/openedx2019/>`_):

.. youtube:: Oqc7c-3qFc4

How does Tutor simplify Open edX deployment?
--------------------------------------------

Tutor simplifies the deployment of Open edX by:

1. Separating the configuration logic from the deployment platforms.
2. Running application processes in cleanly separated `docker containers <https://www.docker.com/resources/what-container>`_.
3. Providing user-friendly, reliable commands for common administration tasks, including upgrades and monitoring.
4. Using a simple :ref:`plugin system <plugins>` that makes it easy to extend and customise Open edX.

.. image:: https://overhang.io/static/img/openedx-plus-docker-is-tutor.png
  :alt: Open edX + Docker = Tutor
  :width: 500px
  :align: center

Because Docker containers are becoming an industry-wide standard, that means that with Tutor it becomes possible to run Open edX anywhere: for now, Tutor supports deploying on a local server, with `docker compose <https://docs.docker.com/compose/overview/>`_, and in a large cluster, with `Kubernetes <http://kubernetes.io/>`_. But in the future, Tutor may support other deployment platforms.

Where can I try Open edX and Tutor?
-----------------------------------

A demo Open edX platform is available at https://demo.openedx.edly.io. This platform was deployed using Tutor and the `Indigo theme <https://github.com/overhangio/indigo>`__. Feel free to play around with the following credentials:

* Admin user: username=admin email=admin@overhang.io password=admin
* Student user: username=student email=student@overhang.io password=student

The Android mobile application for this demo platform can be downloaded at this url: https://mobile.demo.openedx.edly.io/app.apk

Urls:

* LMS: https://demo.openedx.edly.io
* Studio (CMS): https://studio.demo.openedx.edly.io

The platform is reset every day at 9:00 AM, `Paris (France) time <https://time.is/Paris>`__, so feel free to try and break things as much as you want.

.. _how_does_tutor_work:

How does Tutor work?
--------------------

Tutor is a piece of software that takes care of exactly three things:

1. Project configuration: user-specific settings (such as secrets) are stored in a single ``config.yml`` file.
2. Template rendering: all the files that are necessary to run your platform are generated from a set of templates and user-specific settings.
3. Command-line interface (CLI): frequently-used administration commands are gathered in a convenient, unified CLI.

You can experiment with Tutor very quickly: start by `installing <install>`_ Tutor. Then run::

    $ tutor config save --interactive

Then, to view the result of the above command::

    $ cd "$(tutor config printroot)"
    $ ls
    config.yml  env

The ``config.yml`` file contains your user-specific Open edX settings (item #1 above). The ``env/`` folder contains the rendered templates which will be used to run your Open edX platform (item #2). For instance, the ``env/local`` folder contains the ``docker-compose.yml`` file to run Open edX locally.

The values from ``config.yml`` are used to generate the environment files in ``env/``. As a consequence, **every time the values from** ``config.yml`` **are modified, the environment must be regenerated** with ``tutor config save``..

Because the Tutor environment is generated entirely from the values in ``config.yml``, you can ``rm -rf`` the ``env/`` folder at any time and re-create it with ``tutor config save``. Another consequence is that **any manual change made to a file in** ``env/`` **will be overwritten by** ``tutor config save`` **commands**. Consider yourself warned!

You can now take advantage of the Tutor-powered CLI (item #3) to bootstrap your Open edX platform::

    tutor local launch

Under the hood, Tutor simply runs ``docker compose`` and ``docker`` commands to launch your platform. These commands are printed in the standard output, such that you are free to replicate the same behaviour by simply copying/pasting the same commands.

How do I navigate Tutor's command-line interface?
-------------------------------------------------

Tutor commands are structured in an easy-to-follow hierarchy. At the top level, there are command trees for image and configuration management::

    tutor config ...
    tutor images ...

as well as command trees for each mode in which Tutor can run::

    tutor local ...  # Commands for managing a local Open edX deployment.
    tutor k8s ...    # Commands for managing a Kubernetes Open edX deployment.
    tutor dev ...    # Commands for hacking on Open edX in development mode.

Within each mode, Tutor has subcommands for managing that type of Open edX instance. Many of them are common between modes, such as ``launch``, ``start``, ``stop``, ``exec``, and ``logs``. For example::

    tutor local logs  # View logs of a local deployment.
    tutor k8s logs    # View logs of a Kubernetes-managed deployment.
    tutor dev logs    # View logs of a development platform.

Many commands can be further parameterized to specify their target and options, for example::

  tutor local logs cms          # View logs of the CMS container in a local deployment.
  tutor k8s logs mysql          # View logs of MySQL in Kubernetes-managed deployment.
  tutor dev logs lms --tail 10  # View ten lines of logs of the LMS container in development mode.

And that's it! You do not need to understand Tutor's entire command-line interface to get started. Using the ``--help`` option that's available on every command, it is easy to learn as you go. For an in-depth guide, you can also explore the `CLI Reference <reference/index.rst>`_.

I'm ready, where do I start?
----------------------------

Right :ref:`here <gettingstarted>`!
