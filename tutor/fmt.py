import click

STDOUT = None


def title(text: str) -> str:
    indent = 8
    separator = "=" * (len(text) + 2 * indent)
    message = "{separator}\n{indent}{text}\n{separator}".format(
        separator=separator, indent=" " * indent, text=text
    )
    return click.style(message, fg="green")


def echo_info(text: str) -> None:
    echo(info(text))


def info(text: str) -> str:
    return click.style(text, fg="blue")


def error(text: str) -> str:
    return click.style(text, fg="red")


def echo_error(text: str) -> None:
    echo(error(text), err=True)


def command(text: str) -> str:
    return click.style(text, fg="magenta")


def question(text: str) -> str:
    return click.style(text, fg="yellow")


def echo_alert(text: str) -> None:
    echo_error(alert(text))


def alert(text: str) -> str:
    return click.style("⚠️  " + text, fg="yellow", bold=True)


def echo(text: str, err: bool = False) -> None:
    click.echo(text, file=STDOUT, err=err)
