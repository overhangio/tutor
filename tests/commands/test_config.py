import os
import unittest
import tempfile

from click.testing import CliRunner
from tutor.commands.config import *
from tests.test import CONTEXT
from tutor import config as tutor_config


class ConfigTests(unittest.TestCase):
    def test_config_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(config_command, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertFalse(result.exception)

    def test_config_save(self) -> None:
        runner = CliRunner()
        result = runner.invoke(config_command, ["save"], obj=CONTEXT)
        self.assertEqual(0, result.exit_code)
        self.assertFalse(result.exception)

    def test_config_save_interactive(self) -> None:
        runner = CliRunner()
        result = runner.invoke(config_command, ["save", "-i"], obj=CONTEXT)
        self.assertEqual(0, result.exit_code)
        self.assertFalse(result.exception)

    def test_config_save_skip_update(self) -> None:
        runner = CliRunner()
        result = runner.invoke(config_command, ["save", "-e"], obj=CONTEXT)
        self.assertEqual(0, result.exit_code)
        self.assertFalse(result.exception)

    def test_config_save_set_value(self) -> None:
        runner = CliRunner()
        result = runner.invoke(config_command, ["save", "-s", "key=value"], obj=CONTEXT)
        self.assertEqual(0, result.exit_code)
        self.assertFalse(result.exception)
        result = runner.invoke(config_command, ["printvalue", "key"], obj=CONTEXT)
        self.assertNotEqual(-1, result.output.find("value"))

    def test_config_save_unset_value(self) -> None:
        runner = CliRunner()
        result = runner.invoke(config_command, ["save", "-U", "key"], obj=CONTEXT)
        self.assertEqual(0, result.exit_code)
        self.assertFalse(result.exception)
        result = runner.invoke(config_command, ["printvalue", "key"], obj=CONTEXT)
        self.assertEqual(1, result.exit_code)

    def test_config_printroot(self) -> None:
        runner = CliRunner()
        result = runner.invoke(config_command, ["printroot"], obj=CONTEXT)
        self.assertEqual(0, result.exit_code)
        self.assertFalse(result.exception)
        self.assertNotEqual(-1, result.output.find(CONTEXT.root))

    def test_config_printvalue(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            config_command, ["printvalue", "MYSQL_ROOT_PASSWORD"], obj=CONTEXT
        )
        self.assertEqual(0, result.exit_code)
        self.assertFalse(result.exception)
        self.assertTrue(result.output)

    def test_config_render(self) -> None:
        with tempfile.TemporaryDirectory() as dest:
            runner = CliRunner()
            result = runner.invoke(
                config_command, ["render", CONTEXT.root, dest], obj=CONTEXT
            )
            self.assertEqual(0, result.exit_code)
            self.assertFalse(result.exception)

    def test_config_render_with_extra_configs(self) -> None:
        with tempfile.TemporaryDirectory() as dest:
            runner = CliRunner()
            result = runner.invoke(
                config_command,
                [
                    "render",
                    "-x",
                    os.path.join(CONTEXT.root, tutor_config._CONFIG_FILE),
                    CONTEXT.root,
                    dest,
                ],
                obj=CONTEXT,
            )
            self.assertEqual(0, result.exit_code)
            self.assertFalse(result.exception)
