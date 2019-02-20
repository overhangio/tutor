Tutor 🎓 Open edX 1-click install for everyone
==============================================

.. image:: https://img.shields.io/travis/regisb/tutor.svg
    :alt: Build status
    :target: https://travis-ci.org/regisb/tutor

.. image:: https://img.shields.io/badge/docs-current-brightgreen.svg
    :alt: Documentation
    :target: https://docs.tutor.overhang.io

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

.. image:: ./docs/img/quickstart.gif
    :alt: Tutor local quickstart
    :target: https://terminalizer.com/view/91b0bfdd557

Quickstart
----------

1. `Download <https://github.com/regisb/tutor/releases>`_ the latest stable release of Tutor, uncompress the file and place the ``tutor`` executable in your path. From the command line::

       sudo curl -L "https://github.com/regisb/tutor/releases/download/latest/tutor-$(uname -s)_$(uname -m)" -o /usr/local/bin/tutor
       sudo chmod +x /usr/local/bin/tutor

2. Run ``tutor local quickstart``
3. You're done!

Documentation
-------------

Extensive documentation is available online: https://docs.tutor.overhang.io/

Support
-------

To get community support, go to the official discussion forums: https://discuss.overhang.io.

Contributing
------------

We go to great lengths to make it as easy as possible for people to run Open edX inside Docker containers. If you have an improvement idea, feel free to first discuss it on the `Tutor forum <https://discuss.overhang.io>`_. Did you find an issue with Tutor? Please first make sure that it's related to Tutor, and not an issue with Open edX. Then, `open an issue on Github <https://github.com/regisb/tutor/issues/new>`_. `Pull requests <https://github.com/regisb/tutor/pulls>`_ will be happily examined, too!
