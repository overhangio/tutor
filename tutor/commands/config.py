import click

from .. import config as tutor_config
from .. import env
from .. import exceptions
from .. import fmt
from .. import interactive as interactive_config
from .. import serialize


@click.group(
    name="config",
    short_help="Configure Open edX",
    help="""Configure Open edX and store configuration values in $TUTOR_ROOT/config.yml""",
)
def config_command():
    pass


class YamlParamType(click.ParamType):
    name = "yaml"

    def convert(self, value, param, ctx):
        try:
            k, v = value.split("=")
        except ValueError:
            self.fail("'{}' is not of the form 'key=value'.".format(value), param, ctx)
        return k, serialize.parse(v)


@click.command(help="Create and save configuration interactively")
@click.option("-i", "--interactive", is_flag=True, help="Run interactively")
@click.option(
    "-s",
    "--set",
    "set_",
    type=YamlParamType(),
    multiple=True,
    metavar="KEY=VAL",
    help="Set a configuration value (can be used multiple times)",
)
@click.option(
    "-U",
    "--unset",
    multiple=True,
    help="Remove a configuration value (can be used multiple times)",
)
@click.pass_obj
def save(context, interactive, set_, unset):
    config, defaults = interactive_config.load_all(
        context.root, interactive=interactive
    )
    if set_:
        tutor_config.merge(config, dict(set_), force=True)
    for key in unset:
        config.pop(key, None)
    tutor_config.save(context.root, config)
    tutor_config.merge(config, defaults)
    env.save(context.root, config)


@click.command(help="Print the project root")
@click.pass_obj
def printroot(context):
    click.echo(context.root)


@click.command(help="Print a configuration value")
@click.argument("key")
@click.pass_obj
def printvalue(context, key):
    config = tutor_config.load(context.root)
    try:
        fmt.echo(config[key])
    except KeyError:
        raise exceptions.TutorError("Missing configuration value: {}".format(key))


config_command.add_command(save)
config_command.add_command(printroot)
config_command.add_command(printvalue)
