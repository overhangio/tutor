.. _faq:

FAQ
===

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

Because Docker containers are becoming an industry-wide standard, that means that with Tutor it becomes possible to run Open edX anywhere: for now, Tutor supports deploying on a local server, with `docker-compose <https://docs.docker.com/compose/overview/>`_, and in a large cluster, with `Kubernetes <http://kubernetes.io/>`_. But in the future, Tutor may support other deployment platforms.

Where can I try Open edX and Tutor?
-----------------------------------

A demo Open edX platform is available at https://demo.openedx.overhang.io. This platform was deployed using Tutor and the `Indigo theme <https://github.com/overhangio/indigo>`__. Feel free to play around with the following credentials:

* Admin user: username=admin email=admin@overhang.io password=admin
* Student user: username=student email=student@overhang.io password=student

The Android mobile application for this demo platform can be downloaded at this url: https://mobile.demo.openedx.overhang.io/app.apk

Urls:

* LMS: https://demo.openedx.overhang.io
* Studio (CMS): https://studio.demo.openedx.overhang.io

The platform is reset every day at 9:00 AM, `Paris (France) time <https://time.is/Paris>`__, so feel free to try and break things as much as you want.

.. _native:

What's the difference with the official "native" installation?
--------------------------------------------------------------

The `native installation <https://openedx.atlassian.net/wiki/spaces/OpenOPS/pages/146440579/Native+Open+edX+Ubuntu+16.04+64+bit+Installation>`_ maintained by edX relies on `Ansible scripts <https://github.com/openedx/configuration/>`_ to deploy Open edX on one or multiple servers. These scripts suffer from a couple of issues that Tutor tries to address:

1. Complexity: the scripts contain close to 35k lines of code spread over 780 files. They are really hard to understand, debug, and modify, and they are extremely slow. As a consequence, Open edX is often wrongly perceived as a project that is overly complex to manage. In contrast, Tutor generates mostly ``Dockerfile`` and ``docker-compose.yml`` files that make it easy to understand what is going on. Also, the whole installation should take about 10 minutes.
2. Isolation from the OS: Tutor barely needs to touch your server because the entire platform is packaged inside Docker containers. You are thus free to run other services on your server without fear of indirectly crashing your Open edX platform.
3. Compatibility: Open edX is only compatible with Ubuntu 16.04, but that shouldn't mean you are forced to run this specific OS. With Tutor, you can deploy Open edX on just any server you like: Ubuntu 18.04, Red Hat, Debian... All docker-compatible platforms are supported.
4. Security: because you are no longer bound to a single OS, with Tutor you are now free to install security-related upgrades as soon as they become available.
5. Portability: Tutor makes it easy to move your platform from one server to another. Just zip-compress your Tutor project root, send it to another server and you're done.

Many features that are not included in the native installation, such as a `web user interface <https://github.com/overhangio/tutor-webui>`__ for remotely installing the platform, :ref:`Kubernetes deployment <k8s>`, additional languages, etc. You'll discover these differences as you explore Tutor :)

What's the difference with the official devstack?
-------------------------------------------------

The `devstack <https://github.com/openedx/devstack>`_ is meant for development only, not for production deployment. Tutor can be used both for production deployment and :ref:`locally hacking on Open edX <openedx_development>`.

Is Tutor officially supported by edX?
-------------------------------------

Yes: as of the Open edX Maple release (December 9th 2021), Tutor is the only officially supported installation method for Open edX: see the `official installation instructions <https://edx.readthedocs.io/projects/edx-installing-configuring-and-running/en/open-release-olive.master/installation/index.html>`__. 

What features are missing from Tutor?
-------------------------------------

Tutor tries very hard to support all major Open edX features, notably in the form of :ref:`plugins <existing_plugins>`. If you are interested in sponsoring the development of a new plugin, please `get in touch <mailto:worktogether@overhang.io>`__!

It should be noted that the `Insights <https://github.com/openedx/edx-analytics-pipeline>`__ stack is currently unsupported, because of its complexity, lack of support, and extensibility. To replace it, Overhang.IO developed `Cairn <https://overhang.io/tutor/plugin/cairn>`__ the next-generation analytics solution for Open edX, part of the `Tutor Wizard Edition <https://overhang.io/tutor/wizardedition>`__. You should check it out 😉

Are there people already running this in production?
----------------------------------------------------

Yes: system administrators all around the world use Tutor to run their Open edX platforms, from single-class school teachers to renowned universities, Open edX SaaS providers, and nation-wide learning platforms.

Why should I trust software written by some random guy on the Internet?
-----------------------------------------------------------------------

You shouldn't :) Tutor is actively maintained by `Overhang.IO <https://overhang.io>`_, a France-based company founded by `Régis Behmo <https://github.com/regisb/>`_. Régis has been working on Tutor since early 2018; he has been a contributor to the Open edX project since 2015. In particular, he has worked for 2 years at `FUN-MOOC <https://www.fun-mooc.fr/>`_, one of the top 5 largest Open edX platforms in the world. In addition, the Tutor project is a community-led project with many contributions from its :ref:`project maintainers <maintainers>`.

