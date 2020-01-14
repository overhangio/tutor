.. _plugins:

Plugins
=======

Tutor comes with a plugin system that allows anyone to customise the deployment of an Open edX platform very easily. The vision behind this plugin system is that users should not have to fork the Tutor repository to customise their deployments. For instance, if you have created a new application that integrates with Open edX, you should not have to describe how to manually patch the platform settings, ``urls.py`` or ``*.env.json`` files. Instead, you can create a "tutor-myapp" plugin for Tutor. Then, users will start using your application in three simple steps::

    # 1) Install the plugin
    pip install tutor-myapp
    # 2) Enable the plugin
    tutor plugins enable myapp
    # 3) Reconfigure and restart the platform
    tutor local quickstart

In the following we see how to use and create Tutor plugins.

Commands
--------

List installed plugins::
  
    tutor plugins list
    
Enable/disable a plugin::
  
    tutor plugins enable myplugin
    tutor plugins disable myplugin
    
After enabling or disabling a plugin, the environment should be re-generated with::
  
    tutor config save

API
---

Plugins can affect the behaviour of Tutor at multiple levels. First, plugins can define new services with their Docker images, settings and the right initialisation commands. To do so you will have to define custom :ref:`config <plugin_config>`, :ref:`patches <plugin_patches>`, :ref:`hooks <plugin_hooks>` and :ref:`templates <plugin_templates>`. Then, plugins can also extend the CLI by defining their own :ref:`commands <plugin_command>`.

.. _plugin_config:

config
~~~~~~

The ``config`` attribute is used to modify existing and add new configuration parameters:

* ``config["add"]`` are key/values that should be added to the user-specific ``config.yml`` configuration. Add there passwords, secret keys and other values that do not have a default value.
* ``config["defaults"]`` are default key/values for this plugin. These values will not be added to the ``config.yml`` user file unless users override them manually with ``tutor config save --set ...``.
* ``config["set"]`` are existing key/values that should be modified. Be very careful what you add there! Plugins may define conflicting values for some parameters.

 "set" and "default" key names will be automatically prefixed with the plugin name, in upper case.

Example::
  
    config = {
        "add": {
            "SECRET_KEY": "{{ 8|random_string }}"
        }
        "defaults": {
            "DOCKER_IMAGE": "username/imagename:latest",
        },
        "set": {
            "MASTER_PASSWORD": "h4cked",
        },
    }

This configuration from the "myplugin" plugin will set the following values:

- ``MYPLUGIN_SECRET_KEY``: an 8-character random string will be generated and stored in the user configuration.
- ``MYPLUGIN_DOCKER_IMAGE``: this value will by default not be stored in ``config.yml``, but ``tutor config printvalue MYPLUGIN_DOCKER_IMAGE`` will print ``username/imagename:latest``.
- ``MASTER_PASSWORD`` will be set to ``h4cked``. Needless to say, plugin developers should avoid doing this.

.. _plugin_patches:

patches
~~~~~~~

Plugin patches affect the rendered environment templates. In many places the Tutor templates include calls to ``{{ patch("patchname") }}``. This grants plugin developers the possibility to modify the content of rendered templates. Plugins can add content in these places by adding values to the ``patches`` attribute.

.. note::
    The list of existing patches can be found by searching for `{{ patch(` strings in the Tutor source code::
    
        git grep "{{ patch"
    
    The list of patches can also be browsed online `on Github <https://github.com/search?utf8=✓&q={{+patch+repo%3Aoverhangio%2Ftutor+path%3A%2Ftutor%2Ftemplates&type=Code&ref=advsearch&l=&l= 8>`__.
    
Example::
  
    patches = {
        "local-docker-compose-services": """redis:
    image: redis:latest"""
    }

This will add a Redis instance to the services run with ``tutor local`` commands.

.. note::
    The ``patches`` attribute can be a callable function instead of a static dict value.


.. _plugin_hooks:

hooks
~~~~~

Hooks are actions that are run during the lifetime of the platform. For instance, hooks are used to trigger database initialisation and migrations. Each hook has a different specification.

``init``
++++++++

The services that will be run during initialisation should be added to the ``init`` hook, for instance for database creation and migrations.

Example::
  
    hooks = {
      "init": ["myservice1", "myservice2"]
    }
    
During initialisation, "myservice1" and "myservice2" will be run in sequence with the commands defined in the templates ``myplugin/hooks/myservice1/init`` and ``myplugin/hooks/myservice2/init``.

``pre-init``
++++++++++++

This hook will be executed just before the ``init`` hooks. Otherwise, the specs are identical. This is useful for creating databases or other resources that will be required during initialisation, for instance.

``build-image``
+++++++++++++++

This is a hook that will be run to build a docker image for the requested service.

Example::

    hooks = {
        "build-image": {"myimage": "myimage:latest"}
    }
    
With this hook, users will be able to build the ``myimage:latest`` docker image by running::
  
    tutor images build myimage

or::
  
    tutor images build all

This assumes that there is a ``Dockerfile`` file in the ``myplugin/build/myimage`` subfolder of the plugin templates directory.

``remote-image``
++++++++++++++++

This hook allows pulling/pushing images from/to a docker registry.

Example::
  
    hooks = {
        "remote-image": {"myimage": "myimage:latest"},
    }

With this hook, users will be able to pull and push the ``myimage:latest`` docker image by running::
      
    tutor images pull myimage
    tutor images push myimage

or::
  
    tutor images pull all
    tutor images push all

