import click

from . import config as tutor_config
from .. import opts
from .. import plugins


@click.group(
    name="plugins",
    short_help="Manage Tutor plugins",
    help="Manage Tutor plugins to add new features and customize your Open edX platform",
)
def plugins_command():
    pass


@click.command(name="list", help="List installed plugins")
@opts.root
def list_command(root):
    config = tutor_config.load(root)
    for name, _ in plugins.iter_installed():
        status = "" if plugins.is_enabled(config, name) else " (disabled)"
        print("{plugin}{status}".format(plugin=name, status=status))


@click.command(help="Enable a plugin")
@click.argument("plugin")
@opts.root
def enable(plugin, root):
    config = tutor_config.load(root)
    plugins.enable(config, plugin)
    tutor_config.save_config(root, config)
    tutor_config.save(root, silent=True)


@click.command(help="Disable a plugin")
@opts.root
def disable(root):
    pass


plugins_command.add_command(list_command)
plugins_command.add_command(enable)
plugins_command.add_command(disable)
