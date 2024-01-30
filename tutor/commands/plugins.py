from __future__ import annotations

import os
import tempfile
import typing as t

import click
import click.shell_completion

from tutor import config as tutor_config
from tutor import exceptions, fmt, hooks, plugins, utils
from tutor.commands.config import save as config_save_command
from tutor.plugins import indexes
from tutor.plugins.base import PLUGINS_ROOT, PLUGINS_ROOT_ENV_VAR_NAME
from tutor.types import Config

from .context import Context


class PluginName(click.ParamType):
    """
    Convenient param type that supports autocompletion of installed plugin names.
    """

    def __init__(self, allow_all: bool = False):
        self.allow_all = allow_all

    def shell_complete(
        self, ctx: click.Context, param: click.Parameter, incomplete: str
    ) -> list[click.shell_completion.CompletionItem]:
        return [
            click.shell_completion.CompletionItem(name)
            for name in self.get_names(incomplete)
        ]

    def get_names(self, incomplete: str) -> list[str]:
        candidates = []
        if self.allow_all:
            candidates.append("all")
        candidates += [name for name, _ in plugins.iter_info()]

        return [name for name in candidates if name.startswith(incomplete)]


class IndexPluginName(click.ParamType):
    """
    Param type for auto-completion of plugin names found in index cache.
    """

    def shell_complete(
        self, ctx: click.Context, param: click.Parameter, incomplete: str
    ) -> t.List[click.shell_completion.CompletionItem]:
        return [
            click.shell_completion.CompletionItem(entry.name)
            for entry in indexes.iter_cache_entries()
            if entry.name.startswith(incomplete.lower())
        ]


class IndexPluginNameOrLocation(IndexPluginName):
    """
    Same as IndexPluginName but also auto-completes file location.
    """

    def shell_complete(
        self, ctx: click.Context, param: click.Parameter, incomplete: str
    ) -> t.List[click.shell_completion.CompletionItem]:
        # Auto-complete plugin names
        autocompleted = super().shell_complete(ctx, param, incomplete)
        # Auto-complete local paths
        autocompleted += click.Path().shell_complete(ctx, param, incomplete)
        return autocompleted


@click.group(
    name="plugins",
    short_help="Manage Tutor plugins",
)
def plugins_command() -> None:
    """
    Manage Tutor plugins to add new features and customise your Open edX platform.

    Plugins can be downloaded from local and remote indexes. See the `tutor plugins
    index` subcommand.

    After the plugin index cache has been updated, plugins can be searched with:

        tutor plugins search <pattern>

    Plugins are installed with:

        tutor plugins install <name>
    """
    # All plugin commands should work even if there is no existing config file. This is
    # because users might enable or install plugins prior to configuration or
    # environment generation.
    # Thus, usage of `config.load_full` is prohibited.


@click.command(
    short_help="Print the location of file-based plugins",
    help=f"""Print the location of yaml-based plugins: nboth python v1 and yaml v0 plugins. This location can be manually
defined by setting the {PLUGINS_ROOT_ENV_VAR_NAME} environment variable""",
)
def printroot() -> None:
    fmt.echo(PLUGINS_ROOT)


@click.command(name="list")
@click.option(
    "-e",
    "--enabled",
    "show_enabled_only",
    is_flag=True,
    help="Display enabled plugins only",
)
def list_command(show_enabled_only: bool) -> None:
    """
    List installed plugins.
    """
    plugins_table: list[tuple[str, ...]] = [("NAME", "STATUS", "VERSION")]
    for plugin, plugin_info in plugins.iter_info():
        is_enabled = plugins.is_loaded(plugin)
        if is_enabled or not show_enabled_only:
            plugins_table.append(
                (
                    plugin,
                    plugin_status(plugin),
                    (plugin_info or "").replace("\n", " "),
                )
            )
    fmt.echo(utils.format_table(plugins_table))


@click.command(help="Enable a plugin")
@click.argument("plugin_names", metavar="plugin", nargs=-1, type=PluginName())
@click.pass_context
def enable(context: click.Context, plugin_names: list[str]) -> None:
    config = tutor_config.load_minimal(context.obj.root)
    for plugin in plugin_names:
        plugins.load(plugin)
        fmt.echo_info(f"Plugin {plugin} enabled")
    tutor_config.save_enabled_plugins(config)
    tutor_config.save_config_file(context.obj.root, config)
    context.invoke(config_save_command, env_only=True)


