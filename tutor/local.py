import os
import subprocess
from textwrap import indent
from time import sleep

import click

from . import config as tutor_config
from . import env as tutor_env
from . import exceptions
from . import fmt
from . import opts
from . import scripts
from . import utils


@click.group(
    short_help="Run Open edX locally",
    help="Run Open edX platform locally, with docker-compose.",
)
def local():
    pass


@click.command(help="Configure and run Open edX from scratch")
@click.option(
    "-p", "--pullimages", "pullimages_", is_flag=True, help="Update docker images"
)
@opts.root
def quickstart(pullimages_, root):
    click.echo(fmt.title("Interactive platform configuration"))
    tutor_config.save(root)
    click.echo(fmt.title("Stopping any existing platform"))
    stop.callback(root)
    if pullimages_:
        click.echo(fmt.title("Docker image updates"))
        pullimages.callback(root)
    click.echo(fmt.title("Database creation and migrations"))
    databases.callback(root)
    click.echo(fmt.title("HTTPS certificates generation"))
    https_create.callback(root)
    click.echo(fmt.title("Starting the platform in detached mode"))
    start.callback(root, True)


@click.command(help="Update docker images")
@opts.root
def pullimages(root):
    config = tutor_config.load(root)
    docker_compose(root, config, "pull")


@click.command(help="Run all configured Open edX services")
@opts.root
@click.option("-d", "--detach", is_flag=True, help="Start in daemon mode")
def start(root, detach):
    command = ["up", "--remove-orphans"]
    if detach:
        command.append("-d")

    config = tutor_config.load(root)
    docker_compose(root, config, *command)

    if detach:
        click.echo(fmt.info("The Open edX platform is now running in detached mode"))
        http = "https" if config["ACTIVATE_HTTPS"] else "http"
        urls = []
        if not config["ACTIVATE_HTTPS"] and not config["WEB_PROXY"]:
            urls += ["http://localhost", "http://studio.localhost"]
        urls.append(
            "{http}://{lms_host}".format(http=http, lms_host=config["LMS_HOST"])
        )
        urls.append(
            "{http}://{cms_host}".format(http=http, cms_host=config["CMS_HOST"])
        )
        click.echo(
            fmt.info(
                """Your Open edX platform is ready and can be accessed at the following urls:

    {}""".format(
                    "\n    ".join(urls)
                )
            )
        )


@click.command(help="Stop a running platform")
@opts.root
def stop(root):
    config = tutor_config.load(root)
    docker_compose(root, config, "rm", "--stop", "--force")


@click.command(
    help="""Restart some components from a running platform.
You may specify 'openedx' to restart the lms, cms and workers, or 'all' to
restart all services."""
)
@opts.root
@click.argument("service")
def restart(root, service):
    config = tutor_config.load(root)
    command = ["restart"]
    if service == "openedx":
        if config["ACTIVATE_LMS"]:
            command += ["lms", "lms_worker"]
        if config["ACTIVATE_CMS"]:
            command += ["cms", "cms_worker"]
    elif service != "all":
        command += [service]
    docker_compose(root, config, *command)


@click.command(
    help="Run a command in one of the containers",
    context_settings={"ignore_unknown_options": True},
)
@opts.root
@click.argument("service")
@click.argument("command", default=None, required=False)
@click.argument("args", nargs=-1, required=False)
def run(root, service, command, args):
    run_command = ["run", "--rm", service]
    if command:
        run_command.append(command)
    if args:
        run_command += args
    config = tutor_config.load(root)
    docker_compose(root, config, *run_command)


@click.command(
    help="Exec a command in a running container",
    context_settings={"ignore_unknown_options": True},
)
@opts.root
@click.argument("service")
@click.argument("command")
@click.argument("args", nargs=-1, required=False)
def execute(root, service, command, args):
    exec_command = ["exec", service, command]
    if args:
        exec_command += args
    config = tutor_config.load(root)
    docker_compose(root, config, *exec_command)


@click.command(help="Create databases and run database migrations")
@opts.root
def databases(root):
    init_mysql(root)
    scripts.migrate(root, run_sh)


def init_mysql(root):
    config = tutor_config.load(root)
    if not config["ACTIVATE_MYSQL"]:
        return
    mysql_data_path = tutor_env.data_path(root, "mysql", "mysql")
    if os.path.exists(mysql_data_path):
        return
    click.echo(fmt.info("Initializing MySQL database..."))
    docker_compose(root, config, "up", "-d", "mysql")
    while True:
        click.echo(fmt.info("    waiting for mysql initialization"))
        # TODO this is duplicate code with the docker_compose function. We
        # should rely on a dedicated function in utils module.
        mysql_logs = subprocess.check_output(
            [
                "docker-compose",
                "-f",
                tutor_env.pathjoin(root, "local", "docker-compose.yml"),
                "--project-name",
                config["LOCAL_PROJECT_NAME"],
                "logs",
                "mysql",
            ]
        )
        # pylint: disable=unsupported-membership-test
        if b"MySQL init process done. Ready for start up." in mysql_logs:
            click.echo(fmt.info("MySQL database initialized"))
            docker_compose(root, config, "stop", "mysql")
            return
        sleep(4)


@click.group(help="Manage https certificates")
def https():
    pass


