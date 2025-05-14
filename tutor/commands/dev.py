from __future__ import annotations

import json
import typing as t
from urllib.parse import urlparse

import click

from tutor import config as tutor_config
from tutor import env as tutor_env
from tutor import fmt, hooks, utils
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


def parse_ports(docker_compose_ps_output: str) -> list[int]:
    """
    Extracts the ports from the docker ps output in json format.
    """
    exposed_ports = []
    for line in docker_compose_ps_output.splitlines():
        publishers = json.loads(line)["Publishers"]
        for publisher in publishers:
            port = publisher["PublishedPort"]
            if port:
                exposed_ports.append(port)
    return exposed_ports


@click.command(help="List the status of all services.")
@click.pass_obj
def hosts(context: compose.BaseComposeContext) -> None:
    config = tutor_config.load(context.root)
    docker_compose_ps_output = (
        context.job_runner(config)
        .docker_compose_output("ps", "--format", "json")
        .decode()
    )
    exposed_ports = parse_ports(docker_compose_ps_output)
    public_app_hosts: list[tuple[str, ...]] = [("URL", "STATUS")]
    for host in hooks.Filters.APP_PUBLIC_HOSTS.iterate(context.NAME):
        public_app_host = tutor_env.render_str(
            config, "{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://" + host
        )
        port = urlparse(public_app_host).port
        status_marker = " ✅" if port in exposed_ports else ""
        public_app_hosts.append((public_app_host, status_marker))
    fmt.echo(utils.format_table(public_app_hosts))


dev.add_command(hosts)


@hooks.Actions.COMPOSE_PROJECT_STARTED.add()
def _stop_on_local_start(root: str, config: Config, project_name: str) -> None:
    """
    Stop the dev platform as soon as a platform with a different project name is
    started.
    """
    runner = DevTaskRunner(root, config)
    if project_name != runner.project_name and runner.is_running():
        runner.docker_compose("stop")


@hooks.Filters.IMAGES_BUILD_REQUIRED.add()
def _build_openedx_dev_on_launch(
    image_names: list[str], context_name: t.Literal["local", "dev"]
) -> list[str]:
    if context_name == "dev":
        image_names.append("openedx-dev")
    return image_names


compose.add_commands(dev)
