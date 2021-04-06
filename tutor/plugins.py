import importlib
import os
from copy import deepcopy
from glob import glob
from typing import Any, Dict, Iterator, List, Optional, Tuple, Type, Union

import appdirs
import click
import pkg_resources

from . import exceptions, fmt, serialize
from .types import Config, get_typed

CONFIG_KEY = "PLUGINS"


class BasePlugin:
    """
    Tutor plugins are defined by a name and an object that implements one or more of the
    following properties:

    `config` (dict str->dict(str->str)): contains "add", "set", "default" keys. Entries
    in these dicts will be added or override the global configuration. Keys in "add" and
    "set" will be prefixed by the plugin name in uppercase.

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
    in sequence during initialization, you should define:

        hooks["init"] = ["service1", "service2"]

    It is then assumed that there are `myplugin/hooks/service1/init` and
    `myplugin/hooks/service2/init` templates in the plugin `templates` directory.

    `command` (click.Command): if a plugin exposes a `command` attribute, users will be able to run it from the command line as `tutor pluginname`.
    """

    INSTALLED: List["BasePlugin"] = []
    _IS_LOADED = False

    def __init__(self, name: str, obj: Any) -> None:
        self.name = name
        self.config = self.load_config(obj, self.name)
        self.patches = self.load_patches(obj, self.name)
        self.hooks = self.load_hooks(obj, self.name)

        templates_root = get_callable_attr(obj, "templates", default=None)
        if templates_root is not None:
            assert isinstance(templates_root, str)
        self.templates_root = templates_root

        command = getattr(obj, "command", None)
        if command is not None:
            assert isinstance(command, click.Command)
        self.command: click.Command = command

    @staticmethod
    def load_config(obj: Any, plugin_name: str) -> Dict[str, Config]:
        """
        Load config and check types.
        """
        config = get_callable_attr(obj, "config", {})
        if not isinstance(config, dict):
            raise exceptions.TutorError(
                "Invalid config in plugin {}. Expected dict, got {}.".format(
                    plugin_name, config.__class__
                )
            )
        for name, subconfig in config.items():
            if not isinstance(name, str):
                raise exceptions.TutorError(
                    "Invalid config entry '{}' in plugin {}. Expected str, got {}.".format(
                        name, plugin_name, config.__class__
                    )
                )
            if not isinstance(subconfig, dict):
                raise exceptions.TutorError(
                    "Invalid config entry '{}' in plugin {}. Expected str keys, got {}.".format(
                        name, plugin_name, config.__class__
                    )
                )
            for key in subconfig.keys():
                if not isinstance(key, str):
                    raise exceptions.TutorError(
                        "Invalid config entry '{}.{}' in plugin {}. Expected str, got {}.".format(
                            name, key, plugin_name, key.__class__
                        )
                    )
        return config

    @staticmethod
    def load_patches(obj: Any, plugin_name: str) -> Dict[str, str]:
        """
        Load patches and check the types are right.
        """
        patches = get_callable_attr(obj, "patches", {})
        if not isinstance(patches, dict):
            raise exceptions.TutorError(
                "Invalid patches in plugin {}. Expected dict, got {}.".format(
                    plugin_name, patches.__class__
                )
            )
        for patch_name, content in patches.items():
            if not isinstance(patch_name, str):
                raise exceptions.TutorError(
                    "Invalid patch name '{}' in plugin {}. Expected str, got {}.".format(
                        patch_name, plugin_name, patch_name.__class__
                    )
                )
            if not isinstance(content, str):
                raise exceptions.TutorError(
                    "Invalid patch '{}' in plugin {}. Expected str, got {}.".format(
                        patch_name, plugin_name, content.__class__
                    )
                )
        return patches

    @staticmethod
    def load_hooks(
        obj: Any, plugin_name: str
    ) -> Dict[str, Union[Dict[str, str], List[str]]]:
        """
        Load hooks and check types.
        """
        hooks = get_callable_attr(obj, "hooks", default={})
        if not isinstance(hooks, dict):
            raise exceptions.TutorError(
                "Invalid hooks in plugin {}. Expected dict, got {}.".format(
                    plugin_name, hooks.__class__
                )
            )
        for hook_name, hook in hooks.items():
            if not isinstance(hook_name, str):
                raise exceptions.TutorError(
                    "Invalid hook name '{}' in plugin {}. Expected str, got {}.".format(
                        hook_name, plugin_name, hook_name.__class__
                    )
                )
            if isinstance(hook, list):
                for service in hook:
                    if not isinstance(service, str):
                        raise exceptions.TutorError(
                            "Invalid service in hook '{}' from plugin {}. Expected str, got {}.".format(
                                hook_name, plugin_name, service.__class__
                            )
                        )
            elif isinstance(hook, dict):
                for name, value in hook.items():
                    if not isinstance(name, str) or not isinstance(value, str):
                        raise exceptions.TutorError(
                            "Invalid hook '{}' in plugin {}. Only str -> str entries are supported.".format(
                                hook_name, plugin_name
                            )
                        )
            else:
                raise exceptions.TutorError(
                    "Invalid hook '{}' in plugin {}. Expected dict or list, got {}.".format(
                        hook_name, plugin_name, hook.__class__
                    )
                )
        return hooks

    def config_key(self, key: str) -> str:
        """
        Config keys in the "add" and "defaults" dicts should be prefixed by the plugin name, in uppercase.
        """
        return self.name.upper() + "_" + key

    @property
    def config_add(self) -> Config:
        return self.config.get("add", {})

    @property
    def config_set(self) -> Config:
        return self.config.get("set", {})

    @property
    def config_defaults(self) -> Config:
        return self.config.get("defaults", {})

    @property
    def version(self) -> str:
        raise NotImplementedError

    @classmethod
    def iter_installed(cls) -> Iterator["BasePlugin"]:
        if not cls._IS_LOADED:
            for plugin in cls.iter_load():
                cls.INSTALLED.append(plugin)
            cls._IS_LOADED = True
        yield from cls.INSTALLED

    @classmethod
    def iter_load(cls) -> Iterator["BasePlugin"]:
        raise NotImplementedError


