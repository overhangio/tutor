import importlib
import importlib.util
import os
import typing as t
from glob import glob

import click
import importlib_metadata

from tutor import env, exceptions, fmt, hooks, serialize
from tutor.__about__ import __app__
from tutor.types import Config

from .base import PLUGINS_ROOT


class BasePlugin:
    """
    Tutor plugins are defined by a name and an object that implements one or more of the
    following properties:

    `config` (dict str->dict(str->str)): contains "add", "defaults", "set" keys. Entries
    in these dicts will be added or override the global configuration. Keys in "add" and
    "defaults" will be prefixed by the plugin name in uppercase.

    `patches` (dict str->str): entries in this dict will be used to patch the rendered
    Tutor templates. For instance, to add "somecontent" to a template that includes '{{
    patch("mypatch") }}', set: `patches["mypatch"] = "somecontent"`. It is recommended
    to store all patches in separate files, and to dynamically list patches by listing
    the contents of a "patches"  subdirectory.

    `templates` (str): path to a directory that includes new template files for the
    plugin. It is recommended that all files in the template directory are stored in a
    `myplugin` folder to avoid conflicts with other plugins. Plugin templates are useful
    for content re-use, e.g: "{% include 'myplugin/mytemplate.html'}".

    `hooks` (dict str->list[str]): hooks are commands that will be run at various points
    during the lifetime of the platform. For instance, to run `service1` and `service2`
    in sequence during initialisation, you should define:

        hooks["init"] = ["service1", "service2"]

    It is then assumed that there are `myplugin/hooks/service1/init` and
    `myplugin/hooks/service2/init` templates in the plugin `templates` directory.

    `command` (click.Command): if a plugin exposes a `command` attribute, users will be able to run it from the command line as `tutor pluginname`.
    """

    def __init__(self, name: str, loader: t.Optional[t.Any] = None) -> None:
        self.name = name
        self.loader = loader
        self.obj: t.Optional[t.Any] = None
        self._discover()

    def _discover(self) -> None:
        # Add itself to the list of installed plugins
        hooks.Filters.PLUGINS_INSTALLED.add_item(self.name)

        # Add plugin version
        hooks.Filters.PLUGINS_INFO.add_item((self.name, self._version() or ""))

        # Create actions and filters on load
        @hooks.Actions.PLUGIN_LOADED.add()
        def _load_plugin(name: str) -> None:
            if name == self.name:
                self.__load()

    def __load(self) -> None:
        """
        On loading a plugin, we create all the required actions and filters.

        Note that this method is quite costly. Thus it is important that as little is
        done as part of installing the plugin. For instance, we should not import
        modules during installation, but only when the plugin is enabled.
        """
        # Add all actions/filters
        self._load_obj()
        self._load_config()
        self._load_patches()
        self._load_tasks()
        self._load_templates_root()
        self._load_command()

    def _load_obj(self) -> None:
        """
        Override this method to write to the `obj` attribute based on the `loader`.
        """
        raise NotImplementedError

    def _load_config(self) -> None:
        """
        Load config and check types.
        """
        config = get_callable_attr(self.obj, "config", {})
        if not isinstance(config, dict):
            raise exceptions.TutorError(
                f"Invalid config in plugin {self.name}. Expected dict, got {config.__class__}."
            )
        for name, subconfig in config.items():
            if not isinstance(name, str):
                raise exceptions.TutorError(
                    f"Invalid config entry '{name}' in plugin {self.name}. Expected str, got {config.__class__}."
                )
            if not isinstance(subconfig, dict):
                raise exceptions.TutorError(
                    f"Invalid config entry '{name}' in plugin {self.name}. Expected str keys, got {config.__class__}."
                )
            for key in subconfig.keys():
                if not isinstance(key, str):
                    raise exceptions.TutorError(
                        f"Invalid config entry '{name}.{key}' in plugin {self.name}. Expected str, got {key.__class__}."
                    )

        # Config keys in the "add" and "defaults" dicts must be prefixed by
        # the plugin name, in uppercase.
        key_prefix = self.name.upper() + "_"

        hooks.Filters.CONFIG_UNIQUE.add_items(
            [
                (f"{key_prefix}{key}", value)
                for key, value in config.get("add", {}).items()
            ],
        )
        hooks.Filters.CONFIG_DEFAULTS.add_items(
            [
                (f"{key_prefix}{key}", value)
                for key, value in config.get("defaults", {}).items()
            ],
        )
        hooks.Filters.CONFIG_OVERRIDES.add_items(
            [(key, value) for key, value in config.get("set", {}).items()],
        )

    def _load_patches(self) -> None:
        """
        Load patches and check the types are right.
        """
        patches = get_callable_attr(self.obj, "patches", {})
        if not isinstance(patches, dict):
            raise exceptions.TutorError(
                f"Invalid patches in plugin {self.name}. Expected dict, got {patches.__class__}."
            )
        for patch_name, content in patches.items():
            if not isinstance(patch_name, str):
                raise exceptions.TutorError(
                    f"Invalid patch name '{patch_name}' in plugin {self.name}. Expected str, got {patch_name.__class__}."
                )
            if not isinstance(content, str):
                raise exceptions.TutorError(
                    f"Invalid patch '{patch_name}' in plugin {self.name}. Expected str, got {content.__class__}."
                )
            hooks.Filters.ENV_PATCHES.add_item((patch_name, content))

    def _load_tasks(self) -> None:
        """
        Load hooks and check types.
        """
        tasks = get_callable_attr(self.obj, "hooks", default={})
        if not isinstance(tasks, dict):
            raise exceptions.TutorError(
                f"Invalid hooks in plugin {self.name}. Expected dict, got {tasks.__class__}."
            )

        build_image_tasks = tasks.get("build-image", {})
        remote_image_tasks = tasks.get("remote-image", {})
        pre_init_tasks = tasks.get("pre-init", [])
        init_tasks = tasks.get("init", [])

        # Build images: hooks = {"build-image": {"myimage": "myimage:latest"}}
        # We assume that the dockerfile is in the build/myimage folder.
        for img, tag in build_image_tasks.items():
            hooks.Filters.IMAGES_BUILD.add_item(
                (img, ("plugins", self.name, "build", img), tag, ()),
            )
        # Remote images: hooks = {"remote-image": {"myimage": "myimage:latest"}}
        for img, tag in remote_image_tasks.items():
            hooks.Filters.IMAGES_PULL.add_item(
                (img, tag),
            )
            hooks.Filters.IMAGES_PUSH.add_item(
                (img, tag),
            )
        # Pre-init scripts: hooks = {"pre-init": ["myservice1", "myservice2"]}
        for service in pre_init_tasks:
            hooks.Filters.CLI_DO_INIT_TASKS.add_item(
                (
                    service,
                    env.read_template_file(self.name, "hooks", service, "pre-init"),
                ),
                priority=hooks.priorities.HIGH,
            )
        # Init scripts: hooks = {"init": ["myservice1", "myservice2"]}
        for service in init_tasks:
            hooks.Filters.CLI_DO_INIT_TASKS.add_item(
                (service, env.read_template_file(self.name, "hooks", service, "init"))
            )

    def _load_templates_root(self) -> None:
        templates_root = get_callable_attr(self.obj, "templates", default=None)
        if templates_root is None:
            return
        if not isinstance(templates_root, str):
            raise exceptions.TutorError(
                f"Invalid templates in plugin {self.name}. Expected str, got {templates_root.__class__}."
            )

        hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(templates_root)
        # We only add the "apps" and "build" folders and we render them in the
        # "plugins/<plugin name>" folder.
        hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
            [
                (
                    os.path.join(self.name, "apps"),
                    "plugins",
                ),
                (
                    os.path.join(self.name, "build"),
                    "plugins",
                ),
            ]
        )

    def _load_command(self) -> None:
        command = getattr(self.obj, "command", None)
        if command is None:
            return
        if not isinstance(command, click.Command):
            raise exceptions.TutorError(
                f"Invalid command in plugin {self.name}. Expected click.Command, got {command.__class__}."
            )
        # We force the command name to the plugin name
        command.name = self.name
        hooks.Filters.CLI_COMMANDS.add_item(command)

    def _version(self) -> t.Optional[str]:
        return None


