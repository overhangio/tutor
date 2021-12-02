from typing import Iterator, List, Tuple

import click

from .. import config as tutor_config
from .. import env as tutor_env
from .. import exceptions
from .. import images
from .. import plugins
from ..types import Config
from .context import Context

BASE_IMAGE_NAMES = ["openedx", "permissions"]
VENDOR_IMAGES = [
    "caddy",
    "elasticsearch",
    "mongodb",
    "mysql",
    "redis",
    "smtp",
]


@click.group(name="images", short_help="Manage docker images")
def images_command() -> None:
    pass


@click.command(
    short_help="Build docker images",
    help="Build the docker images necessary for an Open edX platform.",
)
@click.argument("image_names", metavar="image", nargs=-1)
@click.option(
    "--no-cache", is_flag=True, help="Do not use cache when building the image"
)
@click.option(
    "-a",
    "--build-arg",
    "build_args",
    multiple=True,
    help="Set build-time docker ARGS in the form 'myarg=value'. This option may be specified multiple times.",
)
@click.option(
    "--add-host",
    "add_hosts",
    multiple=True,
    help="Set a custom host-to-IP mapping (host:ip).",
)
@click.option(
    "--target",
    help="Set the target build stage to build.",
)
@click.option(
    "-d",
    "--docker-arg",
    "docker_args",
    multiple=True,
    help="Set extra options for docker build command.",
)
@click.pass_obj
def build(
    context: Context,
    image_names: List[str],
    no_cache: bool,
    build_args: List[str],
    add_hosts: List[str],
    target: str,
    docker_args: List[str],
) -> None:
    config = tutor_config.load(context.root)
    command_args = []
    if no_cache:
        command_args.append("--no-cache")
    for build_arg in build_args:
        command_args += ["--build-arg", build_arg]
    for add_host in add_hosts:
        command_args += ["--add-host", add_host]
    if target:
        command_args += ["--target", target]
    if docker_args:
        command_args += docker_args
    for image in image_names:
        build_image(context.root, config, image, *command_args)


@click.command(short_help="Pull images from the Docker registry")
@click.argument("image_names", metavar="image", nargs=-1)
@click.pass_obj
def pull(context: Context, image_names: List[str]) -> None:
    config = tutor_config.load(context.root)
    for image in image_names:
        pull_image(config, image)


@click.command(short_help="Push images to the Docker registry")
@click.argument("image_names", metavar="image", nargs=-1)
@click.pass_obj
def push(context: Context, image_names: List[str]) -> None:
    config = tutor_config.load(context.root)
    for image in image_names:
        push_image(config, image)


@click.command(short_help="Print tag associated to a Docker image")
@click.argument("image_names", metavar="image", nargs=-1)
@click.pass_obj
def printtag(context: Context, image_names: List[str]) -> None:
    config = tutor_config.load(context.root)
    for image in image_names:
        to_print = []
        for _img, tag in iter_images(config, image, BASE_IMAGE_NAMES):
            to_print.append(tag)
        for _plugin, _img, tag in iter_plugin_images(config, image, "build-image"):
            to_print.append(tag)

        if not to_print:
            raise ImageNotFoundError(image)

        for tag in to_print:
            print(tag)


def build_image(root: str, config: Config, image: str, *args: str) -> None:
    to_build = []

    # Build base images
    for img, tag in iter_images(config, image, BASE_IMAGE_NAMES):
        to_build.append((tutor_env.pathjoin(root, "build", img), tag, args))

    # Build plugin images
    for plugin, img, tag in iter_plugin_images(config, image, "build-image"):
        to_build.append(
            (tutor_env.pathjoin(root, "plugins", plugin, "build", img), tag, args)
        )

    if not to_build:
        raise ImageNotFoundError(image)

    for path, tag, build_args in to_build:
        images.build(path, tag, *args)


def pull_image(config: Config, image: str) -> None:
    to_pull = []
    for _img, tag in iter_images(config, image, all_image_names(config)):
        to_pull.append(tag)
    for _plugin, _img, tag in iter_plugin_images(config, image, "remote-image"):
        to_pull.append(tag)

    if not to_pull:
        raise ImageNotFoundError(image)

    for tag in to_pull:
        images.pull(tag)


def push_image(config: Config, image: str) -> None:
    to_push = []
    for _img, tag in iter_images(config, image, BASE_IMAGE_NAMES):
        to_push.append(tag)
    for _plugin, _img, tag in iter_plugin_images(config, image, "remote-image"):
        to_push.append(tag)

    if not to_push:
        raise ImageNotFoundError(image)

    for tag in to_push:
        images.push(tag)


def iter_images(
    config: Config, image: str, image_list: List[str]
) -> Iterator[Tuple[str, str]]:
    for img in image_list:
        if image in [img, "all"]:
            tag = images.get_tag(config, img)
            yield img, tag


def iter_plugin_images(
    config: Config, image: str, hook_name: str
) -> Iterator[Tuple[str, str, str]]:
    for plugin, hook in plugins.iter_hooks(config, hook_name):
        if not isinstance(hook, dict):
            raise exceptions.TutorError(
                "Invalid hook '{}': expected dict, got {}".format(
                    hook_name, hook.__class__
                )
            )
        for img, tag in hook.items():
            if image in [img, "all"]:
                tag = tutor_env.render_str(config, tag)
                yield plugin, img, tag


def all_image_names(config: Config) -> List[str]:
    return BASE_IMAGE_NAMES + vendor_image_names(config)


def vendor_image_names(config: Config) -> List[str]:
    vendor_images = VENDOR_IMAGES[:]
    for image in VENDOR_IMAGES:
        if not config.get("RUN_" + image.upper(), True):
            vendor_images.remove(image)
    return vendor_images


class ImageNotFoundError(exceptions.TutorError):
    def __init__(self, image_name: str):
        super().__init__("Image '{}' could not be found".format(image_name))


images_command.add_command(build)
images_command.add_command(pull)
images_command.add_command(push)
images_command.add_command(printtag)
