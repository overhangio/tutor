import os
import shutil
from typing import List
import urllib.request

import click

from .. import config as tutor_config
from .. import env as tutor_env
from .. import exceptions
from .. import fmt
from .. import plugins
from .context import Context


@click.group(
    name="plugins",
    short_help="Manage Tutor plugins",
    help="Manage Tutor plugins to add new features and customize your Open edX platform",
)
def plugins_command() -> None:
    """
    All plugin commands should work even if there is no existing config file. This is
    because users might enable plugins prior to configuration or environment generation.
    """


@click.command(name="list", help="List installed plugins")
@click.pass_obj
def list_command(context: Context) -> None:
    config = tutor_config.load_user(context.root)
    for plugin in plugins.iter_installed():
        status = "" if plugins.is_enabled(config, plugin.name) else " (disabled)"
        print(
            "{plugin}=={version}{status}".format(
                plugin=plugin.name, status=status, version=plugin.version
            )
        )


@click.command(help="Enable a plugin")
@click.argument("plugin_names", metavar="plugin", nargs=-1)
@click.pass_obj
def enable(context: Context, plugin_names: List[str]) -> None:
    config = tutor_config.load_user(context.root)
    for plugin in plugin_names:
        plugins.enable(config, plugin)
        fmt.echo_info("Plugin {} enabled".format(plugin))
    tutor_config.save_config_file(context.root, config)
    fmt.echo_info(
        "You should now re-generate your environment with `tutor config save`."
    )


@click.command(
    short_help="Disable a plugin",
    help="Disable one or more plugins. Specify 'all' to disable all enabled plugins at once.",
)
@click.argument("plugin_names", metavar="plugin", nargs=-1)
@click.pass_obj
def disable(context: Context, plugin_names: List[str]) -> None:
    config = tutor_config.load_user(context.root)
    if "all" in plugin_names:
        plugin_names = [plugin.name for plugin in plugins.iter_enabled(config)]
    for plugin_name in plugin_names:
        plugins.disable(config, plugin_name)
        delete_plugin(context.root, plugin_name)

    tutor_config.save_config_file(context.root, config)
    fmt.echo_info(
        "You should now re-generate your environment with `tutor config save`."
    )


def delete_plugin(root: str, name: str) -> None:
    plugin_dir = tutor_env.pathjoin(root, "plugins", name)
    if os.path.exists(plugin_dir):
        try:
            shutil.rmtree(plugin_dir)
        except PermissionError as e:
            raise exceptions.TutorError(
                "Could not delete file {} from plugin {} in folder {}".format(
                    e.filename, name, plugin_dir
                )
            )


@click.command(
    short_help="Print the location of yaml-based plugins",
    help="""Print the location of yaml-based plugins. This location can be manually
defined by setting the {} environment variable""".format(
        plugins.DictPlugin.ROOT_ENV_VAR_NAME
    ),
)
def printroot() -> None:
    fmt.echo(plugins.DictPlugin.ROOT)


@click.command(
    short_help="Install a plugin",
    help="""Install a plugin, either from a local YAML file or a remote, web-hosted
location. The plugin will be installed to {}.""".format(
        plugins.DictPlugin.ROOT_ENV_VAR_NAME
    ),
)
@click.argument("location")
def install(location: str) -> None:
    basename = os.path.basename(location)
    if not basename.endswith(".yml"):
        basename += ".yml"
    plugin_path = os.path.join(plugins.DictPlugin.ROOT, basename)

    if location.startswith("http"):
        # Download file
        response = urllib.request.urlopen(location)
        content = response.read().decode()
    elif os.path.isfile(location):
        # Read file
        with open(location) as f:
            content = f.read()
    else:
        raise exceptions.TutorError("No plugin found at {}".format(location))

    # Save file
    if not os.path.exists(plugins.DictPlugin.ROOT):
        os.makedirs(plugins.DictPlugin.ROOT)
    with open(plugin_path, "w", newline="\n") as f:
        f.write(content)
    fmt.echo_info("Plugin installed at {}".format(plugin_path))


def add_plugin_commands(command_group: click.Group) -> None:
    """
    Add commands provided by all plugins to the given command group. Each command is
    added with a name that is equal to the plugin name.
    """
    for plugin in plugins.iter_installed():
        if isinstance(plugin.command, click.Command):
            plugin.command.name = plugin.name
            command_group.add_command(plugin.command)


plugins_command.add_command(list_command)
plugins_command.add_command(enable)
plugins_command.add_command(disable)
plugins_command.add_command(printroot)
plugins_command.add_command(install)
