import unittest

from click.testing import CliRunner

from tutor.commands.cli import cli, print_help


class CliTests(unittest.TestCase):
    def test_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(print_help)
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    def test_cli_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    def test_cli_version(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)
        self.assertRegex(result.output, r"cli, version \d+.\d+.\d+\n")
