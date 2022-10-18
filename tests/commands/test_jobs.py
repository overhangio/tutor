import re
import unittest
from io import StringIO
from unittest.mock import patch

from tests.helpers import TestContext, temporary_root
from tutor import config as tutor_config
from tutor.commands import jobs


class JobsTests(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_initialise(self, mock_stdout: StringIO) -> None:
        with temporary_root() as root:
            context = TestContext(root)
            config = tutor_config.load_full(root)
            runner = context.job_runner(config)
            jobs.initialise(runner)
            output = mock_stdout.getvalue().strip()
            self.assertTrue(output.startswith("Initialising all services..."))
            self.assertTrue(output.endswith("All services initialised."))

    def test_create_user_command_without_staff(self) -> None:
        command = jobs.create_user_template("superuser", False, "username", "email", "p4ssw0rd")
        self.assertNotIn("--staff", command)
        self.assertIn("set_password", command)

    def test_create_user_command_with_staff(self) -> None:
        command = jobs.create_user_template("superuser", True, "username", "email", "p4ssw0rd")
        self.assertIn("--staff", command)

    @patch("sys.stdout", new_callable=StringIO)
    def test_import_demo_course(self, mock_stdout: StringIO) -> None:
        with temporary_root() as root:
            context = TestContext(root)
            config = tutor_config.load_full(root)
            runner = context.job_runner(config)
            runner.run_job_from_str("cms", jobs.import_demo_course_template())

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
            command = jobs.set_theme_template("sample_theme", ["domain1", "domain2"])
            runner.run_job_from_str("lms", command)

            output = mock_stdout.getvalue()
            service = re.search(r"Service: (\w*)", output)
            commands = re.search(r"(-----)([\S\s]+)(-----)", output)
            assert service is not None
            assert commands is not None
            self.assertEqual(service.group(1), "lms")
            self.assertTrue(
                commands.group(2)
                .strip()
                .startswith('echo "Loading settings $DJANGO_SETTINGS_MODULE"')
            )
