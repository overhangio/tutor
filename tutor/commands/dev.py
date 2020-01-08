import click

from . import compose
from .context import Context
from .. import env as tutor_env
from .. import fmt
from .. import utils

# pylint: disable=too-few-public-methods
class DevContext(Context):
    @staticmethod
    def docker_compose(root, config, *command):
        return utils.docker_compose(
            "-f",
            tutor_env.pathjoin(root, "local", "docker-compose.yml"),
            "-f",
            tutor_env.pathjoin(root, "dev", "docker-compose.yml"),
            "--project-name",
            config["DEV_PROJECT_NAME"],
            *command,
        )


@click.group(help="Run Open edX platform with development settings")
@click.pass_context
def dev(context):
    context.obj = DevContext(context.obj.root)


@click.command(
    help="Run a development server", context_settings={"ignore_unknown_options": True},
)
@click.argument("options", nargs=-1, required=False)
@click.argument("service", type=click.Choice(["lms", "cms"]))
def runserver(options, service):
    port = 8000 if service == "lms" else 8001

    fmt.echo_info(
        "The {} service will be available at http://localhost:{}".format(service, port)
    )
    args = [
        "-p",
        "{port}:{port}".format(port=port),
        *options,
        service,
        "./manage.py",
        service,
        "runserver",
        "0.0.0.0:{}".format(port),
    ]
    compose.run.callback(args)


dev.add_command(runserver)
compose.add_commands(dev)
