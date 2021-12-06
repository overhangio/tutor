import unittest
from tutor import images, plugins
from unittest.mock import Mock, patch
from click.testing import CliRunner
from tutor.commands.images import images_command, ImageNotFoundError
from tests.helpers import TestContext


class ImagesTests(unittest.TestCase):
    def test_images_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(images_command, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    def test_images_pull_image(self) -> None:
        with TestContext() as context:
            runner = CliRunner()
            result = runner.invoke(images_command, ["pull"], obj=context)
            self.assertEqual(0, result.exit_code)
            self.assertIsNone(result.exception)

    def test_images_pull_plugin_invalid_plugin_should_throw_error(self) -> None:
        with TestContext() as context:
            runner = CliRunner()
            result = runner.invoke(images_command, ["pull", "plugin"], obj=context)
            self.assertEqual(1, result.exit_code)
            self.assertEqual(ImageNotFoundError, type(result.exception))

    @patch.object(plugins.BasePlugin, "iter_installed", return_value=[])
    @patch.object(
        plugins.Plugins,
        "iter_hooks",
        return_value=[
            (
                "dev-plugins",
                {"plugin": "plugin:dev-1.0.0", "plugin2": "plugin2:dev-1.0.0"},
            )
        ],
    )
    @patch.object(images, "pull", return_value=None)
    def test_images_pull_plugin(
        self, _image_pull: Mock, _iter_hooks: Mock, _iter_installed: Mock
    ) -> None:
        with TestContext() as context:
            runner = CliRunner()
            result = runner.invoke(images_command, ["pull", "plugin"], obj=context)
            self.assertEqual(0, result.exit_code)
            self.assertIsNone(result.exception)
            _iter_hooks.assert_called_once_with("remote-image")
            _image_pull.assert_called_once_with("plugin:dev-1.0.0")
            _iter_installed.assert_called()

    def test_images_printtag_image(self) -> None:
        with TestContext() as context:
            runner = CliRunner()
            result = runner.invoke(images_command, ["printtag", "openedx"], obj=context)
            self.assertEqual(0, result.exit_code)
            self.assertIsNone(result.exception)
            self.assertRegex(
                result.output, r"docker.io/overhangio/openedx:\d+.\d+.\d+\n"
            )

    @patch.object(plugins.BasePlugin, "iter_installed", return_value=[])
    @patch.object(
        plugins.Plugins,
        "iter_hooks",
        return_value=[
            (
                "dev-plugins",
                {"plugin": "plugin:dev-1.0.0", "plugin2": "plugin2:dev-1.0.0"},
            )
        ],
    )
    def test_images_printtag_plugin(
        self, _iter_hooks: Mock, _iter_installed: Mock
    ) -> None:
        with TestContext() as context:
            runner = CliRunner()
            result = runner.invoke(images_command, ["printtag", "plugin"], obj=context)
            self.assertEqual(0, result.exit_code)
            self.assertIsNone(result.exception)
            _iter_hooks.assert_called_once_with("build-image")
            _iter_installed.assert_called()
            self.assertEqual(result.output, "plugin:dev-1.0.0\n")

    @patch.object(plugins.BasePlugin, "iter_installed", return_value=[])
    @patch.object(
        plugins.Plugins,
        "iter_hooks",
        return_value=[
            (
                "dev-plugins",
                {"plugin": "plugin:dev-1.0.0", "plugin2": "plugin2:dev-1.0.0"},
            )
        ],
    )
    @patch.object(images, "build", return_value=None)
    def test_images_build_plugin(
        self, _image_build: Mock, _iter_hooks: Mock, _iter_installed: Mock
    ) -> None:
        with TestContext() as context:
            runner = CliRunner()
            result = runner.invoke(images_command, ["build", "plugin"], obj=context)
            self.assertEqual(0, result.exit_code)
            self.assertIsNone(result.exception)
            _iter_hooks.assert_called_once_with("build-image")
            _iter_installed.assert_called()
            _image_build.assert_called()
            self.assertIn("plugin:dev-1.0.0", _image_build.call_args[0])

    @patch.object(plugins.BasePlugin, "iter_installed", return_value=[])
    @patch.object(
        plugins.Plugins,
        "iter_hooks",
        return_value=[
            (
                "dev-plugins",
                {"plugin": "plugin:dev-1.0.0", "plugin2": "plugin2:dev-1.0.0"},
            )
        ],
    )
    @patch.object(images, "build", return_value=None)
    def test_images_build_plugin_with_args(
        self, _image_build: Mock, _iter_hooks: Mock, _iter_installed: Mock
    ) -> None:
        with TestContext() as context:
            runner = CliRunner()
            args = [
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
            ]
            result = runner.invoke(
                images_command,
                args,
                obj=context,
            )
            self.assertEqual(0, result.exit_code)
            self.assertIsNone(result.exception)
            _iter_hooks.assert_called_once_with("build-image")
            _iter_installed.assert_called()
            _image_build.assert_called()
            self.assertIn("plugin:dev-1.0.0", _image_build.call_args[0])
            for arg in _image_build.call_args[0][2:]:
                if arg == "--build-arg":
                    continue
                self.assertIn(arg, args)

    def test_images_push(self) -> None:
        with TestContext() as context:
            runner = CliRunner()
            result = runner.invoke(images_command, ["push"], obj=context)
            self.assertEqual(0, result.exit_code)
            self.assertIsNone(result.exception)
