import typing as t
import unittest
from unittest.mock import MagicMock, patch

from tests.helpers import temporary_root
from tutor import config as tutor_config
from tutor import serialize
from tutor.commands.k8s import K8sTaskRunner

from .base import TestCommandMixin


class K8sTests(unittest.TestCase, TestCommandMixin):
    def test_k8s_help(self) -> None:
        result = self.invoke(["k8s", "--help"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)

    def test_run_task_escapes_dollar_signs(self) -> None:
        jobs = serialize.dumps(
            {
                "kind": "Job",
                "metadata": {"name": "lms-job"},
                "spec": {"template": {"spec": {"containers": [{"name": "lms"}]}}},
            }
        )
        applied: list[t.Any] = []

        def kubectl(*args: str) -> None:
            with open(args[-1], encoding="utf-8") as job_file:
                applied.append(serialize.load(job_file.read()))

        k8s_clients = MagicMock()
        k8s_clients.batch_api.list_namespaced_job.return_value.items = [
            MagicMock(status=MagicMock(active=0, succeeded=1))
        ]
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            runner = K8sTaskRunner(root, tutor_config.load(root))
            with (
                patch.object(runner, "active_job_names", return_value=[]),
                patch("tutor.utils.check_output", return_value=jobs.encode()),
                patch("tutor.utils.kubectl", side_effect=kubectl),
                patch(
                    "tutor.commands.k8s.K8sClients.instance", return_value=k8s_clients
                ),
            ):
                runner.run_task("lms", "echo '$(HOME) $$ $1'")

        # Kubernetes turns "$$" into "$" and leaves "$(HOME)" unexpanded
        self.assertEqual(
            ["sh", "-e", "-c", "echo '$$(HOME) $$$$ $$1'"],
            applied[0]["spec"]["template"]["spec"]["containers"][0]["args"],
        )
