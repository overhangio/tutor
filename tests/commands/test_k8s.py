import unittest

from .base import TestCommandMixin


class K8sTests(unittest.TestCase, TestCommandMixin):
    def test_k8s_help(self) -> None:
        result = self.invoke(["k8s", "--help"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)
