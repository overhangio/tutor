import os
import typing as t
import urllib.request

import click
import click.shell_completion

from tutor import config as tutor_config
from tutor import exceptions, fmt, hooks, plugins
from tutor.plugins.base import PLUGINS_ROOT, PLUGINS_ROOT_ENV_VAR_NAME

from .context import Context


class PluginName(click.ParamType):
    """
    Convenient param type that supports plugin name autocompletion.
    """

    def __init__(self, allow_all: bool = False):
        self.allow_all = allow_all

    def shell_complete(
        self, ctx: click.Context, param: click.Parameter, incomplete: str
    ) -> t.List[click.shell_completion.CompletionItem]:
        return [
            click.shell_completion.CompletionItem(name)
            for name in self.get_names(incomplete)
        ]

    def get_names(self, incomplete: str) -> t.List[str]:
        candidates = []
        if self.allow_all:
            candidates.append("all")
        candidates += [name for name, _ in plugins.iter_info()]

        return [name for name in candidates if name.startswith(incomplete)]


@click.group(
    name="plugins",
    short_help="Manage Tutor plugins",
    help="Manage Tutor plugins to add new features and customise your Open edX platform",
)
def plugins_command() -> None:
    """
    All plugin commands should work even if there is no existing config file. This is
    because users might enable plugins prior to configuration or environment generation.
    """


@click.command(name="list", help="List installed plugins")
def list_command() -> None:
    lines = []
    first_column_width = 1
    for plugin, plugin_info in plugins.iter_info():
        plugin_info = plugin_info or ""
        plugin_info.replace("\n", " ")
        status = "" if plugins.is_loaded(plugin) else "(disabled)"
        lines.append((plugin, status, plugin_info))
        first_column_width = max([first_column_width, len(plugin) + 2])

    for plugin, status, plugin_info in lines:
        print(f"{plugin:{first_column_width}}\t{status:10}\t{plugin_info}")


@click.command(help="Enable a plugin")
@click.argument("plugin_names", metavar="plugin", nargs=-1, type=PluginName())
@click.pass_obj
def enable(context: Context, plugin_names: t.List[str]) -> None:
    config = tutor_config.load_minimal(context.root)
    for plugin in plugin_names:
        plugins.load(plugin)
        fmt.echo_info(f"Plugin {plugin} enabled")
    tutor_config.save_enabled_plugins(config)
    tutor_config.save_config_file(context.root, config)
    fmt.echo_info(
        "You should now re-generate your environment with `tutor config save`."
    )


@click.command(
    short_help="Disable a plugin",
    help="Disable one or more plugins. Specify 'all' to disable all enabled plugins at once.",
)
@click.argument(
    "plugin_names", metavar="plugin", nargs=-1, type=PluginName(allow_all=True)
)
@click.pass_obj
def disable(context: Context, plugin_names: t.List[str]) -> None:
    config = tutor_config.load_minimal(context.root)
    disable_all = "all" in plugin_names
    disabled: t.List[str] = []
    for plugin in tutor_config.get_enabled_plugins(config):
        if disable_all or plugin in plugin_names:
            fmt.echo_info(f"Disabling plugin {plugin}...")
            hooks.Actions.PLUGIN_UNLOADED.do(plugin, context.root, config)
            disabled.append(plugin)
            fmt.echo_info(f"Plugin {plugin} disabled")
    if disabled:
        tutor_config.save_config_file(context.root, config)
        fmt.echo_info(
            "You should now re-generate your environment with `tutor config save`."
        )


@click.command(
    short_help="Print the location of yaml-based plugins",
    help=f"""Print the location of yaml-based plugins. This location can be manually
defined by setting the {PLUGINS_ROOT_ENV_VAR_NAME} environment variable""",
)
def printroot() -> None:
    fmt.echo(PLUGINS_ROOT)


@click.command(
    short_help="Install a plugin",
    help=f"""Install a plugin, either from a local Python/YAML file or a remote, web-hosted
location. The plugin will be installed to {PLUGINS_ROOT_ENV_VAR_NAME}.""",
)
@click.argument("location", type=click.Path(dir_okay=False))
def install(location: str) -> None:
    basename = os.path.basename(location)
    if not basename.endswith(".yml") and not basename.endswith(".py"):
        basename += ".py"
    plugin_path = os.path.join(PLUGINS_ROOT, basename)

    if location.startswith("http"):
        # Download file
        response = urllib.request.urlopen(location)
        content = response.read().decode()
    elif os.path.isfile(location):
        # Read file
        with open(location, encoding="utf-8") as f:
            content = f.read()
    else:
        raise exceptions.TutorError(f"No plugin found at {location}")

    # Save file
    if not os.path.exists(PLUGINS_ROOT):
        os.makedirs(PLUGINS_ROOT)
    with open(plugin_path, "w", newline="\n", encoding="utf-8") as f:
        f.write(content)
    fmt.echo_info(f"Plugin installed at {plugin_path}")


plugins_command.add_command(list_command)
plugins_command.add_command(enable)
plugins_command.add_command(disable)
plugins_command.add_command(printroot)
plugins_command.add_command(install)
