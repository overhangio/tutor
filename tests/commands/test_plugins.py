import unittest

from click.testing import CliRunner
from tutor.commands.plugins import *


class PluginsTests(unittest.TestCase):
    def test_plugins_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(plugins_command, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(None, result.exception)