@click.command(help="Create https certificates", name="create")
@opts.root
def https_create(root):
    """
    Note: there are a couple issues with https certificate generation.
    1. Certificates are generated and renewed by using port 80, which is not necessarily open.
        a. It may be occupied by the nginx container
        b. It may be occupied by an external web server
    2. On certificate renewal, nginx is not reloaded
    """
    config = tutor_config.load(root)
    if not config["ACTIVATE_HTTPS"]:
        click.echo(fmt.info("HTTPS is not activated: certificate generation skipped"))
        return

    script = scripts.render_template(config, "https_create.sh")

    if config["WEB_PROXY"]:
        click.echo(
            fmt.info(
                """You are running Tutor behind a web proxy (WEB_PROXY=true): SSL/TLS
certificates must be generated on the host. For instance, to generate
certificates with Let's Encrypt, run:

{}

See the official certbot documentation for your platform: https://certbot.eff.org/""".format(
                    indent(script, "    ")
                )
            )
        )
        return

    utils.docker_run(
        "--volume",
        "{}:/etc/letsencrypt/".format(tutor_env.data_path(root, "letsencrypt")),
        "-p",
        "80:80",
        "--entrypoint=sh",
        "certbot/certbot:latest",
        "-e",
        "-c",
        script,
    )


@click.command(help="Renew https certificates", name="renew")
@opts.root
def https_renew(root):
    config = tutor_config.load(root)
    if not config["ACTIVATE_HTTPS"]:
        click.echo(fmt.info("HTTPS is not activated: certificate renewal skipped"))
        return
    if config["WEB_PROXY"]:
        click.echo(
            fmt.info(
                """You are running Tutor behind a web proxy (WEB_PROXY=true): SSL/TLS
certificates must be renewed on the host. For instance, to renew Let's Encrypt
certificates, run:

    certbot renew

See the official certbot documentation for your platform: https://certbot.eff.org/"""
            )
        )
        return
    docker_run = [
        "--volume",
        "{}:/etc/letsencrypt/".format(tutor_env.data_path(root, "letsencrypt")),
        "-p",
        "80:80",
        "certbot/certbot:latest",
        "renew",
    ]
    utils.docker_run(*docker_run)


@click.command(help="View output from containers")
@opts.root
@click.option("-f", "--follow", is_flag=True, help="Follow log output")
@click.option("--tail", type=int, help="Number of lines to show from each container")
@click.argument("service", nargs=-1, required=False)
def logs(root, follow, tail, service):
    command = ["logs"]
    if follow:
        command += ["--follow"]
    if tail is not None:
        command += ["--tail", str(tail)]
    command += service
    config = tutor_config.load(root)
    docker_compose(root, config, *command)


@click.command(help="Create an Open edX user and interactively set their password")
@opts.root
@click.option("--superuser", is_flag=True, help="Make superuser")
@click.option("--staff", is_flag=True, help="Make staff user")
@click.argument("name")
@click.argument("email")
def createuser(root, superuser, staff, name, email):
    config = tutor_config.load(root)
    check_service_is_activated(config, "lms")
    scripts.create_user(root, run_sh, superuser, staff, name, email)


@click.command(help="Import the demo course")
@opts.root
def importdemocourse(root):
    config = tutor_config.load(root)
    check_service_is_activated(config, "cms")
    click.echo(fmt.info("Importing demo course"))
    scripts.import_demo_course(root, run_sh)
    click.echo(fmt.info("Re-indexing courses"))
    indexcourses.callback(root)


@click.command(help="Re-index courses for better searching")
@opts.root
def indexcourses(root):
    config = tutor_config.load(root)
    check_service_is_activated(config, "cms")
    scripts.index_courses(root, run_sh)


@click.command(
    help="Run Portainer (https://portainer.io), a UI for container supervision",
    short_help="Run Portainer, a UI for container supervision",
)
@opts.root
@click.option(
    "-p", "--port", type=int, default=9000, show_default=True, help="Bind port"
)
def portainer(root, port):
    docker_run = [
        "--volume=/var/run/docker.sock:/var/run/docker.sock",
        "--volume={}:/data".format(tutor_env.data_path(root, "portainer")),
        "-p",
        "{port}:{port}".format(port=port),
        "portainer/portainer:latest",
        "--bind=:{}".format(port),
    ]
    click.echo(
        fmt.info("View the Portainer UI at http://localhost:{port}".format(port=port))
    )
    utils.docker_run(*docker_run)


def check_service_is_activated(config, service):
    if not config["ACTIVATE_" + service.upper()]:
        raise exceptions.TutorError(
            "This command may only be executed on the server where the {} is running".format(
                service
            )
        )


def run_sh(root, service, command):
    config = tutor_config.load(root)
    docker_compose(root, config, "run", "--rm", service, "sh", "-e", "-c", command)


def docker_compose(root, config, *command):
    return utils.docker_compose(
        "-f",
        tutor_env.pathjoin(root, "local", "docker-compose.yml"),
        "--project-name",
        config["LOCAL_PROJECT_NAME"],
        *command
    )


https.add_command(https_create)
https.add_command(https_renew)

local.add_command(quickstart)
local.add_command(pullimages)
local.add_command(start)
local.add_command(stop)
local.add_command(restart)
local.add_command(run)
local.add_command(execute, name="exec")
local.add_command(databases)
local.add_command(https)
local.add_command(logs)
local.add_command(createuser)
local.add_command(importdemocourse)
local.add_command(indexcourses)
local.add_command(portainer)
