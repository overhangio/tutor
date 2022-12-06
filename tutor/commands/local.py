import typing as t

import click

from tutor import config as tutor_config
from tutor import env as tutor_env
from tutor import exceptions, fmt, hooks
from tutor import interactive as interactive_config
from tutor import utils
from tutor.commands import compose
from tutor.commands.config import save as config_save_command
from tutor.commands.upgrade.local import upgrade_from
from tutor.types import Config, get_typed


class LocalTaskRunner(compose.ComposeTaskRunner):
    def __init__(self, root: str, config: Config):
        """
        Load docker-compose files from local/.
        """
        super().__init__(root, config)
        self.project_name = get_typed(self.config, "LOCAL_PROJECT_NAME", str)
        docker_compose_tmp_path = tutor_env.pathjoin(
            self.root, "local", "docker-compose.tmp.yml"
        )
        docker_compose_jobs_tmp_path = tutor_env.pathjoin(
            self.root, "local", "docker-compose.jobs.tmp.yml"
        )
        self.docker_compose_files += [
            tutor_env.pathjoin(self.root, "local", "docker-compose.yml"),
            tutor_env.pathjoin(self.root, "local", "docker-compose.prod.yml"),
            docker_compose_tmp_path,
            tutor_env.pathjoin(self.root, "local", "docker-compose.override.yml"),
        ]
        self.docker_compose_job_files += [
            tutor_env.pathjoin(self.root, "local", "docker-compose.jobs.yml"),
            docker_compose_jobs_tmp_path,
            tutor_env.pathjoin(self.root, "local", "docker-compose.jobs.override.yml"),
        ]

        # Update docker-compose.tmp files
        self.update_docker_compose_tmp(
            hooks.Filters.COMPOSE_LOCAL_TMP,
            hooks.Filters.COMPOSE_LOCAL_JOBS_TMP,
            docker_compose_tmp_path,
            docker_compose_jobs_tmp_path,
        )


# pylint: disable=too-few-public-methods
class LocalContext(compose.BaseComposeContext):
    COMPOSE_TMP_FILTER = hooks.Filters.COMPOSE_LOCAL_TMP
    COMPOSE_JOBS_TMP_FILTER = hooks.Filters.COMPOSE_LOCAL_JOBS_TMP

    def job_runner(self, config: Config) -> LocalTaskRunner:
        return LocalTaskRunner(self.root, config)


@click.group(help="Run Open edX locally with docker-compose")
@click.pass_context
def local(context: click.Context) -> None:
    context.obj = LocalContext(context.obj.root)


@click.command(help="Configure and run Open edX from scratch")
@compose.mount_option
@click.option("-I", "--non-interactive", is_flag=True, help="Run non-interactively")
@click.option("-p", "--pullimages", is_flag=True, help="Update docker images")
@click.pass_context
def launch(
    context: click.Context,
    mounts: t.Tuple[t.List[compose.MountParam.MountType]],
    non_interactive: bool,
    pullimages: bool,
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

    run_upgrade_from_release = tutor_env.should_upgrade_from_release(context.obj.root)
    if run_upgrade_from_release is not None:
        click.echo(fmt.title("Upgrading from an older release"))
        if not non_interactive:
            to_release = tutor_env.get_package_release()
            question = f"""You are about to upgrade your Open edX platform from {run_upgrade_from_release.capitalize()} to {to_release.capitalize()}

It is strongly recommended to make a backup before upgrading. To do so, run:

    tutor local stop
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

    click.echo(fmt.title("Interactive platform configuration"))
    config = tutor_config.load_minimal(context.obj.root)
    if not non_interactive:
        interactive_config.ask_questions(config)
    tutor_config.save_config_file(context.obj.root, config)
    config = tutor_config.load_full(context.obj.root)
    tutor_env.save(context.obj.root, config)

    if run_upgrade_from_release and not non_interactive:
        question = f"""Your platform is being upgraded from {run_upgrade_from_release.capitalize()}.

If you run custom Docker images, you must rebuild them now by running the following command in a different shell:

    tutor images build all # list your custom images here

See the documentation for more information:

    https://docs.tutor.overhang.io/install.html#upgrading-to-a-new-open-edx-release

Press enter when you are ready to continue"""
        click.confirm(
            fmt.question(question), default=True, abort=True, prompt_suffix=" "
        )

    click.echo(fmt.title("Stopping any existing platform"))
    context.invoke(compose.stop)
    if pullimages:
        click.echo(fmt.title("Docker image updates"))
        context.invoke(compose.dc_command, command="pull")
    click.echo(fmt.title("Starting the platform in detached mode"))
    context.invoke(compose.start, detach=True)
    click.echo(fmt.title("Database creation and migrations"))
    context.invoke(compose.do.commands["init"])

    config = tutor_config.load(context.obj.root)
    fmt.echo_info(
        """The Open edX platform is now running in detached mode
Your Open edX platform is ready and can be accessed at the following urls:

    {http}://{lms_host}
    {http}://{cms_host}
    """.format(
            http="https" if config["ENABLE_HTTPS"] else "http",
            lms_host=config["LMS_HOST"],
            cms_host=config["CMS_HOST"],
        )
    )


@click.command(help="Deprecated alias to 'launch'")
@compose.mount_option
@click.option("-I", "--non-interactive", is_flag=True, help="Run non-interactively")
@click.option("-p", "--pullimages", is_flag=True, help="Update docker images")
@click.pass_context
def quickstart(
    context: click.Context,
    mounts: t.Tuple[t.List[compose.MountParam.MountType]],
    non_interactive: bool,
    pullimages: bool,
) -> None:
    """
    This command has been renamed to 'launch'.
    """
    fmt.echo_alert(
        "The 'quickstart' command is deprecated and will be removed in a later release. Use 'launch' instead."
    )
    context.invoke(
        launch, non_interactive=non_interactive, pullimages=pullimages, mounts=mounts
    )


@click.command(
    short_help="Perform release-specific upgrade tasks",
    help="Perform release-specific upgrade tasks. To perform a full upgrade remember to run `launch`.",
)
@click.option(
    "--from",
    "from_release",
    type=click.Choice(["ironwood", "juniper", "koa", "lilac", "maple"]),
)
@click.pass_context
def upgrade(context: click.Context, from_release: t.Optional[str]) -> None:
    fmt.echo_alert(
        "This command only performs a partial upgrade of your Open edX platform. "
        "To perform a full upgrade, you should run `tutor local launch`."
    )
    if from_release is None:
        from_release = tutor_env.get_env_release(context.obj.root)
    if from_release is None:
        fmt.echo_info("Your environment is already up-to-date")
    else:
        upgrade_from(context, from_release)
    # We update the environment to update the version
    context.invoke(config_save_command)


@hooks.Actions.COMPOSE_PROJECT_STARTED.add()
def _stop_on_dev_start(root: str, config: Config, project_name: str) -> None:
    """
    Stop the local platform as soon as a platform with a different project name is
    started.
    """
    runner = LocalTaskRunner(root, config)
    if project_name != runner.project_name:
        runner.docker_compose("stop")


local.add_command(launch)
local.add_command(quickstart)
local.add_command(upgrade)
compose.add_commands(local)
