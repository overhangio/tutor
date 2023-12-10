"""
Provide API for plugin features.
"""
from __future__ import annotations

import typing as t
from copy import deepcopy

from tutor import exceptions, fmt, hooks
from tutor.types import Config, get_typed

# Import modules to trigger hook creation
from . import openedx, v0, v1

# Cache of plugin patches, for efficiency
ENV_PATCHES_DICT: dict[str, list[str]] = {}


@hooks.Actions.PLUGINS_LOADED.add()
def _fill_patch_cache_on_load() -> None:
    """
    This action is run after plugins have been loaded.
    """
    _fill_patches_cache()


@hooks.Actions.PLUGIN_UNLOADED.add()
def _fill_patch_cache_on_unload(plugin: str, root: str, _config: Config) -> None:
    """
    This action is run after plugins have been unloaded.
    """
    _fill_patches_cache()


def _fill_patches_cache() -> None:
    """
    Some patches are added as (name, content) tuples with the ENV_PATCHES
    filter. We convert these patches to add them to ENV_PATCHES_DICT. This makes it
    easier for end-user to declare patches, and it's more performant.
    """
    ENV_PATCHES_DICT.clear()
    patches: t.Iterable[tuple[str, str]] = hooks.Filters.ENV_PATCHES.iterate()
    for name, content in patches:
        ENV_PATCHES_DICT.setdefault(name, [])
        ENV_PATCHES_DICT[name].append(content)


def is_installed(name: str) -> bool:
    """
    Return true if the plugin is installed.
    """
    return name in iter_installed()


def iter_installed() -> t.Iterator[str]:
    """
    Iterate on all installed plugins, sorted by name.

    This will yield all plugins, including those that have the same name.

    The CORE_READY action must have been triggered prior to calling this function,
    otherwise no installed plugin will be detected.
    """
    yield from sorted(hooks.Filters.PLUGINS_INSTALLED.iterate())


def iter_info() -> t.Iterator[tuple[str, t.Optional[str]]]:
    """
    Iterate on the information of all installed plugins.

    Yields (<plugin name>, <info>) tuples.
    """

    def plugin_info_name(info: tuple[str, t.Optional[str]]) -> str:
        return info[0]

    yield from sorted(hooks.Filters.PLUGINS_INFO.iterate(), key=plugin_info_name)


def is_loaded(name: str) -> bool:
    return name in iter_loaded()


def load_all(names: t.Iterable[str]) -> None:
    """
    Load all plugins one by one.

    Plugins are loaded in alphabetical order. We ignore plugins which failed to load.
    After all plugins have been loaded, the PLUGINS_LOADED action is triggered.
    """
    names = sorted(set(names))
    for name in names:
        try:
            load(name)
        except Exception as e:  # pylint: disable=broad-except
            fmt.echo_alert(f"Failed to enable plugin '{name}': {e}")
    hooks.Actions.PLUGINS_LOADED.do()


def load(name: str) -> None:
    """
    Load a given plugin, thus declaring all its hooks.

    Loading a plugin is done within a context, such that we can remove all hooks when a
    plugin is disabled, or during unit tests.
    """
    if not is_installed(name):
        raise exceptions.TutorError(f"plugin '{name}' is not installed.")
    with hooks.Contexts.PLUGINS.enter():
        with hooks.Contexts.app(name).enter():
            hooks.Actions.PLUGIN_LOADED.do(name)
            hooks.Filters.PLUGINS_LOADED.add_item(name)


def iter_loaded() -> t.Iterator[str]:
    """
    Iterate on the list of loaded plugin names, sorted in alphabetical order.

    Note that loaded plugin names are deduplicated. Thus, if two plugins have
    the same name, just one name will be displayed.
    """
    plugins: t.Iterable[str] = hooks.Filters.PLUGINS_LOADED.iterate()
    yield from sorted(set(plugins))


def iter_patches(name: str) -> t.Iterator[str]:
    """
    Yields: patch (str)
    """
    yield from ENV_PATCHES_DICT.get(name, [])


def unload(plugin: str) -> None:
    """
    Remove all filters and actions associated to a given plugin.
    """
    hooks.clear_all(context=hooks.Contexts.app(plugin).name)


@hooks.Actions.PLUGIN_UNLOADED.add(priority=hooks.priorities.HIGH)
def _unload_on_disable(plugin: str, _root: str, _config: Config) -> None:
    unload(plugin)
