import os
import tempfile
import unittest
from unittest.mock import patch

from tests.helpers import PluginsTestCase, temporary_root
from tutor import hooks
from tutor.commands import jobs
from tutor.commands.jobs_utils import load_env_file, parse_test_env_var
from tutor.exceptions import TutorError
from tutor.plugins.openedx import lms_init_script_template

from .base import TestCommandMixin


class JobsTests(PluginsTestCase, TestCommandMixin):
    def test_initialise(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            result = self.invoke_in_root(root, ["local", "do", "init"])
            self.assertIsNone(result.exception)
            self.assertEqual(0, result.exit_code)
            self.assertIn("All services initialised.", result.stdout)

    def _run_init(self, *args: str) -> list[tuple[str, str]]:
        """
        Run `local do init` and return the (job service, command) tuples.
        """
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            with patch("tutor.utils.docker_compose") as mock_docker_compose:
                result = self.invoke_in_root(root, ["local", "do", "init", *args])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)
        tasks = []
        for call in mock_docker_compose.call_args_list:
            services = [arg for arg in call.args if arg.endswith("-job")]
            if services:
                tasks.append((services[0], call.args[-1]))
        return tasks

    def _add_lms_init_items(self) -> None:
        with hooks.Contexts.app("myplugin").enter():
            hooks.Filters.OPENEDX_SERVICE_USERS.add_item(
                {"username": "myplugin", "staff": True}
            )
            hooks.Filters.OPENEDX_OAUTH2_APPLICATIONS.add_item(
                {
                    "name": "myplugin-sso",
                    "user": "myplugin",
                    "client_id": "myplugin",
                    "client_secret": '{{ LMS_HOST }}\'s "secret" \U0001f600',
                    "skip_authorization": True,
                }
            )
            hooks.Filters.OPENEDX_WAFFLE_FLAGS.add_items(
                [("myplugin.enabled", True), ("myplugin.disabled", False)]
            )

    def test_initialise_lms_init_items(self) -> None:
        # Declare core init tasks and items
        hooks.Actions.CORE_READY.do()
        self._add_lms_init_items()
        tasks = self._run_init()
        lms_tasks = [command for service, command in tasks if service == "lms-job"]
        lms_init = [command for command in lms_tasks if "lms migrate" in command]
        self.assertEqual(1, len(lms_init))
        script = lms_init[0]
        # Core items
        self.assertIn(
            "call_command('manage_user', 'cms', 'cms@openedx', '--unusable-password')",
            script,
        )
        self.assertIn("'cms-sso-dev', 'cms')", script)
        # Plugin items, with rendered and escaped values
        self.assertIn(
            "call_command('manage_user', 'myplugin', 'myplugin@openedx', '--staff')",
            script,
        )
        secret = 'local.openedx.io\'s "secret" \U0001f600'
        self.assertIn(f"'--client-secret', {secret!r}", script)
        self.assertIn(
            "call_command('waffle_flag', 'myplugin.enabled', '--create', '--everyone')",
            script,
        )
        self.assertIn(
            "call_command('waffle_flag', 'myplugin.disabled', '--create', '--deactivate')",
            script,
        )
        # Users are created before the applications that reference them
        self.assertLess(
            script.index("'manage_user', 'myplugin'"),
            script.index("'myplugin-sso', 'myplugin')"),
        )
        # All items are created in a single Django process
        self.assertEqual(1, script.count("./manage.py lms shell"))

    def test_initialise_limit_runs_plugin_lms_init_items(self) -> None:
        hooks.Actions.CORE_READY.do()
        self._add_lms_init_items()
        with hooks.Contexts.app("myplugin").enter():
            hooks.Filters.CLI_DO_INIT_TASKS.add_item(("myplugin", "echo myplugin"))
        tasks = self._run_init("--limit=myplugin")
        self.assertEqual(["lms-job", "myplugin-job"], [service for service, _ in tasks])
        script = tasks[0][1]
        self.assertIn("'manage_user', 'myplugin'", script)
        self.assertIn("'myplugin-sso', 'myplugin')", script)
        # Core items are not included
        self.assertNotIn("'cms-sso'", script)
        self.assertNotIn("lms migrate", script)

    def test_initialise_limit_without_lms_init_items(self) -> None:
        with hooks.Contexts.app("myplugin").enter():
            hooks.Filters.CLI_DO_INIT_TASKS.add_item(("myplugin", "echo myplugin"))
        tasks = self._run_init("--limit=myplugin")
        self.assertEqual(["myplugin-job"], [service for service, _ in tasks])

    def test_lms_init_script_invalid_items(self) -> None:
        hooks.Filters.OPENEDX_OAUTH2_APPLICATIONS.add_item(
            {"name": "app", "user": "user", "redirect_uri": "http://typo"}
        )
        with self.assertRaises(TutorError) as context:
            lms_init_script_template()
        self.assertIn("redirect_uri", str(context.exception))

    def test_lms_init_script_invalid_bool(self) -> None:
        hooks.Filters.OPENEDX_SERVICE_USERS.add_item(
            {"username": "user", "staff": "false"}
        )
        with self.assertRaises(TutorError) as context:
            lms_init_script_template()
        self.assertIn("'staff'", str(context.exception))

    def test_lms_init_script_invalid_waffle_flag(self) -> None:
        hooks.Filters.OPENEDX_WAFFLE_FLAGS.add_item(("flag", True, "extra"))  # type: ignore[arg-type]
        with self.assertRaises(TutorError) as context:
            lms_init_script_template()
        self.assertIn("OPENEDX_WAFFLE_FLAGS", str(context.exception))

    def test_lms_init_script_missing_required_key(self) -> None:
        hooks.Filters.OPENEDX_SERVICE_USERS.add_item({"staff": True})
        with self.assertRaises(TutorError) as context:
            lms_init_script_template()
        self.assertIn("username", str(context.exception))

    def test_create_user_template_without_staff(self) -> None:
        command = jobs.create_user_template(
            "superuser", False, "username", "email", "p4ssw0rd"
        )
        self.assertNotIn("--staff", command)
        self.assertIn("set_password", command)

    def test_create_user_template_with_staff(self) -> None:
        command = jobs.create_user_template(
            "superuser", True, "username", "email", "p4ssw0rd"
        )
        self.assertIn("--staff", command)

    def test_import_demo_course(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            with patch("tutor.utils.docker_compose") as mock_docker_compose:
                result = self.invoke_in_root(root, ["local", "do", "importdemocourse"])
                dc_args, _dc_kwargs = mock_docker_compose.call_args
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)
        self.assertIn("cms-job", dc_args)
        self.assertIn(
            "git clone https://github.com/openedx/openedx-demo-course", dc_args[-1]
        )

    def test_import_demo_libraries(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            with patch("tutor.utils.docker_compose") as mock_docker_compose:
                result = self.invoke_in_root(
                    root,
                    [
                        "local",
                        "do",
                        "importdemolibraries",
                        "admin",
                    ],
                )
                dc_args, _dc_kwargs = mock_docker_compose.call_args
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)
        self.assertIn("cms-job", dc_args)
        self.assertIn(
            "git clone https://github.com/openedx/openedx-demo-course", dc_args[-1]
        )
        self.assertIn(
            "./manage.py cms import_content_library /tmp/library.tar.gz admin",
            dc_args[-1],
        )

    def test_set_theme(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            with patch("tutor.utils.docker_compose") as mock_docker_compose:
                result = self.invoke_in_root(
                    root,
                    [
                        "local",
                        "do",
                        "settheme",
                        "--domain",
                        "domain1",
                        "--domain",
                        "domain2",
                        "beautiful",
                    ],
                )
                dc_args, _dc_kwargs = mock_docker_compose.call_args

            self.assertIsNone(result.exception)
            self.assertEqual(0, result.exit_code)
            self.assertIn("lms-job", dc_args)
            self.assertIn("assign_theme('beautiful', 'domain1')", dc_args[-1])
            self.assertIn("assign_theme('beautiful', 'domain2')", dc_args[-1])

    def test_convert_mysql_utf8mb4_charset_all_tables(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            with patch("tutor.utils.docker_compose") as mock_docker_compose:
                result = self.invoke_in_root(
                    root,
                    [
                        "local",
                        "do",
                        "convert-mysql-utf8mb4-charset",
                        "--non-interactive",
                    ],
                )
                dc_args, _dc_kwargs = mock_docker_compose.call_args

            self.assertIsNone(result.exception)
            self.assertEqual(0, result.exit_code)
            self.assertIn("lms-job", dc_args)
            self.assertIn("utf8mb4", dc_args[-1])
            self.assertIn("openedx", dc_args[-1])
            self.assertIn("utf8mb4_unicode_ci", dc_args[-1])
            self.assertNotIn("regexp", dc_args[-1])

    def test_convert_mysql_utf8mb4_charset_include_tables(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            with patch("tutor.utils.docker_compose") as mock_docker_compose:
                result = self.invoke_in_root(
                    root,
                    [
                        "local",
                        "do",
                        "convert-mysql-utf8mb4-charset",
                        "--include=courseware_studentmodule,xblock",
                    ],
                )
                dc_args, _dc_kwargs = mock_docker_compose.call_args

            self.assertIsNone(result.exception)
            self.assertEqual(0, result.exit_code)
            self.assertIn("lms-job", dc_args)
            self.assertIn("openedx", dc_args[-1])
            self.assertIn("utf8mb4", dc_args[-1])
            self.assertIn("utf8mb4_unicode_ci", dc_args[-1])
            self.assertIn("regexp", dc_args[-1])
            self.assertIn("courseware_studentmodule", dc_args[-1])
            self.assertIn("xblock", dc_args[-1])

    def test_convert_mysql_utf8mb4_charset_exclude_tables(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            with patch("tutor.utils.docker_compose") as mock_docker_compose:
                result = self.invoke_in_root(
                    root,
                    [
                        "local",
                        "do",
                        "convert-mysql-utf8mb4-charset",
                        "--database=discovery",
                        "--exclude=course,auth",
                    ],
                )
                dc_args, _dc_kwargs = mock_docker_compose.call_args

            self.assertIsNone(result.exception)
            self.assertEqual(0, result.exit_code)
            self.assertIn("lms-job", dc_args)
            self.assertIn("utf8mb4", dc_args[-1])
            self.assertIn("utf8mb4_unicode_ci", dc_args[-1])
            self.assertIn("discovery", dc_args[-1])
            self.assertIn("regexp", dc_args[-1])
            self.assertIn("NOT", dc_args[-1])
            self.assertIn("course", dc_args[-1])
            self.assertIn("auth", dc_args[-1])

    def test_update_mysql_authentication_plugin_official_plugin(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            with patch("tutor.utils.docker_compose") as mock_docker_compose:
                result = self.invoke_in_root(
                    root,
                    [
                        "local",
                        "do",
                        "update-mysql-authentication-plugin",
                        "openedx",
                    ],
                )
                dc_args, _dc_kwargs = mock_docker_compose.call_args

            self.assertIsNone(result.exception)
            self.assertEqual(0, result.exit_code)
            self.assertIn("lms-job", dc_args)
            self.assertIn("caching_sha2_password", dc_args[-1])
            self.assertIn("openedx", dc_args[-1])

    def test_update_mysql_authentication_plugin_custom_plugin(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            with patch("tutor.utils.docker_compose") as mock_docker_compose:
                result = self.invoke_in_root(
                    root,
                    [
                        "local",
                        "do",
                        "update-mysql-authentication-plugin",
                        "mypluginuser",
                        "--password=mypluginpassword",
                    ],
                )
                dc_args, _dc_kwargs = mock_docker_compose.call_args

            self.assertIsNone(result.exception)
            self.assertEqual(0, result.exit_code)
            self.assertIn("lms-job", dc_args)
            self.assertIn("caching_sha2_password", dc_args[-1])
            self.assertIn("mypluginuser", dc_args[-1])
            self.assertIn("mypluginpassword", dc_args[-1])


class TestEnvHelpers(unittest.TestCase):
    # --- parse_test_env_var ---

    def test_parse_env_var_basic(self) -> None:
        self.assertEqual(("KEY", "VALUE"), parse_test_env_var("KEY=VALUE"))

    def test_parse_env_var_empty_value(self) -> None:
        self.assertEqual(("KEY", ""), parse_test_env_var("KEY="))

    def test_parse_env_var_value_contains_equals(self) -> None:
        self.assertEqual(("KEY", "a=b=c"), parse_test_env_var("KEY=a=b=c"))

    def test_parse_env_var_no_equals_raises(self) -> None:
        with self.assertRaises(TutorError):
            parse_test_env_var("NOEQUALS")

    def test_parse_env_var_empty_key_raises(self) -> None:
        with self.assertRaises(TutorError):
            parse_test_env_var("=VALUE")

    # --- load_env_file ---

    def test_load_env_file_valid(self) -> None:
        content = "KEY1: value1\nKEY2: value2\n"
        with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as f:
            f.write(content)
            path = f.name
        try:
            result = load_env_file(path)
            self.assertEqual({"KEY1": "value1", "KEY2": "value2"}, result)
        finally:
            os.unlink(path)

    def test_load_env_file_coerces_values_to_str(self) -> None:
        content = "PORT: 8080\nDEBUG: true\n"
        with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as f:
            f.write(content)
            path = f.name
        try:
            result = load_env_file(path)
            self.assertIsInstance(result["PORT"], str)
            self.assertEqual("8080", result["PORT"])
            self.assertIsInstance(result["DEBUG"], str)
        finally:
            os.unlink(path)

    def test_load_env_file_non_dict_raises(self) -> None:
        content = "- item1\n- item2\n"
        with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as f:
            f.write(content)
            path = f.name
        try:
            with self.assertRaises(TutorError):
                load_env_file(path)
        finally:
            os.unlink(path)
