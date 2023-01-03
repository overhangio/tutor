import typing as t
import unittest
from unittest.mock import Mock, patch

from tutor import plugins
from tutor.commands import plugins as plugins_commands

from .base import TestCommandMixin


class PluginsTests(unittest.TestCase, TestCommandMixin):
    def test_plugins_help(self) -> None:
        result = self.invoke(["plugins", "--help"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)

    def test_plugins_printroot(self) -> None:
        result = self.invoke(["plugins", "printroot"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)
        self.assertTrue(result.output)

    @patch.object(plugins, "iter_info", return_value=[])
    def test_plugins_list(self, _iter_info: Mock) -> None:
        result = self.invoke(["plugins", "list"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)
        self.assertEqual("NAME\tSTATUS\tVERSION\n", result.output)
        _iter_info.assert_called()

    def test_plugins_install_not_found_plugin(self) -> None:
        result = self.invoke(["plugins", "install", "notFound"])
        self.assertEqual(1, result.exit_code)
        self.assertTrue(result.exception)

    def test_plugins_enable_not_installed_plugin(self) -> None:
        result = self.invoke(["plugins", "enable", "notFound"])
        self.assertEqual(1, result.exit_code)
        self.assertTrue(result.exception)

    def test_plugins_disable_not_installed_plugin(self) -> None:
        result = self.invoke(["plugins", "disable", "notFound"])
        self.assertEqual(0, result.exit_code)
        self.assertFalse(result.exception)

    @patch.object(
        plugins,
        "iter_info",
        return_value=[("aacd", None), ("abcd", None), ("abef", None), ("alba", None)],
    )
    def test_plugins_name_auto_complete(self, _iter_info: Mock) -> None:
        self.assertEqual([], plugins_commands.PluginName().get_names("z"))
        self.assertEqual(
            ["abcd", "abef"], plugins_commands.PluginName().get_names("ab")
        )
        self.assertEqual(
            ["all", "alba"], plugins_commands.PluginName(allow_all=True).get_names("al")
        )

    def test_format_table(self) -> None:
        rows: t.List[t.Tuple[str, ...]] = [
            ("a", "xyz", "value 1"),
            ("abc", "x", "value 12345"),
        ]
        formatted = plugins_commands.format_table(rows, separator="  ")
        self.assertEqual(
            """
a    xyz  value 1
abc  x    value 12345
""".strip(),
            formatted,
        )
