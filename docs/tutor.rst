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
