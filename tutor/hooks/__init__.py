# The Tutor plugin system is licensed under the terms of the Apache 2.0 license.
__license__ = "Apache 2.0"

import functools
import typing as t

from typing_extensions import ParamSpec

# The imports that follow are the hooks API
from tutor.core.hooks import clear_all, priorities
from tutor.types import Config

from .catalog import Actions, Contexts, Filters


def lru_cache(func: t.Callable[..., t.Any]) -> t.Callable[..., t.Any]:
    """
    LRU cache decorator similar to `functools.lru_cache
    <https://docs.python.org/3/library/functools.html#functools.lru_cache>`__ that is
    automatically cleared whenever plugins are updated.

    Use this to decorate functions that need to be called multiple times with a return
    value that depends on which plugins are loaded. Typically: functions that depend on
    the output of filters.
    """
    decorated = functools.lru_cache(func)

    @Actions.PLUGIN_LOADED.add()
    def _clear_func_cache_on_load(_plugin: str) -> None:
        decorated.cache_clear()

    @Actions.PLUGIN_UNLOADED.add()
    def _clear_func_cache_on_unload(_plugin: str, _root: str, _config: Config) -> None:
        decorated.cache_clear()

    return decorated
