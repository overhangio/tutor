import unittest

import click

from tests.helpers import PluginsTestCase
from tutor import hooks
from tutor.__about__ import __version__
from tutor.commands.cli import cli
from tutor.commands.context import ignore_plugin_errors

from .base import TestCommandMixin


class CliTests(unittest.TestCase, TestCommandMixin):
    def test_help(self) -> None:
        result = self.invoke(["help"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)

    def test_cli_help(self) -> None:
        result = self.invoke(["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    def test_cli_version(self) -> None:
        result = self.invoke(["--version"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)
        self.assertRegex(result.stdout, rf"cli, version {__version__}\n")

    def test_ignore_plugin_errors_flag_in_help(self) -> None:
        """The --ignore-plugin-errors flag should appear in help output."""
        result = self.invoke(["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIn("ignore-plugin-errors", result.output)


class PluginErrorExitCodeTests(PluginsTestCase, TestCommandMixin):
    """Tests for plugin error exit code behavior."""

    def setUp(self) -> None:
        super().setUp()

        @ignore_plugin_errors
        @click.command(name="exempt")
        def exempt_command() -> None:
            click.echo("exempt_command ran")

        @click.command(name="non-exempt")
        def non_exempt_command() -> None:
            click.echo("non_exempt_command ran")

        cli.add_command(exempt_command)
        self.addCleanup(cli.commands.pop, "exempt")
        cli.add_command(non_exempt_command)
        self.addCleanup(cli.commands.pop, "non-exempt")


    def _add_plugin_error(self) -> None:
        """Add a test plugin error."""
        with hooks.Contexts.PLUGINS.enter():
            hooks.Filters.PLUGIN_ERRORS.add_item(("badplugin", "test error"))

    def test_check_plugin_errors_exits_with_code_1(self) -> None:
        """Pugin errors prevent command from running if errors exist."""
        self._add_plugin_error()
        result = self.invoke(["non-exempt"])
        self.assertEqual(result.exit_code, 1)
        self.assertNotIn("non_exempt_command ran", result.output)
        self.assertIn("badplugin", result.output)

    def test_check_plugin_errors_ignore(self) -> None:
        """Command should run when ignore-plugin-errors is set."""
        self._add_plugin_error()
        result = self.invoke(["--ignore-plugin-errors", "non-exempt"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("non_exempt_command ran", result.output)

    def test_check_plugin_exempt_command(self) -> None:
        """Command should run if they are exempt."""
        self._add_plugin_error()
        result = self.invoke(["exempt"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("exempt_command ran", result.output)

