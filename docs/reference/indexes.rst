==============
Plugin indexes
==============

Plugin indexes are a great way to have your plugins discovered by other users. Plugin indexes make it easy for other Tutor users to install and upgrade plugins from other developers. Examples include the official indexes, which can be found in the `overhangio/tpi <https://github.com/overhangio/tpi/>`__ repository.

Index file paths
================

A plugin index is a yaml-formatted file. It can be stored on the web or on your computer. In both cases, the index file location must end with "<current release name>/plugins.yml". For instance, the following are valid index locations if you run the Open edX "Sumac" release:

- https://overhang.io/tutor/main/sumac/plugins.yml
- ``/path/to/your/local/index/sumac/plugins.yml``

To add either indexes, run the ``tutor plugins index add`` command without the suffix. For instance::

    tutor plugins index add https://overhang.io/tutor/main
    tutor plugins index add /path/to/your/local/index/

Your plugin cache should be updated immediately. You can also update the cache at any point by running::

    tutor plugins update

To view current indexes, run::

    tutor plugins index list

To remove an index, run::

    tutor plugins index remove <index url>

Plugin entry syntax
===================

A "plugins.yml" file is a yaml-formatted list of plugin entries. Each plugin entry has two required fields: "name" and "src". For instance, here is a minimal plugin entry::

    - name: mfe
      src: tutor-mfe

"name" (required)
-----------------

A plugin name is how it will be referenced when we run ``tutor plugins install <name>`` or ``tutor plugins enable <name>``. It should be concise and easily identifiable, just like a Python or apt package name.

Plugins with duplicate names will be overridden, depending on the index in which they are declared: indexes further down ``tutor plugins index list`` (which have been added later) will have higher priority.

.. _plugin_index_src:

"src" (required)
----------------

A plugin source can be either:

1. A pip requirement file format specifier (see `reference <https://pip.pypa.io/en/stable/reference/requirements-file-format/>`__).
2. The path to a Python file on your computer.
3. The URL of a Python file on the web.

In the first case, the plugin will be installed as a Python package. In the other two cases, the plugin will be installed as a single-file plugin.

The following "src" attributes are all valid::

    # Pypi package
    src: tutor-mfe

    # Pypi package with version specification
    src: tutor-mfe>=42.0.0,<43.0.0

    # Python package from a private index
    src: |
        --index-url=https://pip.mymirror.org
        my-plugin>=10.0

    # Remote git repository
    src: -e git+https://github.com/myusername/tutor-contrib-myplugin@v27.0.0#egg=tutor-contrib-myplugin

    # Local editable package
    src: -e /path/to/my/plugin

"url" (optional)
----------------

Link to the plugin project, where users can learn more about it and ask for support.

"author" (optional)
-------------------

Original author of the plugin. Feel free to include your company name and email address here. For instance: "Leather Face <niceguy@happyfamily.com>".

"maintainer" (optional)
-----------------------

Current maintainer of the plugin. Same format as "author".

"description" (optional)
------------------------

Multi-line string that should contain extensive information about your plugin. The full description will be displayed with ``tutor plugins show <name>``. It will also be parsed for a match by ``tutor plugins search <pattern>``. Only the first line will be displayed in the output of ``tutor plugins search``. Make sure to keep the first line below 128 characters.


Examples
========

Manage plugins in development
-----------------------------

Plugin developers and maintainers often want to install local versions of their plugins. They usually achieve this with ``pip install -e /path/to/tutor-plugin``. We can improve that workflow by creating an index for local plugins::

    # Create the plugin index directory
    mkdir -p ~/localindex/sumac/
    # Edit the index
    vim ~/localindex/sumac/plugins.yml

Add the following to the index::

    - name: myplugin1
      src: -e /path/to/tutor-myplugin1
    - name: myplugin2
      src: -e /path/to/tutor-myplugin2

Then add the index::

    tutor plugins index add ~/localindex/

Install the plugins::

    tutor plugins install myplugin1 myplugin2

Re-install all plugins::

    tutor plugins upgrade all

The latter commands will install from the local index, and not from the remote indexes, because indexes that are added last have higher priority when plugins with the same names are found.

Install plugins from a private index
------------------------------------

Plugin authors might want to share plugins with a limited number of users. This is for instance the case when a plugin is for internal use only.

First, users should have access to the ``plugins.yml`` file. There are different ways to achieve that:

- Make the index public: after all, it's mostly the plugins which are private. 
- Grant access to the index from behind a VPN.
- Hide the index behing a basic HTTP auth url. The index can then be added with ``tutor plugins index add http://user:password@mycompany.com/index/``.
- Download the index to disk, and then add it from the local path: ``tutor plugins index add ../path/to/index``.

Second, users should be able to install the plugins that are listed in the index. We recommend that the plugins are uploaded to a pip-compatible self-hosted mirror, such as `devpi <https://devpi.net/docs/devpi/devpi/latest/+doc/index.html>`__. Alternatively, packages can be installed from a private Git repository. For instance::

    # Install from private pip index
    - name: myprivateplugin1
      src: |
        --index-url=https://my-pip-index.mycompany.com/
        tutor-contrib-myprivateplugin

    # Install from private git repository
    - name: myprivateplugin2
      src: -e git+https://git.mycompany.com/tutor-contrib-myplugin2.git

Both examples work because the :ref:`"src" <plugin_index_src>` field supports just any syntax that could also be included in a requirements file installed with ``pip install -r requirements.txt``.
