import os
import tempfile
import weakref
from tutor.jobs import BaseJobRunner
from tutor.types import Config
from tutor.commands.context import BaseJobContext
from tutor import config as tutor_config


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
    def __init__(self):
        self._tempDir = tempfile.TemporaryDirectory()
        self._finalizer = weakref.finalize(self, self._cleanup, self._tempDir)
        super().__init__(self._tempDir.name)
        _, self.config = tutor_config.load_all(self.root)
        self.runner = self.job_runner(self.config)

    @classmethod
    def _cleanup(cls, tempDir: tempfile.TemporaryDirectory):
        tempDir.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, exc, value, tb):
        self.cleanup()

    def cleanup(self):
        if self._finalizer.detach():
            self._cleanup(self._tempDir)

    def job_runner(self, config: Config) -> TestJobRunner:
        return TestJobRunner(self.root, config)
