import os
import re
import json
import unittest
import tempfile
from io import StringIO
import click
from unittest.mock import Mock, patch
from tests.helpers import TestContext
from tutor import interactive
from tutor import config as tutor_config
from tutor.types import get_typed, Config


class ConfigTests(unittest.TestCase):
    def test_version(self) -> None:
        defaults = tutor_config.get_defaults({})
        self.assertNotIn("TUTOR_VERSION", defaults)

    def test_merge(self) -> None:
        config1: Config = {"x": "y"}
        config2: Config = {"x": "z"}
        tutor_config.merge(config1, config2)
        self.assertEqual({"x": "y"}, config1)

    def test_merge_not_render(self) -> None:
        config: Config = {}
        base = tutor_config.get_base({})
        with patch.object(tutor_config.utils, "random_string", return_value="abcd"):
            tutor_config.merge(config, base)

        # Check that merge does not perform a rendering
        self.assertNotEqual("abcd", config["MYSQL_ROOT_PASSWORD"])

    @unittest.mock.patch("sys.stdout", new_callable=StringIO)
    def test_update_should_create_config_file(self, mock_stdout: StringIO) -> None:
        with tempfile.TemporaryDirectory() as root:
            tutor_config.update(root)
            config_path = re.search(
                r"Configuration saved to (.*)", mock_stdout.getvalue()
            )
            assert config_path is not None
            self.assertTrue(os.path.exists(config_path.group(1)))

    @patch.object(tutor_config.fmt, "echo")
    def test_save_load(self, _: Mock) -> None:
        with tempfile.TemporaryDirectory() as root:
            config1 = tutor_config.load_minimal(root)
            tutor_config.save_config_file(root, config1)
            config2 = tutor_config.load_minimal(root)

        self.assertEqual(config1, config2)

    @patch.object(tutor_config.fmt, "echo")
    def test_removed_entry_is_added_on_save(self, _: Mock) -> None:
        with tempfile.TemporaryDirectory() as root:
            with patch.object(
                tutor_config.utils, "random_string"
            ) as mock_random_string:
                mock_random_string.return_value = "abcd"
                config1 = tutor_config.load_full(root)
                password1 = config1["MYSQL_ROOT_PASSWORD"]

                config1.pop("MYSQL_ROOT_PASSWORD")
                tutor_config.save_config_file(root, config1)

                mock_random_string.return_value = "efgh"
                config2 = tutor_config.load_full(root)
                password2 = config2["MYSQL_ROOT_PASSWORD"]

        self.assertEqual("abcd", password1)
        self.assertEqual("efgh", password2)

    def test_interactive(self) -> None:
        def mock_prompt(*_args: None, **kwargs: str) -> str:
            return kwargs["default"]

        with tempfile.TemporaryDirectory() as rootdir:
            with patch.object(click, "prompt", new=mock_prompt):
                with patch.object(click, "confirm", new=mock_prompt):
                    config = interactive.load_user_config(rootdir, interactive=True)

        self.assertIn("MYSQL_ROOT_PASSWORD", config)
        self.assertEqual(8, len(get_typed(config, "MYSQL_ROOT_PASSWORD", str)))
        self.assertEqual("www.myopenedx.com", config["LMS_HOST"])
        self.assertEqual("studio.www.myopenedx.com", config["CMS_HOST"])

    def test_is_service_activated(self) -> None:
        config: Config = {"RUN_SERVICE1": True, "RUN_SERVICE2": False}
        self.assertTrue(tutor_config.is_service_activated(config, "service1"))
        self.assertFalse(tutor_config.is_service_activated(config, "service2"))

    def test_load_yml_config(self) -> None:
        with TestContext() as context:
            config = context.load_config()
            current = tutor_config.load(context.root)
            self.assertEqual(config, current)

    @unittest.mock.patch("sys.stdout", new_callable=StringIO)
    def test_load_all_json_config(self, _: StringIO) -> None:
        with tempfile.TemporaryDirectory() as root:
            # arrange
            configYmlPath = os.path.join(root, tutor_config.CONFIG_FILENAME)
            configJsonPath = os.path.join(
                root, tutor_config.CONFIG_FILENAME.replace("yml", "json")
            )
            with TestContext() as context:
                config = context.load_config()
                with open(configJsonPath, "w", encoding="utf-8") as f:
                    json.dump(config, f, ensure_ascii=False, indent=4)
                self.assertFalse(os.path.exists(configYmlPath))
                self.assertTrue(os.path.exists(configJsonPath))

                current, default = tutor_config.load_all(root)
                self.assertTrue(os.path.exists(configYmlPath))
                self.assertFalse(os.path.exists(configJsonPath))
                self.assertNotEqual(default, current)
                self.assertEqual(config, current)
