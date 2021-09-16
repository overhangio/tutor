#! /usr/bin/env python3
import sys

import appdirs
import click

from .config import config_command
from .context import Context
from .dev import dev
from .images import images_command
from .k8s import k8s
from .local import local
from .plugins import plugins_command, add_plugin_commands
from ..__about__ import __version__, __app__
from .. import exceptions
from .. import fmt
from .. import utils


def main() -> None:
    try:
        cli.add_command(images_command)
        cli.add_command(config_command)
        cli.add_command(local)
        cli.add_command(dev)
        cli.add_command(k8s)
        cli.add_command(print_help)
        cli.add_command(plugins_command)
        add_plugin_commands(cli)
        cli()  # pylint: disable=no-value-for-parameter
    except KeyboardInterrupt:
        pass
    except exceptions.TutorError as e:
        fmt.echo_error("Error: {}".format(e.args[0]))
        sys.exit(1)


@click.group(context_settings={"help_option_names": ["-h", "--help", "help"]})
@click.version_option(version=__version__)
@click.option(
    "-r",
    "--root",
    envvar="TUTOR_ROOT",
    default=appdirs.user_data_dir(appname=__app__),
    show_default=True,
    type=click.Path(resolve_path=True),
    help="Root project directory (environment variable: TUTOR_ROOT)",
)
@click.pass_context
def cli(context: click.Context, root: str) -> None:
    if utils.is_root():
        fmt.echo_alert(
            "You are running Tutor as root. This is strongly not recommended. If you are doing this in order to access"
            " the Docker daemon, you should instead add your user to the 'docker' group. (see https://docs.docker.com"
            "/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user)"
        )
    context.obj = Context(root)


@click.command(help="Print this help", name="help")
def print_help() -> None:
    context = click.Context(cli)
    click.echo(cli.get_help(context))


if __name__ == "__main__":
    main()
