Plugin API
==========

Plugins can affect the behaviour of Tutor at multiple levels. First, plugins can define new services with their Docker images, settings and the right initialisation commands. To do so you will have to define custom :ref:`config <plugin_config>`, :ref:`patches <plugin_patches>`, :ref:`hooks <plugin_hooks>` and :ref:`templates <plugin_templates>`. Then, plugins can also extend the CLI by defining their own :ref:`commands <plugin_command>`.

.. _plugin_config:

config
~~~~~~

The ``config`` attribute is used to modify existing and add new configuration parameters:

* ``config["add"]`` are key/values that should be added to the user-specific ``config.yml`` configuration. Add there passwords, secret keys and other values that do not have a default value.
* ``config["defaults"]`` are default key/values for this plugin. These values can be accessed even though they are not added to the ``config.yml`` user file. Users can override them manually with ``tutor config save --set ...``.
* ``config["set"]`` are existing key/values that should be modified. Be very careful what you add there! Different plugins may define conflicting values for some parameters.

 "add" and "defaults" key names will be automatically prefixed with the plugin name, in upper case.

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

To initialise a "foo" service, Tutor runs the "foo-job" service that is found in the ``env/local/docker-compose.jobs.yml`` file. By default, Tutor comes with a few services in this file: mysql-job, lms-job, cms-job. If your plugin requires running custom services during initialisation, you will need to add them to the ``docker-compose.jobs.yml`` template. To do so, just use the "local-docker-compose-jobs-services" patch.

In Kubernetes, the approach is the same, except that jobs are implemented as actual job objects in the ``k8s/jobs.yml`` template. To add your own services there, your plugin should implement the "k8s-jobs" patch.

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

In Tutor, templates are `Jinja2 <https://jinja.palletsprojects.com/en/2.11.x/>`__-formatted files that will be rendered in the Tutor environment (the ``$(tutor config printroot)/env`` folder) when running ``tutor config save``. The environment files are overwritten every time the environment is saved. Plugin developers can create templates that make use of the built-in `Jinja2 API <https://jinja.palletsprojects.com/en/2.11.x/api/>`__. In addition, a couple additional filters are added by Tutor:

* ``common_domain``: Return the longest common name between two domain names. Example: ``{{ "studio.demo.myopenedx.com"|common_domain("lms.demo.myopenedx.com") }}`` is equal to "demo.myopenedx.com".
* ``encrypt``: Encrypt an arbitrary string. The encryption process is compatible with `htpasswd <https://httpd.apache.org/docs/2.4/programs/htpasswd.html>`__ verification.
* ``list_if``: In a list of ``(value, condition)`` tuples, return the list of ``value`` for which the ``condition`` is true.
* ``long_to_base64``: Base-64 encode a long integer.
* ``iter_values_named``: Yield the values of the configuration settings that match a certain pattern. Example: ``{% for value in iter_values_named(prefix="KEY", suffix="SUFFIX")%}...{% endfor %}``. By default, only non-empty values are yielded. To iterate also on empty values, pass the ``allow_empty=True`` argument.
* ``patch``: See :ref:`patches <plugin_patches>`.
* ``random_string``: Return a random string of the given length composed of ASCII letters and digits. Example: ``{{ 8|random_string }}``.
* ``reverse_host``: Reverse a domain name (see `reference <https://en.wikipedia.org/wiki/Reverse_domain_name_notation>`__). Example: ``{{ "demo.myopenedx.com"|reverse_host }}`` is equal to "com.myopenedx.demo".
* ``rsa_import_key``: Import a PEM-formatted RSA key and return the corresponding object.
* ``rsa_private_key``: Export an RSA private key in PEM format.
* ``walk_templates``: Iterate recursively over the templates of the given folder. For instance::

    {% for file in "apps/myplugin"|walk_templates %}
    ...
    {% endfor %}

When saving the environment, template files that are stored in a template root will be rendered to the environment folder. The following files are excluded:

* Binary files with the following extensions: .ico, .jpg, .png, .ttf
* Files that are stored in a folder named "partials", or one of its subfolders.

.. _plugin_command:

command
~~~~~~~

A plugin can provide custom command line commands. Commands are assumed to be `click.Command <https://click.palletsprojects.com/en/8.0.x/api/#commands>`__ objects, and you typically implement them using the `click.command <https://click.palletsprojects.com/en/8.0.x/api/#click.command>`__ decorator.

You may also use the `click.pass_obj <https://click.palletsprojects.com/en/8.0.x/api/#click.pass_obj>`__ decorator to pass the CLI `context <https://click.palletsprojects.com/en/8.0.x/api/#click.Context>`__, such as when you want to access Tutor configuration settings from your command.

Example::

    import click
    from tutor import config as tutor_config

    @click.command(help="I'm a plugin command")
    @click.pass_obj
    def command(context):
        config = tutor_config.load(context.root)
        lms_host = config["LMS_HOST"]
        click.echo("Hello from myplugin!")
        click.echo(f"My LMS host is {lms_host}")

Any user who installs the ``myplugin`` plugin can then run::

    $ tutor myplugin
    Hello from myplugin!
    My LMS host is demo.openedx.overhang.io

You can even define subcommands by creating `command groups <https://click.palletsprojects.com/en/8.0.x/api/#click.Group>`__::

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

See the official `click documentation <https://click.palletsprojects.com/en/8.0.x/>`__ for more information.
