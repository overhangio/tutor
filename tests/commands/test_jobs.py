import os
import tempfile
import unittest
from unittest.mock import patch

from tests.helpers import PluginsTestCase, temporary_root
from tutor.commands import jobs
from tutor.commands.jobs_utils import load_env_file, parse_test_env_var
from tutor.exceptions import TutorError

from .base import TestCommandMixin


class JobsTests(PluginsTestCase, TestCommandMixin):
    def test_initialise(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            result = self.invoke_in_root(root, ["local", "do", "init"])
            self.assertIsNone(result.exception)
            self.assertEqual(0, result.exit_code)
            self.assertIn("All services initialised.", result.output)

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
