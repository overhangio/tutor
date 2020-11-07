#! /usr/bin/env python3
import sys

import appdirs
import click
import click_repl

from .android import android
from .config import config_command
from .context import Context
from .dev import dev
from .images import images_command
from .k8s import k8s
from .local import local
from .plugins import plugins_command, add_plugin_commands
from .ui import ui
from .webui import webui
from ..__about__ import __version__
from .. import exceptions
from .. import fmt
from .. import utils


def main():
    try:
        click_repl.register_repl(cli, name="ui")
        cli.add_command(images_command)
        cli.add_command(config_command)
        cli.add_command(local)
        cli.add_command(dev)
        cli.add_command(android)
        cli.add_command(k8s)
        cli.add_command(ui)
        cli.add_command(webui)
        cli.add_command(print_help)
        cli.add_command(plugins_command)
        add_plugin_commands(cli)
        cli()  # pylint: disable=no-value-for-parameter
    except exceptions.TutorError as e:
        fmt.echo_error("Error: {}".format(e.args[0]))
        sys.exit(1)


@click.group(context_settings={"help_option_names": ["-h", "--help", "help"]})
@click.version_option(version=__version__)
@click.option(
    "-r",
    "--root",
    envvar="TUTOR_ROOT",
    default=appdirs.user_data_dir(appname="tutor"),
    show_default=True,
    type=click.Path(resolve_path=True),
    help="Root project directory (environment variable: TUTOR_ROOT)",
)
@click.pass_context
def cli(context, root):
    if utils.get_user_id() == 0:
        fmt.echo_alert(
            "You are running Tutor as root. This is strongly not recommended. If you are doing this in order to access"
            " the Docker daemon, you should instead add your user to the 'docker' group. (see https://docs.docker.com"
            "/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user)"
        )
    context.obj = Context(root)


@click.command(help="Print this help", name="help")
def print_help():
    with click.Context(cli) as context:
        click.echo(cli.get_help(context))


if __name__ == "__main__":
    main()
