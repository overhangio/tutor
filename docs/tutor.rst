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
- Replace "Unreleased" by the version name and date in CHANGELOG.md.
- Create a commit with the version changelog.
- ``make release`` (this assumes that there are two remotes named "origin" and "overhangio")

After a regular push to ``master``, run ``make nightly`` to update the "nightly" tag.

.. _contributing:

Contributing to Tutor
---------------------

Third-party contributions to Tutor and its plugins are more than welcome! Just make sure to follow these guidelines:

- Outside of obvious bugs, contributions should be discussed first in the `official Tutor forums <https://discuss.overhang.io>`__.
- Once we agree on a high-level solution, you should open a pull request on the `Tutor repository <https://github.com/overhangio/tutor/pulls>`__ or the corresponding plugin.
- Write a good Git commit title and message: explain why you are making this change, what problem you are solving and which solution you adopted. Link to the relevant conversation topics in the forums and describe your use case. We *love* long, verbose descriptions :)
- Make sure that all tests pass by running ``make test`` (see above).
- If your PR is in the Tutor core repository, add an item to the CHANGELOG file, in the "Unreleased" section. Use the same format as the other items::

    - [TYPE] DESCRIPTION

Where "TYPE" is either "Bugfix", "Improvement", "Feature" or "Security". You should add an explosion emoji ("💥") before "[TYPE]" if you are making a breaking change.

Happy hacking! ☘️

Becoming a Tutor Maintainer
---------------------------

Is Tutor a core part of your infrastructure? Would you like to contribute to the project roadmap? Then you should consider becoming a Tutor maintainer. Tutor maintainers are individuals and companies who help make decisions on the future of the prject. Their goal is to support the Tutor community and to make the software as best as possible.

More precisely, project maintainers are responsible for one or more of the following tasks:

- Interaction with the community on the `Tutor forums <discuss.overhang.io/>`__: maintainers are there to answer questions, help users troubleshoot issues, announce new features and changes.
- Address Github issues by triaging, commenting and, when possible, proposing a fix for them.
- Review Github pull requests, both from external contributors and other maintainers.

As a Tutor maintainer, you should expect that your role will require about 4-8 hours of work per month. If maintainers work more than that, then it means that more maintainers should be brought on board. If you find that you cannot sustain this pace of work for an extended period of time (~1 month), then we ask that you clearly signal your new situation by removing yourself from the maintainers group. This will not impede your ability to join the group again at a later time.

In exchange for these responsibilities, Tutor maintainers can contribute to every major decision of the project, including the roadmap. Every pull request must be approved by at least one Tutor maintainer (other than the author). In discussions, every maintainer who contributes as an invididual has one voice. Contributing companies also have once voice, independently of how many maintainers are affiliated to them. In decisions, Tutor maintainers should strive to achieve consensus. When consensus is not possible, Régis Behmo is responsible for making the final decision.

It should be made clear that joining the Tutor maintainers program does *not* grant the following:

- Merge rights to Github repositories from the `Overhang.IO <https://github.com/overhangio>`__ organization.
- Payment or material reward of any nature.
