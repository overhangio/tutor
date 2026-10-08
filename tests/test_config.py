import json
import os
import unittest
from unittest.mock import Mock, patch

import click

from tests.helpers import PluginsTestCase, temporary_root
from tutor import config as tutor_config
from tutor import fmt, hooks, interactive, utils
from tutor.types import Config, get_typed


class ConfigTests(unittest.TestCase):
    def test_version(self) -> None:
        defaults = tutor_config.get_defaults()
        self.assertNotIn("TUTOR_VERSION", defaults)

    def test_merge(self) -> None:
        config1: Config = {"x": "y"}
        config2: Config = {"x": "z"}
        tutor_config.merge(config1, config2)
        self.assertEqual({"x": "y"}, config1)

    def test_merge_not_render(self) -> None:
        config: Config = {}
        base = tutor_config.get_base()
        with patch.object(utils, "random_string", return_value="abcd"):
            tutor_config.merge(config, base)

        # Check that merge does not perform a rendering
        self.assertNotEqual("abcd", config["MYSQL_ROOT_PASSWORD"])

    @patch.object(fmt, "echo")
    def test_update_twice_should_return_same_config(self, _: Mock) -> None:
        with temporary_root() as root:
            config1 = tutor_config.load_minimal(root)
            tutor_config.save_config_file(root, config1)
            config2 = tutor_config.load_minimal(root)

        self.assertEqual(config1, config2)

    def test_interactive(self) -> None:
        def mock_prompt(*_args: None, **kwargs: str) -> str:
            return kwargs["default"]

        with temporary_root() as rootdir:
            with patch.object(click, "prompt", new=mock_prompt):
                with patch.object(click, "confirm", new=mock_prompt):
                    config = tutor_config.load_minimal(rootdir)
                    interactive.ask_questions(config)

        self.assertIn("MYSQL_ROOT_PASSWORD", config)
        self.assertEqual(8, len(get_typed(config, "MYSQL_ROOT_PASSWORD", str)))
        self.assertEqual("local.openedx.io", config["LMS_HOST"])
        self.assertEqual("studio.local.openedx.io", config["CMS_HOST"])

    def test_meilisearch_url_default(self) -> None:
        # MEILISEARCH_URL_DEFAULT is hardcoded, so make sure it does not drift
        # away from the actual default.
        self.assertEqual(
            tutor_config.get_template("defaults.yml")["MEILISEARCH_URL"],
            tutor_config.MEILISEARCH_URL_DEFAULT,
        )

    @patch.object(fmt, "echo")
    def test_check_meilisearch_url(self, echo: Mock) -> None:
        def alerts() -> list[str]:
            return [str(call.args[0]) for call in echo.call_args_list]

        # Tutor runs its own Meilisearch: no warning
        tutor_config._check_meilisearch_url(
            {
                "RUN_MEILISEARCH": True,
                "MEILISEARCH_URL": tutor_config.MEILISEARCH_URL_DEFAULT,
            }
        )
        self.assertFalse(alerts())

        # Meilisearch is hosted externally, but the URL was not changed: warn
        tutor_config._check_meilisearch_url(
            {
                "RUN_MEILISEARCH": False,
                "MEILISEARCH_URL": tutor_config.MEILISEARCH_URL_DEFAULT,
            }
        )
        self.assertTrue(any("MEILISEARCH_URL" in alert for alert in alerts()))

        # Meilisearch is hosted externally and the URL points to it: no new warning
        echo.reset_mock()
        tutor_config._check_meilisearch_url(
            {
                "RUN_MEILISEARCH": False,
                "MEILISEARCH_URL": "http://meilisearch.example.com:7700",
            }
        )
        self.assertFalse(alerts())

    @patch.object(fmt, "echo")
    def test_check_meilisearch_url_on_load(self, echo: Mock) -> None:
        with temporary_root() as root:
            tutor_config.save_config_file(root, {"RUN_MEILISEARCH": False})
            echo.reset_mock()
            tutor_config.load_full(root)
        self.assertTrue(
            any("MEILISEARCH_URL" in str(call.args[0]) for call in echo.call_args_list)
        )

    def test_is_service_activated(self) -> None:
        config: Config = {"RUN_SERVICE1": True, "RUN_SERVICE2": False}
        self.assertTrue(tutor_config.is_service_activated(config, "service1"))
        self.assertFalse(tutor_config.is_service_activated(config, "service2"))

    @patch.object(fmt, "echo")
    def test_json_config_is_overwritten_by_yaml(self, _: Mock) -> None:
        with temporary_root() as root:
            # Create config from scratch
            config_yml_path = os.path.join(root, tutor_config.CONFIG_FILENAME)
            config_json_path = os.path.join(
                root, tutor_config.CONFIG_FILENAME.replace("yml", "json")
            )
            config = tutor_config.load_full(root)

            # Save config to json
            with open(config_json_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            self.assertFalse(os.path.exists(config_yml_path))
            self.assertTrue(os.path.exists(config_json_path))

            # Reload and compare
            current = tutor_config.load_full(root)
            self.assertTrue(os.path.exists(config_yml_path))
            self.assertFalse(os.path.exists(config_json_path))
            self.assertEqual(config, current)


class ConfigPluginTestCase(PluginsTestCase):
    @patch.object(fmt, "echo")
    def test_removed_entry_is_added_on_save(self, _: Mock) -> None:
        with temporary_root() as root:
            mock_random_string = Mock()

            hooks.Filters.ENV_TEMPLATE_FILTERS.add_item(
                ("random_string", mock_random_string),
            )
            mock_random_string.return_value = "abcd"
            config1 = tutor_config.load_full(root)
            password1 = config1.pop("MYSQL_ROOT_PASSWORD")

            tutor_config.save_config_file(root, config1)

            mock_random_string.return_value = "efgh"
            config2 = tutor_config.load_full(root)
            password2 = config2["MYSQL_ROOT_PASSWORD"]

        self.assertEqual("abcd", password1)
        self.assertEqual("efgh", password2)


class ConfigRoundTripTests(unittest.TestCase):
    """
    Check that saving the configuration does not destroy what users wrote by hand
    in config.yml. See https://github.com/overhangio/tutor/issues/1272.
    """

    HAND_WRITTEN = """\
---
# Domain names
# See https://example.com/tickets/1234
LMS_HOST: lms.example.com
CMS_HOST: "studio.{{ LMS_HOST }}"

# Temporarily disabled while we debug the indexer
RUN_MEILISEARCH: false

PLUGINS:
  - mfe
"""

    def write_config(self, root: str, contents: str) -> str:
        path = os.path.join(root, tutor_config.CONFIG_FILENAME)
        with open(path, "w", encoding="utf-8") as f:
            f.write(contents)
        return path

    def read_config(self, path: str) -> str:
        with open(path, encoding="utf-8") as f:
            return f.read()

    @patch.object(fmt, "echo")
    def test_unchanged_save_leaves_file_untouched(self, _: Mock) -> None:
        with temporary_root() as root:
            path = self.write_config(root, self.HAND_WRITTEN)
            config = tutor_config.get_user(root)
            tutor_config.render_full(config)
            tutor_config.save_config_file(root, config)
            self.assertEqual(self.HAND_WRITTEN, self.read_config(path))

    @patch.object(fmt, "echo")
    def test_changed_entry_preserves_comments_and_order(self, _: Mock) -> None:
        with temporary_root() as root:
            path = self.write_config(root, self.HAND_WRITTEN)
            config = tutor_config.get_user(root)
            tutor_config.render_full(config)
            config["LMS_HOST"] = "lms.example.org"
            tutor_config.save_config_file(root, config, explicit=["LMS_HOST"])

            contents = self.read_config(path)
            self.assertIn("# Domain names", contents)
            self.assertIn("# See https://example.com/tickets/1234", contents)
            self.assertIn("# Temporarily disabled while we debug the indexer", contents)
            self.assertIn("LMS_HOST: lms.example.org", contents)
            # Keys keep their original, non-alphabetical order
            self.assertLess(contents.index("LMS_HOST"), contents.index("CMS_HOST"))
            self.assertLess(
                contents.index("CMS_HOST"), contents.index("RUN_MEILISEARCH")
            )
            # The document marker and the sequence indentation are kept too
            self.assertTrue(contents.startswith("---\n"))
            self.assertIn("PLUGINS:\n  - mfe\n", contents)

    @patch.object(fmt, "echo")
    def test_templated_entry_is_not_flattened(self, _: Mock) -> None:
        with temporary_root() as root:
            path = self.write_config(root, self.HAND_WRITTEN)
            config = tutor_config.get_user(root)
            tutor_config.render_full(config)
            self.assertEqual("studio.lms.example.com", config["CMS_HOST"])

            tutor_config.save_config_file(root, config)
            self.assertIn('CMS_HOST: "studio.{{ LMS_HOST }}"', self.read_config(path))

    @patch.object(fmt, "echo")
    def test_templated_entry_survives_change_to_the_entry_it_points_at(
        self, _: Mock
    ) -> None:
        with temporary_root() as root:
            path = self.write_config(root, self.HAND_WRITTEN)
            config = tutor_config.get_user(root)
            tutor_config.render_full(config)
            # Changing LMS_HOST also changes what CMS_HOST renders to. Note that
            # the CMS_HOST we hold in memory is now stale, exactly as it is after
            # `tutor config save --set LMS_HOST=...`: the expression must survive
            # all the same, instead of being frozen to its previous result.
            config["LMS_HOST"] = "lms.example.org"
            self.assertEqual("studio.lms.example.com", config["CMS_HOST"])
            tutor_config.save_config_file(root, config, explicit=["LMS_HOST"])

            contents = self.read_config(path)
            self.assertIn("LMS_HOST: lms.example.org", contents)
            self.assertIn('CMS_HOST: "studio.{{ LMS_HOST }}"', contents)

    @patch.object(fmt, "echo")
    def test_explicit_entry_is_written_as_a_literal(self, _: Mock) -> None:
        with temporary_root() as root:
            path = self.write_config(root, self.HAND_WRITTEN)
            config = tutor_config.get_user(root)
            tutor_config.render_full(config)
            # `tutor config save --set CMS_HOST=studio.lms.example.com` asks for a
            # literal, even though the file holds an expression that renders to it.
            tutor_config.save_config_file(root, config, explicit=["CMS_HOST"])

            contents = self.read_config(path)
            # The expression is gone, but the quoting style the user chose is kept.
            self.assertIn('CMS_HOST: "studio.lms.example.com"', contents)
            self.assertNotIn("{{ LMS_HOST }}", contents)

    @patch.object(fmt, "echo")
    def test_non_deterministic_expression_is_frozen(self, _: Mock) -> None:
        with temporary_root() as root:
            path = self.write_config(
                root, 'MYSQL_ROOT_PASSWORD: "{{ 8|random_string }}"\n'
            )
            config = tutor_config.get_user(root)
            tutor_config.render_full(config)
            password = get_typed(config, "MYSQL_ROOT_PASSWORD", str)
            tutor_config.save_config_file(root, config)

            contents = self.read_config(path)
            self.assertNotIn("random_string", contents)
            self.assertIn(password, contents)

    @patch.object(fmt, "echo")
    def test_new_entries_are_appended(self, _: Mock) -> None:
        with temporary_root() as root:
            path = self.write_config(root, self.HAND_WRITTEN)
            config = tutor_config.get_user(root)
            tutor_config.render_full(config)
            config["ENABLE_HTTPS"] = True
            tutor_config.save_config_file(root, config, explicit=["ENABLE_HTTPS"])

            contents = self.read_config(path)
            self.assertIn("# Domain names", contents)
            self.assertLess(contents.index("PLUGINS"), contents.index("ENABLE_HTTPS"))

    @patch.object(fmt, "echo")
    def test_removed_entry_is_deleted_from_file(self, _: Mock) -> None:
        with temporary_root() as root:
            path = self.write_config(root, self.HAND_WRITTEN)
            config = tutor_config.get_user(root)
            tutor_config.render_full(config)
            config.pop("RUN_MEILISEARCH")
            tutor_config.save_config_file(root, config)

            contents = self.read_config(path)
            self.assertNotIn("RUN_MEILISEARCH", contents)
            self.assertIn("# Domain names", contents)

    @patch.object(fmt, "echo")
    def test_file_is_created_when_missing(self, _: Mock) -> None:
        with temporary_root() as root:
            config: Config = {"LMS_HOST": "lms.example.com"}
            tutor_config.save_config_file(root, config)
            path = os.path.join(root, tutor_config.CONFIG_FILENAME)
            self.assertTrue(os.path.exists(path))
            self.assertIn("LMS_HOST: lms.example.com", self.read_config(path))
