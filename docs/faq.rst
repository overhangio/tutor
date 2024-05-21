.. _faq:

FAQ
===

What is Tutor?
--------------

Tutor is an open source distribution of the `Open edX platform <https://open.edx.org>`_. It uses the original code from the various Open edX repositories, such as `edx-platform <https://github.com/openedx/edx-platform/>`_, `cs_comments_service <https://github.com/openedx/cs_comments_service>`_, etc. and packages everything in a way that makes it very easy to install, administer and upgrade an Open edX installation. In particular, all services are run inside Docker containers.

Tutor makes it possible to deploy an Open edX instance locally, with `docker-compose <https://docs.docker.com/compose/overview/>`_ or on an existing `Kubernetes cluster <http://kubernetes.io/>`_. Want to learn more? Take a look at the :ref:`getting started concepts <intro>`.

What is the purpose of Tutor?
-----------------------------

To make it possible to deploy, administer and upgrade an Open edX installation anywhere, easily.

.. _native:

What's the difference between Tutor and Devstack?
-------------------------------------------------

The `devstack <https://github.com/openedx/devstack>`_ was a tool meant only for local development; it is now deprecated, in favor of Tutor. Tutor can be used both for production deployment and :ref:`locally hacking on Open edX <development>`.

Is Tutor officially supported by the Open edX project?
------------------------------------------------------

As of the Open edX Maple release (December 9th 2021), Tutor is the only community-supported installation method for the Open edX platform: see the `official installation instructions <https://edx.readthedocs.io/projects/edx-installing-configuring-and-running/en/open-release-quince.master/installation/index.html>`__.

What features are missing from Tutor?
-------------------------------------

Tutor tries very hard to support all major Open edX platform features, notably in the form of :ref:`plugins <existing_plugins>`. If you are interested in sponsoring the development of a new plugin, please `get in touch <mailto:worktogether@overhang.io>`__!

It should be noted that the `Insights <https://github.com/openedx/edx-analytics-pipeline>`__ stack is currently unsupported, because of its complexity, lack of support, and extensibility. To replace it, Edly has developed `Cairn <https://github.com/overhangio/tutor-cairn>`__ the next-generation analytics solution for the Open edX platform, and the Open edX community is working on a new analytics project, in beta as of the Redwood release, called `Aspects <https://docs.openedx.org/projects/openedx-aspects/en/latest/concepts/aspects_overview.html>`_. You should check them out 😉

Are there people already running this in production?
----------------------------------------------------

Yes: system administrators all around the world use Tutor to run their Open edX platforms, from single-class school teachers to renowned universities, Open edX SaaS providers, and nation-wide learning platforms.

Why should I trust your software?
---------------------------------

You shouldn't :) Tutor is actively maintained by `Edly <https://edly.io>`__, a US-based ed-tech company facilitating over 40 million learners worldwide through its eLearning solutions. With a credible engineering team that has won clients' hearts globally led by `Régis Behmo <https://github.com/regisb/>`__, Tutor has empowered numerous edtech ventures over the years. Additionally, Tutor is a `community-led project <https://github.com/overhangio/tutor>`__ with many contributions from its :ref:`project maintainers <maintainers>`.
