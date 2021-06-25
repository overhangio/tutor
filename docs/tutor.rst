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

- Bump the ``__version__`` value in ``tutor/__about__.py``.
- Replace "Unreleased" by the version name and date in CHANGELOG.md.
- Create a commit with the version changelog.
- Run ``make release``: this will push to the default repo/branch for the current branch.

.. _contributing:

Contributing to Tutor
---------------------

Third-party contributions to Tutor and its plugins are more than welcome! Just make sure to follow these guidelines:

- Outside of obvious bugs, contributions should be discussed first in the `official Tutor forums <https://discuss.overhang.io>`__.
- Once we agree on a high-level solution, you should open a pull request on the `Tutor repository <https://github.com/overhangio/tutor/pulls>`__ or the corresponding plugin.
- Make sure that all tests pass by running ``make test`` (see above).
- If your PR is in the Tutor core repository, add an item to the CHANGELOG file, in the "Unreleased" section. Use the same format as the other items::

    - [TYPE] DESCRIPTION

Where "TYPE" is either "Bugfix", "Improvement", "Feature" or "Security". You should add an explosion emoji ("💥") before "[TYPE]" if you are making a breaking change.

- Write a good Git commit title and message: explain why you are making this change, what problem you are solving and which solution you adopted. Link to the relevant conversation topics in the forums and describe your use case. We *love* long, verbose descriptions :) As for the title, `conventional commits <https://www.conventionalcommits.org>`__ are preferred. Check the repo history!

Happy hacking! ☘️

.. _maintainers:

Joining the team of Tutor Maintainers
-------------------------------------

We have an open team of volunteers who help support the project. You can read all about it `here <https://discuss.overhang.io/t/the-tutor-maintainer-handbook/1375>`__ -- and we hope that you'll consider joining us 😉
