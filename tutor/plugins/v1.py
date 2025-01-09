import importlib.util
import os
from glob import glob
import sys

import importlib_metadata

from tutor import hooks
from tutor.types import Config

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
            for entrypoint in importlib_metadata.entry_points(group="tutor.plugin.v1"):
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
    @hooks.Actions.PLUGIN_LOADED.add()
    def load(plugin_name: str) -> None:
        if name == plugin_name:
            # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
            spec = importlib.util.spec_from_file_location(
                "tutor.plugin.v1.{name}", path
            )
            if spec is None or spec.loader is None:
                raise ValueError("Plugin could not be found: {path}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)


def discover_package(entrypoint: importlib_metadata.EntryPoint) -> None:
    """
    Install a plugin from a python package.
    """
    name = entrypoint.name

    # Add plugin to the list of installed plugins
    hooks.Filters.PLUGINS_INSTALLED.add_item(name)

    # Add plugin information
    if entrypoint.dist is None:
        raise ValueError(f"Could not read plugin version: {name}")
    dist_version = entrypoint.dist.version if entrypoint.dist else "Unknown"
    hooks.Filters.PLUGINS_INFO.add_item((name, dist_version))

    @hooks.Actions.PLUGIN_LOADED.add()
    def load(plugin_name: str) -> None:
        """
        Import module on enable.
        """
        if name == plugin_name:
            importlib.import_module(entrypoint.value)

    # Remove module from cache on disable
    @hooks.Actions.PLUGIN_UNLOADED.add()
    def unload(plugin_name: str, _root: str, _config: Config) -> None:
        """
        Remove plugin module from import cache on disable.

        This is necessary in one particular use case: when a plugin is enabled,
        disabled, and enabled again -- all within the same call to Tutor. In such a
        case, the following happens:

        1. plugin enabled: the plugin module is imported. It is automatically added by
           Python to the import cache.
        2. plugin disabled: action and filter callbacks are removed, but the module
           remains in the import cache.
        3. plugin enabled again: the plugin module is imported. But because it's in the
           import cache, the module instructions are not executed again.

        This is not supposed to happen when we run Tutor normally from the CLI. But when
        running a long-lived process, such as a web app, where a plugin might be enabled
        and disabled multiple times, this becomes an issue.
        """
        if name == plugin_name and entrypoint.value in sys.modules:
            sys.modules.pop(entrypoint.value)
