import os
import tempfile
from tutor.types import Config
from tutor.jobs import BaseJobRunner
from tutor import config as tutor_config
from tutor.commands.context import Context
from tutor.commands.context import BaseJobContext


CONTEXT = Context(os.path.join(tempfile.gettempdir(), "tutor"))


class TestJobRunner(BaseJobRunner):
    def __init__(self, root: str, config: Config):
        """
        Mock job runner for unit testing.
        """
        super().__init__(root, config)

    def run_job(self, service: str, command: str) -> int:
        print(os.linesep.join([f"Service: {service}", "-----", command, "----- "]))
        return 0


class TestContext(BaseJobContext):
    def __init__(self) -> None:
        super().__init__(CONTEXT.root)

    def load_config(self) -> Config:
        return tutor_config.load_no_check(CONTEXT.root)

    def job_runner(self, config: Config) -> TestJobRunner:
        return TestJobRunner(CONTEXT.root, config)
