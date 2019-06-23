.. _faq:

FAQ
===

What is Tutor?
--------------

Tutor is an open source distribution of `Open edX <https://open.edx.org>`_. It uses the original code from the various Open edX repositories, such as `edx-platform <https://github.com/edx/edx-platform/>`_, `cs_comments_service <https://github.com/edx/cs_comments_service>`_, etc. and packages everything in a way that makes it very easy to install, administer and upgrade Open edX. In particular, all services are run inside Docker containers.

Tutor makes it possible to deploy Open edX locally, with `docker-compose <https://docs.docker.com/compose/overview/>`_ or on an existing `Kubernetes cluster <http://kubernetes.io/>`_.

What is the purpose of Tutor?
-----------------------------

To make it possible to deploy, administer and upgrade Open edX anywhere, easily.

.. _native:

What's the difference with the official "native" install?
---------------------------------------------------------

The `native installation <https://openedx.atlassian.net/wiki/spaces/OpenOPS/pages/146440579/Native+Open+edX+Ubuntu+16.04+64+bit+Installation>`_ maintained by edX relies on `Ansible scripts <https://github.com/edx/configuration/>`_ to deploy Open edX on one or multiple servers. These scripts suffer from a couple issues that Tutor tries to address:

1. Complexity: the scripts contain close to 35k lines of code spread over 780 files. They are really hard to understand, debug, and modify, and they are extremly slow. As a consequence, Open edX is often wrongly perceived as a project that is overly complex to manage. In contrast, Tutor generates mostly ``Dockerfile`` and ``docker-compose.yml`` files that make it easy to understand what is going on. Also, the whole installation should take about 10 minutes.
2. Isolation from the OS: Tutor barely needs to touch your server because the entire platform is packaged inside Docker containers. You are thus free to run other services on your server without fear of indirectly crashing your Open edX platform.
3. Compatibility: Open edX is only compatible with Ubuntu 16.04, but that shouldn't mean you are forced to run this specific OS. With Tutor, you can deploy Open edX on just any server you like: Ubuntu 18.04, Red Hat, Debian... All docker-compatible platforms are supported.
4. Security: because you are no longer bound to a single OS, with Tutor you are now free to install security-related upgrades as soon as they become available.
5. Portability: Tutor makes it easy to move your platform from one server to another. Just zip-compress your Tutor project root, send it to another server and you're done.

There are also many features that are not included in the native install, such as a :ref:`web user interface <webui>` for remotely installing the platform, :ref:`Kubernetes deployment <k8s>`, additional languages, etc. You'll discover these differences as you explore Tutor :)

What's the difference with the official devstack?
-------------------------------------------------

The `devstack <https://github.com/edx/devstack>`_ is meant for development only, not for production deployment. Tutor can be used both for production deployment and :ref:`locally hacking on Open edX <development>`.

Is Tutor officially supported by edX?
-------------------------------------

No. Tutor is developed independently from edX. That means that the folks at edX.org are *not* responsible for troubleshooting issues of this project. Please don't bother Ned ;-)

What features are missing from Tutor?
-------------------------------------

Those features are currently not available in Tutor:

- `discovery service <https://github.com/edx/course-discovery/>`_
- `ecommerce <https://github.com/edx/ecommerce>`_
- `analytics <https://github.com/edx/edx-analytics-pipeline>`_

Those extra services were considered low priority while developing this project, but we are planning on adding them to Tutor, eventually. If you need one or more of these services, feel free to let me know by opening a `Github issue <https://github.com/overhangio/tutor/issues/>`_. In particular, support for the Analytics stack is going to require a lot of work and I am looking forward to financial sponsorship. Please get in touch if you're interested.

Are there people already running this in production?
----------------------------------------------------

Yes, many of them. There is no way to count precisely how many running Open edX platforms were deployed with Tutor, but from feedback collected directly from real users, there must be dozens, if not hundreds. Tutor is also used by some Open edX providers who are hosting platforms for their customers.

Why should I trust software written by some random guy on the Internet?
-----------------------------------------------------------------------

You shouldn't :) Tutor is actively maintained by `Overhang.io <https://overhang.io>`_, a France-based company founded by `Régis Behmo <https://github.com/regisb/>`_. Régis has been working on Tutor since early 2018; he has been a contributor of the Open edX project since 2015. In particular, I have worked for 2 years on `FUN-MOOC <https://www.fun-mooc.fr/>`_, one of the top 5 largest Open edX platforms in the world. He presented several talks at the Open edX conferences:

- *Deploying a robust, scalable Open edX platform in 1 click (or less) with Tutor*, March 2019 (`video <https://www.youtube.com/watch?v=Oqc7c-3qFc4>`_, `slides <https://regisb.github.io/openedx2019/>`_)
- *Videofront: a Self-Hosted YouTube*, June 2017 (`video <https://www.youtube.com/watch?v=e7bJchJrmP8&t=5m53s>`__, `slides <http://regisb.github.io/openedx-conference-2017/>`__)
- *Open edX 101: A Source Code Review*, June 2016 (`video <https://www.youtube.com/watch?v=DVku7Y7XQII>`__, `slides <http://regisb.github.io/openedx-conference-2016/>`__)
- *FUN: Life in the Avant-Garde*, Oct. 2015 (`video <https://www.youtube.com/watch?v=V1EBo1l8BgY>`__, `slides <http://regisb.github.io/openedx-conference-2015/>`__)
