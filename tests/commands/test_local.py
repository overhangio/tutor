import os
import pathlib
import tempfile
import unittest
from unittest.mock import patch

from tests.helpers import caddy_output, fixture, temporary_root, utc
from tutor import caddy
from tutor.exceptions import TutorError

from .base import TestCommandMixin


class LocalTests(unittest.TestCase, TestCommandMixin):
    def test_local_help(self) -> None:
        result = self.invoke(["local", "--help"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)

    def test_local_launch_help(self) -> None:
        result = self.invoke(["local", "launch", "--help"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)

    def test_local_upgrade_help(self) -> None:
        result = self.invoke(["local", "upgrade", "--help"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)

    def test_copyfrom(self) -> None:
        with temporary_root() as root:
            with tempfile.TemporaryDirectory() as directory:
                # resolve actual path, just like click.Path does it.
                directory = os.fsdecode(pathlib.Path(directory).resolve())
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

    def test_https_certificates(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(
                root,
                [
                    "config",
                    "save",
                    "--set=ENABLE_HTTPS=true",
                    "--set=LMS_HOST=learn.example.com",
                    "--set=CMS_HOST=studio.learn.example.com",
                ],
            )
            path = f"{caddy.CERTIFICATES_DIR}/{caddy.LETSENCRYPT}/learn.example.com/learn.example.com.crt"
            output = caddy_output(
                fixture("caddy/adapted-tutor.json"),
                certificates=[(path, fixture("caddy/lms.example.test.crt"), "")],
            )
            with patch("tutor.utils.check_output", return_value=output.encode()) as run:
                with patch.object(caddy, "utcnow", return_value=utc(2026, 11, 19)):
                    result = self.invoke_in_root(root, ["local", "https-certificates"])
            self.assertIsNone(result.exception)
            self.assertEqual(0, result.exit_code)
            command = run.call_args.args
            self.assertEqual(("docker", "compose"), command[:2])
            self.assertEqual(("exec", "-T", "caddy", "sh", "-c"), command[-6:-1])
            self.assertEqual({"hidden": command[-1]}, run.call_args.kwargs)
            lines = result.output.splitlines()
            self.assertTrue(lines[0].startswith("DOMAIN"))
            self.assertTrue(lines[1].startswith("learn.example.com"))
            self.assertIn("valid", lines[1])
            self.assertIn("missing (will be requested)", lines[2])
            self.assertIn("New certificates that Caddy will request: 2.", result.output)

            # Caddy is not running
            with patch("tutor.utils.check_output", side_effect=TutorError("failed")):
                result = self.invoke_in_root(root, ["local", "https-certificates"])
            self.assertEqual(1, result.exit_code)
            self.assertIn("tutor local start -d caddy", str(result.exception))
