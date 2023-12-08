Getting started with plugin development
=======================================

.. include:: legacy.rst

Plugins can be created in two different ways: either as plain YAML files or installable Python packages. YAML files are great when you need to make minor changes to the default platform, such as modifying settings. For creating more complex applications, it is recommended to create python packages.

.. _plugins_yaml:

YAML file
~~~~~~~~~

YAML files that are stored in the tutor plugins root folder will be automatically considered as plugins. The location of the plugin root can be found by running::

    tutor plugins printroot

On Linux, this points to ``~/.local/share/tutor-plugins``. The location of the plugin root folder can be modified by setting the ``TUTOR_PLUGINS_ROOT`` environment variable.

YAML plugins must define two special top-level keys: ``name`` and ``version``. Then, YAML plugins may use two more top-level keys to customise Tutor's behaviour: ``config`` and ``patches``. Custom CLI commands, templates, and hooks are not supported by YAML plugins.

Let's create a simple plugin that adds your own `Google Analytics <https://analytics.google.com/>`__ tracking code to your Open edX platform. We need to add the ``GOOGLE_ANALYTICS_ACCOUNT`` and ``GOOGLE_ANALYTICS_TRACKING_ID`` settings to both the LMS and the CMS settings. To do so, we will only have to create the ``openedx-common-settings`` patch, which is shared by the development and the production settings both for the LMS and the CMS. First, create the plugin directory::

    mkdir "$(tutor plugins printroot)"

Then add the following content to the plugin file located at ``$(tutor plugins printroot)/myplugin.yml``::

    name: googleanalytics
    version: 0.1.0
    patches:
      openedx-common-settings: |
        # googleanalytics special settings
        GOOGLE_ANALYTICS_ACCOUNT = "UA-654321-1"
        GOOGLE_ANALYTICS_TRACKING_ID = "UA-654321-1"

Of course, you should replace your Google Analytics tracking code with your own. You can verify that your plugin is correctly installed, but not enabled yet::

    $ tutor plugins list
    googleanalytics@0.1.0 (disabled)

You can then enable your newly-created plugin::

    tutor plugins enable googleanalytics

You should be able to view your changes in every LMS and CMS settings file::

    grep -r googleanalytics "$(tutor config printroot)/env/apps/openedx/settings/"

Now just restart your platform to start sending tracking events to Google Analytics::

    tutor local launch

That's it! And it's very easy to share your plugins. Just upload them to your Github repo and share the url with other users. They will be able to install your plugin by running::

    tutor plugins install https://raw.githubusercontent.com/username/yourrepo/master/googleanalytics.yml

Python package
~~~~~~~~~~~~~~

Creating a plugin as a Python package allows you to define more complex logic and store your patches in a more structured way. Python Tutor plugins are regular Python packages that define an entry point within the ``tutor.plugin.v0`` group:

Example::

    from setuptools import setup
    setup(
        ...
        entry_points={
          "tutor.plugin.v0": ["myplugin = myplugin.plugin"]
        },
    )

The ``myplugin/plugin.py`` Python module can then define the attributes ``config``, ``patches``, ``hooks``, and ``templates`` to specify the plugin's behaviour. The attributes may be defined either as dictionaries or as zero-argument callables returning dictionaries; in the latter case, the callable will be evaluated upon plugin load. Finally, the ``command`` attribute can be defined as an instance of ``click.Command`` to define the plugin's command line interface.

Example::

  import click

  templates = pkg_resources.resource_filename(...)
  config = {...}
  hooks = {...}

  def patches():
    ...

  @click.command(...)
  def command():
    ...

To get started on the right foot, it is strongly recommended to create your first plugin with the `tutor plugin cookiecutter <https://github.com/overhangio/cookiecutter-tutor-plugin>`__::

    pip install cookiecutter
    cookiecutter https://github.com/overhangio/cookiecutter-tutor-plugin.git
    pip install -e ./tutor-myplugin
    tutor plugins list # your plugin should appear here
    tutor plugins enable myplugin # hack at it!
