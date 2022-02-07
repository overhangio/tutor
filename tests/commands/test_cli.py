import unittest

from tutor.__about__ import __version__

from .base import TestCommandMixin


class CliTests(unittest.TestCase, TestCommandMixin):
    def test_help(self) -> None:
        result = self.invoke(["help"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    def test_cli_help(self) -> None:
        result = self.invoke(["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    def test_cli_version(self) -> None:
        result = self.invoke(["--version"])
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)
        self.assertRegex(result.output, rf"cli, version {__version__}\n")
