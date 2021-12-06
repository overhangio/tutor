import os
import shutil
import tempfile
from typing import Any
from click.testing import CliRunner
from tutor.types import Config
from tutor.jobs import BaseJobRunner
from tutor import config as tutor_config
from tutor.commands.config import config_command
from tutor.commands.context import Context, BaseJobContext


CONTEXT = Context(tempfile.mkdtemp())


class TestJobRunner(BaseJobRunner):
    def __init__(self, root: str, config: Config):
        """
        Mock job runner for unit testing.
        """
        super().__init__(root, config)

    def run_job(self, service: str, command: str) -> int:
        print(
            os.linesep.join(["Service: {}".format(service), "-----", command, "----- "])
        )
        return 0


class TestContext(BaseJobContext):
    def __init__(self) -> None:
        super().__init__(CONTEXT.root)
        runner = CliRunner()
        runner.invoke(config_command, ["save"], obj=CONTEXT)

    def __enter__(self) -> Any:
        return self

    def __exit__(self: Any, exc: Any, value: Any, tb: Any) -> None:
        shutil.rmtree(CONTEXT.root)

    def load_config(self) -> Config:
        return tutor_config.load_no_check(CONTEXT.root)

    def job_runner(self, config: Config) -> TestJobRunner:
        return TestJobRunner(CONTEXT.root, config)
