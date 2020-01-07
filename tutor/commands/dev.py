import click

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
    help="Mount a local edx-platform from the host (environment variable: TUTOR_EDX_PLATFORM_PATH)",
)


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
    docker_compose_run(
        context.root, edx_platform_path, edx_platform_settings, *run_command
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
    docker_compose(context.root, *exec_command)


@click.command(help="Run a development server")
@edx_platform_path_option
@edx_platform_development_settings_option
@click.argument("service", type=click.Choice(["lms", "cms"]))
@click.pass_obj
def runserver(context, edx_platform_path, edx_platform_settings, service):
    port = service_port(service)

    fmt.echo_info(
        "The {} service will be available at http://localhost:{}".format(service, port)
    )
    docker_compose_run(
        context.root,
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
    docker_compose(context.root, "rm", "--stop", "--force")


def docker_compose_run(root, edx_platform_path, edx_platform_settings, *command):
    run_command = ["run", "--rm", "-e", "SETTINGS={}".format(edx_platform_settings)]
    if edx_platform_path:
        run_command += ["--volume={}:/openedx/edx-platform".format(edx_platform_path)]
    run_command += command
    docker_compose(root, *run_command)


def docker_compose(root, *command):
    return utils.docker_compose(
        "-f",
        tutor_env.pathjoin(root, "local", "docker-compose.yml"),
        "-f",
        tutor_env.pathjoin(root, "dev", "docker-compose.yml"),
        "--project-name",
        "tutor_dev",
        *command
    )


def service_port(service):
    return 8000 if service == "lms" else 8001


dev.add_command(run)
dev.add_command(execute)
dev.add_command(runserver)
dev.add_command(stop)
