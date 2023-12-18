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

Contributions to Tutor and its plugins are highly encouraged. Please adhere to the following guidelines:

- **General Discussion**: Before addressing anything other than clear-cut bugs, start a discussion on the `official Open edX forum <https://discuss.openedx.org>`__. This facilitates reaching a consensus on a high-level solution.
- **Pull Requests**: For changes to Tutor core or plugin-specific modifications, open a pull request on the `Tutor repository <https://github.com/overhangio/tutor/pulls>`__.
- **Running Tests and Code Formatting**:
  - Ensure all tests pass by running ``make test``. This is mandatory for both Tutor core and plugin contributions.
  - If formatting tests fail, correct your code format using ``make format``.
- **Changelog Entry**: Create a changelog entry for significant changes (excluding reformatting or documentation) by running ``make changelog-entry``. Edit the newly created file following the given formatting instructions. This applies to both Tutor core and plugin changes.
- **Commit Messages**: Write clear Git commit titles and messages. Detail the rationale for your changes, the issue being addressed, and your solution. Include links to relevant forum discussions and describe your use case. Detailed explanations are valuable. For commit titles, follow `conventional commits <https://www.conventionalcommits.org>`__ guidelines.

Releasing a new version
-----------------------

When releasing a new version:

- **Version Number**: Update the version number in `__about__.py`. For detailed guidelines on version numbering, refer to the [versioning guidelines](:ref:`versioning`).
- **Changelog Compilation**: Compile all changelog entries using ``make changelog``.
- **Git Commit for Release**: Use the format ``git commit -a -m "vX.Y.Z"`` to indicate the new version in the git commit title.

Happy hacking! ☘️

.. _maintainers:

Joining the team of Tutor Maintainers
-------------------------------------

We have an open team of volunteers who help support the project. You can read all about it `here <https://discuss.openedx.org/t/tutor-maintainers/7287>`__ -- and we hope that you'll consider joining us 😉
