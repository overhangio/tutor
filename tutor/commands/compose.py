import os
from typing import Callable, List

import click
from mypy_extensions import VarArg

from .. import bindmounts
from .. import config as tutor_config
from .. import env as tutor_env
from ..exceptions import TutorError
from .. import fmt
from .. import jobs
from ..types import Config
from .. import utils
from .context import Context


class ComposeJobRunner(jobs.BaseJobRunner):
    def __init__(
        self,
        root: str,
        config: Config,
        docker_compose_func: Callable[[str, Config, VarArg(str)], int],
    ):
        super().__init__(root, config)
        self.docker_compose_func = docker_compose_func

    def run_job(self, service: str, command: str) -> int:
        """
        Run the "{{ service }}-job" service from local/docker-compose.jobs.yml with the
        specified command. For backward-compatibility reasons, if the corresponding
        service does not exist, run the service from good old regular
        docker-compose.yml.
        """
        run_command = [
            "-f",
            tutor_env.pathjoin(self.root, "local", "docker-compose.jobs.yml"),
        ]
        override_path = tutor_env.pathjoin(
            self.root, "local", "docker-compose.jobs.override.yml"
        )
        if os.path.exists(override_path):
            run_command += ["-f", override_path]
        run_command += ["run", "--rm"]
        if not utils.is_a_tty():
            run_command += ["-T"]
        job_service_name = "{}-job".format(service)
        return self.docker_compose_func(
            self.root,
            self.config,
            *run_command,
            job_service_name,
            "sh",
            "-e",
            "-c",
            command,
        )


@click.command(
    short_help="Run all or a selection of services.",
    help="Run all or a selection of services. Docker images will be rebuilt where necessary.",
)
@click.option("-d", "--detach", is_flag=True, help="Start in daemon mode")
@click.argument("services", metavar="service", nargs=-1)
@click.pass_obj
def start(context: Context, detach: bool, services: List[str]) -> None:
    command = ["up", "--remove-orphans"]
    if detach:
        command.append("-d")

    config = tutor_config.load(context.root)
    # Rebuild Docker images with a `build: ...` context.
    context.docker_compose(context.root, config, "build")
    # Start services
    context.docker_compose(context.root, config, *command, *services)


@click.command(help="Stop a running platform")
@click.argument("services", metavar="service", nargs=-1)
@click.pass_obj
def stop(context: Context, services: List[str]) -> None:
    config = tutor_config.load(context.root)
    context.docker_compose(context.root, config, "stop", *services)


@click.command(
    short_help="Reboot an existing platform",
    help="This is more than just a restart: with reboot, the platform is fully stopped before being restarted again",
)
@click.option("-d", "--detach", is_flag=True, help="Start in daemon mode")
@click.argument("services", metavar="service", nargs=-1)
@click.pass_context
def reboot(context: click.Context, detach: bool, services: List[str]) -> None:
    context.invoke(stop, services=services)
    context.invoke(start, detach=detach, services=services)


@click.command(
    short_help="Restart some components from a running platform.",
    help="""Specify 'openedx' to restart the lms, cms and workers, or 'all' to
restart all services. Note that this performs a 'docker-compose restart', so new images
may not be taken into account. It is useful for reloading settings, for instance. To
fully stop the platform, use the 'reboot' command.""",
)
@click.argument("services", metavar="service", nargs=-1)
@click.pass_obj
def restart(context: Context, services: List[str]) -> None:
    config = tutor_config.load(context.root)
    command = ["restart"]
    if "all" in services:
        pass
    else:
        for service in services:
            if service == "openedx":
                if config["RUN_LMS"]:
                    command += ["lms", "lms-worker"]
                if config["RUN_CMS"]:
                    command += ["cms", "cms-worker"]
            else:
                command.append(service)
    context.docker_compose(context.root, config, *command)


@click.command(help="Initialise all applications")
@click.option("-l", "--limit", help="Limit initialisation to this service or plugin")
@click.pass_obj
def init(context: Context, limit: str) -> None:
    config = tutor_config.load(context.root)
    runner = ComposeJobRunner(context.root, config, context.docker_compose)
    jobs.initialise(runner, limit_to=limit)


@click.command(help="Create an Open edX user and interactively set their password")
@click.option("--superuser", is_flag=True, help="Make superuser")
@click.option("--staff", is_flag=True, help="Make staff user")
@click.option(
    "-p",
    "--password",
    help="Specify password from the command line. If undefined, you will be prompted to input a password",
)
@click.argument("name")
@click.argument("email")
@click.pass_obj
def createuser(
    context: Context, superuser: str, staff: bool, password: str, name: str, email: str
) -> None:
    config = tutor_config.load(context.root)
    runner = ComposeJobRunner(context.root, config, context.docker_compose)
    command = jobs.create_user_command(superuser, staff, name, email, password=password)
    runner.run_job("lms", command)


