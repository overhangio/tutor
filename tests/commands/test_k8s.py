import unittest
from unittest.mock import patch

from tests.helpers import caddy_output, fixture, temporary_root
from tutor.exceptions import TutorError

from .base import TestCommandMixin


class K8sTests(unittest.TestCase, TestCommandMixin):
    def test_k8s_help(self) -> None:
        result = self.invoke(["k8s", "--help"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)

    @patch("tutor.utils.check_kubectl")
    def test_https_certificates(self, _check_kubectl: object) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save", "--set=ENABLE_HTTPS=true"])
            output = caddy_output(fixture("caddy/adapted-tutor.json"))
            with patch("tutor.utils.check_output", return_value=output.encode()) as run:
                result = self.invoke_in_root(root, ["k8s", "https-certificates"])
            self.assertIsNone(result.exception)
            self.assertEqual(0, result.exit_code)
            self.assertIn("missing (will be requested)", result.output)
            self.assertEqual(
                (
                    "kubectl",
                    "exec",
                    "--namespace",
                    "openedx",
                    "deployment/caddy",
                    "--container=caddy",
                    "--",
                    "sh",
                    "-c",
                ),
                run.call_args.args[:-1],
            )
            self.assertEqual({"echo": False}, run.call_args.kwargs)

            # Caddy is not running
            with patch("tutor.utils.check_output", side_effect=TutorError("failed")):
                result = self.invoke_in_root(root, ["k8s", "https-certificates"])
            self.assertEqual(1, result.exit_code)
            self.assertIn("tutor k8s start caddy", str(result.exception))
