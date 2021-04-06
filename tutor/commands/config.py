from typing import List

import click

from .. import config as tutor_config
from .. import env
from .. import exceptions
from .. import fmt
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
@click.pass_obj
def save(
    context: Context, interactive: bool, set_vars: Config, unset_vars: List[str]
) -> None:
    config, defaults = interactive_config.load_all(
        context.root, interactive=interactive
    )
    if set_vars:
        tutor_config.merge(config, dict(set_vars), force=True)
    for key in unset_vars:
        config.pop(key, None)
    tutor_config.save_config_file(context.root, config)
    tutor_config.merge(config, defaults)
    env.save(context.root, config)


@click.command(help="Render a template folder with eventual extra configuration files")
@click.option(
    "-x",
    "--extra-config",
    "extra_configs",
    multiple=True,
    type=click.Path(exists=True, resolve_path=True, dir_okay=False),
    help="Load extra configuration file (can be used multiple times)",
)
@click.argument("src", type=click.Path(exists=True, resolve_path=True))
@click.argument("dst")
@click.pass_obj
def render(context: Context, extra_configs: List[str], src: str, dst: str) -> None:
    config = tutor_config.load(context.root)
    for extra_config in extra_configs:
        tutor_config.merge(
            config, tutor_config.load_config_file(extra_config), force=True
        )

    renderer = env.Renderer(config, [src])
    renderer.render_all_to(dst)
    fmt.echo_info("Templates rendered to {}".format(dst))


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
        raise exceptions.TutorError(
            "Missing configuration value: {}".format(key)
        ) from e


config_command.add_command(save)
config_command.add_command(render)
config_command.add_command(printroot)
config_command.add_command(printvalue)
