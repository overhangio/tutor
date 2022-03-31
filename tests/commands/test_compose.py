import unittest

from click.testing import CliRunner

from tutor.commands.compose import quickstart, upgrade


class ComposeTests(unittest.TestCase):
    def test_compose_quickstart_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(quickstart, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    def test_compose_upgrade_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(upgrade, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)
