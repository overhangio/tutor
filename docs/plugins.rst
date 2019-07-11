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

There are two mechanisms by which a plugin can integrate with Tutor: patches and hooks. Patches affect the rendered environment templates, while hooks are actions that are run during the lifetime of an Open edX platform. A plugin indicates which templates it patches, and which hooks it needs to run. A plugin can also affect the project configuration by adding new values and modifying existing values.

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

Hooks are actions that are run during the lifetime of the platform. Each hook has a different specification.

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

``templates``
~~~~~~~~~~~~~

In order to define plugin-specific hooks, a plugin should also have a template directory that includes the plugin hooks. The ``templates`` attribute should point to that directory.

Example::
  
    import os
    templates = templates = os.path.join(os.path.abspath(os.path.dirname(__file__)), "templates")

With the above declaration, you can store plugin-specific templates in the ``templates/myplugin`` folder next to the ``plugin.py`` file.
    

Existing plugins
----------------

- `Course discovery <https://pypi.org/project/tutor-discovery>`__: Deploy an API for interacting with your course catalog
- `Ecommerce <https://pypi.org/project/tutor-minio>`__: Sell courses and products on your Open edX platform
- `Figures <https://pypi.org/project/tutor-figures>`__: Visualize daily stats about course engagement
- `MinIO <https://github.com/overhangio/tutor/tree/master/plugins/minio>`__: S3 emulator for object storage and scalable Open edX deployment.
- `Xqueue <https://github.com/overhangio/tutor/tree/master/plugins/xqueue>`__: for external grading
