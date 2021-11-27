import unittest

from click.testing import CliRunner
from tutor.commands.images import *
from tests.test import CONTEXT


class ImagesTests(unittest.TestCase):
    def test_images_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(images_command, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(None, result.exception)

    def test_images_pull_image(self) -> None:
        runner = CliRunner()
        result = runner.invoke(images_command, ["pull"], obj=CONTEXT)
        self.assertEqual(0, result.exit_code)
        self.assertEqual(None, result.exception)

    def test_images_pull_plugin(self) -> None:
        runner = CliRunner()
        result = runner.invoke(images_command, ["pull", "plugin"], obj=CONTEXT)
        self.assertEqual(0, result.exit_code)
        self.assertEqual(None, result.exception)

    def test_images_printtag_image(self) -> None:
        runner = CliRunner()
        result = runner.invoke(images_command, ["printtag", "openedx"], obj=CONTEXT)
        self.assertEqual(0, result.exit_code)
        self.assertEqual(None, result.exception)

    def test_images_printtag_plugin(self) -> None:
        runner = CliRunner()
        result = runner.invoke(images_command, ["printtag", "plugin"], obj=CONTEXT)
        self.assertEqual(0, result.exit_code)
        self.assertEqual(None, result.exception)

    def test_images_build_plugin(self) -> None:
        runner = CliRunner()
        result = runner.invoke(images_command, ["build", "plugin"], obj=CONTEXT)
        self.assertEqual(0, result.exit_code)
        self.assertEqual(None, result.exception)

    def test_images_build_plugin_with_args(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            images_command,
            [
                "build",
                "--no-cache",
                "-a",
                "myarg=value",
                "--add-host",
                "host",
                "--target",
                "target",
                "-d",
                "docker_args",
                "plugin",
            ],
            obj=CONTEXT,
        )
        self.assertEqual(0, result.exit_code)
        self.assertEqual(None, result.exception)

    def test_images_push(self) -> None:
        runner = CliRunner()
        result = runner.invoke(images_command, ["push"], obj=CONTEXT)
        self.assertEqual(0, result.exit_code)
        self.assertEqual(None, result.exception)