class EntrypointPlugin(BasePlugin):
    """
    Entrypoint plugins are regular python packages that have a 'tutor.plugin.v0' entrypoint.

    The API for Tutor plugins is currently in development. The entrypoint will switch to
    'tutor.plugin.v1' once it is stabilised.
    """

    ENTRYPOINT = "tutor.plugin.v0"

    def __init__(self, entrypoint: importlib_metadata.EntryPoint) -> None:
        self.loader: importlib_metadata.EntryPoint = entrypoint
        super().__init__(entrypoint.name, entrypoint)

    def _load_obj(self) -> None:
        self.obj = importlib.import_module(self.loader.value)

    def _version(self) -> t.Optional[str]:
        if not self.loader.dist:
            raise exceptions.TutorError(f"Entrypoint plugin '{self.name}' has no dist.")
        return self.loader.dist.version

    @classmethod
    def discover_all(cls) -> None:
        entrypoints = importlib_metadata.entry_points(group=cls.ENTRYPOINT)
        for entrypoint in entrypoints:
            try:
                error: t.Optional[str] = None
                cls(entrypoint)
            except Exception as e:  # pylint: disable=broad-except
                error = str(e)
            if error:
                fmt.echo_error(
                    f"Failed to load entrypoint '{entrypoint.name} = {entrypoint.module_name}' from distribution {entrypoint.dist}: {error}"
                )


