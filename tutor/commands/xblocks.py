import click
from tutor import fmt, utils
from tutor.commands.context import Context
from tutor import config as tutor_config


@click.group(
    name="xblocks",
    short_help="Manage xblocks",
)
def xblocks_command() -> None:
    """"""

@click.command(name="list")
@click.pass_obj
def list_command(context: Context) -> None:
    """
    List installed xblocks.
    """
    xblocks_table: list[tuple[str, ...]] = [("NAME", "STATUS")]
    config = tutor_config.load(context.root)
    xblocks = config["INSTALLED_XBLOCKS"]
    for xblock in xblocks:
            xblocks_table.append((xblock, "Not Implemented Yet"))
    fmt.echo(utils.format_table(xblocks_table))

xblocks_command.add_command(list_command)