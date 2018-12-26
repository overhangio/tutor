.. Tutor documentation master file, created by
   sphinx-quickstart on Mon Dec  3 21:36:51 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Tutor 🎓 Open edX 1-click install for everyone
==============================================

.. image:: https://img.shields.io/travis/regisb/tutor.svg
    :alt: Build status
    :target: https://travis-ci.org/regisb/tutor

.. image:: https://img.shields.io/github/issues/regisb/tutor.svg
    :alt: GitHub issues
    :target: https://github.com/regisb/tutor/issues

.. image:: https://img.shields.io/github/issues-closed/regisb/tutor.svg?colorB=brightgreen
    :alt: GitHub closed issues
    :target: https://github.com/regisb/tutor/issues?q=is%3Aclosed

**Tutor** is a one-click install of `Open edX <https://openedx.org>`_, both for production and local development, inside docker containers. Tutor is easy to run, fast, full of cool features, and it is already used by dozens of Open edX platforms in the world.

.. image:: https://asciinema.org/a/6DowVk4iJf3AJ2m8xlXDWJKh3.png
    :alt: asciicast
    :target: https://asciinema.org/a/6DowVk4iJf3AJ2m8xlXDWJKh3

----------------------------------

.. include:: quickstart.rst
    :start-line: 1

For more advanced usage of Tutor, please refer to the following sections.

.. toctree::
   :maxdepth: 2
   :caption: User guide

   quickstart
   requirements
   local
   k8s
   options
   customise
   dev
   troubleshooting
   missing
   tutor

Disclaimers & Warnings
----------------------

This project is the follow-up of my work on an `install from scratch of Open edX <https://github.com/regisb/openedx-install>`_. It does not rely on any hack or complex deployment script. In particular, we do not use the Open edX `Ansible deployment playbooks <https://github.com/edx/configuration/>`_. That means that the folks at edX.org are *not* responsible for troubleshooting issues of this project. Please don't bother Ned ;-)

In case of trouble, please follow the instructions in the :ref:`troubleshooting` section.

Contributing
------------

We go to great lengths to make it as easy as possible for people to run Open edX inside Docker containers. If you have an improvement idea, feel free to `open an issue on Github <https://github.com/regisb/tutor/issues/new>`_ so that we can discuss it. `Pull requests <https://github.com/regisb/tutor/pulls>`_ will be happily examined, too! However, we should be careful to keep the project lean and simple: both to use and to modify. Optional features should not make the user experience more complex. Instead, documentation on how to add the feature is preferred.

License
-------

This work is licensed under the terms of the `MIT License <https://github.com/regisb/tutor/blob/master/LICENSE.txt>`_.
