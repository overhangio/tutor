import os

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
        args = []
        for folder in ["local", "dev"]:
            # Add docker-compose.yml and docker-compose.override.yml (if it exists)
            # from "local" and "dev" folders
            args += [
                "-f",
                tutor_env.pathjoin(root, folder, "docker-compose.yml"),
            ]
            override_path = tutor_env.pathjoin(
                root, folder, "docker-compose.override.yml"
            )
            if os.path.exists(override_path):
                args += ["-f", override_path]
        return utils.docker_compose(
            *args, "--project-name", config["DEV_PROJECT_NAME"], *command,
        )


@click.group(help="Run Open edX locally with development settings")
@click.pass_context
def dev(context):
    context.obj = DevContext(context.obj.root)


@click.command(
    help="Run a development server", context_settings={"ignore_unknown_options": True},
)
@click.argument("options", nargs=-1, required=False)
@click.argument("service")
def runserver(options, service):
    if service in ["lms", "cms"]:
        port = 8000 if service == "lms" else 8001
        fmt.echo_info(
            "The {} service will be available at http://localhost:{}".format(
                service, port
            )
        )
    args = ["--service-ports", *options, service]
    compose.run.callback(args)


dev.add_command(runserver)
compose.add_commands(dev)
