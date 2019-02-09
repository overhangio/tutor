import click

from . import env as tutor_env
from . import opts
from . import utils


@click.group(
    help="Run Open edX platform with development settings",
)
def dev():
    pass

@click.command(
    help="Run a command in one of the containers",
    context_settings={"ignore_unknown_options": True},
)
@opts.root
@opts.edx_platform_path
@opts.edx_platform_settings
@click.argument("service")
@click.argument("command", default=None, required=False)
@click.argument("args", nargs=-1, required=False)
def run(root, edx_platform_path, edx_platform_settings, service, command, args):
    run_command = [service]
    if command:
        run_command.append(command)
    if args:
        run_command += args
    port = service_port(service)
    docker_compose_run_with_port(
        root, edx_platform_path, edx_platform_settings, port, *run_command
    )

@click.command(
    help="Run a development server",
)
@opts.root
@opts.edx_platform_path
@opts.edx_platform_settings
@click.argument("service", type=click.Choice(["lms", "cms"]))
def runserver(root, edx_platform_path, edx_platform_settings, service):
    port = service_port(service)
    docker_compose_run_with_port(
        root, edx_platform_path, edx_platform_settings, port,
        service, "./manage.py", "runserver", "0.0.0.0:{}".format(port),
    )

@click.command(
    help="Launch a shell",
)
@opts.root
@opts.edx_platform_path
@opts.edx_platform_settings
@click.argument("service", type=click.Choice(["lms", "cms"]))
def shell(root, edx_platform_path, edx_platform_settings, service):
    port = service_port(service)
    docker_compose_run_with_port(
        root, edx_platform_path, edx_platform_settings, port,
        service, "bash"
    )

@click.command(
    help="Watch for changes in your themes and recompile assets when needed"
)
@opts.root
@opts.edx_platform_path
@opts.edx_platform_settings
def watchthemes(root, edx_platform_path, edx_platform_settings):
    docker_compose_run(
        root, edx_platform_path, edx_platform_settings,
        "--no-deps", "lms", "openedx-assets", "watch-themes", "--env", "dev"
    )

def docker_compose_run_with_port(root, edx_platform_path, edx_platform_settings, port, *command):
    docker_compose_run(
        root, edx_platform_path, edx_platform_settings,
        "-p", "{port}:{port}".format(port=port), *command
    )

def docker_compose_run(root, edx_platform_path, edx_platform_settings, *command):
    run_command = [
        "run", "--rm",
        "-e", "SETTINGS={}".format(edx_platform_settings),
    ]
    if edx_platform_path:
        run_command.append("--volume={}:/openedx/edx-platform".format(edx_platform_path))
    run_command += command
    return utils.docker_compose(
        "-f", tutor_env.pathjoin(root, "local", "docker-compose.yml"),
        "--project-name", "tutor_dev",
        *run_command
    )

def service_port(service):
    return 8000 if service == "lms" else 8001

dev.add_command(run)
dev.add_command(runserver)
dev.add_command(shell)
dev.add_command(watchthemes)
