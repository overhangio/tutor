from textwrap import indent

import click

from .. import config as tutor_config
from .. import env as tutor_env
from .. import fmt
from .. import interactive as interactive_config
from .. import scripts
from .. import utils


@click.group(
    short_help="Run Open edX locally",
    help="Run Open edX platform locally, with docker-compose.",
)
def local():
    pass


@click.command(help="Configure and run Open edX from scratch")
@click.option("-I", "--non-interactive", is_flag=True, help="Run non-interactively")
@click.option(
    "-p", "--pullimages", "pullimages_", is_flag=True, help="Update docker images"
)
@click.pass_obj
def quickstart(context, non_interactive, pullimages_):
    click.echo(fmt.title("Interactive platform configuration"))
    config = interactive_config.update(context.root, interactive=(not non_interactive))
    click.echo(fmt.title("Updating the current environment"))
    tutor_env.save(context.root, config)
    click.echo(fmt.title("Stopping any existing platform"))
    stop.callback([])
    click.echo(fmt.title("HTTPS certificates generation"))
    https_create.callback()
    if pullimages_:
        click.echo(fmt.title("Docker image updates"))
        pullimages.callback()
    click.echo(fmt.title("Starting the platform in detached mode"))
    start.callback(True, [])
    click.echo(fmt.title("Database creation and migrations"))
    init.callback()
    echo_platform_info(config)


@click.command(help="Update docker images")
@click.pass_obj
def pullimages(context):
    config = tutor_config.load(context.root)
    docker_compose(context.root, config, "pull")


@click.command(help="Run all or a selection of configured Open edX services")
@click.option("-d", "--detach", is_flag=True, help="Start in daemon mode")
@click.argument("services", metavar="service", nargs=-1)
@click.pass_obj
def start(context, detach, services):
    command = ["up", "--remove-orphans"]
    if detach:
        command.append("-d")

    config = tutor_config.load(context.root)
    docker_compose(context.root, config, *command, *services)


def echo_platform_info(config):
    fmt.echo_info("The Open edX platform is now running in detached mode")
    http = "https" if config["ACTIVATE_HTTPS"] else "http"
    urls = []
    if not config["ACTIVATE_HTTPS"] and not config["WEB_PROXY"]:
        urls += ["http://localhost", "http://studio.localhost"]
    urls.append("{http}://{lms_host}".format(http=http, lms_host=config["LMS_HOST"]))
    urls.append("{http}://{cms_host}".format(http=http, cms_host=config["CMS_HOST"]))
    fmt.echo_info(
        """Your Open edX platform is ready and can be accessed at the following urls:

    {}""".format(
            "\n    ".join(urls)
        )
    )


@click.command(help="Stop a running platform")
@click.argument("services", metavar="service", nargs=-1)
@click.pass_obj
def stop(context, services):
    config = tutor_config.load(context.root)
    docker_compose(context.root, config, "rm", "--stop", "--force", *services)


@click.command(
    short_help="Reboot an existing platform",
    help="This is more than just a restart: with reboot, the platform is fully stopped before being restarted again",
)
@click.option("-d", "--detach", is_flag=True, help="Start in daemon mode")
@click.argument("services", metavar="service", nargs=-1)
def reboot(detach, services):
    stop.callback(services)
    start.callback(detach, services)


@click.command(
    short_help="Restart some components from a running platform.",
    help="""Specify 'openedx' to restart the lms, cms and workers, or 'all' to
restart all services. Note that this performs a 'docker-compose restart', so new images
may not be taken into account. It is useful for reloading settings, for instance. To
fully stop the platform, use the 'reboot' command.""",
)
@click.argument("service")
@click.pass_obj
def restart(context, service):
    config = tutor_config.load(context.root)
    command = ["restart"]
    if service == "openedx":
        if config["ACTIVATE_LMS"]:
            command += ["lms", "lms_worker"]
        if config["ACTIVATE_CMS"]:
            command += ["cms", "cms_worker"]
    elif service != "all":
        command += [service]
    docker_compose(context.root, config, *command)


