from . import fmt, utils
from .types import Config, get_typed


def get_tag(config: Config, name: str) -> str:
    key = "DOCKER_IMAGE_" + name.upper().replace("-", "_")
    return get_typed(config, key, str)


def build(path: str, tag: str, *args: str) -> None:
    fmt.echo_info("Building image {}".format(tag))
    utils.docker("build", "-t", tag, *args, path)


def pull(tag: str) -> None:
    fmt.echo_info("Pulling image {}".format(tag))
    utils.docker("pull", tag)


def push(tag: str) -> None:
    fmt.echo_info("Pushing image {}".format(tag))
    utils.docker("push", tag)
