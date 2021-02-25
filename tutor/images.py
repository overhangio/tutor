from typing import Any, Dict

from . import fmt
from . import utils


def get_tag(config: Dict[str, Any], name: str) -> Any:
    return config["DOCKER_IMAGE_" + name.upper().replace("-", "_")]


def build(path: str, tag: str, *args: str) -> None:
    fmt.echo_info("Building image {}".format(tag))
    utils.docker("build", "-t", tag, *args, path)


def pull(tag: str) -> None:
    fmt.echo_info("Pulling image {}".format(tag))
    utils.docker("pull", tag)


def push(tag: str) -> None:
    fmt.echo_info("Pushing image {}".format(tag))
    utils.docker("push", tag)
