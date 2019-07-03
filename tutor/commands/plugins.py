import os
import shutil
import click

from .. import config as tutor_config
from .. import env as tutor_env
from .. import fmt
from .. import opts
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
@opts.root
def list_command(root):
    config = tutor_config.load_user(root)
    for name, _ in plugins.iter_installed():
        status = "" if plugins.is_enabled(config, name) else " (disabled)"
        print("{plugin}{status}".format(plugin=name, status=status))


@click.command(help="Enable a plugin")
@opts.root
@click.argument("plugin")
def enable(root, plugin):
    config = tutor_config.load_user(root)
    plugins.enable(config, plugin)
    tutor_config.save(root, config)
    fmt.echo_info(
        "You should now re-generate your environment with `tutor config save`."
    )


@click.command(help="Disable a plugin")
@opts.root
@click.argument("plugin")
def disable(root, plugin):
    config = tutor_config.load_user(root)
    plugins.disable(config, plugin)
    tutor_config.save(root, config)

    plugin_dir = tutor_env.pathjoin(root, "plugins", plugin)
    if os.path.exists(plugin_dir):
        shutil.rmtree(plugin_dir)

    fmt.echo_info(
        "You should now re-generate your environment with `tutor config save`."
    )


plugins_command.add_command(list_command)
plugins_command.add_command(enable)
plugins_command.add_command(disable)
