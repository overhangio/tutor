import click
import click_repl


@click.command(
    short_help="Interactive shell",
    help="Launch an interactive shell for launching Tutor commands",
)
def ui() -> None:
    click.echo(
        """Welcome to the Tutor interactive shell UI!
Type "help" to view all available commands.
Type "local quickstart" to configure and launch a new platform from scratch.
Type <ctrl-d> to exit."""
    )
    while True:
        try:
            click_repl.repl(click.get_current_context())
            return  # this happens on a ctrl+d
        except Exception:  # pylint: disable=broad-except
            pass
