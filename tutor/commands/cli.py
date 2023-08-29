from __future__ import annotations

import sys
import typing as t

import appdirs
import click

from tutor import exceptions, fmt, hooks, utils
from tutor.__about__ import __app__, __version__
from tutor.commands.config import config_command
from tutor.commands.context import Context
from tutor.commands.dev import dev
from tutor.commands.images import images_command
from tutor.commands.k8s import k8s
from tutor.commands.local import local
from tutor.commands.mounts import mounts_command
from tutor.commands.plugins import plugins_command


def main() -> None:
    try:
        # Everyone on board
        # Note that this action should not be triggered in the module scope, because it
        # makes it difficult for tests to rollback changes.
        hooks.Actions.CORE_READY.do()
        cli()  # pylint: disable=no-value-for-parameter
    except KeyboardInterrupt:
        pass
    except exceptions.TutorError as e:
        fmt.echo_error(f"Error: {e.args[0]}")
        sys.exit(1)


class TutorCli(click.Group):
    """
    Dynamically load subcommands at runtime.

    This is necessary to load plugin subcommands, based on the list of enabled
    plugins (and thus of config.yml).
    Docs: https://click.palletsprojects.com/en/latest/commands/#custom-multi-commands
    """

    IS_ROOT_READY = False

    def get_command(
        self, ctx: click.Context, cmd_name: str
    ) -> t.Optional[click.Command]:
        """
        This is run when passing a command from the CLI. E.g: tutor config ...
        """
        self.ensure_plugins_enabled(ctx)
        return super().get_command(ctx, cmd_name=cmd_name)

    def list_commands(self, ctx: click.Context) -> list[str]:
        """
        This is run in the following cases:
        - shell autocompletion: tutor <tab>
        - print help: tutor, tutor -h
        """
        self.ensure_plugins_enabled(ctx)
        return super().list_commands(ctx)

    def ensure_plugins_enabled(self, ctx: click.Context) -> None:
        """
        We enable plugins as soon as possible to have access to commands.
        """
        if not "root" in ctx.params:
            # When generating docs, this function is called with empty args.
            # That's ok, we just ignore it.
            return
        if not self.IS_ROOT_READY:
            hooks.Actions.PROJECT_ROOT_READY.do(ctx.params["root"])
            self.IS_ROOT_READY = True
            for cmd in hooks.Filters.CLI_COMMANDS.iterate():
                self.add_command(cmd)


@click.group(
    cls=TutorCli,
    invoke_without_command=True,
    add_help_option=False,  # Context is incorrectly loaded when help option is automatically added
    help="Tutor is the Docker-based Open edX distribution designed for peace of mind.",
)
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
@click.option(
    "-h",
    "--help",
    "show_help",
    is_flag=True,
    help="Print this help",
)
@click.pass_context
def cli(context: click.Context, root: str, show_help: bool) -> None:
    if utils.is_root():
        fmt.echo_alert(
            "You are running Tutor as root. This is strongly not recommended. If you are doing this in order to access"
            " the Docker daemon, you should instead add your user to the 'docker' group. (see https://docs.docker.com"
            "/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user)"
        )
    context.obj = Context(root)
    context.help_option_names = ["-h", "--help"]
    if context.invoked_subcommand is None or show_help:
        click.echo(context.get_help())


@click.command(help="Print this help", name="help")
@click.pass_context
def help_command(context: click.Context) -> None:
    context.invoke(cli, show_help=True)


hooks.Filters.CLI_COMMANDS.add_items(
    [
        config_command,
        dev,
        help_command,
        images_command,
        k8s,
        local,
        mounts_command,
        plugins_command,
    ]
)


if __name__ == "__main__":
    main()
