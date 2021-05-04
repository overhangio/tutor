import os
from typing import Callable, List, Tuple

import click
from mypy_extensions import VarArg

from .exceptions import TutorError
from .types import Config
from .utils import get_user_id


def create(
    root: str,
    config: Config,
    docker_compose_func: Callable[[str, Config, VarArg(str)], int],
    service: str,
    path: str,
) -> str:
    volumes_root_path = get_root_path(root)
    volume_name = get_name(path)
    container_volumes_root_path = "/tmp/volumes"
    command = """rm -rf {volumes_path}/{volume_name}
cp -r {src_path} {volumes_path}/{volume_name}
chown -R {user_id} {volumes_path}/{volume_name}""".format(
        volumes_path=container_volumes_root_path,
        volume_name=volume_name,
        src_path=path,
        user_id=get_user_id(),
    )

    # Create volumes root dir if it does not exist. Otherwise it is created with root owner and might not be writable
    # in the container, e.g: in the dev containers.
    if not os.path.exists(volumes_root_path):
        os.makedirs(volumes_root_path)

    docker_compose_func(
        root,
        config,
        "run",
        "--rm",
        "--no-deps",
        "--volume",
        "{}:{}".format(volumes_root_path, container_volumes_root_path),
        service,
        "sh",
        "-e",
        "-c",
        command,
    )
    return os.path.join(volumes_root_path, volume_name)


def get_path(root: str, container_bind_path: str) -> str:
    bind_basename = get_name(container_bind_path)
    return os.path.join(get_root_path(root), bind_basename)


def get_name(container_bind_path: str) -> str:
    # We rstrip slashes, otherwise os.path.basename returns an empty string
    # We don't use basename here as it will not work on Windows
    name = container_bind_path.rstrip("/").split("/")[-1]
    if not name:
        raise TutorError("Mounting a container root folder is not supported")
    return name


def get_root_path(root: str) -> str:
    return os.path.join(root, "volumes")


def parse_volumes(docker_compose_args: List[str]) -> Tuple[List[str], List[str]]:
    """
    Parse `-v/--volume` options from an arbitrary list of arguments.
    """

    @click.command(context_settings={"ignore_unknown_options": True})
    @click.option("-v", "--volume", "volumes", multiple=True)
    @click.argument("args", nargs=-1)
    def custom_docker_compose(
        volumes: List[str], args: List[str]
    ) -> None:  # pylint: disable=unused-argument
        pass

    if isinstance(docker_compose_args, tuple):
        docker_compose_args = list(docker_compose_args)
    context = custom_docker_compose.make_context("custom", docker_compose_args)
    return context.params["volumes"], context.params["args"]