@click.command(
    help="Run a command in one of the containers",
    context_settings={"ignore_unknown_options": True},
)
@click.option("--entrypoint", help="Override the entrypoint of the image")
@click.argument("service")
@click.argument("command", default=None, required=False)
@click.argument("args", nargs=-1)
@click.pass_obj
def run(context, entrypoint, service, command, args):
    run_command = ["run", "--rm"]
    if entrypoint:
        run_command += ["--entrypoint", entrypoint]
    run_command.append(service)
    if command:
        run_command.append(command)
    if args:
        run_command += args
    config = tutor_config.load(context.root)
    docker_compose(context.root, config, *run_command)


@click.command(
    help="Exec a command in a running container",
    context_settings={"ignore_unknown_options": True},
)
@click.argument("service")
@click.argument("command")
@click.argument("args", nargs=-1)
@click.pass_obj
def execute(context, service, command, args):
    exec_command = ["exec", service, command]
    if args:
        exec_command += args
    config = tutor_config.load(context.root)
    docker_compose(context.root, config, *exec_command)


@click.command(help="Initialise all applications")
@click.pass_obj
def init(context):
    config = tutor_config.load(context.root)
    runner = ScriptRunner(context.root, config)
    scripts.initialise(runner)


@click.command(
    short_help="Manually trigger hook (advanced users only)",
    help="""
Manually trigger a hook for a given plugin/service. This is a low-level command
that is convenient when developing new plugins. Ex:

    tutor local hook mysql hooks mysql init
    tutor local hook discovery discovery hooks discovery init""",
    name="hook",
)
@click.argument("service")
@click.argument("path", nargs=-1)
@click.pass_obj
def run_hook(context, service, path):
    config = tutor_config.load(context.root)
    runner = ScriptRunner(context.root, config)
    fmt.echo_info(
        "Running '{}' hook in '{}' container...".format(".".join(path), service)
    )
    runner.run(service, *path)


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
    runner = ScriptRunner(context.root, config)
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
        "certbot/certbot:latest",
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


@click.command(help="View output from containers")
@click.option("-f", "--follow", is_flag=True, help="Follow log output")
@click.option("--tail", type=int, help="Number of lines to show from each container")
@click.argument("service", nargs=-1)
@click.pass_obj
def logs(context, follow, tail, service):
    command = ["logs"]
    if follow:
        command += ["--follow"]
    if tail is not None:
        command += ["--tail", str(tail)]
    command += service
    config = tutor_config.load(context.root)
    docker_compose(context.root, config, *command)


@click.command(help="Create an Open edX user and interactively set their password")
@click.option("--superuser", is_flag=True, help="Make superuser")
@click.option("--staff", is_flag=True, help="Make staff user")
@click.option(
    "-p",
    "--password",
    help="Specify password from the command line. If undefined, you will be prompted to input a password",
)
@click.argument("name")
@click.argument("email")
@click.pass_obj
def createuser(context, superuser, staff, password, name, email):
    config = tutor_config.load(context.root)
    runner = ScriptRunner(context.root, config)
    runner.check_service_is_activated("lms")
    command = scripts.create_user_command(
        superuser, staff, name, email, password=password
    )
    runner.exec("lms", command)


@click.command(help="Import the demo course")
@click.pass_obj
def importdemocourse(context):
    config = tutor_config.load(context.root)
    runner = ScriptRunner(context.root, config)
    fmt.echo_info("Importing demo course")
    scripts.import_demo_course(runner)


class ScriptRunner(scripts.BaseRunner):
    def exec(self, service, command):
        docker_compose(
            self.root, self.config, "exec", service, "sh", "-e", "-c", command
        )


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
local.add_command(reboot)
local.add_command(run)
local.add_command(execute, name="exec")
local.add_command(init)
local.add_command(run_hook)
local.add_command(https)
local.add_command(logs)
local.add_command(createuser)
local.add_command(importdemocourse)
