from typing import List

import click

from .. import config as tutor_config
from .. import env, exceptions, fmt
from .. import interactive as interactive_config
from .. import serialize
from ..types import Config
from .context import Context


@click.group(
    name="config",
    short_help="Configure Open edX",
    help="""Configure Open edX and store configuration values in $TUTOR_ROOT/config.yml""",
)
def config_command() -> None:
    pass


@click.command(help="Create and save configuration interactively")
@click.option("-i", "--interactive", is_flag=True, help="Run interactively")
@click.option(
    "-s",
    "--set",
    "set_vars",
    type=serialize.YamlParamType(),
    multiple=True,
    metavar="KEY=VAL",
    help="Set a configuration value (can be used multiple times)",
)
@click.option(
    "-U",
    "--unset",
    "unset_vars",
    multiple=True,
    help="Remove a configuration value (can be used multiple times)",
)
@click.option(
    "-e", "--env-only", "env_only", is_flag=True, help="Skip updating config.yaml"
)
@click.pass_obj
def save(
    context: Context,
    interactive: bool,
    set_vars: Config,
    unset_vars: List[str],
    env_only: bool,
) -> None:
    config = tutor_config.load_minimal(context.root)
    if interactive:
        interactive_config.ask_questions(config)
    if set_vars:
        for key, value in dict(set_vars).items():
            config[key] = env.render_unknown(config, value)
    for key in unset_vars:
        config.pop(key, None)
    if not env_only:
        tutor_config.save_config_file(context.root, config)

    # Reload configuration, without version checking
    config = tutor_config.load_full(context.root)
    env.save(context.root, config)


@click.command(help="Print the project root")
@click.pass_obj
def printroot(context: Context) -> None:
    click.echo(context.root)


@click.command(help="Print a configuration value")
@click.argument("key")
@click.pass_obj
def printvalue(context: Context, key: str) -> None:
    config = tutor_config.load(context.root)
    try:
        # Note that this will incorrectly print None values
        fmt.echo(str(config[key]))
    except KeyError as e:
        raise exceptions.TutorError(f"Missing configuration value: {key}") from e


config_command.add_command(save)
config_command.add_command(printroot)
config_command.add_command(printvalue)
