import unittest

from tests.helpers import temporary_root
from tutor import config as tutor_config

from .base import TestCommandMixin


class ConfigTests(unittest.TestCase, TestCommandMixin):
    def test_config_help(self) -> None:
        result = self.invoke(["config", "--help"])
        self.assertEqual(0, result.exit_code)
        self.assertFalse(result.exception)

    def test_config_save(self) -> None:
        result = self.invoke(["config", "save"])
        self.assertFalse(result.exception)
        self.assertEqual(0, result.exit_code)

    def test_config_save_interactive(self) -> None:
        result = self.invoke(["config", "save", "-i"])
        self.assertFalse(result.exception)
        self.assertEqual(0, result.exit_code)

    def test_config_save_skip_update(self) -> None:
        result = self.invoke(["config", "save", "-e"])
        self.assertFalse(result.exception)
        self.assertEqual(0, result.exit_code)

    def test_config_save_set_value(self) -> None:
        with temporary_root() as root:
            result1 = self.invoke_in_root(root, ["config", "save", "-s", "key=value"])
            result2 = self.invoke_in_root(root, ["config", "printvalue", "key"])
        self.assertFalse(result1.exception)
        self.assertEqual(0, result1.exit_code)
        self.assertIn("value", result2.output)

    def test_config_save_unset_value(self) -> None:
        with temporary_root() as root:
            result1 = self.invoke_in_root(root, ["config", "save", "-U", "key"])
            result2 = self.invoke_in_root(root, ["config", "printvalue", "key"])
        self.assertFalse(result1.exception)
        self.assertEqual(0, result1.exit_code)
        self.assertEqual(1, result2.exit_code)

    def test_config_printroot(self) -> None:
        with temporary_root() as root:
            result = self.invoke_in_root(root, ["config", "printroot"])
        self.assertFalse(result.exception)
        self.assertEqual(0, result.exit_code)
        self.assertIn(root, result.output)

    def test_config_printvalue(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            result = self.invoke_in_root(
                root, ["config", "printvalue", "MYSQL_ROOT_PASSWORD"]
            )
        self.assertFalse(result.exception)
        self.assertEqual(0, result.exit_code)
        self.assertTrue(result.output)

    def test_config_append(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(
                root, ["config", "save", "--append=TEST=value"], catch_exceptions=False
            )
            config1 = tutor_config.load(root)
            self.invoke_in_root(
                root, ["config", "save", "--append=TEST=value"], catch_exceptions=False
            )
            config2 = tutor_config.load(root)
            self.invoke_in_root(
                root, ["config", "save", "--remove=TEST=value"], catch_exceptions=False
            )
            config3 = tutor_config.load(root)
        # Value is appended
        self.assertEqual(["value"], config1["TEST"])
        # Value is not appended a second time
        self.assertEqual(["value"], config2["TEST"])
        # Value is removed
        self.assertEqual([], config3["TEST"])

    def test_config_append_with_existing_default(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(
                root,
                [
                    "config",
                    "save",
                    "--append=OPENEDX_EXTRA_PIP_REQUIREMENTS=my-package==1.0.0",
                ],
                catch_exceptions=False,
            )
            config = tutor_config.load(root)
        assert isinstance(config["OPENEDX_EXTRA_PIP_REQUIREMENTS"], list)
        self.assertEqual(
            ["my-package==1.0.0"], config["OPENEDX_EXTRA_PIP_REQUIREMENTS"]
        )


class PatchesTests(unittest.TestCase, TestCommandMixin):
    def test_config_patches_list(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            result = self.invoke_in_root(root, ["config", "patches", "list"])
        self.assertFalse(result.exception)
        self.assertEqual(0, result.exit_code)
