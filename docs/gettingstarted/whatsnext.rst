What's next
===========

You have gone through the :ref:`Quickstart installation <quickstart>`: at this point, you should have a running Open edX platform. If you don't, please follow the instructions from the :ref:`Troubleshooting <troubleshooting>` section.

Logging-in as administrator
---------------------------

Out of the box, Tutor does not create any user for you. You will want to create a user yourself with staff and administrator privileges to access the studio. There is a :ref:`simple command for that <createuser>`.

Importing a demo course
-----------------------

To get a glimpse of the possibilities of Open edX, we recommend you import the `official demo test course <https://github.com/openedx/edx-demo-course>`__. Tutor provides a :ref:`simple command for that <democourse>`.

Making Open edX look better
---------------------------

Tutor makes it easy to :ref:`install <theming>` and :ref:`develop <theme_development>` your own themes. We also provide `Indigo <https://github.com/overhangio/indigo>`__: a free, customizable theme that you can install today.

Adding features
---------------

Check out the Tutor :ref:`plugins <plugins>` and :ref:`configuration/customization options <configuration_customisation>`.

Hacking into Open edX
---------------------

Tutor works great as a development environment for Open edX developers, both for debugging and developing new features. Please check out the :ref:`development documentation <development>`.

Deploying to Kubernetes
-----------------------

Yes, Tutor comes with Kubernetes deployment support :ref:`out of the box <k8s>`.

Gathering insights and analytics about Open edX
-----------------------------------------------

Check out `Cairn <https://overhang.io/tutor/plugin/cairn>`__, the next-generation analytics solution for Open edX.

Meeting the community
---------------------

Ask your questions and chat with the Tutor community on the official Open edX community forum: https://discuss.openedx.org

.. _autocomplete:

Shell autocompletion
--------------------

Tutor is built on top of `Click <https://click.palletsprojects.com>`_, which is a great library for building command line interface (CLI) tools. As such, Tutor benefits from all Click features, including `auto-completion <https://click.palletsprojects.com/en/8.x/bashcomplete/>`_. After installing Tutor, auto-completion can be enabled in bash by running::

    _TUTOR_COMPLETE=bash_source tutor >> ~/.bashrc

If you are running zsh, run instead::

    _TUTOR_COMPLETE=zsh_source tutor >> ~/.zshrc

After opening a new shell, you can test auto-completion by typing::

    tutor <tab><tab>