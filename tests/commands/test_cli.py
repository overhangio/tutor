import unittest
from unittest.mock import patch

from tutor import hooks
from tutor.__about__ import __version__
from tutor.commands.cli import check_plugin_errors, cli, main

from .base import TestCommandMixin


class CliTests(unittest.TestCase, TestCommandMixin):
    def test_help(self) -> None:
        result = self.invoke(["help"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    def test_cli_help(self) -> None:
        result = self.invoke(["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    def test_cli_version(self) -> None:
        result = self.invoke(["--version"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)
        self.assertRegex(result.output, rf"cli, version {__version__}\n")

    def test_ignore_plugin_errors_flag_in_help(self) -> None:
        """The --ignore-plugin-errors flag should appear in help output."""
        result = self.invoke(["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIn("ignore-plugin-errors", result.output)


class PluginErrorExitCodeTests(unittest.TestCase):
    """Tests for plugin error exit code behavior."""

    def _add_plugin_error(self) -> None:
        """Add a test plugin error."""
        hooks.Filters.PLUGIN_ERRORS.add_item(("badplugin", "test error"))

    def _clear_plugin_errors(self) -> None:
        """Clear all plugin errors by clearing all callbacks."""
        hooks.Filters.PLUGIN_ERRORS.clear()

    def setUp(self) -> None:
        self._clear_plugin_errors()
        self.addCleanup(self._clear_plugin_errors)

    def test_check_plugin_errors_exits_with_code_1(self) -> None:
        """_check_plugin_errors should exit with code 1 when errors exist."""
        self._add_plugin_error()
        with self.assertRaises(SystemExit) as cm:
            check_plugin_errors(False)
        self.assertEqual(cm.exception.code, 1)

    def test_check_plugin_errors_no_exit_when_ignored(self) -> None:
        """_check_plugin_errors should not exit when --ignore-plugin-errors is set."""
        self._add_plugin_error()
        # Should not raise
        check_plugin_errors(True)

    def test_check_plugin_errors_no_exit_when_no_errors(self) -> None:
        """_check_plugin_errors should not exit when there are no errors."""
        # Should not raise
        check_plugin_errors(False)
