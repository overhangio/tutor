.. _tutor:

Tutor development
=================

Start by cloning the Tutor repository::

    git clone https://github.com/overhangio/tutor.git
    cd tutor/

Install requirements
--------------------

::

    pip install -r requirements/dev.txt

Run tests
---------

::

    make test

Yes, there are very few unit tests for now, but this is probably going to change.

Code formatting
---------------

Tutor code formatting is enforced by `black <https://black.readthedocs.io/en/stable/>`_. To check whether your code changes conform to formatting standards, run::

    make test-format

And to automatically fix formatting errors, run::

    make format

Static error detection is performed by `pylint <https://pylint.readthedocs.io/en/latest/>`_. To detect errors, run::

    make test-lint

Bundle ``tutor`` executable
---------------------------

::

    make bundle

Generating the documentation
----------------------------

::

    pip install -r requirements/docs.txt
    cd docs/
    make html

You can then browse the documentation with::

    make browse

Releasing a new version
-----------------------

- Bump the ``__version__`` value in ``tutor/__about__.py``.
- Replace "Latest" by the version name in CHANGELOG.md.
- Create a commit with the version changelog.
- ``make release`` (this assumes that there are two remotes named "origin" and "overhangio")

After a regular push to ``master``, run ``make nightly`` to update the "nightly" tag.
