from typing import List

import click

from .. import config as tutor_config
from .. import env as tutor_env
from .. import fmt
from ..types import Config, get_typed
from . import compose


class DevJobRunner(compose.ComposeJobRunner):
    def __init__(self, root: str, config: Config):
        """
        Load docker-compose files from dev/ and local/
        """
        super().__init__(root, config)
        self.project_name = get_typed(self.config, "DEV_PROJECT_NAME", str)
        self.docker_compose_files += [
            tutor_env.pathjoin(self.root, "local", "docker-compose.yml"),
            tutor_env.pathjoin(self.root, "dev", "docker-compose.yml"),
            tutor_env.pathjoin(self.root, "local", "docker-compose.override.yml"),
            tutor_env.pathjoin(self.root, "dev", "docker-compose.override.yml"),
        ]
        self.docker_compose_job_files += [
            tutor_env.pathjoin(self.root, "local", "docker-compose.jobs.yml"),
            tutor_env.pathjoin(self.root, "dev", "docker-compose.jobs.yml"),
            tutor_env.pathjoin(self.root, "local", "docker-compose.jobs.override.yml"),
            tutor_env.pathjoin(self.root, "dev", "docker-compose.jobs.override.yml"),
        ]


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
