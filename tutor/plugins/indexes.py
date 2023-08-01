from __future__ import annotations

import os
import typing as t

from yaml.parser import ParserError

from tutor import env, fmt, hooks, serialize, utils
from tutor.__about__ import __version__, __version_suffix__
from tutor.exceptions import TutorError
from tutor.types import Config, get_typed

PLUGIN_INDEXES_KEY = "PLUGIN_INDEXES"
# Current release name ('zebulon' or 'nightly') and version (1-26)
RELEASE = __version_suffix__ or env.get_current_open_edx_release_name()
MAJOR_VERSION = int(__version__.split(".", maxsplit=1)[0])


class Indexes:
    # Store index cache path in this singleton.
    CACHE_PATH = ""


@hooks.Actions.PROJECT_ROOT_READY.add()
def _set_indexes_cache_path(root: str) -> None:
    Indexes.CACHE_PATH = env.pathjoin(root, "plugins", "index", "cache.yml")


@hooks.Filters.PLUGIN_INDEX_URL.add()
def _get_index_url_from_alias(url: str) -> str:
    known_aliases = {
        "main": "https://overhang.io/tutor/main",
        "contrib": "https://overhang.io/tutor/contrib",
    }
    return known_aliases.get(url, url)


@hooks.Filters.PLUGIN_INDEX_URL.add()
def _local_absolute_path(url: str) -> str:
    if os.path.exists(url):
        url = os.path.abspath(url)
    return url


class IndexEntry:
    def __init__(self, data: dict[str, str]):
        self._data = data

    @property
    def data(self) -> dict[str, str]:
        return self._data

    @property
    def name(self) -> str:
        return self.data["name"]

    @property
    def src(self) -> str:
        return self.data["src"]

    @property
    def short_description(self) -> str:
        lines = self.description.splitlines() or [""]
        return lines[0][:128]

    @property
    def description(self) -> str:
        return self.data.get("description", "").strip()

    @property
    def author(self) -> str:
        return self.data.get("author", "")

    @property
    def maintainer(self) -> str:
        return self.data.get("maintainer", "")

    @property
    def url(self) -> str:
        return self.data.get("url", "")

    @property
    def index(self) -> str:
        return self.data["index"]

    def match(self, pattern: str) -> bool:
        """
        Simple case-insensitive pattern matching.

        Pattern matching is case-insensitive. Both the name and description fields are
        searched.
        """
        if not pattern:
            return True
        pattern = pattern.lower()
        if pattern in self.name.lower() or pattern in self.description.lower():
            return True
        return False


def add(url: str, config: Config) -> bool:
    """
    Append an index to the list if not already present.

    Return True if if the list of indexes was modified.
    """
    indexes = get_all(config)
    url = hooks.Filters.PLUGIN_INDEX_URL.apply(url)
    if url in indexes:
        return False
    indexes.append(url)
    return True


def remove(url: str, config: Config) -> bool:
    """
    Remove an index to the list if present.

    Return True if if the list of indexes was modified.
    """
    indexes = get_all(config)
    url = hooks.Filters.PLUGIN_INDEX_URL.apply(url)
    if url not in indexes:
        return False
    indexes.remove(url)
    return True


def get_all(config: Config) -> list[str]:
    """
    Return the list of all plugin indexes.
    """
    config.setdefault(PLUGIN_INDEXES_KEY, [])
    indexes = get_typed(config, PLUGIN_INDEXES_KEY, list)
    for url in indexes:
        if not isinstance(url, str):
            raise TutorError(
                f"Invalid plugin index: {url}. Expected 'str', got '{url.__class__}'"
            )
    return indexes


def fetch(config: Config) -> list[dict[str, str]]:
    """
    Fetch the contents of all indexes. Return the list of plugin entries.
    """
    all_plugins: list[dict[str, str]] = []
    indexes = get_all(config)
    indexes = hooks.Filters.PLUGIN_INDEXES.apply(indexes)
    for index in indexes:
        url = named_index_url(index)
        try:
            fmt.echo_info(f"Fetching index {url}...")
            all_plugins += fetch_url(url)
        except TutorError as e:
            fmt.echo_error(f"  Failed to update index. {e.args[0]}")

    return deduplicate_plugins(all_plugins)


def deduplicate_plugins(plugins: list[dict[str, str]]) -> list[dict[str, str]]:
    plugins_dict: dict[str, dict[str, str]] = {}
    for plugin in plugins:
        # Plugins from later indexes override others
        plugin["name"] = plugin["name"].lower()
        plugins_dict[plugin["name"]] = plugin

    return sorted(plugins_dict.values(), key=lambda p: p["name"])


def fetch_url(url: str) -> list[dict[str, str]]:
    content = utils.read_url(url)
    plugins = parse_index(content)
    for plugin in plugins:
        # Store index url in the plugin itself
        plugin["index"] = url
    return plugins


def parse_index(content: str) -> list[dict[str, str]]:
    try:
        plugins = serialize.load(content)
    except ParserError as e:
        raise TutorError(f"Could not parse index: {e}") from e
    validate_index(plugins)
    valid_plugins = []
    for plugin in plugins:
        # check plugin format
        if "name" not in plugin:
            fmt.echo_error("  Invalid plugin: missing 'name' attribute")
        elif not isinstance(plugin["name"], str):
            fmt.echo_error(
                f"  Invalid plugin name: expected str, got {plugin['name'].__class__}"
            )
        else:
            valid_plugins.append(plugin)
    return valid_plugins


def validate_index(plugins: t.Any) -> list[dict[str, str]]:
    if not isinstance(plugins, list):
        raise TutorError(
            f"Invalid plugin index format. Expected list, got {plugins.__class__}"
        )
    return plugins


def named_index_url(url: str) -> str:
    if utils.is_http(url):
        separator = "" if url.endswith("/") else "/"
        return f"{url}{separator}{RELEASE}/plugins.yml"
    return os.path.join(url, RELEASE, "plugins.yml")


def find_in_cache(name: str) -> IndexEntry:
    """
    Find entry in cache. If not found, raise error.
    """
    name = name.lower()
    for entry in iter_cache_entries():
        if entry.name == name:
            return entry
    raise TutorError(f"Plugin '{name}' could not be found in indexes")


def iter_cache_entries() -> t.Iterator[IndexEntry]:
    for data in load_cache():
        yield IndexEntry(data)


def save_cache(plugins: list[dict[str, str]]) -> str:
    env.write_to(serialize.dumps(plugins), Indexes.CACHE_PATH)
    return Indexes.CACHE_PATH


def load_cache() -> list[dict[str, str]]:
    try:
        with open(Indexes.CACHE_PATH, encoding="utf8") as cache_if:
            plugins = serialize.load(cache_if)
    except FileNotFoundError as e:
        raise TutorError(
            f"Local index cache could not be found in {Indexes.CACHE_PATH}. Run `tutor plugins update`."
        ) from e
    return validate_index(plugins)