class EntrypointPlugin(BasePlugin):
    """
    Entrypoint plugins are regular python packages that have a 'tutor.plugin.v0' entrypoint.

    The API for Tutor plugins is currently in development. The entrypoint will switch to
    'tutor.plugin.v1' once it is stabilised.
    """

    ENTRYPOINT = "tutor.plugin.v0"

    def __init__(self, entrypoint: pkg_resources.EntryPoint) -> None:
        super().__init__(entrypoint.name, entrypoint.load())
        self.entrypoint = entrypoint

    @property
    def version(self) -> str:
        if not self.entrypoint.dist:
            return "0.0.0"
        return self.entrypoint.dist.version

    @classmethod
    def iter_load(cls) -> Iterator["EntrypointPlugin"]:
        for entrypoint in pkg_resources.iter_entry_points(cls.ENTRYPOINT):
            yield cls(entrypoint)


class OfficialPlugin(BasePlugin):
    """
    Official plugins have a "plugin" module which exposes a __version__ attribute.
    Official plugins should be manually added by calling `OfficialPlugin.load()`.
    """

    @classmethod
    def load(cls, name: str) -> BasePlugin:
        plugin = cls(name)
        cls.INSTALLED.append(plugin)
        return plugin

    def __init__(self, name: str):
        self.module = importlib.import_module("tutor{}.plugin".format(name))
        super().__init__(name, self.module)

    @property
    def version(self) -> str:
        version = getattr(self.module, "__version__")
        if not isinstance(version, str):
            raise TypeError("OfficialPlugin __version__ must be 'str'")
        return version

    @classmethod
    def iter_load(cls) -> Iterator[BasePlugin]:
        yield from []


class DictPlugin(BasePlugin):
    ROOT_ENV_VAR_NAME = "TUTOR_PLUGINS_ROOT"
    ROOT = os.path.expanduser(
        os.environ.get(ROOT_ENV_VAR_NAME, "")
    ) or appdirs.user_data_dir(appname="tutor-plugins")

    def __init__(self, data: Config):
        name = data["name"]
        if not isinstance(name, str):
            raise exceptions.TutorError(
                "Invalid plugin name: '{}'. Expected str, got {}".format(
                    name, name.__class__
                )
            )

        # Create a generic object (sort of a named tuple) which will contain all key/values from data
        class Module:
            pass

        obj = Module()
        for key, value in data.items():
            setattr(obj, key, value)

        super().__init__(name, obj)

        version = data["version"]
        if not isinstance(version, str):
            raise TypeError("DictPlugin.__version__ must be str")
        self._version: str = version

    @property
    def version(self) -> str:
        return self._version

    @classmethod
    def iter_load(cls) -> Iterator[BasePlugin]:
        for path in glob(os.path.join(cls.ROOT, "*.yml")):
            with open(path) as f:
                data = serialize.load(f)
                if not isinstance(data, dict):
                    raise exceptions.TutorError(
                        "Invalid plugin: {}. Expected dict.".format(path)
                    )
                try:
                    yield cls(data)
                except KeyError as e:
                    raise exceptions.TutorError(
                        "Invalid plugin: {}. Missing key: {}".format(path, e.args[0])
                    )


