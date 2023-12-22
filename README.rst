Tutor: the Docker-based Open edX distribution designed for peace of mind
========================================================================

.. image:: https://overhang.io/static/img/tutor-logo.svg
  :alt: Tutor logo
  :width: 500px
  :align: center

|

.. _readme_intro_start:

.. image:: https://img.shields.io/static/v1?logo=github&label=Git&style=flat-square&color=brightgreen&message=Source%20code
  :alt: Source code
  :target: https://github.com/overhangio/tutor

.. image:: https://img.shields.io/static/v1?logo=discourse&label=Forums&style=flat-square&color=ff0080&message=discuss.openedx.org
  :alt: Forums
  :target: https://discuss.openedx.org/tag/tutor

.. image:: https://img.shields.io/static/v1?logo=readthedocs&label=Documentation&style=flat-square&color=blue&message=docs.tutor.edly.io
  :alt: Documentation
  :target: https://docs.tutor.edly.io

.. image:: https://img.shields.io/pypi/v/tutor?logo=python&logoColor=white
  :alt: PyPI releases
  :target: https://pypi.org/project/tutor

.. image:: https://img.shields.io/github/license/overhangio/tutor.svg?style=flat-square
  :alt: AGPL License
  :target: https://www.gnu.org/licenses/agpl-3.0.en.html

.. image:: https://img.shields.io/static/v1?logo=twitter&label=Twitter&style=flat-square&color=1d9bf0&message=@overhangio
  :alt: Follow us on Twitter
  :target: https://twitter.com/overhangio/

.. image:: https://img.shields.io/static/v1?logo=youtube&label=YouTube&style=flat-square&color=ff0000&message=@overhangio
    :alt: Follow us on Youtube
    :target: https://www.youtube.com/c/OverhangIO

**Tutor** is the official Docker-based `Open edX <https://openedx.org>`_ distribution, both for production and local development. The goal of Tutor is to make it easy to deploy, customise, upgrade and scale Open edX. Tutor is reliable, fast, extensible, and it is already used to deploy hundreds of Open edX platforms around the world.

Do you need professional assistance setting up or managing your Open edX platform? `Edly <https://edly.io>`__ provides online support as part of its `Open edX installation service <https://edly.io/services/open-edx-installation/>`__.

Features
--------

* 100% `open source <https://github.com/overhangio/tutor>`__
* Runs entirely on Docker
* World-famous 1-click `installation and upgrades <https://docs.tutor.edly.io/install.html>`__
* Comes with batteries included: `theming <https://github.com/overhangio/indigo>`__, `SCORM <https://github.com/overhangio/openedx-scorm-xblock>`__, `HTTPS <https://docs.tutor.edly.io/configuration.html#ssl-tls-certificates-for-https-access>`__, `web-based administration interface <https://github.com/overhangio/tutor-webui>`__, `mobile app <https://github.com/overhangio/tutor-android>`__, `custom translations <https://docs.tutor.edly.io/configuration.html#adding-custom-translations>`__...
* Extensible architecture with `plugins <https://docs.tutor.edly.io/plugins/index.html>`__
* Works with `Kubernetes <https://docs.tutor.edly.io/k8s.html>`__
* No technical skill required with the `zero-click Tutor AWS image <https://docs.tutor.edly.io/install.html#zero-click-aws-installation>`__

.. _readme_intro_end:

.. image:: ./docs/img/launch.webp
    :alt: Tutor local launch
    :target: https://www.terminalizer.com/view/3a8d55835686

Quickstart
----------

1. Install the `latest stable release <https://github.com/overhangio/tutor/releases>`_ of Tutor
2. Run ``tutor local launch``
3. You're done!

Documentation
-------------

Extensive documentation is available: https://docs.tutor.edly.io/

Is there a problem?
-------------------

Please follow the instructions from the `troubleshooting section <https://docs.tutor.edly.io/troubleshooting.html>`__ in the docs.

.. _readme_support_start:

Support
-------

To get community support, go to the official Open edX discussion forum: https://discuss.openedx.org. For official support, `Edly <https://edly.io>`__ provides professional assistance as part of its `Open edX installation service <https://edly.io/services/open-edx-installation/>`__.

.. _readme_support_end:

.. _readme_contributing_start:

Contributing
------------

We welcome contributions to Tutor! To learn how you can contribute, please check the relevant section of the Tutor docs: `https://docs.tutor.edly.io/tutor.html#contributing <https://docs.tutor.edly.io/tutor.html#contributing>`__.

.. _readme_contributing_end:

License
-------

This work is licensed under the terms of the `GNU Affero General Public License (AGPL) <https://github.com/overhangio/tutor/blob/master/LICENSE.txt>`_.
