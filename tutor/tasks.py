from tutor import env
from tutor.types import Config


class BaseTaskRunner:
    """
    A task runner is responsible for running bash commands in the right context.

    Commands may be loaded from string or template files. The `run_task` method must be
    implemented by child classes.
    """

    def __init__(self, root: str, config: Config):
        self.root = root
        self.config = config

    def run_task_from_template(self, service: str, *path: str) -> None:
        command = self.render(*path)
        self.run_task(service, command)

    def run_task_from_str(self, service: str, command: str) -> None:
        rendered = env.render_str(self.config, command).strip()
        self.run_task(service, rendered)

    def render(self, *path: str) -> str:
        rendered = env.render_file(self.config, *path).strip()
        if isinstance(rendered, bytes):
            raise TypeError("Cannot load job from binary file")
        return rendered

    def run_task(self, service: str, command: str) -> int:
        """
        Given a (potentially large) string command, run it with the
        corresponding service. Implementations will differ depending on the
        deployment strategy.
        """
        raise NotImplementedError


class BaseComposeTaskRunner(BaseTaskRunner):
    def docker_compose(self, *command: str) -> int:
        raise NotImplementedError
