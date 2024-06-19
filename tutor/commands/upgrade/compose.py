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

    if running_release == "maple":
        upgrade_from_maple(context, config)
        running_release = "nutmeg"

    if running_release == "nutmeg":
        common_upgrade.upgrade_from_nutmeg(context, config)
        running_release = "olive"

    if running_release == "olive":
        upgrade_from_olive(context, config)
        running_release = "palm"

    if running_release == "palm":
        running_release = "quince"

    if running_release == "quince":
        upgrade_from_quince(context, config)
        running_release = "redwood"


def upgrade_from_ironwood(context: click.Context, config: Config) -> None:
    click.echo(fmt.title("Upgrading from Ironwood"))
    tutor_env.save(context.obj.root, config)

    click.echo(fmt.title("Stopping any existing platform"))
    context.invoke(compose.stop)

    upgrade_mongodb(context, config, "3.4", "3.4")
    upgrade_mongodb(context, config, "3.6", "3.6")


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
            "You are not running MongoDB (RUN_MONGODB=false). It is your "
            "responsibility to upgrade your MongoDb instance to v4.0. There is "
            "nothing left to do to upgrade from Koa to Lilac."
        )
        return
    upgrade_mongodb(context, config, "4.0.25", "4.0")


def upgrade_from_maple(context: click.Context, config: Config) -> None:
    click.echo(fmt.title("Upgrading from Maple"))
    # The environment needs to be updated because the management commands are from Nutmeg
    tutor_env.save(context.obj.root, config)
    # Command backpopulate_user_tours
    context.invoke(
        compose.run,
        args=["lms", "sh", "-e", "-c", "./manage.py lms migrate user_tours"],
    )
    context.invoke(
        compose.run,
        args=["lms", "sh", "-e", "-c", "./manage.py lms backpopulate_user_tours"],
    )
    # Command backfill_course_tabs
    context.invoke(
        compose.run,
        args=["cms", "sh", "-e", "-c", "./manage.py cms migrate contentstore"],
    )
    context.invoke(
        compose.run,
        args=[
            "cms",
            "sh",
            "-e",
            "-c",
            "./manage.py cms migrate split_modulestore_django",
        ],
    )
    context.invoke(
        compose.run,
        args=["cms", "sh", "-e", "-c", "./manage.py cms backfill_course_tabs"],
    )
    # Command simulate_publish
    context.invoke(
        compose.run,
        args=["cms", "sh", "-e", "-c", "./manage.py cms migrate course_overviews"],
    )
    context.invoke(
        compose.run,
        args=["cms", "sh", "-e", "-c", "./manage.py cms simulate_publish"],
    )


def upgrade_from_olive(context: click.Context, config: Config) -> None:
    # Note that we need to exec because the ora2 folder is not bind-mounted in the job
    # services.
    context.invoke(compose.start, detach=True, services=["lms"])
    context.invoke(
        compose.execute,
        args=["lms", "sh", "-e", "-c", common_upgrade.PALM_RENAME_ORA2_FOLDER_COMMAND],
    )
    upgrade_mongodb(context, config, "4.2.17", "4.2")
    upgrade_mongodb(context, config, "4.4.22", "4.4")


def upgrade_from_quince(context: click.Context, config: Config) -> None:
    click.echo(fmt.title("Upgrading from Quince"))
    upgrade_mongodb(context, config, "5.0.26", "5.0")
    upgrade_mongodb(context, config, "6.0.14", "6.0")
    upgrade_mongodb(context, config, "7.0.7", "7.0")


def upgrade_mongodb(
    context: click.Context,
    config: Config,
    to_docker_version: str,
    to_compatibility_version: str,
) -> None:
    if not config["RUN_MONGODB"]:
        fmt.echo_info(
            f"You are not running MongoDB (RUN_MONGODB=false). It is your "
            f"responsibility to upgrade your MongoDb instance to {to_docker_version}."
        )
        return

    mongo_version, admin_command = common_upgrade.get_mongo_upgrade_parameters(
        to_docker_version, to_compatibility_version
    )
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
            "mongosh" if mongo_version >= 6 else "mongo",
            "--eval",
            f"db.adminCommand({admin_command})",
        ],
    )
    context.invoke(compose.stop)
