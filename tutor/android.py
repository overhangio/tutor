import click

from . import config as tutor_config
from . import env as tutor_env
from . import fmt
from . import opts
from . import utils


@click.group(help="Build an Android app for your Open edX platform [BETA FEATURE]")
def android():
    pass


@click.group(help="Build the application")
def build():
    pass


@click.command(help="Build the application in debug mode")
@opts.root
def debug(root):
    docker_run(root)
    click.echo(
        fmt.info(
            "The debuggable APK file is available in {}".format(
                tutor_env.data_path(root, "android")
            )
        )
    )


@click.command(help="Build the application in release mode")
@opts.root
def release(root):
    docker_run(root, "./gradlew", "assembleProdRelease")
    click.echo(
        fmt.info(
            "The production APK file is available in {}".format(
                tutor_env.data_path(root, "android")
            )
        )
    )


@click.command(help="Pull the docker image")
@opts.root
def pullimage(root):
    config = tutor_config.load(root)
    utils.execute("docker", "pull", config["DOCKER_IMAGE_ANDROID"])


def docker_run(root, *command):
    config = tutor_config.load(root)
    utils.docker_run(
        "--volume={}:/openedx/config/".format(tutor_env.pathjoin(root, "android")),
        "--volume={}:/openedx/data/".format(tutor_env.data_path(root, "android")),
        config["DOCKER_IMAGE_ANDROID"],
        *command
    )


build.add_command(debug)
build.add_command(release)
android.add_command(build)
android.add_command(pullimage)
