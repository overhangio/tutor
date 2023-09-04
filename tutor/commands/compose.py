from __future__ import annotations

import os
import typing as t

import click

from tutor import bindmount
from tutor import config as tutor_config
from tutor import env as tutor_env
from tutor import fmt, hooks
from tutor import interactive as interactive_config
from tutor import utils
from tutor.commands import images, jobs
from tutor.commands.config import save as config_save_command
from tutor.commands.context import BaseTaskContext
from tutor.commands.upgrade import OPENEDX_RELEASE_NAMES
from tutor.commands.upgrade.compose import upgrade_from
from tutor.core.hooks import Filter  # pylint: disable=unused-import
from tutor.exceptions import TutorError
from tutor.tasks import BaseComposeTaskRunner
from tutor.types import Config


class ComposeTaskRunner(BaseComposeTaskRunner):
    def __init__(self, root: str, config: Config):
        super().__init__(root, config)
        self.project_name = ""
        self.docker_compose_files: list[str] = []
        self.docker_compose_job_files: list[str] = []

    def docker_compose(self, *command: str) -> int:
        """
        Run docker-compose with the right yml files.
        """
        if "start" in command or "up" in command or "restart" in command:
            # Note that we don't trigger the action on "run". That's because we
            # don't want to trigger the action for every initialization script.
            hooks.Actions.COMPOSE_PROJECT_STARTED.do(
                self.root, self.config, self.project_name
            )
        args = []
        for docker_compose_path in self.docker_compose_files:
            if os.path.exists(docker_compose_path):
                args += ["-f", docker_compose_path]
        return utils.docker_compose(
            *args, "--project-name", self.project_name, *command
        )

    def run_task(self, service: str, command: str) -> int:
        """
        Run the "{{ service }}-job" service from local/docker-compose.jobs.yml with the
        specified command.
        """
        run_command = []
        for docker_compose_path in self.docker_compose_job_files:
            path = tutor_env.pathjoin(self.root, docker_compose_path)
            if os.path.exists(path):
                run_command += ["-f", path]
        run_command += ["run", "--rm"]
        if not utils.is_a_tty():
            run_command += ["-T"]
        job_service_name = f"{service}-job"
        return self.docker_compose(
            *run_command,
            job_service_name,
            "sh",
            "-e",
            "-c",
            command,
        )


class BaseComposeContext(BaseTaskContext):
    NAME: t.Literal["local", "dev"]

    def job_runner(self, config: Config) -> ComposeTaskRunner:
        raise NotImplementedError


@click.command(help="Configure and run Open edX from scratch")
@click.option("-I", "--non-interactive", is_flag=True, help="Run non-interactively")
@click.option("-p", "--pullimages", is_flag=True, help="Update docker images")
@click.option("--skip-build", is_flag=True, help="Skip building Docker images")
@click.pass_context
def launch(
    context: click.Context,
    non_interactive: bool,
    pullimages: bool,
    skip_build: bool,
) -> None:
    context_name = context.obj.NAME
    run_for_prod = False if context_name == "dev" else None

    utils.warn_macos_docker_memory()

    # Upgrade has to run before configuration
    interactive_upgrade(context, not non_interactive, run_for_prod=run_for_prod)
    interactive_configuration(context, not non_interactive, run_for_prod=run_for_prod)

    config = tutor_config.load(context.obj.root)

    if not skip_build:
        click.echo(fmt.title("Building Docker images"))
        images_to_build = hooks.Filters.IMAGES_BUILD_REQUIRED.apply([], context_name)
        if not images_to_build:
            fmt.echo_info("No image to build")
        context.invoke(images.build, image_names=images_to_build)

    click.echo(fmt.title("Stopping any existing platform"))
    context.invoke(stop)

    if pullimages:
        click.echo(fmt.title("Docker image updates"))
        context.invoke(dc_command, command="pull")

    click.echo(fmt.title("Starting the platform in detached mode"))
    context.invoke(start, detach=True)

    click.echo(fmt.title("Database creation and migrations"))
    context.invoke(do.commands["init"])

    # Print the urls of the user-facing apps
    public_app_hosts = ""
    for host in hooks.Filters.APP_PUBLIC_HOSTS.iterate(context_name):
        public_app_host = tutor_env.render_str(
            config, "{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://" + host
        )
        public_app_hosts += f"    {public_app_host}\n"
    if public_app_hosts:
        fmt.echo_info(
            f"""The platform is now running and can be accessed at the following urls:

{public_app_hosts}"""
        )


