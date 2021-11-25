import unittest

from click.testing import CliRunner
from tutor.commands.plugins import *
from .test_context import CONTEXT


class PluginsTests(unittest.TestCase):
    def test_plugins_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(plugins_command, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(None, result.exception)

    def test_plugins_printroot(self) -> None:
        runner = CliRunner()
        result = runner.invoke(plugins_command, ["printroot"], obj=CONTEXT)
        self.assertEqual(0, result.exit_code)
        self.assertEqual(None, result.exception)
        self.assertTrue(result.output)

    def test_plugins_list(self) -> None:
        runner = CliRunner()
        result = runner.invoke(plugins_command, ["list"], obj=CONTEXT)
        self.assertEqual(0, result.exit_code)
        self.assertEqual(None, result.exception)
        self.assertFalse(result.output)

    def test_plugins_install_not_found_plugin(self) -> None:
        runner = CliRunner()
        result = runner.invoke(plugins_command, ["install", "notFound"], obj=CONTEXT)
        self.assertEqual(1, result.exit_code)
        self.assertTrue(result.exception)

    def test_plugins_enable_not_installed_plugin(self) -> None:
        runner = CliRunner()
        result = runner.invoke(plugins_command, ["enable", "notFound"], obj=CONTEXT)
        self.assertEqual(1, result.exit_code)
        self.assertTrue(result.exception)

    def test_plugins_disable_not_installed_plugin(self) -> None:
        runner = CliRunner()
        result = runner.invoke(plugins_command, ["disable", "notFound"], obj=CONTEXT)
        self.assertEqual(0, result.exit_code)
        self.assertFalse(result.exception)
