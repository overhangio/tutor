import click

from .. import config as tutor_config
from .. import env
from .. import exceptions
from .. import fmt
from .. import interactive
from .. import opts


@click.group(
    name="config",
    short_help="Configure Open edX",
    help="""Configure Open edX and store configuration values in $TUTOR_ROOT/config.yml""",
)
def config_command():
    pass


@click.command(help="Create and save configuration interactively")
@opts.root
@click.option("-y", "--yes", "silent1", is_flag=True, help="Run non-interactively")
@click.option("--silent", "silent2", is_flag=True, hidden=True)
@opts.key_value
def save(root, silent1, silent2, set_):
    silent = silent1 or silent2
    config, defaults = interactive.load_all(root, silent=silent)
    if set_:
        tutor_config.merge(config, dict(set_), force=True)
    tutor_config.save(root, config)
    tutor_config.merge(config, defaults)
    env.save(root, config)


@click.command(help="Print the project root")
@opts.root
def printroot(root):
    click.echo(root)


@click.command(help="Print a configuration value")
@opts.root
@click.argument("key")
def printvalue(root, key):
    config = tutor_config.load(root)
    try:
        fmt.echo(config[key])
    except KeyError:
        raise exceptions.TutorError("Missing configuration value: {}".format(key))


config_command.add_command(save)
config_command.add_command(printroot)
config_command.add_command(printvalue)
