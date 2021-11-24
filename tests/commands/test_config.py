import unittest

from click.testing import CliRunner
from tutor.commands.config import *


class ConfigTests(unittest.TestCase):
    def test_config_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(config_command, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(None, result.exception)

    def test_config_printroot(self) -> None:
        runner = CliRunner()
        result = runner.invoke(config_command, ["printroot", "--help"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(None, result.exception)

    def test_config_printvalue(self) -> None:
        runner = CliRunner()
        result = runner.invoke(config_command, ["printvalue", "--help"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(None, result.exception)

    def test_config_render(self) -> None:
        runner = CliRunner()
        result = runner.invoke(config_command, ["render", "--help"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(None, result.exception)

    def test_config_save(self) -> None:
        runner = CliRunner()
        result = runner.invoke(config_command, ["save", "--help"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(None, result.exception)
