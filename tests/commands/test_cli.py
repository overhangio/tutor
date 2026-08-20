import unittest
from contextlib import contextmanager
from typing import Iterator

from tests.helpers import PluginsTestCase, temporary_root
from tutor import config as tutor_config
from tutor import hooks
from tutor.__about__ import __version__
from tutor.commands.cli import check_plugin_errors
from tutor.commands.context import Context
from tutor.types import Config

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
        self.assertRegex(result.output, rf"cli, version {__version__}\n")

    def test_ignore_plugin_errors_flag_in_help(self) -> None:
        """The --ignore-plugin-errors flag should appear in help output."""
        result = self.invoke(["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIn("ignore-plugin-errors", result.output)


class PluginErrorExitCodeTests(PluginsTestCase):
    """Tests for plugin error exit code behavior."""

    def _add_plugin_error(self) -> None:
        """Add a test plugin error."""
        with hooks.Contexts.PLUGINS.enter():
            hooks.Filters.PLUGIN_ERRORS.add_item(("badplugin", "test error"))

    @contextmanager
    def _prev_config(self, ignore_errors=False) -> Iterator[tuple[Context, Config]]:
        with temporary_root() as root:
            context = Context(root, ignore_errors)
            yield context, tutor_config.get_user(root)

    def test_check_plugin_errors_exits_with_code_1(self) -> None:
        """_check_plugin_errors should exit with code 1 when errors exist."""
        with self._prev_config() as (context, config):
            self._add_plugin_error()
            with self.assertRaises(SystemExit) as cm:
                check_plugin_errors(context, config)
            self.assertEqual(cm.exception.code, 1)

    def test_check_plugin_errors_no_exit_when_ignored(self) -> None:
        """_check_plugin_errors should not exit when --ignore-plugin-errors is set."""
        with self._prev_config(ignore_errors=True) as (context, config):
            self._add_plugin_error()
            # Should not raise
            check_plugin_errors(context, config)

    def test_check_plugin_errors_no_exit_when_no_errors(self) -> None:
        """_check_plugin_errors should not exit when there are no errors."""
        with self._prev_config() as (context, config):
            # Should not raise
            check_plugin_errors(context, config)
