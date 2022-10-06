import typing as t

import click

from tutor import config as tutor_config
from tutor import env as tutor_env
from tutor import exceptions, hooks, images
from tutor.commands.context import Context
from tutor.types import Config

BASE_IMAGE_NAMES = ["openedx", "permissions"]
VENDOR_IMAGES = [
    "caddy",
    "elasticsearch",
    "mongodb",
    "mysql",
    "redis",
    "smtp",
]


@hooks.Filters.IMAGES_BUILD.add()
def _add_core_images_to_build(
    build_images: t.List[t.Tuple[str, t.Tuple[str, ...], str, t.Tuple[str, ...]]],
    config: Config,
) -> t.List[t.Tuple[str, t.Tuple[str, ...], str, t.Tuple[str, ...]]]:
    """
    Add base images to the list of Docker images to build on `tutor build all`.
    """
    for image in BASE_IMAGE_NAMES:
        tag = images.get_tag(config, image)
        build_images.append((image, ("build", image), tag, ()))
    return build_images


@hooks.Filters.IMAGES_PULL.add()
def _add_images_to_pull(
    remote_images: t.List[t.Tuple[str, str]], config: Config
) -> t.List[t.Tuple[str, str]]:
    """
    Add base and vendor images to the list of Docker images to pull on `tutor pull all`.
    """
    for image in VENDOR_IMAGES:
        if config.get(f"RUN_{image.upper()}", True):
            remote_images.append((image, images.get_tag(config, image)))
    for image in BASE_IMAGE_NAMES:
        remote_images.append((image, images.get_tag(config, image)))
    return remote_images


@hooks.Filters.IMAGES_PUSH.add()
def _add_core_images_to_push(
    remote_images: t.List[t.Tuple[str, str]], config: Config
) -> t.List[t.Tuple[str, str]]:
    """
    Add base images to the list of Docker images to push on `tutor push all`.
    """
    for image in BASE_IMAGE_NAMES:
        remote_images.append((image, images.get_tag(config, image)))
    return remote_images


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
    image_names: t.List[str],
    no_cache: bool,
    build_args: t.List[str],
    add_hosts: t.List[str],
    target: str,
    docker_args: t.List[str],
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
        for _name, path, tag, custom_args in find_images_to_build(config, image):
            images.build(
                tutor_env.pathjoin(context.root, *path),
                tag,
                *command_args,
                *custom_args,
            )


@click.command(short_help="Pull images from the Docker registry")
@click.argument("image_names", metavar="image", nargs=-1)
@click.pass_obj
def pull(context: Context, image_names: t.List[str]) -> None:
    config = tutor_config.load_full(context.root)
    for image in image_names:
        for tag in find_remote_image_tags(config, hooks.Filters.IMAGES_PULL, image):
            images.pull(tag)


@click.command(short_help="Push images to the Docker registry")
@click.argument("image_names", metavar="image", nargs=-1)
@click.pass_obj
def push(context: Context, image_names: t.List[str]) -> None:
    config = tutor_config.load_full(context.root)
    for image in image_names:
        for tag in find_remote_image_tags(config, hooks.Filters.IMAGES_PUSH, image):
            images.push(tag)


@click.command(short_help="Print tag associated to a Docker image")
@click.argument("image_names", metavar="image", nargs=-1)
@click.pass_obj
def printtag(context: Context, image_names: t.List[str]) -> None:
    config = tutor_config.load_full(context.root)
    for image in image_names:
        for _name, _path, tag, _args in find_images_to_build(config, image):
            print(tag)


def find_images_to_build(
    config: Config, image: str
) -> t.Iterator[t.Tuple[str, t.Tuple[str, ...], str, t.Tuple[str, ...]]]:
    """
    Iterate over all images to build.

    If no corresponding image is found, raise exception.

    Yield: (name, path, tag, build args)
    """
    found = False
    for name, path, tag, args in hooks.Filters.IMAGES_BUILD.iterate(config):
        if image in [name, "all"]:
            found = True
            tag = tutor_env.render_str(config, tag)
            yield (name, path, tag, args)

    if not found:
        raise ImageNotFoundError(image)


def find_remote_image_tags(
    config: Config,
    filtre: "hooks.filters.Filter[t.List[t.Tuple[str, str]], [Config]]",
    image: str,
) -> t.Iterator[str]:
    """
    Iterate over all images to push or pull.

    If no corresponding image is found, raise exception.

    Yield: tag
    """
    all_remote_images = filtre.iterate(config)
    found = False
    for name, tag in all_remote_images:
        if image in [name, "all"]:
            found = True
            yield tutor_env.render_str(config, tag)
    if not found:
        raise ImageNotFoundError(image)


class ImageNotFoundError(exceptions.TutorError):
    def __init__(self, image_name: str):
        super().__init__(f"Image '{image_name}' could not be found")


images_command.add_command(build)
images_command.add_command(pull)
images_command.add_command(push)
images_command.add_command(printtag)
