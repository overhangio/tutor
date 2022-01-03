import re
import unittest
from io import StringIO
from unittest.mock import patch

from tests.helpers import TestContext, temporary_root
from tutor import config as tutor_config
from tutor import jobs


class JobsTests(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_initialise(self, mock_stdout: StringIO) -> None:
        with temporary_root() as root:
            context = TestContext(root)
            config = tutor_config.load_full(root)
            runner = context.job_runner(config)
            jobs.initialise(runner)

            output = mock_stdout.getvalue().strip()
            service = re.search(r"Service: (\w*)", output)
            commands = re.search(r"(-----)([\S\s]+)(-----)", output)
            assert service is not None
            assert commands is not None
            self.assertTrue(output.startswith("Initialising all services..."))
            self.assertTrue(output.endswith("All services initialised."))
            self.assertEqual(service.group(1), "mysql")
            self.assertTrue(commands.group(2))

    def test_create_user_command_without_staff(self) -> None:
        command = jobs.create_user_command("superuser", False, "username", "email")
        self.assertNotIn("--staff", command)

    def test_create_user_command_with_staff(self) -> None:
        command = jobs.create_user_command("superuser", True, "username", "email")
        self.assertIn("--staff", command)

    def test_create_user_command_with_staff_with_password(self) -> None:
        command = jobs.create_user_command(
            "superuser", True, "username", "email", "command"
        )
        self.assertIn("set_password", command)

    @patch("sys.stdout", new_callable=StringIO)
    def test_import_demo_course(self, mock_stdout: StringIO) -> None:
        with temporary_root() as root:
            context = TestContext(root)
            config = tutor_config.load_full(root)
            runner = context.job_runner(config)
            jobs.import_demo_course(runner)

            output = mock_stdout.getvalue()
            service = re.search(r"Service: (\w*)", output)
            commands = re.search(r"(-----)([\S\s]+)(-----)", output)
            assert service is not None
            assert commands is not None
            self.assertEqual(service.group(1), "cms")
            self.assertTrue(
                commands.group(2)
                .strip()
                .startswith('echo "Loading settings $DJANGO_SETTINGS_MODULE"')
            )

    @patch("sys.stdout", new_callable=StringIO)
    def test_set_theme(self, mock_stdout: StringIO) -> None:
        with temporary_root() as root:
            context = TestContext(root)
            config = tutor_config.load_full(root)
            runner = context.job_runner(config)
            jobs.set_theme("sample_theme", ["domain1", "domain2"], runner)

            output = mock_stdout.getvalue()
            service = re.search(r"Service: (\w*)", output)
            commands = re.search(r"(-----)([\S\s]+)(-----)", output)
            assert service is not None
            assert commands is not None
            self.assertEqual(service.group(1), "lms")
            self.assertTrue(
                commands.group(2)
                .strip()
                .startswith(
                    "export DJANGO_SETTINGS_MODULE=$SERVICE_VARIANT.envs.$SETTINGS"
                )
            )

    def test_get_all_openedx_domains(self) -> None:
        with temporary_root() as root:
            config = tutor_config.load_full(root)
            domains = jobs.get_all_openedx_domains(config)
            self.assertTrue(domains)
            self.assertEqual(6, len(domains))
