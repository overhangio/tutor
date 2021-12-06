import unittest

from click.testing import CliRunner
from tutor.commands.k8s import k8s


class K8sTests(unittest.TestCase):
    def test_k8s_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(k8s, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)
