from __future__ import annotations

import os
import typing as t

import click

from tutor import bindmount
from tutor import config as tutor_config
from tutor import env as tutor_env
from tutor import exceptions, fmt, hooks, images, utils
from tutor.commands.context import Context
from tutor.commands.params import ConfigLoaderParam
from tutor.core.hooks import Filter
from tutor.types import Config

BASE_IMAGE_NAMES = [
    ("openedx", "DOCKER_IMAGE_OPENEDX"),
    ("permissions", "DOCKER_IMAGE_PERMISSIONS"),
]


@hooks.Filters.IMAGES_BUILD.add()
def _add_core_images_to_build(
    build_images: list[tuple[str, t.Union[str, tuple[str, ...]], str, tuple[str, ...]]],
    config: Config,
) -> list[tuple[str, t.Union[str, tuple[str, ...]], str, tuple[str, ...]]]:
    """
    Add base images to the list of Docker images to build on `tutor build all`.
    """
    for image, tag in BASE_IMAGE_NAMES:
        build_images.append(
            (
                image,
                os.path.join("build", image),
                tutor_config.get_typed(config, tag, str),
                (),
            )
        )

    # Build openedx-dev image
    build_images.append(
        (
            "openedx-dev",
            os.path.join("build", "openedx"),
            tutor_config.get_typed(config, "DOCKER_IMAGE_OPENEDX_DEV", str),
            (
                "--target=development",
                f"--build-arg=APP_USER_ID={utils.get_user_id() or 1000}",
            ),
        )
    )

    return build_images


@hooks.Filters.IMAGES_PULL.add()
def _add_images_to_pull(
    remote_images: list[tuple[str, str]], config: Config
) -> list[tuple[str, str]]:
    """
    Add base and vendor images to the list of Docker images to pull on `tutor pull all`.
    """
    vendor_images = [
        ("caddy", "DOCKER_IMAGE_CADDY"),
        ("elasticsearch", "DOCKER_IMAGE_ELASTICSEARCH"),
        ("mongodb", "DOCKER_IMAGE_MONGODB"),
        ("mysql", "DOCKER_IMAGE_MYSQL"),
        ("redis", "DOCKER_IMAGE_REDIS"),
        ("smtp", "DOCKER_IMAGE_SMTP"),
    ]
    for image, tag_name in vendor_images:
        if config.get(f"RUN_{image.upper()}", True):
            remote_images.append((image, tutor_config.get_typed(config, tag_name, str)))
    for image, tag in BASE_IMAGE_NAMES:
        remote_images.append((image, tutor_config.get_typed(config, tag, str)))
    return remote_images


@hooks.Filters.IMAGES_PUSH.add()
def _add_core_images_to_push(
    remote_images: list[tuple[str, str]], config: Config
) -> list[tuple[str, str]]:
    """
    Add base images to the list of Docker images to push on `tutor push all`.
    """
    for image, tag in BASE_IMAGE_NAMES:
        remote_images.append((image, tutor_config.get_typed(config, tag, str)))
    return remote_images


class ImageNameParam(ConfigLoaderParam):
    """
    Convenient auto-completion of image names.
    """

    def shell_complete(
        self, ctx: click.Context, param: click.Parameter, incomplete: str
    ) -> list[click.shell_completion.CompletionItem]:
        results = []
        for name in self.iter_image_names():
            if name.startswith(incomplete):
                results.append(click.shell_completion.CompletionItem(name))
        return results

    def iter_image_names(self) -> t.Iterable["str"]:
        raise NotImplementedError


class BuildImageNameParam(ImageNameParam):
    def iter_image_names(self) -> t.Iterable["str"]:
        for name, _path, _tag, _args in hooks.Filters.IMAGES_BUILD.iterate(self.config):
            yield name


class PullImageNameParam(ImageNameParam):
    def iter_image_names(self) -> t.Iterable["str"]:
        for name, _tag in hooks.Filters.IMAGES_PULL.iterate(self.config):
            yield name


class PushImageNameParam(ImageNameParam):
    def iter_image_names(self) -> t.Iterable["str"]:
        for name, _tag in hooks.Filters.IMAGES_PUSH.iterate(self.config):
            yield name


@click.group(name="images", short_help="Manage docker images")
def images_command() -> None:
    pass


