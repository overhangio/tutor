import os

import click

from .. import config as tutor_config
from .. import env as tutor_env
from .. import fmt, utils
from . import compose
from .config import save as config_save_command
from .context import Context


# pylint: disable=too-few-public-methods
class LocalContext(Context):
    @staticmethod
    def docker_compose(root, config, *command):
        args = []
        override_path = tutor_env.pathjoin(root, "local", "docker-compose.override.yml")
        if os.path.exists(override_path):
            args += ["-f", override_path]
        return utils.docker_compose(
            "-f",
            tutor_env.pathjoin(root, "local", "docker-compose.yml"),
            "-f",
            tutor_env.pathjoin(root, "local", "docker-compose.prod.yml"),
            *args,
            "--project-name",
            config["LOCAL_PROJECT_NAME"],
            *command
        )


@click.group(help="Run Open edX locally with docker-compose")
@click.pass_context
def local(context):
    context.obj = LocalContext(context.obj.root)


@click.command(help="Configure and run Open edX from scratch")
@click.option("-I", "--non-interactive", is_flag=True, help="Run non-interactively")
@click.option(
    "-p", "--pullimages", "pullimages_", is_flag=True, help="Update docker images"
)
@click.pass_obj
def quickstart(context, non_interactive, pullimages_):
    if tutor_env.needs_major_upgrade(context.root):
        click.echo(fmt.title("Upgrading from an older release"))
        upgrade.callback(
            from_version=tutor_env.current_release(context.root),
            non_interactive=non_interactive,
        )

    click.echo(fmt.title("Interactive platform configuration"))
    config_save_command.callback(
        interactive=(not non_interactive), set_vars=[], unset_vars=[]
    )
    click.echo(fmt.title("Stopping any existing platform"))
    compose.stop.callback([])
    if pullimages_:
        click.echo(fmt.title("Docker image updates"))
        compose.dc_command.callback(["pull"])
    click.echo(fmt.title("Starting the platform in detached mode"))
    compose.start.callback(True, [])
    click.echo(fmt.title("Database creation and migrations"))
    compose.init.callback(limit=None)

    config = tutor_config.load(context.root)
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
    default="juniper",
    type=click.Choice(["ironwood", "juniper"]),
)
@click.option("-I", "--non-interactive", is_flag=True, help="Run non-interactively")
@click.pass_obj
def upgrade(context, from_version, non_interactive):
    config = tutor_config.load_no_check(context.root)

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


def upgrade_from_ironwood(context, config):
    click.echo(fmt.title("Upgrading from Ironwood"))
    tutor_env.save(context.root, config)

    click.echo(fmt.title("Stopping any existing platform"))
    compose.stop.callback([])

    if not config["RUN_MONGODB"]:
        fmt.echo_info(
            "You are not running MongDB (RUN_MONGODB=false). It is your "
            "responsibility to upgrade your MongoDb instance to v3.6. There is "
            "nothing left to do to upgrade from Ironwood."
        )
        return

    # Note that the DOCKER_IMAGE_MONGODB value is never saved, because we only save the
    # environment, not the configuration.
    click.echo(fmt.title("Upgrading MongoDb from v3.2 to v3.4"))
    config["DOCKER_IMAGE_MONGODB"] = "mongo:3.4.24"
    tutor_env.save(context.root, config)
    compose.start.callback(detach=True, services=["mongodb"])
    compose.execute.callback(
        [
            "mongodb",
            "mongo",
            "--eval",
            'db.adminCommand({ setFeatureCompatibilityVersion: "3.4" })',
        ]
    )
    compose.stop.callback([])

    click.echo(fmt.title("Upgrading MongoDb from v3.4 to v3.6"))
    config["DOCKER_IMAGE_MONGODB"] = "mongo:3.6.18"
    tutor_env.save(context.root, config)
    compose.start.callback(detach=True, services=["mongodb"])
    compose.execute.callback(
        [
            "mongodb",
            "mongo",
            "--eval",
            'db.adminCommand({ setFeatureCompatibilityVersion: "3.6" })',
        ]
    )
    compose.stop.callback([])


def upgrade_from_juniper(context, config):
    click.echo(fmt.title("Upgrading from Juniper"))
    tutor_env.save(context.root, config)

    click.echo(fmt.title("Stopping any existing platform"))
    compose.stop.callback([])

    if not config["RUN_MYSQL"]:
        fmt.echo_info(
            "You are not running MySQL (RUN_MYSQL=false). It is your "
            "responsibility to upgrade your MySQL instance to v5.7. There is "
            "nothing left to do to upgrade from Juniper."
        )
        return

    click.echo(fmt.title("Upgrading MySQL from v5.6 to v5.7"))
    compose.start.callback(detach=True, services=["mysql"])
    compose.execute.callback(
        [
            "mysql",
            "bash",
            "-e",
            "-c",
            "mysql_upgrade -u {} --password='{}'".format(
                config["MYSQL_ROOT_USERNAME"], config["MYSQL_ROOT_PASSWORD"]
            ),
        ]
    )
    compose.stop.callback([])


local.add_command(quickstart)
local.add_command(upgrade)
compose.add_commands(local)
