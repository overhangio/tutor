import click

from tutor import config as tutor_config
from tutor import env as tutor_env
from tutor import fmt
from tutor.commands import k8s
from tutor.commands.context import Context
from tutor.types import Config


def upgrade_from(
    context: Context, from_version: str, interactive: bool = False
) -> None:
    config = tutor_config.load(context.root)

    running_version = from_version
    if running_version == "ironwood":
        upgrade_from_ironwood(config)
        running_version = "juniper"

    if running_version == "juniper":
        upgrade_from_juniper(config)
        running_version = "koa"

    if running_version == "koa":
        upgrade_from_koa(config)
        running_version = "lilac"

    if running_version == "lilac":
        upgrade_from_lilac(config)
        running_version = "maple"

    # Update env such that the build environment is up-to-date
    tutor_env.save(context.root, config)
    if interactive:
        question = f"""Your platform was successfuly upgraded from {from_version} to {running_version}.

Depending on your setup, you might have to rebuild some of your Docker images
and push them to your private registry (if any). You can do this now by running
the following command in a different shell:

    tutor images build openedx # add your custom images here
    tutor images push openedx

Press enter when you are ready to continue"""
        click.confirm(
            fmt.question(question), default=True, abort=True, prompt_suffix=" "
        )


def upgrade_from_ironwood(config: Config) -> None:
    if not config["RUN_MONGODB"]:
        fmt.echo_info(
            "You are not running MongDB (RUN_MONGODB=false). It is your "
            "responsibility to upgrade your MongoDb instance to v3.6. There is "
            "nothing left to do to upgrade from Ironwood."
        )
        return
    message = """Automatic release upgrade is unsupported in Kubernetes. To upgrade from Ironwood, you should upgrade
your MongoDb cluster from v3.2 to v3.6. You should run something similar to:

    # Upgrade from v3.2 to v3.4
    tutor k8s stop
    tutor config save --set DOCKER_IMAGE_MONGODB=mongo:3.4.24
    tutor k8s start
    tutor k8s exec mongodb mongo --eval 'db.adminCommand({ setFeatureCompatibilityVersion: "3.4" })'

    # Upgrade from v3.4 to v3.6
    tutor k8s stop
    tutor config save --set DOCKER_IMAGE_MONGODB=mongo:3.6.18
    tutor k8s start
    tutor k8s exec mongodb mongo --eval 'db.adminCommand({ setFeatureCompatibilityVersion: "3.6" })'

    tutor config save --unset DOCKER_IMAGE_MONGODB"""
    fmt.echo_info(message)


def upgrade_from_juniper(config: Config) -> None:
    if not config["RUN_MYSQL"]:
        fmt.echo_info(
            "You are not running MySQL (RUN_MYSQL=false). It is your "
            "responsibility to upgrade your MySQL instance to v5.7. There is "
            "nothing left to do to upgrade from Juniper."
        )
        return

    message = """Automatic release upgrade is unsupported in Kubernetes. To upgrade from Juniper, you should upgrade
your MySQL database from v5.6 to v5.7. You should run something similar to:

    tutor k8s start
    tutor k8s exec mysql bash -e -c "mysql_upgrade \
        -u $(tutor config printvalue MYSQL_ROOT_USERNAME) \
        --password='$(tutor config printvalue MYSQL_ROOT_PASSWORD)'
"""
    fmt.echo_info(message)


def upgrade_from_koa(config: Config) -> None:
    if not config["RUN_MONGODB"]:
        fmt.echo_info(
            "You are not running MongDB (RUN_MONGODB=false). It is your "
            "responsibility to upgrade your MongoDb instance to v4.0. There is "
            "nothing left to do to upgrade to Lilac from Koa."
        )
        return
    message = """Automatic release upgrade is unsupported in Kubernetes. To upgrade from Koa to Lilac, you should upgrade
your MongoDb cluster from v3.6 to v4.0. You should run something similar to:

    tutor k8s stop
    tutor config save --set DOCKER_IMAGE_MONGODB=mongo:4.0.25
    tutor k8s start
    tutor k8s exec mongodb mongo --eval 'db.adminCommand({ setFeatureCompatibilityVersion: "4.0" })'
    tutor config save --unset DOCKER_IMAGE_MONGODB
    """
    fmt.echo_info(message)


def upgrade_from_lilac(config: Config) -> None:
    fmt.echo_info(
        "All Kubernetes services and deployments need to be deleted during "
        "upgrade from Lilac to Maple"
    )
    k8s.delete_resources(config, resources=["deployments", "services"])