@click.command(
    short_help="Disable a plugin",
    help="Disable one or more plugins. Specify 'all' to disable all enabled plugins at once.",
)
@click.argument(
    "plugin_names", metavar="plugin", nargs=-1, type=PluginName(allow_all=True)
)
@click.pass_context
def disable(context: click.Context, plugin_names: list[str]) -> None:
    config = tutor_config.load_minimal(context.obj.root)
    disable_all = "all" in plugin_names
    disabled: list[str] = []
    for plugin in tutor_config.get_enabled_plugins(config):
        if disable_all or plugin in plugin_names:
            fmt.echo_info(f"Disabling plugin {plugin}...")
            hooks.Actions.PLUGIN_UNLOADED.do(plugin, context.obj.root, config)
            disabled.append(plugin)
            fmt.echo_info(f"Plugin {plugin} disabled")
    if disabled:
        tutor_config.save_config_file(context.obj.root, config)
        context.invoke(config_save_command, env_only=True)


@click.command(name="update")
@click.pass_obj
def update(context: Context) -> None:
    """
    Update the list of available plugins.
    """
    config = tutor_config.load(context.root)
    update_indexes(config)


def update_indexes(config: Config) -> None:
    all_plugins = indexes.fetch(config)
    cache_path = indexes.save_cache(all_plugins)
    fmt.echo_info(f"Plugin index local cache: {cache_path}")


@click.command()
@click.argument("names", metavar="name", type=IndexPluginNameOrLocation(), nargs=-1)
def install(names: list[str]) -> None:
    """
    Install one or more plugins.

    Each plugin name can be one of:

    1. A plugin name from the plugin indexes (see `tutor plugins search`)
    2. A local file that will be copied to the plugins root
    3. An http(s) location that will be downloaded to the plugins root

    In cases 2. and 3., the plugin root corresponds to the path given by `tutor plugins
    printroot`.
    """
    find_and_install(names, [])


@click.command()
@click.argument("names", metavar="name", type=IndexPluginName(), nargs=-1)
def upgrade(names: list[str]) -> None:
    """
    Upgrade one or more plugins.

    Specify "all" to upgrade all installed plugins. This command will only print a
    warning for plugins which cannot be found.
    """
    if "all" in names:
        names = list(plugins.iter_installed())
    available_names = []
    for name in names:
        try:
            indexes.find_in_cache(name)
        except exceptions.TutorError:
            fmt.echo_error(
                f"Failed to upgrade '{name}': plugin could not be found in indexes"
            )
        else:
            available_names.append(name)

    find_and_install(available_names, ["--upgrade"])


def find_and_install(names: list[str], pip_install_opts: t.List[str]) -> None:
    """
    Find and install a list of plugins, given by name. Single-file plugins are
    downloaded/copied. Python packages are or pip-installed.
    """
    single_file_plugins = []
    pip_requirements = []
    for name in names:
        if utils.is_url(name):
            single_file_plugins.append(name)
        else:
            plugin = indexes.find_in_cache(name)
            src = hooks.Filters.PLUGIN_INDEX_ENTRY_TO_INSTALL.apply(plugin.data)[
                "src"
            ].strip()
            if utils.is_url(src):
                single_file_plugins.append(src)
            else:
                # Create requirements file where each plugin reqs is prefixed by a
                # comment with its name
                pip_requirements.append(f"# {name}\n{src}")

    for url in single_file_plugins:
        install_single_file_plugin(url)

    if pip_requirements:
        # pip install -r reqs.txt
        requirements_txt = "\n".join(pip_requirements)
        with tempfile.NamedTemporaryFile(
            prefix="tutor-reqs-", suffix=".txt", mode="w"
        ) as tmp_reqs:
            tmp_reqs.write(requirements_txt)
            tmp_reqs.flush()
            fmt.echo_info(f"Installing pip requirements:\n{requirements_txt}")
            utils.execute(
                "pip", "install", *pip_install_opts, "--requirement", tmp_reqs.name
            )


