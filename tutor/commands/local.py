from time import sleep

import click

from .. import config as tutor_config
from .. import env as tutor_env
from .. import fmt
from ..types import Config, get_typed
from .. import utils
from .. import exceptions
from . import compose
from .config import save as config_save_command


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
        utils.check_macos_memory()
    except exceptions.TutorError as e:
        fmt.echo_alert(
            """Could not verify sufficient RAM allocation in Docker:
    {}
Tutor may not work if Docker is configured with < 4 GB RAM. Please follow instructions from:
    https://docs.tutor.overhang.io/install.html
            """.format(
                str(e)
            )
        )

    if tutor_env.needs_major_upgrade(context.obj.root):
        click.echo(fmt.title("Upgrading from an older release"))
        context.invoke(
            upgrade,
            from_version=tutor_env.current_release(context.obj.root),
            non_interactive=non_interactive,
        )

    click.echo(fmt.title("Interactive platform configuration"))
    context.invoke(
        config_save_command,
        interactive=(not non_interactive),
        set_vars=[],
        unset_vars=[],
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


@click.command(help="Upgrade from a previous Open edX named release")
@click.option(
    "--from",
    "from_version",
    default="koa",
    type=click.Choice(["ironwood", "juniper", "koa", "lilac"]),
)
@click.option("-I", "--non-interactive", is_flag=True, help="Run non-interactively")
@click.pass_context
def upgrade(context: click.Context, from_version: str, non_interactive: bool) -> None:
    config = tutor_config.load_full(context.obj.root)

    if not non_interactive:
        question = """You are about to upgrade your Open edX platform. It is strongly recommended to make a backup before upgrading. To do so, run:

    tutor local stop
    sudo rsync -avr "$(tutor config printroot)"/ /tmp/tutor-backup/

In case of problem, to restore your backup you will then have to run: sudo rsync -avr /tmp/tutor-backup/ "$(tutor config printroot)"/

Are you sure you want to continue?"""
        click.confirm(
            fmt.question(question), default=True, abort=True, prompt_suffix=" "
        )

    running_version = from_version
    if running_version == "ironwood":
        upgrade_from_ironwood(context, config)
        running_version = "juniper"

    if running_version == "juniper":
        upgrade_from_juniper(context, config)
        running_version = "koa"

    if running_version == "koa":
        upgrade_from_koa(context, config)
        running_version = "lilac"

    if running_version == "lilac":
        # Nothing to do here
        running_version = "maple"

    if not non_interactive:
        question = f"""
Your platform was successfuly upgraded from {from_version} to {running_version}. Depending on your setup, you might have to rebuild some of your Docker images. You can do this now by running the following command in a different shell:

    tutor images build openedx # add your custom images here

Press enter when you are ready to continue"""
        click.confirm(
            fmt.question(question), default=True, abort=True, prompt_suffix=" "
        )


def upgrade_from_ironwood(context: click.Context, config: Config) -> None:
    click.echo(fmt.title("Upgrading from Ironwood"))
    tutor_env.save(context.obj.root, config)

    click.echo(fmt.title("Stopping any existing platform"))
    context.invoke(compose.stop)

    if not config["RUN_MONGODB"]:
        fmt.echo_info(
            "You are not running MongDB (RUN_MONGODB=false). It is your "
            "responsibility to upgrade your MongoDb instance to v3.6. There is "
            "nothing left to do to upgrade from Ironwood to Juniper."
        )
        return

    upgrade_mongodb(context, config, "3.4", "3.4")
    context.invoke(compose.stop)
    upgrade_mongodb(context, config, "3.6", "3.6")
    context.invoke(compose.stop)


def upgrade_from_juniper(context: click.Context, config: Config) -> None:
    click.echo(fmt.title("Upgrading from Juniper"))
    tutor_env.save(context.obj.root, config)

    click.echo(fmt.title("Stopping any existing platform"))
    context.invoke(compose.stop)

    if not config["RUN_MYSQL"]:
        fmt.echo_info(
            "You are not running MySQL (RUN_MYSQL=false). It is your "
            "responsibility to upgrade your MySQL instance to v5.7. There is "
            "nothing left to do to upgrade from Juniper."
        )
        return

    click.echo(fmt.title("Upgrading MySQL from v5.6 to v5.7"))
    context.invoke(compose.start, detach=True, services=["mysql"])
    context.invoke(
        compose.execute,
        args=[
            "mysql",
            "bash",
            "-e",
            "-c",
            "mysql_upgrade -u {} --password='{}'".format(
                config["MYSQL_ROOT_USERNAME"], config["MYSQL_ROOT_PASSWORD"]
            ),
        ],
    )
    context.invoke(compose.stop)


def upgrade_from_koa(context: click.Context, config: Config) -> None:
    if not config["RUN_MONGODB"]:
        fmt.echo_info(
            "You are not running MongDB (RUN_MONGODB=false). It is your "
            "responsibility to upgrade your MongoDb instance to v4.0. There is "
            "nothing left to do to upgrade from Koa to Lilac."
        )
        return
    upgrade_mongodb(context, config, "4.0.25", "4.0")


def upgrade_mongodb(
    context: click.Context,
    config: Config,
    to_docker_version: str,
    to_compatibility_version: str,
) -> None:
    click.echo(fmt.title("Upgrading MongoDb to v{}".format(to_docker_version)))
    # Note that the DOCKER_IMAGE_MONGODB value is never saved, because we only save the
    # environment, not the configuration.
    config["DOCKER_IMAGE_MONGODB"] = "mongo:{}".format(to_docker_version)
    tutor_env.save(context.obj.root, config)
    context.invoke(compose.start, detach=True, services=["mongodb"])
    fmt.echo_info("Waiting for mongodb to boot...")
    sleep(10)
    context.invoke(
        compose.execute,
        args=[
            "mongodb",
            "mongo",
            "--eval",
            'db.adminCommand({ setFeatureCompatibilityVersion: "%s" })'
            % to_compatibility_version,
        ],
    )
    context.invoke(compose.stop)


local.add_command(quickstart)
local.add_command(upgrade)
compose.add_commands(local)
