.. _plugins:

============
Introduction
============

Tutor comes with a plugin system that allows anyone to customise the deployment of an Open edX platform very easily. The vision behind this plugin system is that users should not have to fork the Tutor repository to customise their deployments. For instance, if you have created a new application that integrates with Open edX, you should not have to describe how to manually patch the platform settings, ``urls.py`` or ``*.env.yml`` files. Instead, you can create a "tutor-myapp" plugin for Tutor. This plugin will be in charge of making changes to the platform settings. Then, users will be able to use your application in three simple steps::

    # 1) Install the plugin
    pip install tutor-myapp
    # 2) Enable the plugin
    tutor plugins enable myapp
    # 3) Reconfigure and restart the platform
    tutor local launch

For simple changes, it may be extremely easy to create a Tutor plugin: even non-technical users may get started with our :ref:`plugin_development_tutorial` tutorial. We also provide a list of :ref:`simple example plugins <plugins_examples>`.

To learn about the different ways in which plugins can extend Tutor, check out the :ref:`hooks catalog <hooks_catalog>`.

Plugin commands cheatsheet
==========================

List installed plugins::

    tutor plugins list

Enable/disable a plugin::

    tutor plugins enable myplugin
    tutor plugins disable myplugin

The full plugins CLI is described in the :ref:`reference documentation <cli_plugins>`.

.. _existing_plugins:

Existing plugins
================

Many plugins are available from plugin indexes. These indexes are lists of plugins, similar to the `pypi <https://pypi.org>`__ or `npm <npmjs.com/>`__ indexes. By default, Tutor comes with the "main" plugin index. You can check available plugins from this index by running::

    tutor plugins update
    tutor plugins search

More plugins can be downloaded from the "contrib" index::

    tutor plugins index add contrib
    tutor plugins search

The "main" and "contrib" indexes include a curated list of plugins that are well maintained and introduce useful features to Open edX. These indexes are maintained by `Overhang.IO <https://overhang.io>`__. For more information about these indexes, refer to the official `overhangio/tpi <https://github.com/overhangio/tpi>`__ repository.

Thanks to these indexes, it is very easy to download and upgrade plugins. For instance, to install the `notes plugin <https://github.com/overhangio/tutor-notes/>`__::

    tutor plugins install notes

Upgrade all your plugins with::

    tutor plugins upgrade all

To list indexes that you are downloading plugins from, run::

    tutor plugins index list

For more information about these indexes, check the `official Tutor plugin indexes (TPI) <https://github.com/overhangio/tpi/>`__ repository.
