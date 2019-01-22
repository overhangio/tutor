import click

from . import config
from . import env as tutor_env
from . import fmt
from . import opts
from . import utils


DOCKER_IMAGE = "regis/openedx-android:hawthorn"

@click.group(
    help="Build an Android app for your Open edX platform [BETA FEATURE]"
)
def android():
    pass

@click.command(
    help="Generate the environment required for building the application"
)
@opts.root
def env(root):
    tutor_env.render_target(root, config.load(root), "android")

@click.group(
    help="Build the application"
)
def build():
    pass

@click.command(
    help="Build the application in debug mode"
)
@opts.root
def debug(root):
    docker_run(
        root, "./gradlew", "assembleProdDebuggable", "&&",
        "cp", "OpenEdXMobile/build/outputs/apk/prod/debuggable/*.apk", "/openedx/data/"
    )
    click.echo(fmt.info("The debuggable APK file is available in {}".format(tutor_env.data_path(root, "android"))))

@click.command(
    help="Build the application in release mode"
)
@opts.root
def release(root):
    docker_run(root, "./gradlew", "assembleProdRelease")
    click.echo(fmt.info("The production APK file is available in {}".format(tutor_env.data_path(root, "android"))))

@click.command(
    help="Pull the docker image"
)
@opts.root
def pullimage():
    utils.execute("docker", "pull", DOCKER_IMAGE)

def docker_run(root, *command):
    utils.docker_run(
        "--volume={}/:/openedx/config/".format(tutor_env.pathjoin(root, "android")),
        "--volume={}:/openedx/data".format(tutor_env.data_path(root, "android")),
        DOCKER_IMAGE,
        *command
    )

build.add_command(debug)
build.add_command(release)
android.add_command(build)
android.add_command(env)
android.add_command(pullimage)
