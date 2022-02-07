import unittest

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
