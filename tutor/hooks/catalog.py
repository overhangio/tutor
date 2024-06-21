"""
List of all the action, filter and context names used across Tutor. This module is used
to generate part of the reference documentation.
"""

from __future__ import annotations

# The Tutor plugin system is licensed under the terms of the Apache 2.0 license.
__license__ = "Apache 2.0"

from typing import Any, Callable, Iterable, Literal, Union

import click

from tutor.core.hooks import Action, Context, Filter
from tutor.types import Config

__all__ = ["Actions", "Filters", "Contexts"]


class Actions:
    """
    This class is a container for all actions used across Tutor (see
    :py:class:`tutor.core.hooks.Action`). Actions are used to trigger callback functions at
    specific moments in the Tutor life cycle.

    To create a new callback for an existing action, start by importing the hooks
    module::

        from tutor import hooks

    Then create your callback function and decorate it with the :py:meth:`add <tutor.core.hooks.Action.add>` method of the
    action you're interested in::

        @hooks.Actions.SOME_ACTION.add()
        def your_action():
            # Do stuff here

    Your callback function should have the same signature as the original action. For
    instance, to add a callback to the :py:data:`COMPOSE_PROJECT_STARTED` action::

        @hooks.Actions.COMPOSE_PROJECT_STARTED.add():
        def run_this_on_start(root, config, name):
            print(root, config["LMS_HOST", name])

    Your callback function will then be called whenever the ``COMPOSE_PROJECT_STARTED.do`` method
    is called, i.e: when ``tutor local start`` or ``tutor dev start`` is run.

    Note that action callbacks do not return anything.

    For more information about how actions work, check out the :py:class:`tutor.core.hooks.Action` API.
    """

    #: Triggered whenever a "docker compose start", "up" or "restart" command is executed.
    #:
    #: :parameter str root: project root.
    #: :parameter dict config: project configuration.
    #: :parameter str name: docker-compose project name.
    COMPOSE_PROJECT_STARTED: Action[[str, Config, str]] = Action()

    #: Triggered after all interactive questions have been asked.
    #: You should use this action if you want to add new questions.
    #:
    #: :parameter dict config: project configuration.
    CONFIG_INTERACTIVE: Action[[Config]] = Action()

    #: This action is called at the end of the tutor.config.load_full function.
    #: Modifying this object will not trigger changes in the configuration.
    #: For all purposes, it should be considered read-only.
    #:
    #: :parameter dict config: project configuration.
    CONFIG_LOADED: Action[[Config]] = Action()

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
    CORE_READY: Action[[]] = Action()

    #: Called just before triggering the job tasks of any ``... do <job>`` command.
    #:
    #: :parameter str job: job name.
    #: :parameter args: job positional arguments.
    #: :parameter kwargs: job named arguments.
    DO_JOB: Action[[str, Any]] = Action()

    #: Triggered when a single plugin needs to be loaded. Only plugins that have previously been
    #: discovered can be loaded (see :py:data:`CORE_READY`).
    #:
    #: Plugins are typically loaded because they were enabled by the user; the list of
    #: plugins to enable is found in the project root (see
    #: :py:data:`PROJECT_ROOT_READY`).
    #:
    #: Most plugin developers will not have to implement this action themselves, unless
    #: they want to perform a specific action at the moment the plugin is enabled.
    #:
    #: :parameter str plugin: plugin name.
    PLUGIN_LOADED: Action[[str]] = Action()

    #: Triggered after all plugins have been loaded. At this point the list of loaded
    #: plugins may be obtained from the :py:data:`Filters.PLUGINS_LOADED` filter.
    #:
    #: This action does not have any parameter.
    PLUGINS_LOADED: Action[[]] = Action()

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
    PLUGIN_UNLOADED: Action[str, str, Config] = Action()

    #: Called as soon as we have access to the Tutor project root.
    #:
    #: :parameter str root: absolute path to the project root.
    PROJECT_ROOT_READY: Action[str] = Action()


