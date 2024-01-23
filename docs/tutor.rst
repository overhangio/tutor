.. _tutor:

Tutor development
=================

Setting up your development environment
---------------------------------------

Start by cloning the Tutor repository::

    git clone https://github.com/overhangio/tutor.git
    cd tutor/

Install requirements
~~~~~~~~~~~~~~~~~~~~

::

    pip install -r requirements/dev.txt

Run tests
~~~~~~~~~

::

    make test

Yes, there are very few unit tests for now, but this is probably going to change.

Code formatting
~~~~~~~~~~~~~~~

Tutor code formatting is enforced by `black <https://black.readthedocs.io/en/stable/>`_. To check whether your code changes conform to formatting standards, run::

    make test-format

And to automatically fix formatting errors, run::

    make format

Static error detection is performed by `pylint <https://pylint.readthedocs.io/en/latest/>`_. To detect errors, run::

    make test-lint

Common developer tasks
----------------------

Generating the ``tutor`` executable binary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    make bundle

Generating the documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install -r requirements/docs.txt
    cd docs/
    make html

You can then browse the documentation with::

    make browse

Releasing a new version
~~~~~~~~~~~~~~~~~~~~~~~

Releasing a version includes two phases:

1. Add changes and generate individual changelog entries:

- run ``make changelog-entry``(or ``scriv create``) command - It will create changelog entries in a folder named changelog.d for the changes user has done for releasing a new version.
- Commit and merge all the changes including the changelog entries. e.g this `commit <https://github.com/overhangio/tutor-discovery/commit/e30a78936d63439bde069aeff11960585bd81592>`_.

2. Update version and compile changelogs:

- Now bump the ``__version__`` value in ``tutor/__about__.py``. (see :ref:`versioning` below).
- Collect changelog entries with ``make changelog``(or ``scriv collect``) command - It will delete all previous changelog entries from changelog.d folder and will add records of those entries to CHANGELOG.md file.
- Create a commit with the version changelog e.g. this `commit <https://github.com/overhangio/tutor-discovery/commit/18cce706a794c4968e713f0f72c6b912a2ff1e53>`_.
- Run tests with ``make test``.
- Push your changes to the upstream repository.

.. _versioning:

Versioning
----------

The versioning format used in Tutor is the following::

    RELEASE.MAJOR.MINOR(-BRANCH)

When making a new Tutor release, increment the:

- RELEASE version when a new Open edX release comes out. The new value should match the ordinal value of the first letter of the release name: Aspen 🡒 1, Birch 🡒 2, ... Zebra 🡒 26.
- MAJOR version when making a backward-incompatible change (prefixed by "💥" in the changelog, as explained below).
- MINOR version when making a backward-compatible change.

An optional BRANCH suffix may be appended to the release name to indicate that extra changes were added on top of the latest release. For instance, "x.y.z-nightly" corresponds to release x.y.z on top of which extra changes were added to make it compatible with the Open edX master branches (see the :ref:`tutorial on running Tutor Nightly <nightly>`).

`Officially-supported plugins <https://overhang.io/tutor/plugins>`__ follow the same versioning pattern. As a third-party plugin developer, you are encouraged to use the same pattern to make it immediately clear to your end-users which Open edX versions are supported.

.. _contributing:

Contributing to Tutor
---------------------

Third-party contributions to Tutor and its plugins are more than welcome! Just make sure to follow these guidelines:

- Outside of obvious bugs, contributions should be discussed first in the `official Open edX forum <https://discuss.openedx.org>`__.
- Once we agree on a high-level solution, you should open a pull request on the `Tutor repository <https://github.com/overhangio/tutor/pulls>`__ or the corresponding plugin.
- Make sure that all tests pass by running ``make test`` (see above).
- If your PR is in the Tutor core repository, add a changelog entry by running ``make changelog-entry``. Edit the new file and follow the formatting instructions that it contains.
- Write a good Git commit title and message: explain why you are making this change, what problem you are solving and which solution you adopted. Link to the relevant conversation topics in the forums and describe your use case. We *love* long, verbose descriptions :) As for the title, `conventional commits <https://www.conventionalcommits.org>`__ are preferred. Check the repo history!

Happy hacking! ☘️

.. _maintainers:

Joining the team of Tutor Maintainers
-------------------------------------

We have an open team of volunteers who help support the project. You can read all about it `here <https://discuss.openedx.org/t/tutor-maintainers/7287>`__ -- and we hope that you'll consider joining us 😉
