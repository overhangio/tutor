import os
from typing import List

import click

from .. import config as tutor_config
from .. import env as tutor_env
from .. import fmt
from ..types import Config
from .. import utils
from . import compose


class DevJobRunner(compose.ComposeJobRunner):
    def docker_compose(self, *command: str) -> int:
        """
        Run docker-compose with dev arguments.
        """
        args = []
        for folder in ["local", "dev"]:
            # Add docker-compose.yml and docker-compose.override.yml (if it exists)
            # from "local" and "dev" folders (but not docker-compose.prod.yml)
            args += [
                "-f",
                tutor_env.pathjoin(self.root, folder, "docker-compose.yml"),
            ]
            override_path = tutor_env.pathjoin(
                self.root, folder, "docker-compose.override.yml"
            )
            if os.path.exists(override_path):
                args += ["-f", override_path]
        return utils.docker_compose(
            *args,
            "--project-name",
            str(self.config["DEV_PROJECT_NAME"]),
            *command,
        )


class DevContext(compose.BaseComposeContext):
    def job_runner(self, config: Config) -> DevJobRunner:
        return DevJobRunner(self.root, config)


@click.group(help="Run Open edX locally with development settings")
@click.pass_context
def dev(context: click.Context) -> None:
    context.obj = DevContext(context.obj.root)


@click.command(
    help="Run a development server",
    context_settings={"ignore_unknown_options": True},
)
@click.argument("options", nargs=-1, required=False)
@click.argument("service")
@click.pass_context
def runserver(context: click.Context, options: List[str], service: str) -> None:
    config = tutor_config.load(context.obj.root)
    if service in ["lms", "cms"]:
        port = 8000 if service == "lms" else 8001
        host = config["LMS_HOST"] if service == "lms" else config["CMS_HOST"]
        fmt.echo_info(
            "The {} service will be available at http://{}:{}".format(
                service, host, port
            )
        )
    args = ["--service-ports", *options, service]
    context.invoke(compose.run, args=args)


dev.add_command(runserver)
compose.add_commands(dev)
