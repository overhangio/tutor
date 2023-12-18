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

- Bump the ``__version__`` value in ``tutor/__about__.py``. (see :ref:`versioning` below)
- Collect changelog entries with ``make changelog``.
- Create a commit with the version changelog.
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

- **General Discussion**: For anything beyond obvious bugs, initiate a discussion in the `official Open edX forum <https://discuss.openedx.org>`__. This helps in agreeing on a high-level solution.
- **Pull Requests**: Open a pull request on the `Tutor repository <https://github.com/overhangio/tutor/pulls>`__ for changes to the Tutor core or the corresponding plugin for plugin-specific changes.
- **Running Tests**: Ensure that all tests pass by running ``make test``. This applies to both the Tutor core and plugin contributions.
- **Changelog Entry**: If your PR is in the Tutor core repository or affects plugin users, add a changelog entry by running ``make changelog-entry``. Edit the new file as per the formatting instructions.
- **Code Formatting**: Format your code, if necessary, using ``make format``.
- **Commit Messages**: Craft a clear Git commit title and message. Explain the rationale behind your changes, the problem you're addressing, and the chosen solution. Link to relevant forum discussions and detail your use case. We appreciate detailed explanations. Use `conventional commits <https://www.conventionalcommits.org>`__ for the title.

Plugin-Specific Guidelines
--------------------------

For plugin contributions, keep the following additional points in mind:

- Do not bump the version number in your contributions. This is handled separately during the release process.

Releasing a New Version
-----------------------

For releasing a new version :

- **Version Number**: Bump the version number in ``__about__.py``.
- **Changelog Compilation**: Collect all changelog entries using ``make changelog``.
- **Git Commit for Release**: Indicate the new version in the git commit title with the format ``git commit -a -m "vX.Y.Z"``.

Happy hacking! ☘️☘️

.. _maintainers:

Joining the team of Tutor Maintainers
-------------------------------------

We have an open team of volunteers who help support the project. You can read all about it `here <https://discuss.openedx.org/t/tutor-maintainers/7287>`__ -- and we hope that you'll consider joining us 😉
