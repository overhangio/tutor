import unittest

from click.testing import CliRunner
from tutor.commands.compose import bindmount_command
from tutor.commands.dev import dev


class DevTests(unittest.TestCase):
    def test_dev_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(dev, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    def test_dev_bindmount(self) -> None:
        runner = CliRunner()
        result = runner.invoke(bindmount_command, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)
