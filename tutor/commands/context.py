from ..jobs import BaseJobRunner
from ..types import Config
from ..exceptions import TutorError


class Context:
    """
    Context object that is passed to all subcommands.

    The project `root` and its loaded `config` are passed to all subcommands of `tutor`;
    that's because it is defined as an argument of the top-level command. For instance:

        $ tutor --root=... local run ...
    """

    def __init__(self, root: str) -> None:
        self.root = root

    def job_runner(self) -> BaseJobRunner:
        """
        We cannot run jobs in this context. Raise an error.
        """
        raise TutorError(
            "Jobs may not be run under the root context. "
            + "Please specify dev, local, or k8s context.\n"
            + "\n"
            + "For example, if you just ran:\n"
            + "    tutor <command>\n"
            + "\n"
            + "then you should instead run one of:\n"
            + "  tutor dev   <command>\n"
            + "  tutor local <command>\n"
            + "  tutor k8s   <command>"
        )


class BaseJobContext(Context):
    """
    Specialized context that subcommands may use.

    For instance `dev`, `local` and `k8s` define custom runners to run jobs.
    """

    def __init__(self, root: str, config: Config) -> None:
        super().__init__(root)
        self._config = config

    @property
    def config(self) -> Config:
        """
        Return this context's configuration dictionary.

        Mutations to the dictionary will not affect the context's underlying config.
        """
        return self._config.copy()

    def job_runner(self) -> BaseJobRunner:
        """
        Return a runner capable of running docker-compose/kubectl commands.

        All concrete subclasses of BaseJobContext should define this method,
        so we raise a `NotImplementedError` here instead of falling back to the
        `TutorError` that Context.job_runner raises.
        """
        raise NotImplementedError
