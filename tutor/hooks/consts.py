"""
List of all the action, filter and context names used across Tutor. This module is used
to generate part of the reference documentation.
"""
from __future__ import annotations

# The Tutor plugin system is licensed under the terms of the Apache 2.0 license.
__license__ = "Apache 2.0"

from typing import Any, Callable

import click

from tutor.types import Config

from . import actions, contexts, filters
from .actions import Action, ActionTemplate
from .filters import Filter, FilterTemplate

__all__ = ["Actions", "Filters", "Contexts"]


class Actions:
    """
    This class is a container for the names of all actions used across Tutor
    (see :py:mod:`tutor.hooks.actions.do`). For each action, we describe the
    arguments that are passed to the callback functions.

    To create a new callback for an existing action, write the following::

        from tutor import hooks

        @hooks.Actions.YOUR_ACTION.add()
        def your_action():
            # Do stuff here
    """

    #: Triggered whenever a "docker-compose start", "up" or "restart" command is executed.
    #:
    #: :parameter: str root: project root.
    #: :parameter: dict config: project configuration.
    #: :parameter: str name: docker-compose project name.
    COMPOSE_PROJECT_STARTED: Action[[str, Config, str]] = actions.get(
        "compose:project:started"
    )

    #: Called whenever the core project is ready to run. This action is called as soon
    #: as possible. This is the right time to discover plugins, for instance. In
    #: particular, we auto-discover the following plugins:
    #:
    #: - Python packages that declare a "tutor.plugin.v0" entrypoint.
    #: - Python packages that declare a "tutor.plugin.v1" entrypoint.
    #: - YAML and Python plugins stored in ~/.local/share/tutor-plugins (as indicated by ``tutor plugins printroot``)
    #: - When running the binary version of Tutor, official plugins that ship with the binary are automatically discovered.
    #:
    #: Discovering a plugin is typically done by the Tutor plugin mechanism. Thus, plugin
    #: developers probably don't have to implement this action themselves.
    #:
    #: This action does not have any parameter.
    CORE_READY: Action[[]] = actions.get("core:ready")

    #: Called as soon as we have access to the Tutor project root.
    #:
    #: :parameter str root: absolute path to the project root.
    PROJECT_ROOT_READY: Action[str] = actions.get("project:root:ready")

    #: Triggered when a single plugin needs to be loaded. Only plugins that have previously been
    #: discovered can be loaded (see :py:data:`CORE_READY`).
    #:
    #: Plugins are typically loaded because they were enabled by the user; the list of
    #: plugins to enable is found in the project root (see
    #: :py:data:``PROJECT_ROOT_READY``).
    #:
    #: Most plugin developers will not have to implement this action themselves, unless
    #: they want to perform a specific action at the moment the plugin is enabled.
    #:
    #: This action does not have any parameter.
    PLUGIN_LOADED: ActionTemplate[[]] = actions.get_template("plugins:loaded:{0}")

    #: Triggered after all plugins have been loaded. At this point the list of loaded
    #: plugins may be obtained from the :py:data:``Filters.PLUGINS_LOADED`` filter.
    #:
    #: This action does not have any parameter.
    PLUGINS_LOADED: Action[[]] = actions.get("plugins:loaded")

    #: Triggered when a single plugin is unloaded. Only plugins that have previously been
    #: loaded can be unloaded (see :py:data:`PLUGIN_LOADED`).
    #:
    #: Plugins are typically unloaded because they were disabled by the user.
    #:
    #: Most plugin developers will not have to implement this action themselves, unless
    #: they want to perform a specific action at the moment the plugin is disabled.
    #:
    #: :parameter str plugin: plugin name.
    #: :parameter str root: absolute path to the project root.
    #: :parameter config: full project configuration
    PLUGIN_UNLOADED: Action[str, str, Config] = actions.get("plugins:unloaded")


