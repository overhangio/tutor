from __future__ import annotations

import typing as t

import click

from tutor import env as tutor_env
from tutor import hooks
from tutor.commands import compose
from tutor.types import Config, get_typed


class DevTaskRunner(compose.ComposeTaskRunner):
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
    NAME = "dev"

    def job_runner(self, config: Config) -> DevTaskRunner:
        return DevTaskRunner(self.root, config)


@click.group(help="Run Open edX locally with development settings")
@click.pass_context
def dev(context: click.Context) -> None:
    context.obj = DevContext(context.obj.root)


@hooks.Actions.COMPOSE_PROJECT_STARTED.add()
def _stop_on_local_start(root: str, config: Config, project_name: str) -> None:
    """
    Stop the dev platform as soon as a platform with a different project name is
    started.
    """
    runner = DevTaskRunner(root, config)
    if project_name != runner.project_name:
        runner.docker_compose("stop")


@hooks.Filters.IMAGES_BUILD_REQUIRED.add()
def _build_openedx_dev_on_launch(
    image_names: list[str], context_name: t.Literal["local", "dev"]
) -> list[str]:
    if context_name == "dev":
        image_names.append("openedx-dev")
    return image_names


compose.add_commands(dev)
