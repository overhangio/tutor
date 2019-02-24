.. _tutor:

Tutor development
=================

Start by cloning the Tutor repository::

    git clone https://github.com/regisb/tutor.git
    cd tutor/

Install requirements
--------------------

::

    pip install -r requirements/dev.txt

Bundle ``tutor`` executable
---------------------------

::

    make bundle

Generate the documentation
--------------------------

::

    pip install sphinx sphinx_rtd_theme
    cd docs/
    make html

You can then browse the documentation with::

    make browse

Releasing a new version
-----------------------

- Bump the ``__version__`` value in ``tutor/__about__.py``.
- Replace "Latest" by the version name in CHANGELOG.md.
- Create a commit with the version changelog.
- ``git push``
- ``make tag``
