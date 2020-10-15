import os
from textwrap import indent

import click

from . import compose
from .context import Context
from .. import config as tutor_config
from .. import env as tutor_env
from .. import fmt
from .. import interactive as interactive_config
from .. import utils


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
    config = interactive_config.update(context.root, interactive=(not non_interactive))
    click.echo(fmt.title("Updating the current environment"))
    tutor_env.save(context.root, config)
    click.echo(fmt.title("Stopping any existing platform"))
    compose.stop.callback([])
    click.echo(fmt.title("HTTPS certificates generation"))
    https_create.callback()
    if pullimages_:
        click.echo(fmt.title("Docker image updates"))
        compose.pullimages.callback()
    click.echo(fmt.title("Starting the platform in detached mode"))
    compose.start.callback(True, [])
    click.echo(fmt.title("Database creation and migrations"))
    compose.init.callback(limit=None)

    fmt.echo_info(
        """The Open edX platform is now running in detached mode
Your Open edX platform is ready and can be accessed at the following urls:

    {http}://{lms_host}
    {http}://{cms_host}
    """.format(
            http="https" if config["ACTIVATE_HTTPS"] else "http",
            lms_host=config["LMS_HOST"],
            cms_host=config["CMS_HOST"],
        )
    )


@click.group(help="Manage https certificates")
def https():
    pass


@click.command(help="Create https certificates", name="create")
@click.pass_obj
def https_create(context):
    """
    Note: there are a couple issues with https certificate generation.
    1. Certificates are generated and renewed by using port 80, which is not necessarily open.
        a. It may be occupied by the nginx container
        b. It may be occupied by an external web server
    2. On certificate renewal, nginx is not reloaded
    """
    config = tutor_config.load(context.root)
    runner = compose.ScriptRunner(context.root, config, context.docker_compose)
    if not config["ACTIVATE_HTTPS"]:
        fmt.echo_info("HTTPS is not activated: certificate generation skipped")
        return

    script = runner.render("hooks", "certbot", "create")

    if config["WEB_PROXY"]:
        fmt.echo_info(
            """You are running Tutor behind a web proxy (WEB_PROXY=true): SSL/TLS
certificates must be generated on the host. For instance, to generate
certificates with Let's Encrypt, run:

{}

See the official certbot documentation for your platform: https://certbot.eff.org/""".format(
                indent(script, "    ")
            )
        )
        return

    utils.docker_run(
        "--volume",
        "{}:/etc/letsencrypt/".format(tutor_env.data_path(context.root, "letsencrypt")),
        "-p",
        "80:80",
        "--entrypoint=sh",
        "docker.io/certbot/certbot:latest",
        "-e",
        "-c",
        script,
    )


@click.command(help="Renew https certificates", name="renew")
@click.pass_obj
def https_renew(context):
    config = tutor_config.load(context.root)
    if not config["ACTIVATE_HTTPS"]:
        fmt.echo_info("HTTPS is not activated: certificate renewal skipped")
        return
    if config["WEB_PROXY"]:
        fmt.echo_info(
            """You are running Tutor behind a web proxy (WEB_PROXY=true): SSL/TLS
certificates must be renewed on the host. For instance, to renew Let's Encrypt
certificates, run:

    certbot renew

See the official certbot documentation for your platform: https://certbot.eff.org/"""
        )
        return
    docker_run = [
        "--volume",
        "{}:/etc/letsencrypt/".format(tutor_env.data_path(context.root, "letsencrypt")),
        "-p",
        "80:80",
        "certbot/certbot:latest",
        "renew",
    ]
    utils.docker_run(*docker_run)


@click.command(help="Upgrade from a previous Open edX named release")
@click.option(
    "--from", "from_version", default="ironwood", type=click.Choice(["ironwood"])
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

    if from_version == "ironwood":
        upgrade_from_ironwood(context, config)


def upgrade_from_ironwood(context, config):
    click.echo(fmt.title("Upgrading from Ironwood"))
    tutor_env.save(context.root, config)

    click.echo(fmt.title("Stopping any existing platform"))
    compose.stop.callback([])

    if not config["ACTIVATE_MONGODB"]:
        fmt.echo_info(
            "You are not running MongDB (ACTIVATE_MONGODB=false). It is your "
            "responsibility to upgrade your MongoDb instance to v3.6. There is "
            "nothing left to do."
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


https.add_command(https_create)
https.add_command(https_renew)
local.add_command(https)
local.add_command(quickstart)
local.add_command(upgrade)
compose.add_commands(local)
