import typing as t

import click

from tutor import config as tutor_config
from tutor import env as tutor_env
from tutor import exceptions, fmt, hooks
from tutor import interactive as interactive_config
from tutor import utils
from tutor.commands import compose
from tutor.types import Config, get_typed


class DevJobRunner(compose.ComposeJobRunner):
    def __init__(self, root: str, config: Config):
        """
        Load docker-compose files from dev/ and local/
        """
        super().__init__(root, config)
        self.project_name = get_typed(self.config, "DEV_PROJECT_NAME", str)
        docker_compose_tmp_path = tutor_env.pathjoin(
            self.root, "dev", "docker-compose.tmp.yml"
        )
        docker_compose_jobs_tmp_path = tutor_env.pathjoin(
            self.root, "dev", "docker-compose.jobs.tmp.yml"
        )
        self.docker_compose_files += [
            tutor_env.pathjoin(self.root, "local", "docker-compose.yml"),
            tutor_env.pathjoin(self.root, "dev", "docker-compose.yml"),
            docker_compose_tmp_path,
            tutor_env.pathjoin(self.root, "local", "docker-compose.override.yml"),
            tutor_env.pathjoin(self.root, "dev", "docker-compose.override.yml"),
        ]
        self.docker_compose_job_files += [
            tutor_env.pathjoin(self.root, "local", "docker-compose.jobs.yml"),
            tutor_env.pathjoin(self.root, "dev", "docker-compose.jobs.yml"),
            docker_compose_jobs_tmp_path,
            tutor_env.pathjoin(self.root, "local", "docker-compose.jobs.override.yml"),
            tutor_env.pathjoin(self.root, "dev", "docker-compose.jobs.override.yml"),
        ]
        # Update docker-compose.tmp files
        self.update_docker_compose_tmp(
            hooks.Filters.COMPOSE_DEV_TMP,
            hooks.Filters.COMPOSE_DEV_JOBS_TMP,
            docker_compose_tmp_path,
            docker_compose_jobs_tmp_path,
        )


class DevContext(compose.BaseComposeContext):
    COMPOSE_TMP_FILTER = hooks.Filters.COMPOSE_DEV_TMP
    COMPOSE_JOBS_TMP_FILTER = hooks.Filters.COMPOSE_DEV_JOBS_TMP

    def job_runner(self, config: Config) -> DevJobRunner:
        return DevJobRunner(self.root, config)


@click.group(help="Run Open edX locally with development settings")
@click.pass_context
def dev(context: click.Context) -> None:
    context.obj = DevContext(context.obj.root)


@click.command(help="Configure and run Open edX from scratch, for development")
@click.option("-I", "--non-interactive", is_flag=True, help="Run non-interactively")
@click.option("-p", "--pullimages", is_flag=True, help="Update docker images")
@compose.mount_option
@click.pass_context
def quickstart(
    context: click.Context,
    non_interactive: bool,
    pullimages: bool,
    mounts: t.Tuple[t.List[compose.MountParam.MountType]],
) -> None:
    compose.mount_tmp_volumes(mounts, context.obj)
    try:
        utils.check_macos_docker_memory()
    except exceptions.TutorError as e:
        fmt.echo_alert(
            f"""Could not verify sufficient RAM allocation in Docker:
    {e}
Tutor may not work if Docker is configured with < 4 GB RAM. Please follow instructions from:
    https://docs.tutor.overhang.io/install.html"""
        )

    click.echo(fmt.title("Interactive platform configuration"))
    config = tutor_config.load_minimal(context.obj.root)
    if not non_interactive:
        interactive_config.ask_questions(config, run_for_prod=False)
    tutor_config.save_config_file(context.obj.root, config)
    config = tutor_config.load_full(context.obj.root)
    tutor_env.save(context.obj.root, config)

    click.echo(fmt.title("Stopping any existing platform"))
    context.invoke(compose.stop)

    if pullimages:
        click.echo(fmt.title("Docker image updates"))
        context.invoke(compose.dc_command, command="pull")

    click.echo(fmt.title("Building Docker image for LMS and CMS development"))
    context.invoke(compose.dc_command, command="build", args=["lms"])

    click.echo(fmt.title("Starting the platform in detached mode"))
    context.invoke(compose.start, detach=True)

    click.echo(fmt.title("Database creation and migrations"))
    context.invoke(compose.init)

    fmt.echo_info(
        """The Open edX platform is now running in detached mode
Your Open edX platform is ready and can be accessed at the following urls:
    {http}://{lms_host}:8000
    {http}://{cms_host}:8001
    """.format(
            http="https" if config["ENABLE_HTTPS"] else "http",
            lms_host=config["LMS_HOST"],
            cms_host=config["CMS_HOST"],
        )
    )


@click.command(
    help="DEPRECATED: Use 'tutor dev start ...' instead!",
    context_settings={"ignore_unknown_options": True},
)
@compose.mount_option
@click.argument("options", nargs=-1, required=False)
@click.argument("service")
@click.pass_context
def runserver(
    context: click.Context,
    mounts: t.Tuple[t.List[compose.MountParam.MountType]],
    options: t.List[str],
    service: str,
) -> None:
    depr_warning = "'runserver' is deprecated and will be removed in a future release. Use 'start' instead."
    for option in options:
        if option.startswith("-v") or option.startswith("--volume"):
            depr_warning += " Bind-mounts can be specified using '-m/--mount'."
            break
    fmt.echo_alert(depr_warning)
    config = tutor_config.load(context.obj.root)
    if service in ["lms", "cms"]:
        port = 8000 if service == "lms" else 8001
        host = config["LMS_HOST"] if service == "lms" else config["CMS_HOST"]
        fmt.echo_info(
            f"The {service} service will be available at http://{host}:{port}"
        )
    args = ["--service-ports", *options, service]
    context.invoke(compose.run, mounts=mounts, args=args)


@hooks.Actions.COMPOSE_PROJECT_STARTED.add()
def _stop_on_local_start(root: str, config: Config, project_name: str) -> None:
    """
    Stop the dev platform as soon as a platform with a different project name is
    started.
    """
    runner = DevJobRunner(root, config)
    if project_name != runner.project_name:
        runner.docker_compose("stop")


dev.add_command(quickstart)
dev.add_command(runserver)
compose.add_commands(dev)
