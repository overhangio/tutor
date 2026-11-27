from __future__ import annotations

import click

from tutor import caddy, hooks
from tutor import config as tutor_config
from tutor import env as tutor_env
from tutor.commands import compose
from tutor.types import Config, get_typed


class LocalTaskRunner(compose.ComposeTaskRunner):
    def __init__(self, root: str, config: Config):
        """
        Load docker-compose files from local/.
        """
        super().__init__(root, config)
        self.project_name = get_typed(self.config, "LOCAL_PROJECT_NAME", str)
        self.docker_compose_files += [
            tutor_env.pathjoin(self.root, "local", "docker-compose.yml"),
            tutor_env.pathjoin(self.root, "local", "docker-compose.prod.yml"),
            tutor_env.pathjoin(self.root, "local", "docker-compose.override.yml"),
            tutor_env.pathjoin(self.root, "local", "docker-compose.prod.override.yml"),
        ]
        self.docker_compose_job_files += [
            tutor_env.pathjoin(self.root, "local", "docker-compose.jobs.yml"),
            tutor_env.pathjoin(self.root, "local", "docker-compose.jobs.override.yml"),
        ]


class LocalContext(compose.BaseComposeContext):
    NAME = "local"
    OPENEDX_SERVICES = ["lms", "cms", "lms-worker", "cms-worker"]

    def job_runner(self, config: Config) -> LocalTaskRunner:
        return LocalTaskRunner(self.root, config)


@click.group(help="Run Open edX locally with docker-compose")
@click.pass_context
def local(context: click.Context) -> None:
    context.obj = LocalContext(context.obj.root)


@hooks.Actions.COMPOSE_PROJECT_STARTED.add()
def _stop_on_dev_start(root: str, config: Config, project_name: str) -> None:
    """
    Stop the local platform as soon as a platform with a different project name is
    started.
    """
    runner = LocalTaskRunner(root, config)
    if project_name != runner.project_name and runner.is_running():
        runner.docker_compose("stop")


@click.command(
    name="https-certificates",
    short_help=caddy.COMMAND_SHORT_HELP,
    help=caddy.COMMAND_HELP,
)
@click.pass_obj
def https_certificates(context: LocalContext) -> None:
    config = tutor_config.load(context.root)
    runner = context.job_runner(config)

    def run_script(script: str) -> bytes:
        return runner.docker_compose_output(
            "exec", "-T", "caddy", "sh", "-c", script, hidden=script
        )

    caddy.print_certificates(
        config,
        run_script,
        start_command="tutor local start -d caddy",
        restart_command="tutor local reboot -d caddy",
        logs_command="tutor local logs --tail=100 caddy",
    )


compose.add_commands(local)
local.add_command(https_certificates)
