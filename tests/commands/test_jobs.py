from unittest.mock import patch

from tests.helpers import PluginsTestCase, temporary_root
from tutor.commands import jobs

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
