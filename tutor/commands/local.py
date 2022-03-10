from typing import Optional

import click

from tutor import config as tutor_config
from tutor import env as tutor_env
from tutor import exceptions, fmt, utils
from tutor.commands import compose
from tutor.commands.config import save as config_save_command
from tutor.commands.upgrade.local import upgrade_from
from tutor.types import Config, get_typed


class LocalJobRunner(compose.ComposeJobRunner):
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
        ]
        self.docker_compose_job_files += [
            tutor_env.pathjoin(self.root, "local", "docker-compose.jobs.yml"),
            tutor_env.pathjoin(self.root, "local", "docker-compose.jobs.override.yml"),
        ]


# pylint: disable=too-few-public-methods
class LocalContext(compose.BaseComposeContext):
    def job_runner(self, config: Config) -> LocalJobRunner:
        return LocalJobRunner(self.root, config)


@click.group(help="Run Open edX locally with docker-compose")
@click.pass_context
def local(context: click.Context) -> None:
    context.obj = LocalContext(context.obj.root)


@click.command(help="Configure and run Open edX from scratch")
@click.option("-I", "--non-interactive", is_flag=True, help="Run non-interactively")
@click.option("-p", "--pullimages", is_flag=True, help="Update docker images")
@click.pass_context
def quickstart(context: click.Context, non_interactive: bool, pullimages: bool) -> None:
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
            non_interactive=non_interactive,
        )

    click.echo(fmt.title("Interactive platform configuration"))
    context.invoke(config_save_command, interactive=(not non_interactive))

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
    context.invoke(compose.init)

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


@click.command(
    short_help="Perform release-specific upgrade tasks",
    help="Perform release-specific upgrade tasks. To perform a full upgrade remember to run `quickstart`.",
)
@click.option(
    "--from",
    "from_release",
    type=click.Choice(["ironwood", "juniper", "koa", "lilac"]),
)
@click.pass_context
def upgrade(context: click.Context, from_release: Optional[str]) -> None:
    fmt.echo_alert(
        "This command only performs a partial upgrade of your Open edX platform. "
        "To perform a full upgrade, you should run `tutor local quickstart`."
    )
    if from_release is None:
        from_release = tutor_env.get_env_release(context.obj.root)
    if from_release is None:
        fmt.echo_info("Your environment is already up-to-date")
    else:
        upgrade_from(context, from_release)
    # We update the environment to update the version
    context.invoke(config_save_command)


local.add_command(quickstart)
local.add_command(upgrade)
compose.add_commands(local)