class OfficialPlugin(BasePlugin):
    """
    Official plugins have a "plugin" module which exposes a __version__ attribute.
    Official plugins should be manually added by instantiating them with: `OfficialPlugin('name')`.
    """

    NAMES = [
        "android",
        "discovery",
        "ecommerce",
        "forum",
        "license",
        "mfe",
        "minio",
        "notes",
        "webui",
        "xqueue",
    ]

    def _load_obj(self) -> None:
        self.obj = importlib.import_module(f"tutor{self.name}.plugin")

    def _version(self) -> t.Optional[str]:
        try:
            module = importlib.import_module(f"tutor{self.name}.__about__")
        except ModuleNotFoundError:
            return None
        version = getattr(module, "__version__")
        if version is None:
            return None
        if not isinstance(version, str):
            raise TypeError("OfficialPlugin __version__ must be 'str'")
        return version

    @classmethod
    def discover_all(cls) -> None:
        """
        This function must be called explicitely from the main. This is to handle
        detection of official plugins from within the compiled binary. When not running
        the binary, official plugins are treated as regular entrypoint plugins.
        """
        for plugin_name in cls.NAMES:
            if importlib.util.find_spec(f"tutor{plugin_name}") is not None:
                OfficialPlugin(plugin_name)


class DictPlugin(BasePlugin):
    def __init__(self, data: Config):
        self.loader: Config
        name = data["name"]
        if not isinstance(name, str):
            raise exceptions.TutorError(
                f"Invalid plugin name: '{name}'. Expected str, got {name.__class__}"
            )
        super().__init__(name, data)

    def _load_obj(self) -> None:
        # Create a generic object (sort of a named tuple) which will contain all
        # key/values from data
        class Module:
            pass

        self.obj = Module()
        for key, value in self.loader.items():
            setattr(self.obj, key, value)

    def _version(self) -> t.Optional[str]:
        version = self.loader.get("version", None)
        if version is None:
            return None
        if not isinstance(version, str):
            raise TypeError("DictPlugin.version must be str")
        return version

    @classmethod
    def discover_all(cls) -> None:
        for path in glob(os.path.join(PLUGINS_ROOT, "*.yml")):
            with open(path, encoding="utf-8") as f:
                data = serialize.load(f)
                if not isinstance(data, dict):
                    raise exceptions.TutorError(
                        f"Invalid plugin: {path}. Expected dict."
                    )
                try:
                    cls(data)
                except KeyError as e:
                    raise exceptions.TutorError(
                        f"Invalid plugin: {path}. Missing key: {e.args[0]}"
                    )


@hooks.Actions.CORE_READY.add()
def _discover_v0_plugins() -> None:
    """
    Install all entrypoint and dict plugins.

    Plugins from both classes are discovered in a context, to make it easier to disable
    them in tests.

    Note that official plugins are not discovered here. That's because they are expected
    to be discovered manually from within the tutor binary.

    Installing entrypoint or dict plugins can be disabled by defining the
    ``TUTOR_IGNORE_DICT_PLUGINS`` and ``TUTOR_IGNORE_ENTRYPOINT_PLUGINS``
    environment variables.
    """
    with hooks.Contexts.PLUGINS.enter():
        if "TUTOR_IGNORE_ENTRYPOINT_PLUGINS" not in os.environ:
            with hooks.Contexts.PLUGINS_V0_ENTRYPOINT.enter():
                EntrypointPlugin.discover_all()
        if "TUTOR_IGNORE_DICT_PLUGINS" not in os.environ:
            with hooks.Contexts.PLUGINS_V0_YAML.enter():
                DictPlugin.discover_all()


def get_callable_attr(
    plugin: t.Any, attr_name: str, default: t.Optional[t.Any] = None
) -> t.Optional[t.Any]:
    """
    Return the attribute of a plugin. If this attribute is a callable, return
    the return value instead.
    """
    attr = getattr(plugin, attr_name, default)
    if callable(attr):
        attr = attr()  # pylint: disable=not-callable
    return attr
