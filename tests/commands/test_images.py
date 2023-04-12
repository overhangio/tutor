from unittest.mock import Mock, patch

from tests.helpers import PluginsTestCase, temporary_root
from tutor import images, plugins
from tutor.__about__ import __version__
from tutor.commands.images import ImageNotFoundError

from .base import TestCommandMixin


class ImagesTests(PluginsTestCase, TestCommandMixin):
    def test_images_help(self) -> None:
        result = self.invoke(["images", "--help"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)

    def test_images_pull_image(self) -> None:
        result = self.invoke(["images", "pull"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)

    def test_images_pull_plugin_invalid_plugin_should_throw_error(self) -> None:
        result = self.invoke(["images", "pull", "plugin"])
        self.assertEqual(1, result.exit_code)
        self.assertEqual(ImageNotFoundError, type(result.exception))

    @patch.object(images, "pull", return_value=None)
    def test_images_pull_plugin(self, image_pull: Mock) -> None:
        plugins.v0.DictPlugin(
            {
                "name": "plugin1",
                "hooks": {
                    "remote-image": {
                        "service1": "service1:1.0.0",
                        "service2": "service2:2.0.0",
                    }
                },
            }
        )
        plugins.load("plugin1")
        result = self.invoke(["images", "pull", "service1"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)
        image_pull.assert_called_once_with("service1:1.0.0")

    @patch.object(images, "pull", return_value=None)
    def test_images_pull_all_vendor_images(self, image_pull: Mock) -> None:
        result = self.invoke(["images", "pull", "mysql"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)
        # Note: we should update this tag whenever the mysql image is updated
        image_pull.assert_called_once_with("docker.io/mysql:8.0.33")

    def test_images_printtag_image(self) -> None:
        result = self.invoke(["images", "printtag", "openedx"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)
        self.assertRegex(
            result.output, rf"docker.io/overhangio/openedx:{__version__}\n"
        )

    def test_images_printtag_plugin(self) -> None:
        plugins.v0.DictPlugin(
            {
                "name": "plugin1",
                "hooks": {
                    "build-image": {
                        "service1": "service1:1.0.0",
                        "service2": "service2:2.0.0",
                    }
                },
            }
        )
        plugins.load("plugin1")
        result = self.invoke(["images", "printtag", "service1"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code, result)
        self.assertEqual(result.output, "service1:1.0.0\n")

    @patch.object(images, "build", return_value=None)
    def test_images_build_plugin(self, mock_image_build: Mock) -> None:
        plugins.v0.DictPlugin(
            {
                "name": "plugin1",
                "hooks": {
                    "build-image": {
                        "service1": "service1:1.0.0",
                        "service2": "service2:2.0.0",
                    }
                },
            }
        )
        plugins.load("plugin1")
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            result = self.invoke_in_root(root, ["images", "build", "service1"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)
        mock_image_build.assert_called()
        self.assertIn("service1:1.0.0", mock_image_build.call_args[0])

    @patch.object(images, "build", return_value=None)
    def test_images_build_plugin_with_args(self, image_build: Mock) -> None:
        plugins.v0.DictPlugin(
            {
                "name": "plugin1",
                "hooks": {
                    "build-image": {
                        "service1": "service1:1.0.0",
                        "service2": "service2:2.0.0",
                    }
                },
            }
        )
        plugins.load("plugin1")
        build_args = [
            "images",
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
            "service1",
        ]
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            result = self.invoke_in_root(root, build_args)
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)
        image_build.assert_called()
        self.assertIn("service1:1.0.0", image_build.call_args[0])
        for arg in image_build.call_args[0][2:]:
            # The only extra args are `--build-arg`
            if arg != "--build-arg":
                self.assertIn(arg, build_args)

    def test_images_push(self) -> None:
        result = self.invoke(["images", "push"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)
