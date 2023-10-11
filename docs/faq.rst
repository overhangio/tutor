.. _faq:

FAQ
===

What is Tutor?
--------------

Tutor is an open source distribution of `Open edX <https://open.edx.org>`_. It uses the original code from the various Open edX repositories, such as `edx-platform <https://github.com/openedx/edx-platform/>`_, `cs_comments_service <https://github.com/openedx/cs_comments_service>`_, etc. and packages everything in a way that makes it very easy to install, administer and upgrade Open edX. In particular, all services are run inside Docker containers.

Tutor makes it possible to deploy Open edX locally, with `docker-compose <https://docs.docker.com/compose/overview/>`_ or on an existing `Kubernetes cluster <http://kubernetes.io/>`_. Want to learn more? Take a look at the :ref:`getting started concepts <intro>`.

What is the purpose of Tutor?
-----------------------------

To make it possible to deploy, administer and upgrade Open edX anywhere, easily.

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

The `devstack <https://github.com/openedx/devstack>`_ is meant for development only, not for production deployment. Tutor can be used both for production deployment and :ref:`locally hacking on Open edX <development>`.

Is Tutor officially supported by edX?
-------------------------------------

Yes: as of the Open edX Maple release (December 9th 2021), Tutor is the only officially supported installation method for Open edX: see the `official installation instructions <https://edx.readthedocs.io/projects/edx-installing-configuring-and-running/en/open-release-quince.master/installation/index.html>`__.

What features are missing from Tutor?
-------------------------------------

Tutor tries very hard to support all major Open edX features, notably in the form of :ref:`plugins <existing_plugins>`. If you are interested in sponsoring the development of a new plugin, please `get in touch <mailto:worktogether@overhang.io>`__!

It should be noted that the `Insights <https://github.com/openedx/edx-analytics-pipeline>`__ stack is currently unsupported, because of its complexity, lack of support, and extensibility. To replace it, we developed `Cairn <https://github.com/overhangio/tutor-cairn>`__ the next-generation analytics solution for Open edX. You should check it out 😉

Are there people already running this in production?
----------------------------------------------------

Yes: system administrators all around the world use Tutor to run their Open edX platforms, from single-class school teachers to renowned universities, Open edX SaaS providers, and nation-wide learning platforms.

Why should I trust your software?
---------------------------------

You shouldn't :) Tutor is actively maintained by `Edly <https://edly.io>`__, a US-based ed-tech company facilitating over 40 million learners worldwide through its eLearning solutions. With a credible engineering team that has won clients' hearts globally led by `Régis Behmo <https://github.com/regisb/>`__, Tutor has empowered numerous edtech ventures over the years. Additionally, Tutor is a `community-led project <https://github.com/overhangio/tutor>`__ with many contributions from its :ref:`project maintainers <maintainers>`.
