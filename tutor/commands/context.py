from ..types import Config


def unimplemented_docker_compose(root: str, config: Config, *command: str) -> int:
    raise NotImplementedError


# pylint: disable=too-few-public-methods
class Context:
    def __init__(self, root: str) -> None:
        self.root = root
        self.docker_compose_func = unimplemented_docker_compose

    def docker_compose(self, root: str, config: Config, *command: str) -> int:
        return self.docker_compose_func(root, config, *command)