class Filters:
    """
    Here are the names of all filters used across Tutor. (see
    :py:class:`tutor.core.hooks.Filter`) Filters are used to modify some data at
    specific points during the Tutor life cycle.

    To add a callback to an existing filter, start by importing the hooks module::

        from tutor import hooks

    Then create your callback function and decorate it with :py:meth:`add
    <tutor.core.hooks.Filter.add>` method of the filter instance you need::

        @hooks.Filters.SOME_FILTER.add()
        def your_filter_callback(some_data):
            # Do stuff here with the data
            ...
            # return the modified data
            return some_data

    Note that your filter callback should have the same signature as the original
    filter. The return value should also have the same type as the first argument of the
    callback function.

    Many filters have a list of items as the first argument. Quite often, plugin
    developers just want to add a new item at the end of that list. In such cases there
    is no need for a callback function. Instead, you can use the ``add_item`` method. For
    instance, you can add a "hello" to the init task of the lms container by modifying
    the :py:data:`CLI_DO_INIT_TASKS` filter::

        hooks.Filters.CLI_DO_INIT_TASKS.add_item(("lms", "echo hello"))

    To add multiple items at a time, use ``add_items``::

        hooks.Filters.CLI_DO_INIT_TASKS.add_items(
            ("lms", "echo 'hello from lms'"),
            ("cms", "echo 'hello from cms'"),
        )

    The ``echo`` commands will then be run every time the "init" tasks are run, for
    instance during ``tutor local launch``.

    For more information about how filters work, check out the
    :py:class:`tutor.core.hooks.Filter` API.
    """

    #: Hostnames of user-facing applications.
    #:
    #: So far this filter is only used to inform the user of application urls after they have run ``launch``.
    #:
    #: :parameter list[str] hostnames: items from this list are templates that will be
    #:   rendered by the environment.
    #: :parameter str context_name: either "local" or "dev", depending on the calling context.
    APP_PUBLIC_HOSTS: Filter[list[str], [Literal["local", "dev"]]] = Filter()

    #: List of command line interface (CLI) commands.
    #:
    #: :parameter list commands: commands are instances of ``click.Command``. They will
    #:   all be added as subcommands of the main ``tutor`` command.
    CLI_COMMANDS: Filter[list[click.Command], []] = Filter()

    #: List of ``do ...`` commands.
    #:
    #: :parameter list commands: see :py:data:`CLI_COMMANDS`. These commands will be
    #:   added as subcommands to the ``local/dev/k8s do`` commands. They must return a list of
    #:   ("service name", "service command") tuples. Each "service command" will be executed
    #:   in the "service" container, both in local, dev and k8s mode.
    CLI_DO_COMMANDS: Filter[list[Callable[[Any], Iterable[tuple[str, str]]]], []] = (
        Filter()
    )

    #: List of initialization tasks (scripts) to be run in the ``init`` job. This job
    #: includes all database migrations, setting up, etc. To run some tasks before or
    #: after others, they should be assigned a different priority.
    #:
    #: :parameter list[tuple[str, str]] tasks: list of ``(service, task)`` tuples. Each
    #:   task is essentially a bash script to be run in the "service" container. Scripts
    #:   may contain Jinja markup, similar to templates.
    CLI_DO_INIT_TASKS: Filter[list[tuple[str, str]], []] = Filter()

    #: List of folders to bind-mount in docker-compose containers, either in ``tutor local`` or ``tutor dev``.
    #:
    #: This filter is for processing values of the ``MOUNTS`` setting such as::
    #:
    #:     tutor mounts add /path/to/edx-platform
    #:
    #: In this example, this host folder would be bind-mounted in different containers
    #: (lms, lms-worker, cms, cms-worker, lms-job, cms-job) at the
    #: /openedx/edx-platform location. Plugin developers may implement this filter to
    #: define custom behaviour when mounting folders that relate to their plugins. For
    #: instance, the ecommerce plugin may process the ``/path/to/ecommerce`` value.
    #:
    #: To also bind-mount these folder at build time, implement also the
    #: :py:data:`IMAGES_BUILD_MOUNTS` filter.
    #:
    #: :parameter list[tuple[str, str]] mounts: each item is a ``(service, path)``
    #:   tuple, where ``service`` is the name of the docker-compose service and ``path`` is
    #:   the location in the container where the folder should be bind-mounted. Note: the
    #:   path must be slash-separated ("/"). Thus, do not use ``os.path.join`` to generate
    #:   the ``path`` because it will fail on Windows.
    #: :parameter str name: basename of the host-mounted folder. In the example above,
    #:   this is "edx-platform". When implementing this filter you should check this name to
    #:   conditionally add mounts.
    COMPOSE_MOUNTS: Filter[list[tuple[str, str]], [str]] = Filter()

    #: Declare new default configuration settings that don't necessarily have to be saved in the user
    #: ``config.yml`` file. Default settings may be overridden with ``tutor config save --set=...``, in which
    #: case they will automatically be added to ``config.yml``.
    #:
    #: :parameter list[tuple[str, ...]] items: list of (name, value) new settings. All
    #:    new entries must be prefixed with the plugin name in all-caps.
    CONFIG_DEFAULTS: Filter[list[tuple[str, Any]], []] = Filter()

    #: Modify existing settings, either from Tutor core or from other plugins. Beware not to override any
    #: important setting, such as passwords! Overridden setting values will be printed to stdout when the plugin
    #: is disabled, such that users have a chance to back them up.
    #:
    #: :parameter list[tuple[str, ...]] items: list of (name, value) settings.
    CONFIG_OVERRIDES: Filter[list[tuple[str, Any]], []] = Filter()

    #: Declare unique configuration settings that must be saved in the user ``config.yml`` file. This is where
    #: you should declare passwords and randomly-generated values that are different from one environment to the next.
    #:
    #: :parameter list[tuple[str, ...]] items: list of (name, value) new settings. All
    #:   names must be prefixed with the plugin name in all-caps.
    CONFIG_UNIQUE: Filter[list[tuple[str, Any]], []] = Filter()

    #: Used to declare unique key:value pairs in the ``config.yml`` file that will be overwritten on ``tutor config save``.
    #: This is where you should declare passwords and other secrets that need to be fetched live from an external secrets
    #: store. Most users will not need to use this filter but it will allow you to programmatically fetch and set secrets
    #: from an external secrets store such as AWS Secrets Manager via boto3.
    #:
    #: Values passed in to this filter will overwrite existing values in the ``config.yml`` file.
    #:
    #: :parameter list[tuple[str, ...]] items: list of (name, value) new settings. All
    #:   names must be prefixed with the plugin name in all-caps.
    CONFIG_USER: Filter[list[tuple[str, Any]], []] = Filter()

    #: Use this filter to modify the ``docker build`` command.
    #:
    #: :parameter list[str] command: the full build command, including options and
    #:   arguments. Note that these arguments do not include the leading ``docker`` command.
    DOCKER_BUILD_COMMAND: Filter[list[str], []] = Filter()

    #: List of patches that should be inserted in a given location of the templates.
    #:
    #: :parameter list[tuple[str, str]] patches: pairs of (name, content) tuples. Use this
    #:   filter to modify the Tutor templates.
    ENV_PATCHES: Filter[list[tuple[str, str]], []] = Filter()

    #: List of template path patterns to be ignored when rendering templates to the project root. By default, we ignore:
    #:
    #: - hidden files (``.*``)
    #: - ``__pycache__`` directories and ``*.pyc`` files
    #: - "partials" directories.
    #:
    #: Ignored patterns are overridden by include patterns; see :py:data:`ENV_PATTERNS_INCLUDE`.
    #:
    #: :parameter list[str] patterns: list of regular expression patterns. E.g: ``r"(.*/)?ignored_file_name(/.*)?"``.
    ENV_PATTERNS_IGNORE: Filter[list[str], []] = Filter()

    #: List of template path patterns to be included when rendering templates to the project root.
    #: Patterns from this list will take priority over the patterns from :py:data:`ENV_PATTERNS_IGNORE`.
    #:
    #: :parameter list[str] patterns: list of regular expression patterns. See :py:data:`ENV_PATTERNS_IGNORE`.
    ENV_PATTERNS_INCLUDE: Filter[list[str], []] = Filter()

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
    ENV_TEMPLATE_FILTERS: Filter[list[tuple[str, Callable[..., Any]]], []] = Filter()

    #: List of all template root folders.
    #:
    #: :parameter list[str] templates_root: absolute paths to folders which contain templates.
    #:   The templates in these folders will then be accessible by the environment
    #:   renderer using paths that are relative to their template root.
    ENV_TEMPLATE_ROOTS: Filter[list[str], []] = Filter()

    #: List of template source/destination targets.
    #:
    #: :parameter list[tuple[str, str]] targets: list of (source, destination) pairs.
    #:   Each source is a path relative to one of the template roots, and each destination
    #:   is a path relative to the environment root. For instance: adding ``("c/d",
    #:   "a/b")`` to the filter will cause all files from "c/d" to be rendered to the ``a/b/c/d``
    #:   subfolder.
    ENV_TEMPLATE_TARGETS: Filter[list[tuple[str, str]], []] = Filter()

    #: List of extra variables to be included in all templates.
    #:
    #: Out of the box, this filter will include all configuration settings, but also the following:
    #:
    #: - ``HOST_USER_ID``: the numerical ID of the user on the host.
    #: - ``TUTOR_APP``: the app name ("tutor" by default), used to determine the dev/local project names.
    #: - ``TUTOR_VERSION``: the current version of Tutor.
    #: - ``iter_values_named``: a function to iterate on variables that start or end with a given string.
    #: - ``iter_mounts``: a function that yields compose-compatible bind-mounts for any given service.
    #: - ``iter_mounted_directories``: iterate on bind-mounted directory names.
    #: - ``patch``: a function to incorporate extra content into a template.
    #:
    #: :parameter filters: list of (name, value) tuples.
    ENV_TEMPLATE_VARIABLES: Filter[list[tuple[str, Any]], []] = Filter()

    #: List of images to be built when we run ``tutor images build ...``.
    #:
    #: :parameter list[tuple[str, tuple[str, ...], str, tuple[str, ...]]] tasks: list of ``(name, path, tag, args)`` tuples.
    #:
    #:    - ``name`` is the name of the image, as in ``tutor images build myimage``.
    #:    - ``path`` is the relative path to the folder that contains the Dockerfile. This can be either a string or a tuple of strings.
    #:      For instance ``("myplugin", "build", "myservice")`` indicates that the template will be read from
    #:      ``myplugin/build/myservice/Dockerfile``. This argument value would be equivalent to "myplugin/build/myservice".
    #:    - ``tag`` is the Docker tag that will be applied to the image. It will be
    #:      rendered at runtime with the user configuration. Thus, the image tag could
    #:      be ``"{{ DOCKER_REGISTRY }}/myimage:{{ TUTOR_VERSION }}"``.
    #:    - ``args`` is a list of arguments that will be passed to ``docker build ...``.
    #: :parameter Config config: user configuration.
    IMAGES_BUILD: Filter[
        list[tuple[str, Union[str, tuple[str, ...]], str, tuple[str, ...]]], [Config]
    ] = Filter()

    #: List of image names which must be built prior to launching the platform. These
    #: images will be built on launch, in "dev" and "local" mode (but not in Kubernetes).
    #:
    #: :parameter list[str] names: list of image names.
    #: :parameter str context_name: either "local" or "dev", depending on the calling context.
    IMAGES_BUILD_REQUIRED: Filter[list[str], [Literal["local", "dev"]]] = Filter()

    #: List of host directories to be automatically bind-mounted in Docker images at
    #: build time. For instance, this is useful to build Docker images using a custom
    #: repository on the host.
    #:
    #: This filter works similarly to the :py:data:`COMPOSE_MOUNTS` filter, with a few differences.
    #:
    #: :parameter list[tuple[str, str]] mounts: each item is a pair of ``(name, value)``
    #:   used to generate a build context at build time. See the corresponding `Docker
    #:   documentation <https://docs.docker.com/engine/reference/commandline/buildx_build/#build-context>`__.
    #:   The following option will be added to the ``docker buildx build`` command:
    #:   ``--build-context={name}={value}``. If the Dockerfile contains a "name" stage, then
    #:   that stage will be replaced by the corresponding directory on the host.
    #: :parameter str name: full path to the host-mounted folder. As opposed to
    #:   :py:data:`COMPOSE_MOUNTS`, this is not just the basename, but the full path. When
    #:   implementing this filter you should check this path (for instance: with
    #:   ``os.path.basename(path)``) to conditionally add mounts.
    IMAGES_BUILD_MOUNTS: Filter[list[tuple[str, str]], [str]] = Filter()

    #: List of images to be pulled when we run ``tutor images pull ...``.
    #:
    #: :parameter list[tuple[str, str]] tasks: list of ``(name, tag)`` tuples.
    #:
    #:    - ``name`` is the name of the image, as in ``tutor images pull myimage``.
    #:    - ``tag`` is the Docker tag that will be applied to the image. (see :py:data:`IMAGES_BUILD`).
    #: :parameter Config config: user configuration.
    IMAGES_PULL: Filter[list[tuple[str, str]], [Config]] = Filter()

    #: List of images to be pushed when we run ``tutor images push ...``.
    #: Parameters are the same as for :py:data:`IMAGES_PULL`.
    IMAGES_PUSH: Filter[list[tuple[str, str]], [Config]] = Filter()

    #: List of directories that will be automatically bind-mounted in an image (at
    #: build-time) and a container (at run-time).
    #:
    #: Whenever a user runs: ``tutor mounts add /path/to/name``, "name" will be matched to
    #: the regular expressions in this filter. If it matches, then the directory will be
    #: automatically bind-mounted in the matching Docker image at build time and run
    #: time. At build-time, they will be added to a layer named "mnt-{name}". At
    #: run-time, they wll be mounted in ``/mnt/<name>``.
    #:
    #: In the case of edx-platform, ``pip install -e .`` will be run in this directory
    #: at build-time. And the same host directory will be bind-mounted in that location
    #: at run time. This allows users to transparently work on edx-platform
    #: dependencies, such as Python packages.
    #:
    #: By default, xblocks and some common edx-platform packages are already present in
    #: this filter, and associated to the "openedx" image. Add your own Python
    #: dependencies to this filter to make it easier for users to work on the
    #: dependencies of your app.
    #:
    #: See the list of all edx-platform base requirements here:
    #: https://github.com/openedx/edx-platform/blob/master/requirements/edx/base.txt
    #:
    #: This filter was mostly designed for edx-platform, but it can be used by any
    #: Python-based Docker image as well. The Dockerfile must declare mounted layers::
    #:
    #:     {% for name in iter_mounted_directories(MOUNTS, "yourimage") %}
    #:     FROM scratch AS mnt-{{ name }}
    #:     {% endfor %}
    #:
    #: Then, Python packages are installed with::
    #:
    #:     {% for name in iter_mounted_directories(MOUNTS, "yourimage") %}
    #:     COPY --from=mnt-{{ name }} --chown=app:app / /mnt/{{ name }}
    #:     RUN pip install -e "/mnt/{{ name }}"
    #:     {% endfor %}
    #:
    #: And the docker-compose service must include the following::
    #:
    #:    volumes:
    #:      {%- for mount in iter_mounts(MOUNTS, "yourimage") %}
    #:      - {{ mount }}
    #:      {%- endfor %}
    #:
    #: :parameter list[tuple[str, str]] name_regex: Each tuple is the name of an image and a
    #:   regular expression. For instance: ``("openedx", r".*xblock.*")``.
    MOUNTED_DIRECTORIES: Filter[list[tuple[str, str]], []] = Filter()

    #: List of plugin indexes that are loaded when we run ``tutor plugins update``. By
    #: default, the plugin indexes are stored in the user configuration. This filter makes
    #: it possible to extend and modify this list with plugins.
    #:
    #: :parameter list[str] indexes: list of index URLs. Remember that entries further
    #:   in the list have priority.
    PLUGIN_INDEXES: Filter[list[str], []] = Filter()

    #: Filter to modify the url of a plugin index url. This is convenient to alias
    #: plugin indexes with a simple name, such as "main" or "contrib".
    #:
    #: :parameter str url: value passed to the ``index add/remove`` commands.
    PLUGIN_INDEX_URL: Filter[str, []] = Filter()

    #: When installing an entry from a plugin index, the plugin data from the index will
    #: go through this filter before it is passed along to ``pip install``. Thus, this is a
    #: good place to add custom authentication when you need to install from a private
    #: index.
    #:
    #: :parameter dict[str, str] plugin: the dict entry from the plugin index. It
    #:   includes an additional "index" key which contains the plugin index URL.
    PLUGIN_INDEX_ENTRY_TO_INSTALL: Filter[dict[str, str], []] = Filter()

    #: Information about each installed plugin, including its version.
    #: Keep this information to a single line for easier parsing by 3rd-party scripts.
    #:
    #: :param list[tuple[str, str]] versions: each pair is a ``(plugin, info)`` tuple.
    PLUGINS_INFO: Filter[list[tuple[str, str]], []] = Filter()

    #: List of installed plugins. In order to be added to this list, a plugin must first
    #: be discovered (see :py:data:`Actions.CORE_READY`).
    #:
    #: :param list[str] plugins: plugin developers probably don't have to implement this
    #:   filter themselves, but they can apply it to check for the presence of other
    #:   plugins.
    PLUGINS_INSTALLED: Filter[list[str], []] = Filter()

    #: List of loaded plugins.
    #:
    #: :param list[str] plugins: plugin developers probably don't have to modify this
    #:   filter themselves, but they can apply it to check whether other plugins are enabled.
    PLUGINS_LOADED: Filter[list[str], []] = Filter()

    #: Use this filter to determine whether a file should be rendered. This can be useful in scenarios where
    #: certain types of files need special handling, such as binary files, which should not be rendered as text.
    #:
    #: This filter expects a boolean return value that indicates whether the file should be rendered.
    #:
    #: :param bool should_render: Initial decision on rendering the file, typically set to True.
    #: :param str file_path: The path to the file being checked.
    IS_FILE_RENDERED: Filter[bool, [str]] = Filter()