class Filters:
    """
    Here are the names of all filters used across Tutor. For each filter, the
    type of the first argument also indicates the type of the expected returned value.

    Filter names are all namespaced with domains separated by colons (":").

    To add custom data to any filter, write the following in your plugin::

        from tutor import hooks

        @hooks.Filters.YOUR_FILTER.add()
        def your_filter(items):
            # do stuff with items
            ...
            # return the modified list of items
            return items
    """

    #: List of commands to be executed during initialization. These commands typically
    #: include database migrations, setting feature flags, etc.
    #:
    #: :parameter list[tuple[str, tuple[str, ...]]] tasks: list of ``(service, path)`` tasks.
    #:
    #:     - ``service`` is the name of the container in which the task will be executed.
    #:     - ``path`` is a tuple that corresponds to a template relative path.
    #:       Example: ``("myplugin", "hooks", "myservice", "pre-init")`` (see:py:data:`IMAGES_BUILD`).
    #:       The command to execute will be read from that template, after it is rendered.
    COMMANDS_INIT: Filter[list[tuple[str, tuple[str, ...]]], str] = filters.get(
        "commands:init"
    )

    #: List of commands to be executed prior to initialization. These commands are run even
    #: before the mysql databases are created and the migrations are applied.
    #:
    #: :parameter list[tuple[str, tuple[str, ...]]] tasks: list of ``(service, path)`` tasks. (see :py:data:`COMMANDS_INIT`).
    COMMANDS_PRE_INIT: Filter[list[tuple[str, tuple[str, ...]]], []] = filters.get(
        "commands:pre-init"
    )

    #: Same as :py:data:`COMPOSE_LOCAL_TMP` but for the development environment.
    COMPOSE_DEV_TMP: Filter[Config, []] = filters.get("compose:dev:tmp")

    #: Same as :py:data:`COMPOSE_LOCAL_JOBS_TMP` but for the development environment.
    COMPOSE_DEV_JOBS_TMP: Filter[Config, []] = filters.get("compose:dev-jobs:tmp")

    #: List of folders to bind-mount in docker-compose containers, either in ``tutor local`` or ``tutor dev``.
    #:
    #: Many ``tutor local`` and ``tutor dev`` commands support ``--mounts`` options
    #: that allow plugins to define custom behaviour at runtime. For instance
    #: ``--mount=/path/to/edx-platform`` would cause this host folder to be
    #: bind-mounted in different containers (lms, lms-worker, cms, cms-worker) at the
    #: /openedx/edx-platform location. Plugin developers may implement this filter to
    #: define custom behaviour when mounting folders that relate to their plugins. For
    #: instance, the ecommerce plugin may process the ``--mount=/path/to/ecommerce``
    #: option.
    #:
    #: :parameter list[tuple[str, str]] mounts: each item is a ``(service, path)``
    #:   tuple, where ``service`` is the name of the docker-compose service and ``path`` is
    #:   the location in the container where the folder should be bind-mounted. Note: the
    #:   path must be slash-separated ("/"). Thus, do not use ``os.path.join`` to generate
    #:   the ``path`` because it will fail on Windows.
    #: :parameter str name: basename of the host-mounted folder. In the example above,
    #:   this is "edx-platform". When implementing this filter you should check this name to
    #:   conditionnally add mounts.
    COMPOSE_MOUNTS: Filter[list[tuple[str, str]], [str]] = filters.get("compose:mounts")

    #: Contents of the (local|dev)/docker-compose.tmp.yml files that will be generated at
    #: runtime. This is used for instance to bind-mount folders from the host (see
    #: :py:data:`COMPOSE_MOUNTS`)
    #:
    #: :parameter dict[str, ...] docker_compose_tmp: values which will be serialized to local/docker-compose.tmp.yml.
    #:   Keys and values will be rendered before saving, such that you may include ``{{ ... }}`` statements.
    COMPOSE_LOCAL_TMP: Filter[Config, []] = filters.get("compose:local:tmp")

    #: Same as :py:data:`COMPOSE_LOCAL_TMP` but for jobs
    COMPOSE_LOCAL_JOBS_TMP: Filter[Config, []] = filters.get("compose:local-jobs:tmp")

    #: List of images to be built when we run ``tutor images build ...``.
    #:
    #: :parameter list[tuple[str, tuple[str, ...], str, tuple[str, ...]]] tasks: list of ``(name, path, tag, args)`` tuples.
    #:
    #:    - ``name`` is the name of the image, as in ``tutor images build myimage``.
    #:    - ``path`` is the relative path to the folder that contains the Dockerfile.
    #:      For instance ``("myplugin", "build", "myservice")`` indicates that the template will be read from
    #:      ``myplugin/build/myservice/Dockerfile``
    #:    - ``tag`` is the Docker tag that will be applied to the image. It will be
    #:      rendered at runtime with the user configuration. Thus, the image tag could
    #:      be ``"{{ DOCKER_REGISTRY }}/myimage:{{ TUTOR_VERSION }}"``.
    #:    - ``args`` is a list of arguments that will be passed to ``docker build ...``.
    #: :parameter Config config: user configuration.
    IMAGES_BUILD: Filter[
        list[tuple[str, tuple[str, ...], str, tuple[str, ...]]], [Config]
    ] = filters.get("images:build")

    #: List of images to be pulled when we run ``tutor images pull ...``.
    #:
    #: :parameter list[tuple[str, str]] tasks: list of ``(name, tag)`` tuples.
    #:
    #:    - ``name`` is the name of the image, as in ``tutor images pull myimage``.
    #:    - ``tag`` is the Docker tag that will be applied to the image. (see :py:data:`IMAGES_BUILD`).
    #: :parameter Config config: user configuration.
    IMAGES_PULL: Filter[list[tuple[str, str]], [Config]] = filters.get("images:pull")

    #: List of images to be pushed when we run ``tutor images push ...``.
    #: Parameters are the same as for :py:data:`IMAGES_PULL`.
    IMAGES_PUSH: Filter[list[tuple[str, str]], [Config]] = filters.get("images:push")

    #: List of command line interface (CLI) commands.
    #:
    #: :parameter list commands: commands are instances of ``click.Command``. They will
    #:   all be added as subcommands of the main ``tutor`` command.
    CLI_COMMANDS: Filter[list[click.Command], []] = filters.get("cli:commands")

    #: Declare new default configuration settings that don't necessarily have to be saved in the user
    #: ``config.yml`` file. Default settings may be overridden with ``tutor config save --set=...``, in which
    #: case they will automatically be added to ``config.yml``.
    #:
    #: :parameter list[tuple[str, ...]] items: list of (name, value) new settings. All
    #:    new entries must be prefixed with the plugin name in all-caps.
    CONFIG_DEFAULTS: Filter[list[tuple[str, Any]], []] = filters.get("config:defaults")

    #: Modify existing settings, either from Tutor core or from other plugins. Beware not to override any
    #: important setting, such as passwords! Overridden setting values will be printed to stdout when the plugin
    #: is disabled, such that users have a chance to back them up.
    #:
    #: :parameter list[tuple[str, ...]] items: list of (name, value) settings.
    CONFIG_OVERRIDES: Filter[list[tuple[str, Any]], []] = filters.get(
        "config:overrides"
    )

    #: Declare uniqaue configuration settings that must be saved in the user ``config.yml`` file. This is where
    #: you should declare passwords and randomly-generated values that are different from one environment to the next.
    #:
    #: :parameter list[tuple[str, ...]] items: list of (name, value) new settings. All
    #:   names must be prefixed with the plugin name in all-caps.
    CONFIG_UNIQUE: Filter[list[tuple[str, Any]], []] = filters.get("config:unique")

    #: List of patches that should be inserted in a given location of the templates. The
    #: filter name must be formatted with the patch name.
    #: This filter is not so convenient and plugin developers will probably
    #: prefer :py:data:`ENV_PATCHES`.
    #:
    #: :parameter list[str] patches: each item is the unrendered patch content.
    ENV_PATCH: FilterTemplate[list[str], []] = filters.get_template("env:patches:{0}")

    #: List of patches that should be inserted in a given location of the templates. This is very similar to :py:data:`ENV_PATCH`, except that the patch is added as a ``(name, content)`` tuple.
    #:
    #: :parameter list[tuple[str, str]] patches: pairs of (name, content) tuples. Use this
    #:   filter to modify the Tutor templates.
    ENV_PATCHES: Filter[list[tuple[str, str]], []] = filters.get("env:patches")

    #: List of template path patterns to be ignored when rendering templates to the project root. By default, we ignore:
    #:
    #: - hidden files (``.*``)
    #: - ``__pycache__`` directories and ``*.pyc`` files
    #: - "partials" directories.
    #:
    #: Ignored patterns are overridden by include patterns; see :py:data:`ENV_PATTERNS_INCLUDE`.
    #:
    #: :parameter list[str] patterns: list of regular expression patterns. E.g: ``r"(.*/)?ignored_file_name(/.*)?"``.
    ENV_PATTERNS_IGNORE: Filter[list[str], []] = filters.get("env:patterns:ignore")

    #: List of template path patterns to be included when rendering templates to the project root.
    #: Patterns from this list will take priority over the patterns from :py:data:`ENV_PATTERNS_IGNORE`.
    #:
    #: :parameter list[str] patterns: list of regular expression patterns. See :py:data:`ENV_PATTERNS_IGNORE`.
    ENV_PATTERNS_INCLUDE: Filter[list[str], []] = filters.get("env:patterns:include")

    #: List of all template root folders.
    #:
    #: :parameter list[str] templates_root: absolute paths to folders which contain templates.
    #:   The templates in these folders will then be accessible by the environment
    #:   renderer using paths that are relative to their template root.
    ENV_TEMPLATE_ROOTS: Filter[list[str], []] = filters.get("env:templates:roots")

    #: List of template source/destination targets.
    #:
    #: :parameter list[tuple[str, str]] targets: list of (source, destination) pairs.
    #:   Each source is a path relative to one of the template roots, and each destination
    #:   is a path relative to the environment root. For instance: adding ``("c/d",
    #:   "a/b")`` to the filter will cause all files from "c/d" to be rendered to the ``a/b/c/d``
    #:   subfolder.
    ENV_TEMPLATE_TARGETS: Filter[list[tuple[str, str]], []] = filters.get(
        "env:templates:targets"
    )

    #: List of `Jinja2 filters <https://jinja.palletsprojects.com/en/latest/templates/#filters>`__ that will be
    #: available in templates. Jinja2 filters are basically functions that can be used
    #: as follows within templates::
    #:
    #:    {{ "somevalue"|my_filter }}
    #:
    #: Note that Jinja2 filters are a completely different thing than the Tutor hook
    #: filters, although they share the same name.
    #:
    #: Out of the box, Tutor comes with the following filters:
    #:
    #: - ``common_domain``: Return the longest common name between two domain names. Example: ``{{ "studio.demo.myopenedx.com"|common_domain("lms.demo.myopenedx.com") }}`` is equal to "demo.myopenedx.com".
    #: - ``encrypt``: Encrypt an arbitrary string. The encryption process is compatible with `htpasswd <https://httpd.apache.org/docs/2.4/programs/htpasswd.html>`__ verification.
    #: - ``list_if``: In a list of ``(value, condition)`` tuples, return the list of ``value`` for which the ``condition`` is true.
    #: - ``long_to_base64``: Base-64 encode a long integer.
    #: - ``iter_values_named``: Yield the values of the configuration settings that match a certain pattern. Example: ``{% for value in iter_values_named(prefix="KEY", suffix="SUFFIX")%}...{% endfor %}``. By default, only non-empty values are yielded. To iterate also on empty values, pass the ``allow_empty=True`` argument.
    #: - ``patch``: See :ref:`patches <v0_plugin_patches>`.
    #: - ``random_string``: Return a random string of the given length composed of ASCII letters and digits. Example: ``{{ 8|random_string }}``.
    #: - ``reverse_host``: Reverse a domain name (see `reference <https://en.wikipedia.org/wiki/Reverse_domain_name_notation>`__). Example: ``{{ "demo.myopenedx.com"|reverse_host }}`` is equal to "com.myopenedx.demo".
    #: - ``rsa_import_key``: Import a PEM-formatted RSA key and return the corresponding object.
    #: - ``rsa_private_key``: Export an RSA private key in PEM format.
    #: - ``walk_templates``: Iterate recursively over the templates of the given folder. For instance::
    #:
    #:     {% for file in "apps/myplugin"|walk_templates %}
    #:     ...
    #:     {% endfor %}
    #:
    #: :parameter filters: list of (name, function) tuples. The function signature
    #:   should correspond to its usage in templates.
    ENV_TEMPLATE_FILTERS: Filter[
        list[tuple[str, Callable[..., Any]]], []
    ] = filters.get("env:templates:filters")

    #: List of extra variables to be included in all templates.
    #:
    #: :parameter filters: list of (name, value) tuples.
    ENV_TEMPLATE_VARIABLES: Filter[list[tuple[str, Any]], []] = filters.get(
        "env:templates:variables"
    )

    #: List of installed plugins. In order to be added to this list, a plugin must first
    #: be discovered (see :py:data:`Actions.CORE_READY`).
    #:
    #: :param list[str] plugins: plugin developers probably don't have to implement this
    #:   filter themselves, but they can apply it to check for the presence of other
    #:   plugins.
    PLUGINS_INSTALLED: Filter[list[str], []] = filters.get("plugins:installed")

    #: Information about each installed plugin, including its version.
    #: Keep this information to a single line for easier parsing by 3rd-party scripts.
    #:
    #: :param list[tuple[str, str]] versions: each pair is a ``(plugin, info)`` tuple.
    PLUGINS_INFO: Filter[list[tuple[str, str]], []] = filters.get(
        "plugins:installed:versions"
    )

    #: List of loaded plugins.
    #:
    #: :param list[str] plugins: plugin developers probably don't have to modify this
    #:   filter themselves, but they can apply it to check whether other plugins are enabled.
    PLUGINS_LOADED: Filter[list[str], []] = filters.get("plugins:loaded")


