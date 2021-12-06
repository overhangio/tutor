import unittest
from unittest.mock import Mock, patch
from click.testing import CliRunner
from tutor.commands.plugins import plugins_command
from tutor import plugins
from tests.helpers import TestContext


class PluginsTests(unittest.TestCase):
    def test_plugins_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(plugins_command, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    def test_plugins_printroot(self) -> None:
        with TestContext() as context:
            runner = CliRunner()
            result = runner.invoke(plugins_command, ["printroot"], obj=context)
            self.assertEqual(0, result.exit_code)
            self.assertIsNone(result.exception)
            self.assertTrue(result.output)

    @patch.object(plugins.BasePlugin, "iter_installed", return_value=[])
    def test_plugins_list(self, _iter_installed: Mock) -> None:
        with TestContext() as context:
            runner = CliRunner()
            result = runner.invoke(plugins_command, ["list"], obj=context)
            self.assertEqual(0, result.exit_code)
            self.assertIsNone(result.exception)
            self.assertFalse(result.output)
            _iter_installed.assert_called()

    def test_plugins_install_not_found_plugin(self) -> None:
        with TestContext() as context:
            runner = CliRunner()
            result = runner.invoke(
                plugins_command, ["install", "notFound"], obj=context
            )
            self.assertEqual(1, result.exit_code)
            self.assertTrue(result.exception)

    def test_plugins_enable_not_installed_plugin(self) -> None:
        with TestContext() as context:
            runner = CliRunner()
            result = runner.invoke(plugins_command, ["enable", "notFound"], obj=context)
            self.assertEqual(1, result.exit_code)
            self.assertTrue(result.exception)

    def test_plugins_disable_not_installed_plugin(self) -> None:
        with TestContext() as context:
            runner = CliRunner()
            result = runner.invoke(
                plugins_command, ["disable", "notFound"], obj=context
            )
            self.assertEqual(0, result.exit_code)
            self.assertFalse(result.exception)
