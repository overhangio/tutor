from collections import namedtuple
from copy import deepcopy
from glob import glob
import importlib
import os
import pkg_resources

import appdirs

from . import exceptions
from . import serialize


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

    def __init__(self, name, obj):
        self.name = name
        self.config = get_callable_attr(obj, "config", {})
        self.patches = get_callable_attr(obj, "patches", default={})
        self.hooks = get_callable_attr(obj, "hooks", default={})
        self.templates_root = get_callable_attr(obj, "templates", default=None)
        self.command = getattr(obj, "command", None)

    def config_key(self, key):
        """
        Config keys in the "add" and "defaults" dicts should be prefixed by the plugin name, in uppercase.
        """
        return self.name.upper() + "_" + key

    @property
    def config_add(self):
        return self.config.get("add", {})

    @property
    def config_set(self):
        return self.config.get("set", {})

    @property
    def config_defaults(self):
        return self.config.get("defaults", {})

    @property
    def version(self):
        raise NotImplementedError

    @classmethod
    def iter_installed(cls):
        raise NotImplementedError


class EntrypointPlugin(BasePlugin):
    """
    Entrypoint plugins are regular python packages that have a 'tutor.plugin.v0' entrypoint.

    The API for Tutor plugins is currently in development. The entrypoint will switch to
    'tutor.plugin.v1' once it is stabilised.
    """

    ENTRYPOINT = "tutor.plugin.v0"

    def __init__(self, entrypoint):
        super().__init__(entrypoint.name, entrypoint.load())
        self.entrypoint = entrypoint

    @property
    def version(self):
        return self.entrypoint.dist.version

    @classmethod
    def iter_installed(cls):
        for entrypoint in pkg_resources.iter_entry_points(cls.ENTRYPOINT):
            yield cls(entrypoint)


class OfficialPlugin(BasePlugin):
    """
    Official plugins have a "plugin" module which exposes a __version__
    attribute.
    Official plugins should be manually added to INSTALLED.
    """

    INSTALLED = []

    def __init__(self, name):
        self.module = importlib.import_module("tutor{}.plugin".format(name))
        super().__init__(name, self.module)

    @property
    def version(self):
        return self.module.__version__

    @classmethod
    def iter_installed(cls):
        yield from cls.INSTALLED


class DictPlugin(BasePlugin):
    ROOT_ENV_VAR_NAME = "TUTOR_PLUGINS_ROOT"
    ROOT = os.path.expanduser(
        os.environ.get(ROOT_ENV_VAR_NAME, "")
    ) or appdirs.user_data_dir(appname="tutor-plugins")

    def __init__(self, data):
        Module = namedtuple("Module", data.keys())
        obj = Module(**data)
        super().__init__(data["name"], obj)
        self._version = data["version"]

    @property
    def version(self):
        return self._version

    @classmethod
    def iter_installed(cls):
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

    INSTANCE = None

    def __init__(self, config):
        self.config = deepcopy(config)
        self.patches = {}
        self.hooks = {}
        self.template_roots = {}

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
    def clear(cls):
        cls.INSTANCE = None
        OfficialPlugin.INSTALLED.clear()

    @classmethod
    def instance(cls, config):
        if cls.INSTANCE is None or cls.INSTANCE.config != config:
            cls.INSTANCE = cls(config)
        return cls.INSTANCE

    @classmethod
    def iter_installed(cls):
        """
        Iterate on all installed plugins. Plugins are deduplicated by name.
        """
        classes = [OfficialPlugin, EntrypointPlugin, DictPlugin]
        installed_plugin_names = set()
        for PluginClass in classes:
            for plugin in PluginClass.iter_installed():
                if plugin.name not in installed_plugin_names:
                    installed_plugin_names.add(plugin.name)
                    yield plugin

    def iter_enabled(self):
        for plugin in self.iter_installed():
            if is_enabled(self.config, plugin.name):
                yield plugin

    def iter_patches(self, name):
        plugin_patches = self.patches.get(name, {})
        plugins = sorted(plugin_patches.keys())
        for plugin in plugins:
            yield plugin, plugin_patches[plugin]

    def iter_hooks(self, hook_name):
        yield from self.hooks.get(hook_name, {}).items()


def get_callable_attr(plugin, attr_name, default=None):
    attr = getattr(plugin, attr_name, default)
    if callable(attr):
        attr = attr()
    return attr


def is_installed(name):
    plugin_names = [plugin.name for plugin in iter_installed()]
    return name in plugin_names


def iter_installed():
    yield from Plugins.iter_installed()


def enable(config, name):
    if not is_installed(name):
        raise exceptions.TutorError("plugin '{}' is not installed.".format(name))
    if is_enabled(config, name):
        return
    if CONFIG_KEY not in config:
        config[CONFIG_KEY] = []
    config[CONFIG_KEY].append(name)
    config[CONFIG_KEY].sort()


def disable(config, name):
    while name in config[CONFIG_KEY]:
        config[CONFIG_KEY].remove(name)


def iter_enabled(config):
    yield from Plugins.instance(config).iter_enabled()


def is_enabled(config, name):
    return name in config.get(CONFIG_KEY, [])


def iter_patches(config, name):
    yield from Plugins.instance(config).iter_patches(name)


def iter_hooks(config, hook_name):
    yield from Plugins.instance(config).iter_hooks(hook_name)
