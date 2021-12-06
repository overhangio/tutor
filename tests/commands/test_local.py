import unittest

from click.testing import CliRunner
from tutor.commands.local import local, quickstart, upgrade


class LocalTests(unittest.TestCase):
    def test_local_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(local, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    def test_local_quickstart_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(quickstart, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    def test_local_upgrade_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(upgrade, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)