class Contexts:
    """
    Contexts are used to track in which parts of the code filters and actions have been
    declared. Let's look at an example::

        from tutor import hooks

        with hooks.contexts.enter("c1"):
            @filters.add("f1") def add_stuff_to_filter(...):
                ...

    The fact that our custom filter was added in a certain context allows us to later
    remove it. To do so, we write::

        from tutor import hooks
        filters.clear("f1", context="c1")

    This makes it easy to disable side-effects by plugins, provided they were created with appropriate contexts.

    Here we list all the contexts that are used across Tutor. It is not expected that
    plugin developers will ever need to use contexts. But if you do, this is how it
    should be done::

        from tutor import hooks

        with hooks.Contexts.MY_CONTEXT.enter():
            # do stuff and all created hooks will include MY_CONTEXT

        # Apply only the hook callbacks that were created within MY_CONTEXT
        hooks.Actions.MY_ACTION.do_from_context(str(hooks.Contexts.MY_CONTEXT))
        hooks.Filters.MY_FILTER.apply_from_context(hooks.Contexts.MY_CONTEXT.name)
    """

    #: We enter this context whenever we create hooks for a specific application or :
    #: plugin. For instance, plugin "myplugin" will be enabled within the "app:myplugin"
    #: context.
    APP = contexts.ContextTemplate("app:{0}")

    #: Plugins will be installed and enabled within this context.
    PLUGINS = contexts.Context("plugins")

    #: YAML-formatted v0 plugins will be installed within this context.
    PLUGINS_V0_YAML = contexts.Context("plugins:v0:yaml")

    #: Python entrypoint plugins will be installed within this context.
    PLUGINS_V0_ENTRYPOINT = contexts.Context("plugins:v0:entrypoint")
