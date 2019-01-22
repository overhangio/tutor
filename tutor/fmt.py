import click

def title(text):
    indent = 8
    separator = "=" * (len(text) + 2 * indent)
    message = "{separator}\n{indent}{text}\n{separator}".format(
        separator=separator,
        indent=" " * indent,
        text=text,
    )
    return click.style(message, fg="green")

def info(text):
    return click.style(text, fg="blue")

def error(text):
    return click.style(text, fg="red")

def command(text):
    return click.style(text, fg="magenta")

def question(text):
    return click.style(text, fg="yellow")

def alert(text):
    return click.style("⚠️  " + text, fg="yellow", bold=True)
