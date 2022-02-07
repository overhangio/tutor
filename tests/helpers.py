import os
import tempfile
import typing as t
import unittest
import unittest.result

from tutor import hooks
from tutor.commands.context import BaseJobContext
from tutor.jobs import BaseJobRunner
from tutor.types import Config


class TestJobRunner(BaseJobRunner):
    """
    Mock job runner for unit testing.

    This runner does nothing except print the service name and command,
    separated by dashes.
    """

    def run_job(self, service: str, command: str) -> int:
        print(os.linesep.join([f"Service: {service}", "-----", command, "----- "]))
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


class TestContext(BaseJobContext):
    """
    Click context that will use only test job runners.
    """

    def job_runner(self, config: Config) -> TestJobRunner:
        return TestJobRunner(self.root, config)


class PluginsTestCase(unittest.TestCase):
    """
    This test case class clears the hooks created during tests. It also makes sure that
    we don't accidentally load entrypoint/dict plugins from the user.
    """

    def setUp(self) -> None:
        self.clean()
        self.addCleanup(self.clean)
        super().setUp()

    def clean(self) -> None:
        # We clear hooks created in some contexts, such that user plugins are never loaded.
        for context in [
            hooks.Contexts.PLUGINS.name,
            hooks.Contexts.PLUGINS_V0_ENTRYPOINT.name,
            hooks.Contexts.PLUGINS_V0_YAML.name,
            "unittests",
        ]:
            hooks.filters.clear_all(context=context)
            hooks.actions.clear_all(context=context)

    def run(
        self, result: t.Optional[unittest.result.TestResult] = None
    ) -> t.Optional[unittest.result.TestResult]:
        """
        Run all actions and filters with a test context, such that they can be cleared
        from one run to the next.
        """
        with hooks.contexts.enter("unittests"):
            return super().run(result=result)
