import click


def title(text):
    indent = 8
    separator = "=" * (len(text) + 2 * indent)
    message = "{separator}\n{indent}{text}\n{separator}".format(
        separator=separator, indent=" " * indent, text=text
    )
    return click.style(message, fg="green")


def echo_info(text):
    echo(info(text))


def info(text):
    return click.style(text, fg="blue")


def error(text):
    return click.style(text, fg="red")


def echo_error(text):
    echo(error(text), err=True)


def command(text):
    return click.style(text, fg="magenta")


def question(text):
    return click.style(text, fg="yellow")


def echo_alert(text):
    echo(alert(text))


def alert(text):
    return click.style("⚠️  " + text, fg="yellow", bold=True)


def echo(text, err=False):
    click.echo(text, err=err)
