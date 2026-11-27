import ast
import os
import shlex
import tempfile
import unittest
from unittest.mock import patch

from tests.helpers import PluginsTestCase, temporary_root
from tutor import env
from tutor.commands import jobs, jobs_utils
from tutor.commands.jobs_utils import load_env_file, parse_test_env_var
from tutor.exceptions import TutorError

from .base import TestCommandMixin

# Values that must reach the job commands unchanged: they must not be interpreted as
# template markup on the host, nor as shell, Python or SQL code in the container.
UNTRUSTED_VALUES = [
    "{{ 7*7 }}",
    "{{ cycler.__init__.__globals__.os.popen('id').read() }}",
    "{% raw %}{% endraw %}{# comment #}",
    "a'b\"c\\d",
    "$(id) `id` ${HOME}",
    "x; id; #",
    "line\nbreak",
    "--upload-pack=id",
]


def python_strings(code: str) -> list[str]:
    """
    Return the string literals of a Python script, in order of appearance.
    """
    nodes = sorted(
        (node for node in ast.walk(ast.parse(code)) if isinstance(node, ast.Constant)),
        key=lambda node: (node.lineno, node.col_offset),
    )
    return [node.value for node in nodes if isinstance(node.value, str)]


class JobsTests(PluginsTestCase, TestCommandMixin):
    def run_job(self, root: str, args: list[str]) -> str:
        """
        Run `tutor local do ARGS` and return the script that is run in the container.
        """
        with patch("tutor.utils.docker_compose") as mock_docker_compose:
            result = self.invoke_in_root(root, ["local", "do", *args])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)
        script: str = mock_docker_compose.call_args[0][-1]
        return script

    def test_initialise(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            result = self.invoke_in_root(root, ["local", "do", "init"])
            self.assertIsNone(result.exception)
            self.assertEqual(0, result.exit_code)
            self.assertIn("All services initialised.", result.stdout)

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
            "git clone --branch release/verawood.2 --depth 1 -- https://github.com/openedx/openedx-demo-course /tmp/course",
            dc_args[-1],
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
            "git clone --branch release/verawood.2 --depth 1 -- https://github.com/openedx/openedx-demo-course /tmp/library",
            dc_args[-1],
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
            python_command = shlex.split(dc_args[-1])[-1]
            self.assertIn("assign_theme('beautiful', 'domain1')", python_command)
            self.assertIn("assign_theme('beautiful', 'domain2')", python_command)
            self.assertNotIn("local.openedx.io", python_command)

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

    def test_createuser_untrusted_values(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            for value in UNTRUSTED_VALUES:
                with self.subTest(value=value):
                    script = self.run_job(
                        root, ["createuser", "--staff", "-p", value, "--", value, value]
                    )
                    words = shlex.split(script)
                    self.assertEqual(11, len(words))
                    self.assertEqual(
                        ["./manage.py", "lms", "manage_user", "--staff", value, value],
                        words[:6],
                    )
                    self.assertEqual(["./manage.py", "lms", "shell", "-c"], words[6:10])
                    # Username and password
                    self.assertEqual([value, value], python_strings(words[10]))

    def test_set_theme_untrusted_values(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            for value in UNTRUSTED_VALUES:
                with self.subTest(value=value):
                    script = self.run_job(root, ["settheme", "-d", value, "--", value])
                    words = shlex.split(script)
                    self.assertEqual(5, len(words))
                    self.assertEqual(["./manage.py", "lms", "shell", "-c"], words[:4])
                    # The only top-level expression is the assign_theme(...) call
                    calls = [
                        node.value
                        for node in ast.parse(words[4]).body
                        if isinstance(node, ast.Expr)
                    ]
                    self.assertEqual(1, len(calls))
                    assert isinstance(calls[0], ast.Call)
                    self.assertEqual(
                        [value, value], [ast.literal_eval(a) for a in calls[0].args]
                    )

    def test_set_theme_default_domains(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            script = self.run_job(root, ["settheme", "mytheme"])
        python_command = shlex.split(script)[-1]
        for domain in [
            "local.openedx.io",
            "local.openedx.io:8000",
            "studio.local.openedx.io",
            "studio.local.openedx.io:8001",
        ]:
            self.assertIn(f"assign_theme('mytheme', '{domain}')", python_command)

    def test_print_edx_platform_setting(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            script = self.run_job(root, ["print-edx-platform-setting", "SECRET_KEY"])
            self.assertEqual(
                [
                    "./manage.py",
                    "lms",
                    "shell",
                    "-c",
                    "from django.conf import settings; print(settings.SECRET_KEY)",
                ],
                shlex.split(script),
            )
            # The setting may be a Python expression, evaluated in the container, but
            # it is neither rendered by Jinja2 nor interpreted by the shell.
            for value in UNTRUSTED_VALUES + ["FEATURES['ENABLE_X']"]:
                with self.subTest(value=value):
                    script = self.run_job(
                        root, ["print-edx-platform-setting", "--", value]
                    )
                    self.assertEqual(
                        [
                            "./manage.py",
                            "lms",
                            "shell",
                            "-c",
                            f"from django.conf import settings; print(settings.{value})",
                        ],
                        shlex.split(script),
                    )

    def test_sqlshell_untrusted_values(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            for value in UNTRUSTED_VALUES:
                with self.subTest(value=value):
                    script = self.run_job(root, ["sqlshell", "-e", value])
                    self.assertEqual(["-e", value], shlex.split(script)[-2:])

    def test_import_demo_course_untrusted_values(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            for value in UNTRUSTED_VALUES:
                with self.subTest(value=value):
                    script = self.run_job(
                        root,
                        [
                            "importdemocourse",
                            f"--repo={value}",
                            f"--version={value}",
                            f"--repo-dir={value}",
                        ],
                    )
                    words = shlex.split(script, comments=True)
                    clone = words.index("clone")
                    self.assertEqual(
                        ["--branch", value, "--depth", "1", "--", value, "/tmp/course"],
                        words[clone + 1 : clone + 8],
                    )
                    self.assertEqual(f"repo_dir={value}", words[clone + 8])

    def test_import_demo_libraries_untrusted_values(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            for value in UNTRUSTED_VALUES:
                with self.subTest(value=value):
                    script = self.run_job(
                        root,
                        [
                            "importdemolibraries",
                            f"--repo={value}",
                            f"--version={value}",
                            "--",
                            value,
                        ],
                    )
                    words = shlex.split(script, comments=True)
                    clone = words.index("clone")
                    self.assertEqual(
                        [
                            "--branch",
                            value,
                            "--depth",
                            "1",
                            "--",
                            value,
                            "/tmp/library",
                        ],
                        words[clone + 1 : clone + 8],
                    )
                    self.assertEqual(["/tmp/library.tar.gz", value, "done"], words[-3:])

    def test_convert_mysql_utf8mb4_charset_untrusted_values(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            script = self.run_job(
                root,
                [
                    "convert-mysql-utf8mb4-charset",
                    "--include={{ 7*7 }},a'b",
                    "--exclude=c\\d",
                    "--database=my`{{ db }}'",
                ],
            )
        words = shlex.split(script)
        self.assertEqual(["--database=my`{{ db }}'", "-e"], words[-3:-1])
        query = words[-1]
        self.assertIn("AND table_name  regexp '^{{ 7*7 }}|^a''b'", query)
        self.assertIn("AND table_name NOT regexp '^c\\\\d'", query)
        self.assertIn("TABLE_SCHEMA = 'my`{{ db }}'''", query)
        self.assertIn("use `my``{{ db }}'`;", query)
        self.assertIn("ALTER DATABASE `my``{{ db }}'` CHARACTER SET", query)

    def test_update_mysql_authentication_plugin_untrusted_values(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            for value in UNTRUSTED_VALUES:
                with self.subTest(value=value):
                    script = self.run_job(
                        root,
                        [
                            "update-mysql-authentication-plugin",
                            f"--password={value}",
                            "--",
                            value,
                        ],
                    )
                    words = shlex.split(script)
                    self.assertEqual("-e", words[-2])
                    sql_value = value.replace("\\", "\\\\").replace("'", "''")
                    self.assertEqual(
                        f"ALTER USER IF EXISTS '{sql_value}'@'%' IDENTIFIED with "
                        f"caching_sha2_password BY '{sql_value}';",
                        words[-1],
                    )

    def test_tests_templates_untrusted_values(self) -> None:
        for value in UNTRUSTED_VALUES:
            with self.subTest(value=value):
                setup = env.render_str(
                    {},
                    jobs_utils.tests_setup_template(value, value, value, value, value),
                )
                words = shlex.split(setup, comments=True)
                self.assertEqual(17, len(words))
                self.assertEqual(
                    ["./manage.py", "lms", "manage_user", "--staff", "--superuser"],
                    words[:5],
                )
                self.assertEqual([value, value], words[5:7])
                self.assertEqual(["./manage.py", "lms", "shell", "-c"], words[7:11])
                # Username, password, then username again in the printed message
                set_password = python_strings(words[11])
                self.assertEqual([value, value], set_password[:2])
                self.assertEqual(value, set_password[3])
                self.assertEqual(["./manage.py", "lms", "shell", "-c"], words[12:16])
                # Username, client ID and client secret
                self.assertEqual(3, python_strings(words[16]).count(value))

                teardown_lms = env.render_str(
                    {}, jobs_utils.tests_teardown_lms_template(value)
                )
                words = shlex.split(teardown_lms)
                self.assertEqual(["./manage.py", "lms", "shell", "-c"], words[:4])
                self.assertEqual(value, python_strings(words[4])[0])

                teardown_cms = env.render_str(
                    {}, jobs_utils.tests_teardown_cms_template(value)
                )
                self.assertEqual(
                    ["yes", "|", "./manage.py", "cms", "delete_course", value],
                    shlex.split(teardown_cms)[:6],
                )


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