@click.command()
@click.argument(
    "image_names",
    metavar="image",
    nargs=-1,
    type=BuildImageNameParam(),
)
@click.option(
    "--no-cache", is_flag=True, help="Do not use cache when building the image"
)
@click.option(
    "--no-registry-cache",
    is_flag=True,
    help="Do not use registry cache when building the image",
)
@click.option(
    "--cache-to-registry",
    is_flag=True,
    help="Push the build cache to the remote registry. You should only enable this option if you have push rights to the remote registry.",
)
@click.option(
    "--output",
    "docker_output",
    # Export image to docker. This is necessary to make the image available to docker-compose.
    # The `--load` option is a shorthand for `--output=type=docker`.
    default="type=docker",
    help="Same as `docker build --output=...`.",
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
    image_names: list[str],
    no_cache: bool,
    no_registry_cache: bool,
    cache_to_registry: bool,
    docker_output: str,
    build_args: list[str],
    add_hosts: list[str],
    target: str,
    docker_args: list[str],
) -> None:
    """
    Build docker images

    Build the docker images necessary for an Open edX platform. By default, the remote
    registry cache will be used for better performance.
    """
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
    if docker_output:
        command_args.append(f"--output={docker_output}")
    if docker_args:
        command_args += docker_args
    # Build context mounts
    build_contexts = get_image_build_contexts(config)

    for image in image_names:
        for name, path, tag, custom_args in find_images_to_build(config, image):
            image_build_args = [*command_args, *custom_args]

            # Registry cache
            if not no_registry_cache:
                image_build_args.append(f"--cache-from=type=registry,ref={tag}-cache")
            if cache_to_registry:
                image_build_args.append(
                    f"--cache-to=type=registry,mode=max,ref={tag}-cache"
                )

            # Build contexts
            for host_path, stage_name in build_contexts.get(name, []):
                fmt.echo_info(
                    f"Adding {host_path} to the build context '{stage_name}' of image '{image}'"
                )
                image_build_args.append(f"--build-context={stage_name}={host_path}")

            # Build
            images.build(
                tutor_env.pathjoin(context.root, path),
                tag,
                *image_build_args,
            )


def get_image_build_contexts(config: Config) -> dict[str, list[tuple[str, str]]]:
    """
    Return all build contexts for all images.

    A build context is to bind-mount a host directory at build-time. This is useful, for
    instance to build a Docker image with a local git checkout of a remote repo.

    Users configure bind-mounts with the `MOUNTS` config setting. Plugins can then
    automatically add build contexts based on these values.
    """
    build_contexts: dict[str, list[tuple[str, str]]] = {}
    for user_mount in bindmount.get_mounts(config):
        for image_name, stage_name in hooks.Filters.IMAGES_BUILD_MOUNTS.iterate(
            user_mount
        ):
            if image_name not in build_contexts:
                build_contexts[image_name] = []
            build_contexts[image_name].append((user_mount, stage_name))
    return build_contexts


@click.command(short_help="Pull images from the Docker registry")
@click.argument("image_names", metavar="image", type=PullImageNameParam(), nargs=-1)
@click.pass_obj
def pull(context: Context, image_names: list[str]) -> None:
    config = tutor_config.load_full(context.root)
    for image in image_names:
        for tag in find_remote_image_tags(config, hooks.Filters.IMAGES_PULL, image):
            images.pull(tag)


@click.command(short_help="Push images to the Docker registry")
@click.argument("image_names", metavar="image", type=PushImageNameParam(), nargs=-1)
@click.pass_obj
def push(context: Context, image_names: list[str]) -> None:
    config = tutor_config.load_full(context.root)
    for image in image_names:
        for tag in find_remote_image_tags(config, hooks.Filters.IMAGES_PUSH, image):
            images.push(tag)


@click.command(short_help="Print tag associated to a Docker image")
@click.argument("image_names", metavar="image", type=BuildImageNameParam(), nargs=-1)
@click.pass_obj
def printtag(context: Context, image_names: list[str]) -> None:
    config = tutor_config.load_full(context.root)
    for image in image_names:
        for _name, _path, tag, _args in find_images_to_build(config, image):
            print(tag)


def find_images_to_build(
    config: Config, image: str
) -> t.Iterator[tuple[str, str, str, tuple[str, ...]]]:
    """
    Iterate over all images to build.

    If no corresponding image is found, raise exception.

    Yield: (name, path, tag, build args)
    """
    found = False
    for name, path, tag, args in hooks.Filters.IMAGES_BUILD.iterate(config):
        relative_path = path if isinstance(path, str) else os.path.join(*path)
        if image in [name, "all"]:
            found = True
            tag = tutor_env.render_str(config, tag)
            yield (name, relative_path, tag, args)

    if not found:
        raise ImageNotFoundError(image)


def find_remote_image_tags(
    config: Config,
    filtre: Filter[list[tuple[str, str]], [Config]],
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
