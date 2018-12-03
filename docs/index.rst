.. Tutor documentation master file, created by
   sphinx-quickstart on Mon Dec  3 21:36:51 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Tutor: Open edX 1-click install for everyone
============================================

.. image:: https://img.shields.io/travis/regisb/openedx-docker.svg
    :alt: Build status
    :target: https://travis-ci.org/regisb/openedx-docker

.. image:: https://img.shields.io/github/issues/regisb/openedx-docker.svg
    :alt: GitHub issues
    :target: https://github.com/regisb/openedx-docker/issues

.. image:: https://img.shields.io/github/issues-closed/regisb/openedx-docker.svg?colorB=brightgreen
    :alt: GitHub closed issues
    :target: https://github.com/regisb/openedx-docker/issues?q=is%3Aclosed

Tutor is a one-click install of `Open edX <https://openedx.org>`_, both for production and local development, inside docker containers.

.. image:: https://asciinema.org/a/6DowVk4iJf3AJ2m8xlXDWJKh3.png
    :alt: asciicast
    :target: https://asciinema.org/a/6DowVk4iJf3AJ2m8xlXDWJKh3

----------------------------------

**Quickstart**::

    git clone https://github.com/regisb/openedx-docker
    cd openedx-docker/
    make all

**That's it?**

Yes :) When running `make all`, you will be asked a few questions about the configuration of your Open edX platform. Then, all the components for a functional Open edX platform will be downloaded and assembled to and you will have both an LMS and a CMS running behind a web server on port 80, ready for production. You should be able to access your platform at the address you gave during the configuration phase.

All of this without touching your host environment! You don't even need root access.

To be honest, I really don't like 1-click installs :-p They tend to hide much of the important details. So I strongly recommend you read the more detailed instructions below to understand what is going on exactly and to troubleshoot potential issues. Also, instructions are given to setup a local development environment.

This might seem too simple to be true, but there's no magic -- just good packaging of already existing Open edX code. The code for building the Docker images is 100% available and fits in less than 1000 lines of code, in this repository.

.. toctree::
   :maxdepth: 2
   :caption: User guide

   requirements
   step
   options
   customise
   dev
   troubleshooting
   missing

Disclaimers & Warnings
----------------------

This project is the follow-up of my work on an `install from scratch of Open edX <https://github.com/regisb/openedx-install>`_. It does not rely on any hack or complex deployment script. In particular, we do not use the Open edX `Ansible deployment playbooks <https://github.com/edx/configuration/>`_. That means that the folks at edX.org are *not* responsible for troubleshooting issues of this project. Please don't bother Ned ;-)

Do you have a problem?

1. Carefully read the README, and in particular the :ref:`troubleshooting` section
2. Search for your problem in the `open and closed Github issues <https://github.com/regisb/openedx-docker/issues?utf8=%E2%9C%93&q=is%3Aissue>`_.
3. If necessary, open an `issue on Github <https://github.com/regisb/openedx-docker/issues/new>`_.


Contributing
------------

Pull requests will be happily examined! However, we should be careful to keep the project lean and simple: both to use and to modify. Optional features should not make the user experience more complex. Instead, documentation on how to add the feature is preferred.

License
-------

This work is licensed under the terms of the `MIT License <https://github.com/regisb/openedx-docker/blob/master/LICENSE.txt>`_.
