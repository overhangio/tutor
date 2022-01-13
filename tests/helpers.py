import os
import tempfile

from tutor.commands.context import BaseJobContext, Context
from tutor.jobs import BaseJobRunner
from tutor.types import Config


class TestJobRunner(BaseJobRunner):
    def __init__(self, root: str, config: Config):
        """
        Mock job runner for unit testing.

        This runner does nothing except print the service name and command,
        separated by dashes.
        """
        super().__init__(root, config)

    def run_job(self, service: str, command: str) -> int:
        print(
            os.linesep.join(["Service: {}".format(service), "-----", command, "----- "])
        )
        return 0


def temporary_root() -> "tempfile.TemporaryDirectory[str]":
    """
    Context manager to handle temporary test root.

    This function can be used as follows:

        with temporary_root() as root:
            config = tutor_config.load_full(root)
            ...
    """
    return tempfile.TemporaryDirectory(prefix="tutor-test-root-")


class TestContext(Context):
    """
    Barebones click test context.
    """


class TestJobContext(TestContext, BaseJobContext):
    """
    Click context that will use only test job runners.
    """

    def job_runner(self) -> TestJobRunner:
        return TestJobRunner(self.root, self.config)