.. _plugin_templates:

templates
~~~~~~~~~

In order to define plugin-specific hooks, a plugin should also have a template directory that includes the plugin hooks. The ``templates`` attribute should point to that directory.

Example::
  
    import os
    templates = os.path.join(os.path.abspath(os.path.dirname(__file__)), "templates")

With the above declaration, you can store plugin-specific templates in the ``templates/myplugin`` folder next to the ``plugin.py`` file.

.. _plugin_command:

command
~~~~~~~

A plugin can provide custom command line commands. Commands are assumed to be `click.Command <https://click.palletsprojects.com/en/7.x/api/#commands>`__ objects.

Example::
    
    import click
    
    @click.command(help="I'm a plugin command")
    def command():
        click.echo("Hello from myplugin!")

Any user who installs the ``myplugin`` plugin can then run::
    
    $ tutor myplugin
    Hello from myplugin!

You can even define subcommands by creating `command groups <https://click.palletsprojects.com/en/7.x/api/#click.Group>`__::
    
    import click
    
    @click.group(help="I'm a plugin command group")
    def command():
        pass
    
    @click.command(help="I'm a plugin subcommand")
    def dosomething():
        click.echo("This subcommand is awesome")

This would allow any user to run::

    $ tutor myplugin dosomething
    This subcommand is awesome
    
See the official `click documentation <https://click.palletsprojects.com/en/7.x/>`__ for more information.


Creating a new plugin
---------------------

Plugins can be created in two different ways: either as plain YAML files or installable Python packages. YAML files are great when you need to make minor changes to the default platform, such as modifying settings. For creating more complex applications, it is recommended to create python packages.

YAML file
~~~~~~~~~

YAML files that are stored in the tutor plugins root folder will be automatically considered as plugins. The location of the plugin root can be found by running::
    
    tutor plugins printroot

On Linux, this points to ``~/.local/share/tutor-plugins``. The location of the plugin root folder can be modified by setting the ``TUTOR_PLUGINS_ROOT`` environment variable.

YAML plugins need to define two extra keys: "name" and "version". Custom CLI commands are not supported by YAML plugins.

Let's create a simple plugin that adds your own `Google Analytics <https://analytics.google.com/>`__ tracking code to your Open edX platform. We need to add the ``GOOGLE_ANALYTICS_ACCOUNT`` and ``GOOGLE_ANALYTICS_TRACKING_ID`` settings to both the LMS and the CMS settings. To do so, we will only have to create the ``openedx-common-settings`` patch, which is shared by the development and the production settings both for the LMS and the CMS. First, create the plugin directory::
    
    mkdir "$(tutor plugins printroot)"

Then add the following content to the plugin file located at ``$(tutor plugins printroot)/myplugin.yml``::

    name: myplugin
    version: 0.1.0
    patches:
      openedx-common-settings: |
        # myplugin special settings
        GOOGLE_ANALYTICS_ACCOUNT = "UA-654321-1"
        GOOGLE_ANALYTICS_TRACKING_ID = "UA-654321-1"

Of course, you should replace your Google Analytics tracking code with your own. You can verify that your plugin is correctly installed, but not enabled yet::
    
    $ tutor plugins list
    myplugin@0.1.0 (disabled)
    
You can then enable your newly-created plugin::
    
    tutor plugins enable myplugin

Update your environment to apply changes from your plugin::
    
    tutor config save

You should be able to view your changes in every LMS and CMS settings file::

    grep -r myplugin "$(tutor config printroot)/env/apps/openedx/settings/"

Now just restart your platform to start sending tracking events to Google Analytics::
    
    tutor local quickstart

That's it! And it's very easy to share your plugins. Just upload them to your Github repo and share the url with other users. They will be able to install your plugin by running::
    
    tutor plugins install https://raw.githubusercontent.com/username/yourrepo/master/myplugin.yml

Python package
~~~~~~~~~~~~~~

Creating a plugin as a Python package allows you to define more complex logic and to store your patches in a more structured way. Python Tutor plugins are regular Python packages that define a specific entrypoint: ``tutor.plugin.v0``.

Example::
  
    from setuptools import setup
    setup(
        ...
        entry_points={"tutor.plugin.v0": ["myplugin = myplugin.plugin"]},
    )

The ``myplugin.plugin`` python module should then declare the ``config``, ``hooks``, etc. attributes that will define its behaviour.

To get started on the right foot, it is strongly recommended to create your first plugin with the `tutor plugin cookiecutter <https://github.com/overhangio/cookiecutter-tutor-plugin>`__::

    pip install cookiecutter
    cookiecutter https://github.com/overhangio/cookiecutter-tutor-plugin.git
    pip install -e ./tutor-myplugin
    tutor plugins list # your plugin should appear here
    tutor plugins enable myplugin # hack at it!

.. _existing_plugins:

Existing plugins
----------------

- `Course discovery <https://pypi.org/project/tutor-discovery>`__: Deploy an API for interacting with your course catalog
- `Ecommerce <https://pypi.org/project/tutor-ecommerce>`__: Sell courses and products on your Open edX platform
- `Figures <https://pypi.org/project/tutor-figures>`__: Visualize daily stats about course engagement
- `MinIO <https://pypi.org/project/tutor-minio>`__: S3 emulator for object storage and scalable Open edX deployment.
- `Notes <https://pypi.org/project/tutor-notes>`__:  Allows students to annotate portions of the courseware.
- `Xqueue <https://pypi.org/project/tutor-xqueue>`__: for external grading
