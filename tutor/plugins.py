import pkg_resources

from . import exceptions

"""
Tutor plugins are regular python packages that have a 'tutor.plugin.v1' entrypoint. This entrypoint must point to a module or a class that implements I don't know what (yet).
TODO
"""

# TODO switch to v1
ENTRYPOINT = "tutor.plugin.v0"
CONFIG_KEY = "PLUGINS"


class Patches:
    """
    Provide a patch cache on which we can conveniently iterate without having to parse again all plugin patches for every environment file.

    The CACHE static attribute is a dict of the form:

        {
            "patchname": {
                "pluginname": "patch content",
                ...
            },
            ...
        }
    """

    CACHE = {}

    def __init__(self, config, name):
        self.name = name
        if not self.CACHE:
            self.fill_cache(config)

    def __iter__(self):
        """
        Yields:
            plugin name (str)
            patch content (str)
        """
        plugin_patches = self.CACHE.get(self.name, {})
        plugins = sorted(plugin_patches.keys())
        for plugin in plugins:
            yield plugin, plugin_patches[plugin]

    @classmethod
    def fill_cache(cls, config):
        for plugin_name, plugin in iter_enabled(config):
            patches = get_callable_attr(plugin, "patches")
            for patch_name, content in patches.items():
                if patch_name not in cls.CACHE:
                    cls.CACHE[patch_name] = {}
                cls.CACHE[patch_name][plugin_name] = content


def get_callable_attr(plugin, attr_name):
    attr = getattr(plugin, attr_name, {})
    if callable(attr):
        # TODO pass config here for initialization
        attr = attr()
    return attr


def is_installed(name):
    plugin_names = [name for name, _ in iter_installed()]
    return name in plugin_names


def iter_installed():
    for entrypoint in pkg_resources.iter_entry_points(ENTRYPOINT):
        yield entrypoint.name, entrypoint.load()


def enable(config, name):
    if not is_installed(name):
        raise exceptions.TutorError("plugin '{}' is not installed.".format(name))
    if is_enabled(config, name):
        return
    if CONFIG_KEY not in config:
        config[CONFIG_KEY] = []
    config[CONFIG_KEY].append(name)
    config[CONFIG_KEY].sort()


def iter_enabled(config):
    for name, plugin in iter_installed():
        if is_enabled(config, name):
            yield name, plugin


def is_enabled(config, name):
    return name in config.get(CONFIG_KEY, [])


def iter_patches(config, name):
    for plugin, patch in Patches(config, name):
        yield plugin, patch


def load_config(config):
    """
    TODO Return:
    
    add_config (dict): config key/values to add, if they are not already present
    set_config (dict): config key/values to set and override existing values
    """
    add_config = {}
    set_config = {}
    defaults_config = {}
    for plugin_name, plugin in iter_enabled(config):
        plugin_prefix = plugin_name.upper() + "_"
        plugin_config = get_callable_attr(plugin, "config")

        # Add new config key/values
        for key, value in plugin_config.get("add", {}).items():
            add_config[plugin_prefix + key] = value

        # Set existing config key/values
        for key, value in plugin_config.get("set", {}).items():
            # TODO crash in case of conflicting keys between plugins
            # If key already exists
            set_config[key] = value

        # Create new defaults
        for key, value in plugin_config.get("defaults", {}).items():
            defaults_config[plugin_prefix + key] = value
    return add_config, set_config, defaults_config


def iter_scripts(config, script_name):
    """
    Scripts are of the form:

    scripts = {
        "script-name": [
            {
                "service": "service-name",
                "command": "...",
            },
            ...
        ],
        ...
    }
    """
    for plugin_name, plugin in iter_enabled(config):
        scripts = get_callable_attr(plugin, "scripts")
        for script in scripts.get(script_name, []):
            try:
                yield plugin_name, script["service"], script["command"]
            except KeyError as e:
                raise exceptions.TutorError(
                    "plugin script configuration requires key '{}'".format(e.args[0])
                )