def interactive_upgrade(
    context: click.Context, interactive: bool, run_for_prod: t.Optional[bool]
) -> None:
    """
    Piece of code that is only used in launch.
    """
    run_upgrade_from_release = tutor_env.should_upgrade_from_release(context.obj.root)
    if run_upgrade_from_release is not None:
        click.echo(fmt.title("Upgrading from an older release"))
        if interactive:
            to_release = tutor_env.get_current_open_edx_release_name()
            question = f"""You are about to upgrade your Open edX platform from {run_upgrade_from_release.capitalize()} to {to_release.capitalize()}

It is strongly recommended to make a backup before upgrading. To do so, run:

    tutor local stop # or 'tutor dev stop' in development
    sudo rsync -avr "$(tutor config printroot)"/ /tmp/tutor-backup/

In case of problem, to restore your backup you will then have to run: sudo rsync -avr /tmp/tutor-backup/ "$(tutor config printroot)"/

Are you sure you want to continue?"""
            click.confirm(
                fmt.question(question), default=True, abort=True, prompt_suffix=" "
            )
        context.invoke(
            upgrade,
            from_release=run_upgrade_from_release,
        )

        # Update env and configuration
        # Don't run in interactive mode, otherwise users gets prompted twice.
        interactive_configuration(context, False, run_for_prod)

        # Post upgrade
        if interactive:
            question = f"""Your platform is being upgraded from {run_upgrade_from_release.capitalize()}.

    If you run custom Docker images, you must rebuild them now by running the following command in a different shell:

        tutor images build all # list your custom images here

    See the documentation for more information:

        https://docs.tutor.edly.io/install.html#upgrading-to-a-new-open-edx-release

    Press enter when you are ready to continue"""
            click.confirm(
                fmt.question(question), default=True, abort=True, prompt_suffix=" "
            )


def interactive_configuration(
    context: click.Context, interactive: bool, run_for_prod: t.Optional[bool] = None
) -> None:
    click.echo(fmt.title("Interactive platform configuration"))
    config = tutor_config.load_minimal(context.obj.root)
    if interactive:
        interactive_config.ask_questions(config, run_for_prod=run_for_prod)
    tutor_config.save_config_file(context.obj.root, config)
    config = tutor_config.load_full(context.obj.root)
    tutor_env.save(context.obj.root, config)


@click.command(
    short_help="Perform release-specific upgrade tasks",
    help="Perform release-specific upgrade tasks. To perform a full upgrade remember to run `launch`.",
)
@click.option(
    "--from",
    "from_release",
    type=click.Choice(OPENEDX_RELEASE_NAMES),
)
@click.pass_context
def upgrade(context: click.Context, from_release: t.Optional[str]) -> None:
    fmt.echo_alert(
        "This command only performs a partial upgrade of your Open edX platform. "
        "To perform a full upgrade, you should run `tutor local launch` (or `tutor dev launch` "
        "in development)."
    )
    if from_release is None:
        from_release = tutor_env.get_env_release(context.obj.root)
    if from_release is None:
        fmt.echo_info("Your environment is already up-to-date")
    else:
        upgrade_from(context, from_release)
    # We update the environment to update the version
    context.invoke(config_save_command)


@click.command(
    short_help="Run all or a selection of services.",
    help="Run all or a selection of services. Docker images will be rebuilt where necessary.",
)
@click.option("--build", is_flag=True, help="Build images on start")
@click.option("-d", "--detach", is_flag=True, help="Start in daemon mode")
@click.argument("services", metavar="service", nargs=-1)
@click.pass_obj
def start(
    context: BaseComposeContext,
    build: bool,
    detach: bool,
    services: list[str],
) -> None:
    command = ["up", "--remove-orphans"]
    if build:
        command.append("--build")
    if detach:
        command.append("-d")

    # Start services
    config = tutor_config.load(context.root)
    context.job_runner(config).docker_compose(*command, *services)


@click.command(help="Stop a running platform")
@click.argument("services", metavar="service", nargs=-1)
@click.pass_obj
def stop(context: BaseComposeContext, services: list[str]) -> None:
    config = tutor_config.load(context.root)
    context.job_runner(config).docker_compose("stop", *services)


@click.command(
    short_help="Reboot an existing platform",
    help="This is more than just a restart: with reboot, the platform is fully stopped before being restarted again",
)
@click.option("-d", "--detach", is_flag=True, help="Start in daemon mode")
@click.argument("services", metavar="service", nargs=-1)
@click.pass_context
def reboot(context: click.Context, detach: bool, services: list[str]) -> None:
    context.invoke(stop, services=services)
    context.invoke(start, detach=detach, services=services)


