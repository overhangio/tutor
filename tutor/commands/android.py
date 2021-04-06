import click

from .compose import ComposeJobRunner
from .local import docker_compose as local_docker_compose
from .. import config as tutor_config
from .. import env as tutor_env
from .. import fmt
from ..types import Config
from .context import Context


@click.group(help="Build an Android app for your Open edX platform [BETA FEATURE]")
def android() -> None:
    pass


@click.command(help="Build the application")
@click.argument("mode", type=click.Choice(["debug", "release"]))
@click.pass_obj
def build(context: Context, mode: str) -> None:
    config = tutor_config.load(context.root)
    docker_run(context.root, build_command(config, mode))
    fmt.echo_info(
        "The {} APK file is available in {}".format(
            mode, tutor_env.data_path(context.root, "android")
        )
    )


def build_command(config: Config, target: str) -> str:
    gradle_target = {
        "debug": "assembleProdDebuggable",
        "release": "assembleProdRelease",
    }[target]
    apk_folder = {"debug": "debuggable", "release": "release"}[target]

    command = """
sed -i "s/APPLICATION_ID = .*/APPLICATION_ID = \\"{{ LMS_HOST|reverse_host|replace("-", "_") }}\\"/g" constants.gradle
./gradlew {gradle_target}
cp OpenEdXMobile/build/outputs/apk/prod/{apk_folder}/*.apk /openedx/data/"""
    command = tutor_env.render_str(config, command)
    command = command.format(gradle_target=gradle_target, apk_folder=apk_folder)
    return command


def docker_run(root: str, command: str) -> None:
    config = tutor_config.load(root)
    runner = ComposeJobRunner(root, config, local_docker_compose)
    runner.run_job("android", command)


android.add_command(build)
