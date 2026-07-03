from __future__ import annotations

import sys
import typing as t

import appdirs
import click

from tutor import config, exceptions, fmt, hooks, utils
from tutor.__about__ import __app__, __version__
from tutor.commands.config import config_command
from tutor.commands.context import Context
from tutor.commands.dev import dev
from tutor.commands.images import images_command
from tutor.commands.k8s import k8s
from tutor.commands.local import local
from tutor.commands.mounts import mounts_command
from tutor.commands.plugins import plugins_command
from tutor.types import Config


def main() -> None:
    try:
        # Everyone on board
        # Note that this action should not be triggered in the module scope, because it
        # makes it difficult for tests to rollback changes.
        hooks.Actions.CORE_READY.do()
        cli()
    except KeyboardInterrupt:
        pass
    except exceptions.TutorError as e:
        fmt.echo_error(f"Error: {e.args[0]}")
        sys.exit(1)


def check_plugin_errors(context: Context, prev_config: Config) -> None:
    """
    Check for plugin loading errors and exit with code 1 if any were found,
    unless --ignore-plugin-errors is set or if the config file was changed.

    In case the config file was changed, the errors might no longer be valid
    with the new configuration, so warn the user instead.
    """
    errors: list[tuple[str, str]] = list(hooks.Filters.PLUGIN_ERRORS.iterate())
    ignore = context.ignore_plugin_errors
    if not errors:
        return
    has_config_changed = config.get_user(context.root) != prev_config
    for plugin, error in errors:
        if has_config_changed or ignore:
            fmt.echo_alert(f"Failed to enable plugin '{plugin}': {error}")
        else:
            fmt.echo_error(f"Plugin '{plugin}' failed to load: {error}")
    if has_config_changed:
        fmt.echo_alert(
            "The Config file was changed by running this command "
            "so the above errors might no longer be valid. \n"
            "Please run 'tutor config save' to check if the errors persist."
        )
    # Only exit with an error code if:
    #   - errors are not being ignored
    #   - the config file hasn't changed
    #   - no exception has already been raised that would return its own error codek
    if ignore or has_config_changed:
        return
    match sys.exc_info()[1]:
        case None:
            sys.exit(1)
        case SystemExit(code=code) | click.exceptions.Exit(exit_code=code) if code == 0:
            sys.exit(1)
        case _:
            return


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
        if "root" not in ctx.params:
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
@click.option(
    "--ignore-plugin-errors",
    "ignore_plugin_errors",
    is_flag=True,
    default=False,
    help="Continue running even if plugin loading fails",
)
@click.pass_context
def cli(
    context: click.Context, root: str, show_help: bool, ignore_plugin_errors: bool
) -> None:
    if utils.is_root():
        fmt.echo_alert(
            "You are running Tutor as root. This is strongly not recommended. If you are doing this in order to access"
            " the Docker daemon, you should instead add your user to the 'docker' group. (see https://docs.docker.com"
            "/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user)"
        )
    context.obj = Context(root, ignore_plugin_errors)
    context.help_option_names = ["-h", "--help"]
    # If showing help, don't check plugin errors
    is_showing_help = show_help or context.invoked_subcommand in (
        None,
        help_command.name,
    )
    if not is_showing_help:
        init_config = config.get_user(root)
        context.call_on_close(lambda: check_plugin_errors(context.obj, init_config))
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
