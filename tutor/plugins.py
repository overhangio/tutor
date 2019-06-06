import pkg_resources

from . import exceptions


CONFIG_KEY = "PLUGINS"


class Plugins:
    """
    Tutor plugins are regular python packages that have a 'tutor.plugin.v0' entrypoint.

    The API for Tutor plugins is currently in development. The entrypoint will switch to
    'tutor.plugin.v1' once it is stabilised.

    This entrypoint must point to a module or a class that implements one or more of the
    following properties:

    `patches` (dict str->str): entries in this dict will be used to patch the rendered
    Tutor templates. For instance, to add "somecontent" to a template that includes '{{
    patch("mypatch") }}', set: `patches["mypatch"] = "somecontent"`. It is recommended
    to store all patches in separate files, and to dynamically list patches by listing
    the contents of a "patches"  subdirectory.

    `templates` (str): path to a directory that includes new template files for the
    plugin. It is recommended that all files in the template directory are stored in a
    `myplugin` folder to avoid conflicts with other plugins. Plugin templates are useful
    for content re-use, e.g: "{% include 'myplugin/mytemplate.html'}".

    `scripts` (dict str->list[str]): script hooks that will be run at various points
    during the lifetime of the platform. For instance, to run `service1` and `service2`
    in sequence during initialization, you should define:

        scripts["init"] = ["service1", "service2"]

    It is then assumed that there are `myplugin/scripts/service1/init` and
    `myplugin/scripts/service2/init` templates in the plugin `templates` directory.
    """

    ENTRYPOINT = "tutor.plugin.v0"
    INSTANCE = None
    EXTRA_INSTALLED = {}

    def __init__(self, config):
        self.config = config
        self.patches = {}
        self.scripts = {}
        self.templates = {}

        for plugin_name, plugin in self.iter_enabled():
            patches = get_callable_attr(plugin, "patches", {})
            for patch_name, content in patches.items():
                if patch_name not in self.patches:
                    self.patches[patch_name] = {}
                self.patches[patch_name][plugin_name] = content

            scripts = get_callable_attr(plugin, "scripts", {})
            for script_name, services in scripts.items():
                if script_name not in self.scripts:
                    self.scripts[script_name] = {}
                self.scripts[script_name][plugin_name] = services

            templates = get_callable_attr(plugin, "templates")
            if templates:
                self.templates[plugin_name] = templates

    @classmethod
    def clear(cls):
        cls.INSTANCE = None
        cls.EXTRA_INSTALLED.clear()

    @classmethod
    def instance(cls, config):
        if cls.INSTANCE is None or cls.INSTANCE.config != config:
            cls.INSTANCE = cls(config)
        return cls.INSTANCE

    @classmethod
    def iter_installed(cls):
        yield from cls.EXTRA_INSTALLED.items()
        for name, module in cls.iter_installed_entrypoints():
            if name not in cls.EXTRA_INSTALLED:
                yield name, module

    @classmethod
    def iter_installed_entrypoints(cls):
        for entrypoint in pkg_resources.iter_entry_points(cls.ENTRYPOINT):
            yield (entrypoint.name, entrypoint.load())

    def iter_enabled(self):
        for name, plugin in self.iter_installed():
            if is_enabled(self.config, name):
                yield name, plugin

    def iter_patches(self, name):
        plugin_patches = self.patches.get(name, {})
        plugins = sorted(plugin_patches.keys())
        for plugin in plugins:
            yield plugin, plugin_patches[plugin]

    def iter_scripts(self, script_name):
        for plugin_name, services in self.scripts.get(script_name, {}).items():
            for service in services:
                yield plugin_name, service

    def iter_templates(self):
        yield from self.templates.items()


def get_callable_attr(plugin, attr_name, default=None):
    attr = getattr(plugin, attr_name, default)
    if callable(attr):
        attr = attr()
    return attr


def is_installed(name):
    plugin_names = [name for name, _ in iter_installed()]
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


def iter_scripts(config, script_name):
    yield from Plugins.instance(config).iter_scripts(script_name)


def iter_templates(config):
    yield from Plugins.instance(config).iter_templates()
