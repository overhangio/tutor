import json
import os
import unittest
from unittest.mock import Mock, patch

import click

from tests.helpers import PluginsTestCase, temporary_root
from tutor import config as tutor_config
from tutor import env, fmt, hooks, interactive, utils
from tutor.commands import (
    compose,  # noqa: F401  # defines the "iter_mounts" template variable
)
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

    def test_upgrade_obsolete_uwsgi_workers(self) -> None:
        config: Config = {
            "OPENEDX_LMS_UWSGI_WORKERS": 4,
            "OPENEDX_CMS_UWSGI_WORKERS": 3,
        }
        tutor_config.upgrade_obsolete(config)
        self.assertEqual(
            {"OPENEDX_LMS_GRANIAN_WORKERS": 4, "OPENEDX_CMS_GRANIAN_WORKERS": 3},
            config,
        )

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

    @patch.object(fmt, "echo")
    def test_interactive_answer_replaces_expression(self, _: Mock) -> None:
        def mock_prompt(question: str, **kwargs: str) -> str:
            if "teachers" in question:
                return "teach.example.com"
            return kwargs["default"]

        with temporary_root() as root:
            path = self.write_config(root, self.HAND_WRITTEN)
            config = tutor_config.load_minimal(root)
            with patch.object(click, "prompt", new=mock_prompt):
                with patch.object(click, "confirm", new=mock_prompt):
                    answered = interactive.ask_questions(config, run_for_prod=True)
            self.assertIn("CMS_HOST", answered)
            self.assertNotIn("LMS_HOST", answered)
            tutor_config.save_config_file(root, config, explicit=answered)

            contents = self.read_config(path)
            self.assertIn('CMS_HOST: "teach.example.com"', contents)
            self.assertEqual(
                "teach.example.com", tutor_config.get_user(root)["CMS_HOST"]
            )

    @patch.object(fmt, "echo")
    def test_interactive_default_keeps_expression(self, _: Mock) -> None:
        def mock_prompt(*_args: None, **kwargs: str) -> str:
            return kwargs["default"]

        with temporary_root() as root:
            path = self.write_config(root, self.HAND_WRITTEN)
            config = tutor_config.load_minimal(root)
            with patch.object(click, "prompt", new=mock_prompt):
                with patch.object(click, "confirm", new=mock_prompt):
                    answered = interactive.ask_questions(config, run_for_prod=True)
            self.assertNotIn("CMS_HOST", answered)
            tutor_config.save_config_file(root, config, explicit=answered)

            self.assertIn('CMS_HOST: "studio.{{ LMS_HOST }}"', self.read_config(path))

    @patch.object(fmt, "echo")
    def test_yaml_11_keyword_string_is_quoted(self, _: Mock) -> None:
        with temporary_root() as root:
            path = self.write_config(root, self.HAND_WRITTEN)
            config = tutor_config.get_user(root)
            # Under YAML 1.2 these are plain strings, but PyYAML, which reads
            # config.yml, would load them as a boolean, an integer and a null.
            config["MY_FLAG"] = "on"
            config["MY_MODE"] = "0777"
            config["MY_NULL"] = "~"
            tutor_config.save_config_file(
                root, config, explicit=["MY_FLAG", "MY_MODE", "MY_NULL"]
            )

            contents = self.read_config(path)
            self.assertIn("MY_FLAG: 'on'", contents)
            reloaded = tutor_config.get_user(root)
            self.assertEqual("on", reloaded["MY_FLAG"])
            self.assertEqual("0777", reloaded["MY_MODE"])
            self.assertEqual("~", reloaded["MY_NULL"])

    @patch.object(fmt, "echo")
    def test_yaml_11_keyword_is_not_rewritten(self, _: Mock) -> None:
        with temporary_root() as root:
            hand_written = self.HAND_WRITTEN + "ENABLE_HTTPS: yes\nMY_MODE: 0777\n"
            path = self.write_config(root, hand_written)
            config = tutor_config.get_user(root)
            self.assertIs(True, config["ENABLE_HTTPS"])
            self.assertEqual(0o777, config["MY_MODE"])
            tutor_config.save_config_file(root, config)
            self.assertEqual(hand_written, self.read_config(path))

    @patch.object(fmt, "echo")
    def test_duplicate_keys_keep_the_last_value(self, _: Mock) -> None:
        with temporary_root() as root:
            path = self.write_config(
                root,
                "# Domain names\nLMS_HOST: lms.example.com\nLMS_HOST: lms.example.org\n",
            )
            config = tutor_config.get_user(root)
            self.assertEqual("lms.example.org", config["LMS_HOST"])
            config["PLATFORM_NAME"] = "My platform"
            tutor_config.save_config_file(root, config, explicit=["PLATFORM_NAME"])

            contents = self.read_config(path)
            self.assertIn("# Domain names", contents)
            self.assertEqual(1, contents.count("LMS_HOST"))
            self.assertEqual("lms.example.org", tutor_config.get_user(root)["LMS_HOST"])


