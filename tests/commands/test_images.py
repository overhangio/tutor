import unittest

from click.testing import CliRunner
from tutor.commands.images import *


class ImagesTests(unittest.TestCase):
    def test_images_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(images_command, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(None, result.exception)
