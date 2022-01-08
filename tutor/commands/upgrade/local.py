from time import sleep

import click

from tutor import config as tutor_config
from tutor import env as tutor_env
from tutor import fmt
from tutor.commands import compose
from tutor.types import Config
from . import common as common_upgrade


def upgrade_from(context: click.Context, from_release: str) -> None:
    # Make sure to bypass current version check
    config = tutor_config.load_full(context.obj.root)
    running_release = from_release
    if running_release == "ironwood":
        upgrade_from_ironwood(context, config)
        running_release = "juniper"

    if running_release == "juniper":
        upgrade_from_juniper(context, config)
        running_release = "koa"

    if running_release == "koa":
        upgrade_from_koa(context, config)
        running_release = "lilac"

    if running_release == "lilac":
        common_upgrade.upgrade_from_lilac(config)
        running_release = "maple"


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
            f"mysql_upgrade -u {config['MYSQL_ROOT_USERNAME']} --password='{config['MYSQL_ROOT_PASSWORD']}'",
        ],
    )
    context.invoke(compose.stop)


def upgrade_from_koa(context: click.Context, config: Config) -> None:
    click.echo(fmt.title("Upgrading from Koa"))
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
    click.echo(fmt.title(f"Upgrading MongoDb to v{to_docker_version}"))
    # Note that the DOCKER_IMAGE_MONGODB value is never saved, because we only save the
    # environment, not the configuration.
    config["DOCKER_IMAGE_MONGODB"] = f"mongo:{to_docker_version}"
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
            f'db.adminCommand({{ setFeatureCompatibilityVersion: "{to_compatibility_version}" }})',
        ],
    )
    context.invoke(compose.stop)
