import click

from tutor import config as tutor_config
from tutor import fmt
from tutor.commands.context import Context


@click.group(
    name="packages",
    short_help="Manage packages",
)
def packages_command() -> None:
    """ """


@click.command(name="list")
@click.pass_obj
def list_command(context: Context) -> None:
    """
    List installed persistent packages.

    Entries will be fetched from the `PERSISTENT_PIP_PACKAGES` config setting.
    """

    config = tutor_config.load(context.root)
    packages = [package for package in config["PERSISTENT_PIP_PACKAGES"]]
    fmt.echo(sorted(packages))


packages_command.add_command(list_command)
