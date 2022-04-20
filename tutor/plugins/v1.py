import importlib.util
import os
from glob import glob

import pkg_resources

from tutor import hooks

from .base import PLUGINS_ROOT


@hooks.Actions.CORE_READY.add()
def _discover_module_plugins() -> None:
    """
    Discover .py files in the plugins root folder.
    """
    with hooks.Contexts.PLUGINS.enter():
        for path in glob(os.path.join(PLUGINS_ROOT, "*.py")):
            discover_module(path)


@hooks.Actions.CORE_READY.add()
def _discover_entrypoint_plugins() -> None:
    """
    Discover all plugins that declare a "tutor.plugin.v1" entrypoint.
    """
    with hooks.Contexts.PLUGINS.enter():
        if "TUTOR_IGNORE_ENTRYPOINT_PLUGINS" not in os.environ:
            for entrypoint in pkg_resources.iter_entry_points("tutor.plugin.v1"):
                discover_package(entrypoint)


def discover_module(path: str) -> None:
    """
    Install a plugin written as a single file module.
    """
    name = os.path.splitext(os.path.basename(path))[0]

    # Add plugin to the list of installed plugins
    hooks.Filters.PLUGINS_INSTALLED.add_item(name)

    # Add plugin information
    hooks.Filters.PLUGINS_INFO.add_item((name, path))

    # Import module on enable
    load_plugin_action = hooks.Actions.PLUGIN_LOADED(name)

    @load_plugin_action.add()
    def load() -> None:
        # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
        spec = importlib.util.spec_from_file_location("tutor.plugin.v1.{name}", path)
        if spec is None or spec.loader is None:
            raise ValueError("Plugin could not be found: {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)


def discover_package(entrypoint: pkg_resources.EntryPoint) -> None:
    """
    Install a plugin from a python package.
    """
    name = entrypoint.name

    # Add plugin to the list of installed plugins
    hooks.Filters.PLUGINS_INSTALLED.add_item(name)

    # Add plugin information
    if entrypoint.dist is None:
        raise ValueError(f"Could not read plugin version: {name}")
    hooks.Filters.PLUGINS_INFO.add_item((name, entrypoint.dist.version))

    # Import module on enable
    load_plugin_action = hooks.Actions.PLUGIN_LOADED(name)

    @load_plugin_action.add()
    def load() -> None:
        entrypoint.load()
