import unittest

from .base import TestCommandMixin


class DevTests(unittest.TestCase, TestCommandMixin):
    def test_dev_help(self) -> None:
        result = self.invoke(["dev", "--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    def test_dev_bindmount(self) -> None:
        result = self.invoke(["dev", "bindmount", "--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)
