.. Tutor documentation master file, created by
   sphinx-quickstart on Mon Dec  3 21:36:51 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Tutor 🎓 Open edX 1-click install for everyone
==============================================

.. image:: https://img.shields.io/travis/regisb/tutor.svg
    :alt: Build status
    :target: https://travis-ci.org/regisb/tutor

.. image:: https://readthedocs.org/projects/tutor/badge/?version=latest
    :alt: Documentation Status
    :target: https://docs.tutor.overhang.io/en/latest/?badge=latest

.. image:: https://img.shields.io/github/stars/regisb/tutor.svg?style=social
    :alt: Github stars
    :target: https://github.com/regisb/tutor/

.. image:: https://img.shields.io/github/issues/regisb/tutor.svg
    :alt: GitHub issues
    :target: https://github.com/regisb/tutor/issues

.. image:: https://img.shields.io/github/issues-closed/regisb/tutor.svg?colorB=brightgreen
    :alt: GitHub closed issues
    :target: https://github.com/regisb/tutor/issues?q=is%3Aclosed

.. image:: https://img.shields.io/github/license/regisb/tutor.svg
    :alt: AGPL License
    :target: https://www.gnu.org/licenses/agpl-3.0.en.html

**Tutor** is a one-click install of `Open edX <https://openedx.org>`_, both for production and local development, inside docker containers. Tutor is easy to run, fast, full of cool features, and it is already used by dozens of Open edX platforms in the world.

.. image:: ./img/quickstart.gif
    :alt: Tutor local quickstart
    :target: https://terminalizer.com/view/91b0bfdd557

----------------------------------

.. include:: quickstart.rst
    :start-line: 1

But there's a lot more to Tutor than that! For more advanced usage, please refer to the following sections.

.. toctree::
   :maxdepth: 2
   :caption: User guide

   install
   quickstart
   local
   options
   customise
   dev
   k8s
   webui
   troubleshooting
   tutor
   faq

Source code
-----------

The complete source code for Tutor is available on Github: https://github.com/regisb/tutor

Support
-------

To get community support, go to the official discussion forums: https://discuss.overhang.io.

Contributing
------------

We go to great lengths to make it as easy as possible for people to run Open edX inside Docker containers. If you have an improvement idea, feel free to first discuss it on the `Tutor forum <https://discuss.overhang.io>`_. Did you find an issue with Tutor? Please first make sure that it's related to Tutor, and not an issue with Open edX. Then, `open an issue on Github <https://github.com/regisb/tutor/issues/new>`_. `Pull requests <https://github.com/regisb/tutor/pulls>`_ will be happily examined, too!

License
-------

This work is licensed under the terms of the `GNU Affero General Public License (AGPL) <https://github.com/regisb/tutor/blob/master/LICENSE.txt>`_.

The AGPL license covers the Tutor code, including the Dockerfiles, but not the content of the Docker images which can be downloaded from https://hub.docker.com. Software other than Tutor provided with the docker images retain their original license.

The :ref:`Tutor Web UI <webui>` depends on the `Gotty <https://github.com/yudai/gotty/>`_ binary, which is provided under the terms of the `MIT license <https://github.com/yudai/gotty/blob/master/LICENSE>`_.
