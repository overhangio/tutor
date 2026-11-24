import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from tutor.commands import k8s
from tutor.exceptions import TutorError

from .base import TestCommandMixin


class K8sTests(unittest.TestCase, TestCommandMixin):
    def test_k8s_help(self) -> None:
        result = self.invoke(["k8s", "--help"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)


class WaitForPodRunningTests(unittest.TestCase):
    @staticmethod
    def pod(phase: str, deleting: bool = False) -> SimpleNamespace:
        return SimpleNamespace(
            status=SimpleNamespace(phase=phase),
            metadata=SimpleNamespace(deletion_timestamp="now" if deleting else None),
        )

    def wait(self, *pod_lists: list[SimpleNamespace], timeout: int = 600) -> Mock:
        core_api = Mock()
        core_api.list_namespaced_pod.side_effect = [
            SimpleNamespace(items=pods) for pods in pod_lists
        ]
        with (
            patch.object(
                k8s.K8sClients, "instance", return_value=Mock(core_api=core_api)
            ),
            patch.object(k8s, "sleep"),
        ):
            k8s.wait_for_pod_running({"K8S_NAMESPACE": "openedx"}, "lms", timeout)
        return core_api

    def test_returns_once_a_pod_is_running(self) -> None:
        core_api = self.wait([], [self.pod("Pending")], [self.pod("Running")])
        self.assertEqual(3, core_api.list_namespaced_pod.call_count)
        core_api.list_namespaced_pod.assert_called_with(
            namespace="openedx", label_selector="app.kubernetes.io/name=lms"
        )

    def test_ignores_terminating_pods(self) -> None:
        core_api = self.wait(
            [self.pod("Running", deleting=True)],
            [self.pod("Running", deleting=True), self.pod("Running")],
        )
        self.assertEqual(2, core_api.list_namespaced_pod.call_count)

    def test_times_out(self) -> None:
        with self.assertRaises(TutorError):
            self.wait([self.pod("Pending")], [self.pod("Pending")], timeout=4)
