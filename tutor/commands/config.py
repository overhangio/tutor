import click

from .. import config
from .. import exceptions
from .. import fmt
from .. import opts


@click.group(
    name="config",
    short_help="Configure Open edX",
    help="""Configure Open edX and store configuration values in $TUTOR_ROOT/config.yml""",
)
def config_command():
    pass


@click.command(name="save", help="Create and save configuration interactively")
@opts.root
@click.option("-y", "--yes", "silent1", is_flag=True, help="Run non-interactively")
@click.option("--silent", "silent2", is_flag=True, hidden=True)
@opts.key_value
def save_command(root, silent1, silent2, set_):
    silent = silent1 or silent2
    config.save(root, silent=silent, keyvalues=set_)


@click.command(help="Print the project root")
@opts.root
def printroot(root):
    click.echo(root)


@click.command(help="Print a configuration value")
@opts.root
@click.argument("key")
def printvalue(root, key):
    local = config.load(root)
    try:
        fmt.echo(local[key])
    except KeyError:
        raise exceptions.TutorError("Missing configuration value: {}".format(key))


config_command.add_command(save_command)
config_command.add_command(printroot)
config_command.add_command(printvalue)
