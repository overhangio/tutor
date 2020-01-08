import click

from .. import config as tutor_config
from .. import env as tutor_env
from .. import fmt
from .. import utils


@click.group(help="Run Open edX platform with development settings")
def dev():
    pass


edx_platform_path_option = click.option(
    "-P",
    "--edx-platform-path",
    envvar="TUTOR_EDX_PLATFORM_PATH",
    type=click.Path(exists=True, dir_okay=True, resolve_path=True),
    help="Mount a local edx-platform from the host (environment variable: TUTOR_EDX_PLATFORM_PATH)",
)

edx_platform_development_settings_option = click.option(
    "-S",
    "--edx-platform-settings",
    envvar="TUTOR_EDX_PLATFORM_SETTINGS",
    default="tutor.development",
    help="Load custom development settings (environment variable: TUTOR_EDX_PLATFORM_SETTINGS)",
)


@click.command(
    help="Run all or a selection of configured Open edX services in development mode"
)
@click.option("-d", "--detach", is_flag=True, help="Start in daemon mode")
@click.argument("services", metavar="service", nargs=-1)
@click.pass_obj
def start(context, detach, services):
    """
    TODO document this
    """
    command = ["up", "--remove-orphans"]
    if detach:
        command.append("-d")

    config = tutor_config.load(context.root)
    docker_compose(context.root, config, *command, *services)


@click.command(
    help="Run a command in one of the containers",
    context_settings={"ignore_unknown_options": True},
)
@edx_platform_path_option
@edx_platform_development_settings_option
@click.argument("service")
@click.argument("command", default=None, required=False)
@click.argument("args", nargs=-1)
@click.pass_obj
def run(context, edx_platform_path, edx_platform_settings, service, command, args):
    run_command = [service]
    if command:
        run_command.append(command)
    if args:
        run_command += args

    config = tutor_config.load(context.root)
    docker_compose_run(
        context.root, config, edx_platform_path, edx_platform_settings, *run_command
    )


@click.command(
    help="Exec a command in a running container",
    context_settings={"ignore_unknown_options": True},
    name="exec",
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


@click.command(help="Run a development server")
@edx_platform_path_option
@edx_platform_development_settings_option
@click.argument("service", type=click.Choice(["lms", "cms"]))
@click.pass_obj
def runserver(context, edx_platform_path, edx_platform_settings, service):
    port = 8000 if service == "lms" else 8001

    fmt.echo_info(
        "The {} service will be available at http://localhost:{}".format(service, port)
    )
    config = tutor_config.load(context.root)
    docker_compose_run(
        context.root,
        config,
        edx_platform_path,
        edx_platform_settings,
        "-p",
        "{port}:{port}".format(port=port),
        service,
        "./manage.py",
        service,
        "runserver",
        "0.0.0.0:{}".format(port),
    )


@click.command(help="Stop a running development platform")
@click.pass_obj
def stop(context):
    config = tutor_config.load(context.root)
    docker_compose(context.root, config, "rm", "--stop", "--force")


def docker_compose_run(
    root, config, edx_platform_path, edx_platform_settings, *command
):
    run_command = ["run", "--rm", "-e", "SETTINGS={}".format(edx_platform_settings)]
    if edx_platform_path:
        run_command += ["--volume={}:/openedx/edx-platform".format(edx_platform_path)]
    run_command += command
    docker_compose(root, config, *run_command)


def docker_compose(root, config, *command):
    return utils.docker_compose(
        "-f",
        tutor_env.pathjoin(root, "local", "docker-compose.yml"),
        "-f",
        tutor_env.pathjoin(root, "dev", "docker-compose.yml"),
        "--project-name",
        config["DEV_PROJECT_NAME"],
        *command
    )


dev.add_command(start)
dev.add_command(run)
dev.add_command(execute)
dev.add_command(runserver)
dev.add_command(stop)