class Plugins:
    PLUGIN_CLASSES: List[Type[BasePlugin]] = [
        OfficialPlugin,
        EntrypointPlugin,
        DictPlugin,
    ]

    def __init__(self, config: Config):
        self.config = deepcopy(config)
        # patches has the following structure:
        # {patch_name -> {plugin_name -> "content"}}
        self.patches: Dict[str, Dict[str, str]] = {}
        # some hooks have a dict-like structure, like "build", others are list of services.
        self.hooks: Dict[str, Dict[str, Union[Dict[str, str], List[str]]]] = {}
        self.template_roots: Dict[str, str] = {}

        for plugin in self.iter_enabled():
            for patch_name, content in plugin.patches.items():
                if patch_name not in self.patches:
                    self.patches[patch_name] = {}
                self.patches[patch_name][plugin.name] = content

            for hook_name, services in plugin.hooks.items():
                if hook_name not in self.hooks:
                    self.hooks[hook_name] = {}
                self.hooks[hook_name][plugin.name] = services

    @classmethod
    def clear(cls) -> None:
        for PluginClass in cls.PLUGIN_CLASSES:
            PluginClass.INSTALLED.clear()

    @classmethod
    def iter_installed(cls) -> Iterator[BasePlugin]:
        """
        Iterate on all installed plugins. Plugins are deduplicated by name. The list of installed plugins is cached to
        prevent too many re-computations, which happens a lot.
        """
        installed_plugin_names = set()
        for PluginClass in cls.PLUGIN_CLASSES:
            for plugin in PluginClass.iter_installed():
                if plugin.name not in installed_plugin_names:
                    installed_plugin_names.add(plugin.name)
                    yield plugin

    def iter_enabled(self) -> Iterator[BasePlugin]:
        for plugin in self.iter_installed():
            if is_enabled(self.config, plugin.name):
                yield plugin

    def iter_patches(self, name: str) -> Iterator[Tuple[str, str]]:
        plugin_patches = self.patches.get(name, {})
        plugins = sorted(plugin_patches.keys())
        for plugin in plugins:
            yield plugin, plugin_patches[plugin]

    def iter_hooks(
        self, hook_name: str
    ) -> Iterator[Tuple[str, Union[Dict[str, str], List[str]]]]:
        yield from self.hooks.get(hook_name, {}).items()


def get_callable_attr(
    plugin: Any, attr_name: str, default: Optional[Any] = None
) -> Optional[Any]:
    attr = getattr(plugin, attr_name, default)
    if callable(attr):
        attr = attr()
    return attr


def is_installed(name: str) -> bool:
    for plugin in iter_installed():
        if name == plugin.name:
            return True
    return False


def iter_installed() -> Iterator[BasePlugin]:
    yield from Plugins.iter_installed()


def enable(config: Config, name: str) -> None:
    if not is_installed(name):
        raise exceptions.TutorError("plugin '{}' is not installed.".format(name))
    if is_enabled(config, name):
        return
    enabled = enabled_plugins(config)
    enabled.append(name)
    enabled.sort()


def disable(config: Config, name: str) -> None:
    fmt.echo_info("Disabling plugin {}...".format(name))
    for plugin in Plugins(config).iter_enabled():
        if name == plugin.name:
            # Remove "set" config entries
            for key, value in plugin.config_set.items():
                config.pop(key, None)
                fmt.echo_info("    Removed config entry {}={}".format(key, value))
    # Remove plugin from list
    enabled = enabled_plugins(config)
    while name in enabled:
        enabled.remove(name)
    fmt.echo_info("    Plugin disabled")


def iter_enabled(config: Config) -> Iterator[BasePlugin]:
    yield from Plugins(config).iter_enabled()


def is_enabled(config: Config, name: str) -> bool:
    return name in enabled_plugins(config)


def enabled_plugins(config: Config) -> List[str]:
    if not config.get(CONFIG_KEY):
        config[CONFIG_KEY] = []
    plugins = get_typed(config, CONFIG_KEY, list)
    return plugins


def iter_patches(config: Config, name: str) -> Iterator[Tuple[str, str]]:
    yield from Plugins(config).iter_patches(name)


def iter_hooks(
    config: Config, hook_name: str
) -> Iterator[Tuple[str, Union[Dict[str, str], List[str]]]]:
    yield from Plugins(config).iter_hooks(hook_name)