@click.command(
    short_help="Restart some components from a running platform.",
    help="""Specify 'openedx' to restart the lms, cms and workers, or 'all' to
restart all services. Note that this performs a 'docker compose restart', so new images
may not be taken into account. It is useful for reloading settings, for instance. To
fully stop the platform, use the 'reboot' command.""",
)
@click.argument("services", metavar="service", nargs=-1)
@click.pass_obj
def restart(context: BaseComposeContext, services: list[str]) -> None:
    config = tutor_config.load(context.root)
    command = ["restart"]
    if "all" in services:
        pass
    else:
        for service in services:
            if service == "openedx":
                command += ["lms", "lms-worker", "cms", "cms-worker"]
            else:
                command.append(service)
    context.job_runner(config).docker_compose(*command)


@jobs.do_group
def do() -> None:
    """
    Run a custom job in the right container(s).
    """


@click.command(
    short_help="Run a command in a new container",
    help=(
        "Run a command in a new container. This is a wrapper around `docker compose run`. Any option or argument passed"
        " to this command will be forwarded to docker compose. Thus, you may use `-v` or `-p` to mount volumes and"
        " expose ports."
    ),
    context_settings={"ignore_unknown_options": True},
)
@click.argument("args", nargs=-1, required=True)
@click.pass_context
def run(
    context: click.Context,
    args: list[str],
) -> None:
    extra_args = ["--rm"]
    if not utils.is_a_tty():
        extra_args.append("-T")
    context.invoke(dc_command, command="run", args=[*extra_args, *args])


@click.command(
    name="copyfrom",
    help="Copy files/folders from a container directory to the local filesystem.",
)
@click.argument("service")
@click.argument("container_path")
@click.argument(
    "host_path",
    type=click.Path(dir_okay=True, file_okay=False, resolve_path=True),
)
@click.pass_obj
def copyfrom(
    context: BaseComposeContext, service: str, container_path: str, host_path: str
) -> None:
    # Path management
    container_root_path = "/tmp/mount"
    container_dst_path = container_root_path
    if not os.path.exists(host_path):
        # Emulate cp semantics, where if the destination path does not exist
        # then we copy to its parent and rename to the destination folder
        container_dst_path += "/" + os.path.basename(host_path)
        host_path = os.path.dirname(host_path)
    if not os.path.exists(host_path):
        raise TutorError(
            f"Cannot create directory {host_path}. No such file or directory."
        )

    # cp/mv commands
    command = f"cp --recursive --preserve {container_path} {container_dst_path}"
    config = tutor_config.load(context.root)
    runner = context.job_runner(config)
    runner.docker_compose(
        "run",
        "--rm",
        "--no-deps",
        "--user=0",
        f"--volume={host_path}:{container_root_path}",
        service,
        "sh",
        "-e",
        "-c",
        command,
    )


@click.command(
    short_help="Run a command in a running container",
    help=(
        "Run a command in a running container. This is a wrapper around `docker compose exec`. Any option or argument"
        " passed to this command will be forwarded to docker-compose. Thus, you may use `-e` to manually define"
        " environment variables."
    ),
    context_settings={"ignore_unknown_options": True},
    name="exec",
)
@click.argument("args", nargs=-1, required=True)
@click.pass_context
def execute(context: click.Context, args: list[str]) -> None:
    context.invoke(dc_command, command="exec", args=args)


@click.command(
    short_help="View output from containers",
    help="View output from containers. This is a wrapper around `docker compose logs`.",
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


@click.command(help="Print status information for containers")
@click.pass_context
def status(context: click.Context) -> None:
    context.invoke(dc_command, command="ps")


@click.command(
    short_help="Direct interface to docker compose.",
    help=(
        "Direct interface to docker compose. This is a wrapper around `docker compose`. Most commands, options and"
        " arguments passed to this command will be forwarded as-is to docker compose."
    ),
    context_settings={"ignore_unknown_options": True},
    name="dc",
)
@click.argument("command")
@click.argument("args", nargs=-1)
@click.pass_obj
def dc_command(
    context: BaseComposeContext,
    command: str,
    args: list[str],
) -> None:
    config = tutor_config.load(context.root)
    context.job_runner(config).docker_compose(command, *args)


hooks.Filters.ENV_TEMPLATE_VARIABLES.add_item(("iter_mounts", bindmount.iter_mounts))


def add_commands(command_group: click.Group) -> None:
    command_group.add_command(launch)
    command_group.add_command(upgrade)
    command_group.add_command(start)
    command_group.add_command(stop)
    command_group.add_command(restart)
    command_group.add_command(reboot)
    command_group.add_command(dc_command)
    command_group.add_command(run)
    command_group.add_command(copyfrom)
    command_group.add_command(execute)
    command_group.add_command(logs)
    command_group.add_command(status)

    @hooks.Actions.PLUGINS_LOADED.add()
    def _add_do_commands() -> None:
        jobs.add_job_commands(do)
        command_group.add_command(do)
