#! /usr/bin/env python3
import sys

import click
import click_repl

from .__about__ import __version__
from .android import android
from .config import config
from .dev import dev
from .images import images
from .k8s import k8s
from .local import local
from .ui import ui
from .webui import webui
from . import exceptions
from . import fmt


def main():
    try:
        cli()
    except exceptions.TutorError as e:
        sys.stderr.write(fmt.error("Error: {}\n".format(e.args[0])))
        sys.exit(1)

@click.group(context_settings={'help_option_names': ['-h', '--help', 'help']})
@click.version_option(version=__version__)
def cli():
    pass

@click.command(
    help="Print this help",
    name="help",
)
def print_help():
    with click.Context(cli) as context:
        click.echo(cli.get_help(context))

click_repl.register_repl(cli, name="ui")
cli.add_command(images)
cli.add_command(config)
cli.add_command(local)
cli.add_command(dev)
cli.add_command(android)
cli.add_command(k8s)
cli.add_command(ui)
cli.add_command(webui)
cli.add_command(print_help)

if __name__ == "__main__":
    main()