@click.command(
    help="Assign a theme to the LMS and the CMS. To reset to the default theme , use 'default' as the theme name."
)
@click.option(
    "-d",
    "--domain",
    "domains",
    multiple=True,
    help=(
        "Limit the theme to these domain names. By default, the theme is "
        "applied to the LMS and the CMS, both in development and production mode"
    ),
)
@click.argument("theme_name")
@click.pass_obj
def settheme(context: Context, domains: List[str], theme_name: str) -> None:
    config = tutor_config.load(context.root)
    runner = ComposeJobRunner(context.root, config, context.docker_compose)
    domains = domains or jobs.get_all_openedx_domains(config)
    jobs.set_theme(theme_name, domains, runner)


@click.command(help="Import the demo course")
@click.pass_obj
def importdemocourse(context: Context) -> None:
    config = tutor_config.load(context.root)
    runner = ComposeJobRunner(context.root, config, context.docker_compose)
    fmt.echo_info("Importing demo course")
    jobs.import_demo_course(runner)


@click.command(
    short_help="Run a command in a new container",
    help=(
        "Run a command in a new container. This is a wrapper around `docker-compose run`. Any option or argument passed"
        " to this command will be forwarded to docker-compose. Thus, you may use `-v` or `-p` to mount volumes and"
        " expose ports."
    ),
    context_settings={"ignore_unknown_options": True},
)
@click.argument("args", nargs=-1, required=True)
@click.pass_context
def run(context: click.Context, args: List[str]) -> None:
    extra_args = ["--rm"]
    if not utils.is_a_tty():
        extra_args.append("-T")
    context.invoke(dc_command, command="run", args=[*extra_args, *args])


@click.command(
    name="bindmount",
    help="Copy the contents of a container directory to a ready-to-bind-mount host directory",
)
@click.argument(
    "service",
)
@click.argument("path")
@click.pass_obj
def bindmount_command(context: Context, service: str, path: str) -> None:
    config = tutor_config.load(context.root)
    host_path = bindmounts.create(
        context.root, config, context.docker_compose, service, path
    )
    fmt.echo_info(
        "Bind-mount volume created at {}. You can now use it in all `local` and `dev` commands with the `--volume={}` option.".format(
            host_path, path
        )
    )


@click.command(
    short_help="Run a command in a running container",
    help=(
        "Run a command in a running container. This is a wrapper around `docker-compose exec`. Any option or argument"
        " passed to this command will be forwarded to docker-compose. Thus, you may use `-e` to manually define"
        " environment variables."
    ),
    context_settings={"ignore_unknown_options": True},
    name="exec",
)
@click.argument("args", nargs=-1, required=True)
@click.pass_context
def execute(context: click.Context, args: List[str]) -> None:
    context.invoke(dc_command, command="exec", args=args)


@click.command(
    short_help="View output from containers",
    help="View output from containers. This is a wrapper around `docker-compose logs`.",
)
@click.option("-f", "--follow", is_flag=True, help="Follow log output")
@click.option("--tail", type=int, help="Number of lines to show from each container")
@click.argument("service", nargs=-1)
@click.pass_context
def logs(context: click.Context, follow: bool, tail: bool, service: str) -> None:
    args = []
    if follow:
        args.append("--follow")
    if tail is not None:
        args += ["--tail", str(tail)]
    args += service
    context.invoke(dc_command, command="logs", args=args)


@click.command(
    short_help="Direct interface to docker-compose.",
    help=(
        "Direct interface to docker-compose. This is a wrapper around `docker-compose`. Most commands, options and"
        " arguments passed to this command will be forwarded as-is to docker-compose."
    ),
    context_settings={"ignore_unknown_options": True},
    name="dc",
)
@click.argument("command")
@click.argument("args", nargs=-1)
@click.pass_obj
def dc_command(context: Context, command: str, args: List[str]) -> None:
    config = tutor_config.load(context.root)
    volumes, non_volume_args = bindmounts.parse_volumes(args)
    volume_args = []
    for volume_arg in volumes:
        if ":" not in volume_arg:
            # This is a bind-mounted volume from the "volumes/" folder.
            host_bind_path = bindmounts.get_path(context.root, volume_arg)
            if not os.path.exists(host_bind_path):
                raise TutorError(
                    (
                        "Bind-mount volume directory {} does not exist. It must first be created"
                        " with the '{}' command."
                    ).format(host_bind_path, bindmount_command.name)
                )
            volume_arg = "{}:{}".format(host_bind_path, volume_arg)
        volume_args += ["--volume", volume_arg]
    context.docker_compose(
        context.root, config, command, *volume_args, *non_volume_args
    )


def add_commands(command_group: click.Group) -> None:
    command_group.add_command(start)
    command_group.add_command(stop)
    command_group.add_command(restart)
    command_group.add_command(reboot)
    command_group.add_command(init)
    command_group.add_command(createuser)
    command_group.add_command(importdemocourse)
    command_group.add_command(settheme)
    command_group.add_command(dc_command)
    command_group.add_command(run)
    command_group.add_command(bindmount_command)
    command_group.add_command(execute)
    command_group.add_command(logs)
