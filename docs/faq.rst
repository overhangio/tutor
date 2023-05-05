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

What's the difference between Tutor and Devstack?
-------------------------------------------------

The `devstack <https://github.com/openedx/devstack>`_ was a tool meant only for local development; it is now deprecated, in favor of Tutor. Tutor can be used both for production deployment and :ref:`locally hacking on Open edX <development>`.

Is Tutor officially supported by the Open edX project?
------------------------------------------------------

As of the Open edX Maple release (December 9th 2021), Tutor is the only community-supported installation method for the Open edX platform: see the `official installation instructions <https://docs.tutor.edly.io/>`__.

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