class MongoDbCredentialsTests(unittest.TestCase):
    """
    Credentials of the MongoDB instance run by Tutor are generated once and stored in
    config.yml, but only applied when Tutor actually runs MongoDB.
    """

    def load(self, user_config: str = "", **environ: str) -> tuple[Config, Config]:
        """
        Save the configuration in a fresh root, then return both what was written to
        config.yml and the full configuration.
        """
        with temporary_root() as root:
            if user_config:
                with open(tutor_config.config_path(root), "w", encoding="utf-8") as f:
                    f.write(user_config)
            with patch.dict(os.environ, environ), patch.object(fmt, "echo"):
                tutor_config.save_config_file(root, tutor_config.load_minimal(root))
                return tutor_config.get_user(root), tutor_config.load_full(root)

    def test_credentials_are_generated(self) -> None:
        saved, config = self.load()
        password = get_typed(saved, "MONGODB_INTERNAL_PASSWORD", str)
        self.assertEqual(24, len(password))
        self.assertEqual("openedx", config["MONGODB_USERNAME"])
        self.assertEqual(password, config["MONGODB_PASSWORD"])
        # Derived values are never written to config.yml
        self.assertNotIn("MONGODB_USERNAME", saved)
        self.assertNotIn("MONGODB_PASSWORD", saved)

    def test_credentials_are_stable(self) -> None:
        with temporary_root() as root, patch.object(fmt, "echo"):
            tutor_config.save_config_file(root, tutor_config.load_minimal(root))
            password1 = tutor_config.load_full(root)["MONGODB_PASSWORD"]
            tutor_config.save_config_file(root, tutor_config.load_minimal(root))
            password2 = tutor_config.load_full(root)["MONGODB_PASSWORD"]
        self.assertEqual(password1, password2)

    def test_credentials_are_added_to_existing_config(self) -> None:
        _saved, config = self.load("LMS_HOST: lms.example.org\n")
        self.assertEqual("openedx", config["MONGODB_USERNAME"])
        self.assertEqual(24, len(get_typed(config, "MONGODB_PASSWORD", str)))

    def test_external_mongodb_without_credentials(self) -> None:
        _saved, config = self.load("RUN_MONGODB: false\n")
        self.assertEqual("", config["MONGODB_USERNAME"])
        self.assertEqual("", config["MONGODB_PASSWORD"])

    def test_external_mongodb_disabled_from_environment(self) -> None:
        _saved, config = self.load(TUTOR_RUN_MONGODB="false")
        self.assertEqual("", config["MONGODB_USERNAME"])
        self.assertEqual("", config["MONGODB_PASSWORD"])

    def test_external_mongodb_credentials_are_preserved(self) -> None:
        _saved, config = self.load(
            "RUN_MONGODB: false\nMONGODB_USERNAME: admin\nMONGODB_PASSWORD: secret\n"
        )
        self.assertEqual("admin", config["MONGODB_USERNAME"])
        self.assertEqual("secret", config["MONGODB_PASSWORD"])

    def render(self, user_config: str = "") -> tuple[Config, dict[str, str]]:
        """
        Save the configuration and the environment in a fresh root, and return the
        full configuration along with a few rendered files.
        """
        with temporary_root() as root:
            if user_config:
                with open(tutor_config.config_path(root), "w", encoding="utf-8") as f:
                    f.write(user_config)
            with patch.object(fmt, "echo"):
                tutor_config.save_config_file(root, tutor_config.load_minimal(root))
                config = tutor_config.load_full(root)
                env.save(root, config)
            files = {}
            for path in [
                "apps/openedx/settings/lms/production.py",
                "local/docker-compose.yml",
                "k8s/deployments.yml",
                "kustomization.yml",
            ]:
                with open(env.pathjoin(root, path), encoding="utf-8") as f:
                    files[path] = f.read()
        return config, files

    def test_credentials_are_rendered(self) -> None:
        config, files = self.render()
        password = config["MONGODB_PASSWORD"]
        settings = files["apps/openedx/settings/lms/production.py"]
        self.assertIn('"user": "openedx",', settings)
        self.assertIn(f'"password": "{password}",', settings)

        compose = files["local/docker-compose.yml"]
        self.assertIn('entrypoint: ["bash", "/openedx/mongodb/entrypoint.sh"]', compose)
        self.assertIn(f'MONGODB_PASSWORD: "{password}"', compose)
        self.assertNotIn("command: mongod", compose)

        deployments = files["k8s/deployments.yml"]
        self.assertIn(
            'command: ["bash", "/openedx/mongodb/entrypoint.sh"]', deployments
        )
        self.assertIn(f'value: "{password}"', deployments)
        self.assertIn("name: mongodb-config", deployments)
        self.assertIn("apps/mongodb/entrypoint.sh", files["kustomization.yml"])

    def test_mongodb_without_password_runs_without_authentication(self) -> None:
        # Users can opt out by setting an empty password
        config, files = self.render('MONGODB_PASSWORD: ""\n')
        self.assertEqual("", config["MONGODB_USERNAME"])
        self.assertIn('"user": None,', files["apps/openedx/settings/lms/production.py"])
        compose = files["local/docker-compose.yml"]
        self.assertIn("command: mongod --storageEngine wiredTiger", compose)
        self.assertNotIn('entrypoint: ["bash", "/openedx/mongodb/', compose)
        deployments = files["k8s/deployments.yml"]
        self.assertIn('args: ["mongod", "--storageEngine", "wiredTiger"]', deployments)
        self.assertNotIn('command: ["bash", "/openedx/mongodb/', deployments)

    def test_entrypoint_is_not_altered_by_rendering(self) -> None:
        _saved, config = self.load()
        rendered = env.render_file(config, "apps", "mongodb", "entrypoint.sh")
        raw = env.read_core_template_file("apps", "mongodb", "entrypoint.sh")
        self.assertEqual(raw.strip(), rendered.strip())
