import os
import tempfile
import unittest

from click.testing import CliRunner

from tests.helpers import TestContext, temporary_root
from tutor import config as tutor_config
from tutor.commands.config import config_command


class ConfigTests(unittest.TestCase):
    def test_config_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(config_command, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertFalse(result.exception)

    def test_config_save(self) -> None:
        with temporary_root() as root:
            context = TestContext(root)
            runner = CliRunner()
            result = runner.invoke(config_command, ["save"], obj=context)
            self.assertEqual(0, result.exit_code)
            self.assertFalse(result.exception)

    def test_config_save_interactive(self) -> None:
        with temporary_root() as root:
            context = TestContext(root)
            runner = CliRunner()
            result = runner.invoke(config_command, ["save", "-i"], obj=context)
            self.assertEqual(0, result.exit_code)
            self.assertFalse(result.exception)

    def test_config_save_skip_update(self) -> None:
        with temporary_root() as root:
            context = TestContext(root)
            runner = CliRunner()
            result = runner.invoke(config_command, ["save", "-e"], obj=context)
            self.assertEqual(0, result.exit_code)
            self.assertFalse(result.exception)

    def test_config_save_set_value(self) -> None:
        with temporary_root() as root:
            context = TestContext(root)
            runner = CliRunner()
            result = runner.invoke(
                config_command, ["save", "-s", "key=value"], obj=context
            )
            self.assertEqual(0, result.exit_code)
            self.assertFalse(result.exception)
            result = runner.invoke(config_command, ["printvalue", "key"], obj=context)
            self.assertIn("value", result.output)

    def test_config_save_unset_value(self) -> None:
        with temporary_root() as root:
            context = TestContext(root)
            runner = CliRunner()
            result = runner.invoke(config_command, ["save", "-U", "key"], obj=context)
            self.assertEqual(0, result.exit_code)
            self.assertFalse(result.exception)
            result = runner.invoke(config_command, ["printvalue", "key"], obj=context)
            self.assertEqual(1, result.exit_code)

    def test_config_printroot(self) -> None:
        with temporary_root() as root:
            context = TestContext(root)
            runner = CliRunner()
            result = runner.invoke(config_command, ["printroot"], obj=context)
            self.assertEqual(0, result.exit_code)
            self.assertFalse(result.exception)
            self.assertIn(context.root, result.output)

    def test_config_printvalue(self) -> None:
        with temporary_root() as root:
            context = TestContext(root)
            runner = CliRunner()
            runner.invoke(config_command, ["save"], obj=context)
            result = runner.invoke(
                config_command, ["printvalue", "MYSQL_ROOT_PASSWORD"], obj=context
            )
            self.assertEqual(0, result.exit_code)
            self.assertFalse(result.exception)
            self.assertTrue(result.output)

    def test_config_render(self) -> None:
        with tempfile.TemporaryDirectory() as dest:
            with temporary_root() as root:
                context = TestContext(root)
                runner = CliRunner()
                runner.invoke(config_command, ["save"], obj=context)
                result = runner.invoke(
                    config_command, ["render", context.root, dest], obj=context
                )
                self.assertEqual(0, result.exit_code)
                self.assertFalse(result.exception)

    def test_config_render_with_extra_configs(self) -> None:
        with tempfile.TemporaryDirectory() as dest:
            with temporary_root() as root:
                context = TestContext(root)
                runner = CliRunner()
                runner.invoke(config_command, ["save"], obj=context)
                result = runner.invoke(
                    config_command,
                    [
                        "render",
                        "-x",
                        os.path.join(context.root, tutor_config.CONFIG_FILENAME),
                        context.root,
                        dest,
                    ],
                    obj=context,
                )
                self.assertEqual(0, result.exit_code)
                self.assertFalse(result.exception)
