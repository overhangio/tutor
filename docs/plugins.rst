.. _plugins:

Plugins
=======

Since v3.4.0, Tutor comes with a plugin system that allows anyone to customise the deployment of an Open edX platform very easily. The vision behind this plugin system is that users should not have to fork the Tutor repository to customise their deployments. For instance, if you have created a new application that integrates with Open edX, you should not have to describe how to manually patch the platform settings, ``urls.py`` or ``*.env.json`` files. Instead, you can create a "tutor-myapp" plugin for Tutor. Then, users will start using your application in three simple steps::

    # 1) Install the plugin
    pip install tutor-myapp
    # 2) Enable the plugin
    tutor plugins enable myapp
    # 3) Restart the platform
    tutor local quickstart

Commands
--------

List installed plugins::
  
    tutor plugins list
    
Enable/disable a plugin::
  
    tutor plugins enable myplugin
    tutor plugins disable myplugin
    
After enabling or disabling a plugin, the environment should be re-generated with::
  
    tutor config save

API (v0)
--------

Note: The API for developing Tutor plugins is still considered unstable: profound changes should be expected for some time.

There are two mechanisms by which a plugin can integrate with Tutor: patches and hooks. Patches affect the rendered environment templates, while hooks are actions that are run during the lifetime of an Open edX platform. A plugin indicates which templates it patches, and which hooks it needs to run.

Entrypoint
~~~~~~~~~~

A plugin is a regular python package with a specific entrypoint: ``tutor.plugin.v0``.

Example::
  
    from setuptools import setup
    setup(
        ...
        entry_points={"tutor.plugin.v0": ["myplugin = myplugin.plugin"]},
    )

The ``myplugin.plugin`` python module should then declare a few attributes that will define its behaviour.

``config``
~~~~~~~~~~

The ``config`` attribute is used to modify existing and add new configuration parameters:

* ``config["set"]`` are key/values that should be modified.
* ``config["defaults"]`` are default key/values for this plugin. Key names will automatically be prefixed with the plugin name (as declared in the entrypoint), in upper case.

Example::
  
    config = {
        "set": {
            "DOCKER_IMAGE_OPENEDX": "openedx:mytag",
        },
        "defaults": {
            "PARAM": "somevalue",
        },
    }

This will override the ``DOCKER_IMAGE_OPENEDX`` configuration parameter and will add a new parameter ``MYPLUGIN_PARAM`` that will be equal to "somevalue".

``patches``
~~~~~~~~~~~

The Tutor templates include calls to ``{{ patch("patchname") }}`` in many different places. Plugins can add content in these places by adding values to the ``patches`` attribute.

The ``patches`` attribute can be a callable function instead of a static attribute.

Example::
  
    patches = {
        "local-docker-compose-services": """redis:
    image: redis:latest"""
    }

This will add a Redis instance to the services run with ``tutor local`` commands.

``hooks``
~~~~~~~~~

Hooks are services that are run during the lifetime of the platform. Currently, there is just one ``init`` hook. You should add there the services that will be run during initialisation, for instance for database creation and migrations.

Example::
  
    hooks = {"init": ["myservice1", "myservice2"]}
    
During initialisation, "myservice1" and "myservice2" will be run in sequence with the commands defined in the templates ``myplugin/hooks/myservice1/init`` and ``myplugin/hooks/myservice2/init``.

``templates``
~~~~~~~~~~~~~

In order to define plugin-specific hooks, a plugin should also have a template directory that includes the plugin hooks. The ``templates`` attribute should point to that directory.

Example::
  
    import os
    templates = templates = os.path.join(os.path.abspath(os.path.dirname(__file__)), "templates")

With the above declaration, you can store plugin-specific templates in the ``templates/myplugin`` folder next to the ``plugin.py`` file.
    

Existing plugins
----------------

There exists just one Tutor plugin, for now. In the future, Xqueue and Student Notes will be moved outside of the main configuration and will have their own plugin.

MinIO
~~~~~

::
  
    tutor plugins enable minio

See the `plugin documentation <https://github.com/overhangio/tutor/tree/master/plugins/minio>`_.