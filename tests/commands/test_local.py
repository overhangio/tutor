import os
import tempfile
import unittest
from unittest.mock import patch

from tests.helpers import temporary_root

from .base import TestCommandMixin


class LocalTests(unittest.TestCase, TestCommandMixin):
    def test_local_help(self) -> None:
        result = self.invoke(["local", "--help"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)

    def test_local_quickstart_help(self) -> None:
        result = self.invoke(["local", "quickstart", "--help"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)

    def test_local_upgrade_help(self) -> None:
        result = self.invoke(["local", "upgrade", "--help"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)

    def test_copyfrom(self) -> None:
        with temporary_root() as root:
            with tempfile.TemporaryDirectory() as directory:
                with patch("tutor.utils.docker_compose") as mock_docker_compose:
                    self.invoke_in_root(root, ["config", "save"])

                    # Copy to existing directory
                    result = self.invoke_in_root(
                        root, ["local", "copyfrom", "lms", "/openedx/venv", directory]
                    )
                    self.assertIsNone(result.exception)
                    self.assertEqual(0, result.exit_code)
                    self.assertIn(
                        f"--volume={directory}:/tmp/mount",
                        mock_docker_compose.call_args[0],
                    )
                    self.assertIn(
                        "cp --recursive --preserve /openedx/venv /tmp/mount",
                        mock_docker_compose.call_args[0],
                    )

                    # Copy to non-existing directory
                    result = self.invoke_in_root(
                        root,
                        [
                            "local",
                            "copyfrom",
                            "lms",
                            "/openedx/venv",
                            os.path.join(directory, "venv2"),
                        ],
                    )
                    self.assertIsNone(result.exception)
                    self.assertEqual(0, result.exit_code)
                    self.assertIn(
                        f"--volume={directory}:/tmp/mount",
                        mock_docker_compose.call_args[0],
                    )
                    self.assertIn(
                        "cp --recursive --preserve /openedx/venv /tmp/mount/venv2",
                        mock_docker_compose.call_args[0],
                    )
