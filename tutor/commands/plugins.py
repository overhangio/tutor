import os
import shutil
import click

from .. import config as tutor_config
from .. import env as tutor_env
from .. import fmt
from .. import plugins


@click.group(
    name="plugins",
    short_help="Manage Tutor plugins",
    help="Manage Tutor plugins to add new features and customize your Open edX platform",
)
def plugins_command():
    """
    All plugin commands should work even if there is no existing config file. This is
    because users might enable plugins prior to configuration or environment generation.
    """


@click.command(name="list", help="List installed plugins")
@click.pass_obj
def list_command(context):
    config = tutor_config.load_user(context.root)
    for plugin in plugins.iter_installed():
        status = "" if plugins.is_enabled(config, plugin.name) else " (disabled)"
        print(
            "{plugin}@{version}{status}".format(
                plugin=plugin.name, status=status, version=plugin.version
            )
        )


@click.command(help="Enable a plugin")
@click.argument("plugin_names", metavar="plugin", nargs=-1)
@click.pass_obj
def enable(context, plugin_names):
    config = tutor_config.load_user(context.root)
    for plugin in plugin_names:
        plugins.enable(config, plugin)
        fmt.echo_info("Plugin {} enabled".format(plugin))
    tutor_config.save(context.root, config)
    fmt.echo_info(
        "You should now re-generate your environment with `tutor config save`."
    )


@click.command(help="Disable a plugin")
@click.argument("plugin_names", metavar="plugin", nargs=-1)
@click.pass_obj
def disable(context, plugin_names):
    config = tutor_config.load_user(context.root)
    for plugin in plugin_names:
        plugins.disable(config, plugin)

        plugin_dir = tutor_env.pathjoin(context.root, "plugins", plugin)
        if os.path.exists(plugin_dir):
            shutil.rmtree(plugin_dir)
        fmt.echo_info("Plugin {} disabled".format(plugin))

    tutor_config.save(context.root, config)
    fmt.echo_info(
        "You should now re-generate your environment with `tutor config save`."
    )


def add_plugin_commands(command_group):
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