def install_single_file_plugin(location: str) -> None:
    """
    Download or copy a single file to the plugins root.
    """
    plugin_path = os.path.join(PLUGINS_ROOT, os.path.basename(location))
    if not plugin_path.endswith(".yml") and not plugin_path.endswith(".py"):
        plugin_path += ".py"
    # Read url
    fmt.echo_info(f"Downloading plugin from {location}...")
    content = utils.read_url(location)
    # Save file
    utils.ensure_file_directory_exists(plugin_path)
    with open(plugin_path, "w", newline="\n", encoding="utf-8") as f:
        f.write(content)
    fmt.echo_info(f"Plugin installed at {plugin_path}")


@click.command()
@click.argument("pattern", default="")
def search(pattern: str) -> None:
    """
    Search in plugin descriptions.
    """
    results: list[tuple[str, ...]] = [("NAME", "STATUS", "DESCRIPTION")]
    for plugin in indexes.iter_cache_entries():
        if plugin.match(pattern):
            results.append(
                (
                    plugin.name,
                    plugin_status(plugin.name),
                    plugin.short_description,
                )
            )
    print(utils.format_table(results))


@click.command()
@click.argument("name", type=IndexPluginName())
def show(name: str) -> None:
    """
    Show plugin details from index.
    """
    name = name.lower()
    for plugin in indexes.iter_cache_entries():
        if plugin.name == name:
            fmt.echo(
                f"""Name: {plugin.name}
Source: {plugin.src}
Status: {plugin_status(name)}
Author: {plugin.author}
Maintainer: {plugin.maintainer}
Homepage: {plugin.url}
Index: {plugin.index}
Description: {plugin.description}"""
            )
            return
    raise exceptions.TutorError(
        f"No information available for plugin: '{name}'. Plugin could not be found in indexes."
    )


def plugin_status(name: str) -> str:
    """
    Return the status of a plugin. Either: "enabled", "installed" or "not installed".
    """
    if plugins.is_loaded(name):
        return "✅ enabled"
    if plugins.is_installed(name):
        return "installed"
    return "not installed"


@click.group(name="index", short_help="Manage plugin indexes")
def index_command() -> None:
    """
    Manage plugin indices.

    A plugin index is a list of Tutor plugins. An index can be public and shared with
    the community, or private, for instance to share plugins with a select group of
    users. Plugin indexes are a great way to share your plugins with other Tutor users.
    By default, only the official plugin index is enabled.

    Plugin indexes are fetched by running:

        tutor plugins update

    Plugin index cache is stored locally in the following subdirectory of the Tutor project environment:

        plugins/index/cache.yml
    """


@click.command(name="list", help="List plugin indexes")
@click.pass_obj
def index_list(context: Context) -> None:
    """
    Print plugin indexes.
    """
    config = tutor_config.load(context.root)
    for index in indexes.get_all(config):
        fmt.echo(index)


@click.command(name="add")
@click.argument("url", type=click.Path())
@click.pass_obj
def index_add(context: Context, url: str) -> None:
    """
    Add a plugin index.

    The index URL will be appended with '{version}/plugins.yml'. The index path can be
    either an http(s) url or a local file path.

    For official indexes, there is no need to pass a full URL. Instead, use "main" or
    "contrib".
    """
    config = tutor_config.load_minimal(context.root)
    if indexes.add(url, config):
        tutor_config.save_config_file(context.root, config)
        update_indexes(config)
    else:
        fmt.echo_alert("Plugin index was already added")


@click.command(name="remove")
@click.argument("url")
@click.pass_obj
def index_remove(context: Context, url: str) -> None:
    """
    Remove a plugin index.
    """
    config = tutor_config.load_minimal(context.root)
    if indexes.remove(url, config):
        tutor_config.save_config_file(context.root, config)
        update_indexes(config)
    else:
        fmt.echo_alert("Plugin index not present")


index_command.add_command(index_add)
index_command.add_command(index_list)
index_command.add_command(index_remove)
plugins_command.add_command(index_command)
plugins_command.add_command(list_command)
plugins_command.add_command(printroot)
plugins_command.add_command(enable)
plugins_command.add_command(disable)
plugins_command.add_command(update)
plugins_command.add_command(search)
plugins_command.add_command(install)
plugins_command.add_command(upgrade)
plugins_command.add_command(show)
