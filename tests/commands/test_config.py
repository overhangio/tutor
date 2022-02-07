import os
import tempfile
import unittest

from tests.helpers import temporary_root
from tutor import config as tutor_config

from .base import TestCommandMixin


class ConfigTests(unittest.TestCase, TestCommandMixin):
    def test_config_help(self) -> None:
        result = self.invoke(["config", "--help"])
        self.assertEqual(0, result.exit_code)
        self.assertFalse(result.exception)

    def test_config_save(self) -> None:
        result = self.invoke(["config", "save"])
        self.assertFalse(result.exception)
        self.assertEqual(0, result.exit_code)

    def test_config_save_interactive(self) -> None:
        result = self.invoke(["config", "save", "-i"])
        self.assertFalse(result.exception)
        self.assertEqual(0, result.exit_code)

    def test_config_save_skip_update(self) -> None:
        result = self.invoke(["config", "save", "-e"])
        self.assertFalse(result.exception)
        self.assertEqual(0, result.exit_code)

    def test_config_save_set_value(self) -> None:
        with temporary_root() as root:
            result1 = self.invoke_in_root(root, ["config", "save", "-s", "key=value"])
            result2 = self.invoke_in_root(root, ["config", "printvalue", "key"])
        self.assertFalse(result1.exception)
        self.assertEqual(0, result1.exit_code)
        self.assertIn("value", result2.output)

    def test_config_save_unset_value(self) -> None:
        with temporary_root() as root:
            result1 = self.invoke_in_root(root, ["config", "save", "-U", "key"])
            result2 = self.invoke_in_root(root, ["config", "printvalue", "key"])
        self.assertFalse(result1.exception)
        self.assertEqual(0, result1.exit_code)
        self.assertEqual(1, result2.exit_code)

    def test_config_printroot(self) -> None:
        with temporary_root() as root:
            result = self.invoke_in_root(root, ["config", "printroot"])
        self.assertFalse(result.exception)
        self.assertEqual(0, result.exit_code)
        self.assertIn(root, result.output)

    def test_config_printvalue(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            result = self.invoke_in_root(
                root, ["config", "printvalue", "MYSQL_ROOT_PASSWORD"]
            )
        self.assertFalse(result.exception)
        self.assertEqual(0, result.exit_code)
        self.assertTrue(result.output)

    def test_config_render(self) -> None:
        with tempfile.TemporaryDirectory() as dest:
            with temporary_root() as root:
                self.invoke_in_root(root, ["config", "save"])
                result = self.invoke_in_root(root, ["config", "render", root, dest])
        self.assertEqual(0, result.exit_code)
        self.assertFalse(result.exception)

    def test_config_render_with_extra_configs(self) -> None:
        with tempfile.TemporaryDirectory() as dest:
            with temporary_root() as root:
                self.invoke_in_root(root, ["config", "save"])
                result = self.invoke_in_root(
                    root,
                    [
                        "config",
                        "render",
                        "-x",
                        os.path.join(root, tutor_config.CONFIG_FILENAME),
                        root,
                        dest,
                    ],
                )
        self.assertEqual(0, result.exit_code)
        self.assertFalse(result.exception)