class Contexts:
    """
    Here we list all the :py:class:`contexts <tutor.core.hooks.Context>` that are used across Tutor. It is not expected that
    plugin developers will ever need to use contexts. But if you do, this is how it
    should be done::

        from tutor import hooks

        with hooks.Contexts.SOME_CONTEXT.enter():
            # do stuff and all created hooks will include SOME_CONTEXT
            ...

        # Apply only the hook callbacks that were created within SOME_CONTEXT
        hooks.Actions.MY_ACTION.do_from_context(str(hooks.Contexts.SOME_CONTEXT))
        hooks.Filters.MY_FILTER.apply_from_context(hooks.Contexts.SOME_CONTEXT.name)
    """

    #: Dictionary of name/contexts. Each value is a context that we enter whenever we
    #: create hooks for a specific application or plugin. For instance, plugin
    #: "myplugin" will be enabled within the "app:myplugin" context.
    APP: dict[str, Context] = {}

    @classmethod
    def app(cls, name: str) -> Context:
        if name not in cls.APP:
            cls.APP[name] = Context(f"app:{name}")
        return cls.APP[name]

    #: Plugins will be installed and enabled within this context.
    PLUGINS = Context("plugins")

    #: YAML-formatted v0 plugins will be installed within this context.
    PLUGINS_V0_YAML = Context("plugins:v0:yaml")

    #: Python entrypoint plugins will be installed within this context.
    PLUGINS_V0_ENTRYPOINT = Context("plugins:v0:entrypoint")
