from tutor.tasks import BaseTaskRunner
from tutor.types import Config


class Context:
    """
    Context object that is passed to all subcommands.

    The project `root` is passed to all subcommands of `tutor`; that's because
    it is defined as an argument of the top-level command. For instance:

        $ tutor --root=... local run ...
    """

    def __init__(self, root: str) -> None:
        self.root = root


class BaseTaskContext(Context):
    """
    Specialized context that subcommands may use.

    For instance `dev`, `local` and `k8s` define custom runners to run jobs.
    """

    def job_runner(self, config: Config) -> BaseTaskRunner:
        """
        Return a runner capable of running docker-compose/kubectl commands.
        """
        raise NotImplementedError
