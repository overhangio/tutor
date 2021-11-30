import re
import unittest
import unittest.mock
import tutor.jobs as jobs
from io import StringIO
from tests.test import TestContext


class JobsTests(unittest.TestCase):
    @unittest.mock.patch("sys.stdout", new_callable=StringIO)
    def test_initialise(self, mock_stdout: StringIO) -> None:
        context = TestContext()
        config = context.load_config()
        runner = context.job_runner(config)
        jobs.initialise(runner)

        output = mock_stdout.getvalue()
        service = re.search(r"Service: (\w*)", output)
        commands = re.search(r"(-----)([\S\s]+)(-----)", output)
        assert service is not None
        assert commands is not None
        self.assertTrue(output.strip().startswith("Initialising all services..."))
        self.assertTrue(output.strip().endswith("All services initialised."))
        self.assertEqual(service.group(1), "mysql")
        self.assertTrue(commands.group(2))

    def test_create_user_command_without_staff(self) -> None:
        result = jobs.create_user_command("superuser", False, "username", "email")
        self.assertTrue(result)

    def test_create_user_command_with_staff(self) -> None:
        result = jobs.create_user_command("superuser", True, "username", "email")
        self.assertTrue(result)

    def test_create_user_command_with_staff_with_password(self) -> None:
        result = jobs.create_user_command(
            "superuser", True, "username", "email", "password"
        )
        self.assertTrue(result)

    @unittest.mock.patch("sys.stdout", new_callable=StringIO)
    def test_import_demo_course(self, mock_stdout: StringIO) -> None:
        context = TestContext()
        config = context.load_config()
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

    @unittest.mock.patch("sys.stdout", new_callable=StringIO)
    def test_set_theme(self, mock_stdout: StringIO) -> None:
        context = TestContext()
        config = context.load_config()
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
            .startswith("export DJANGO_SETTINGS_MODULE=$SERVICE_VARIANT.envs.$SETTINGS")
        )

    def test_get_all_openedx_domains(self) -> None:
        context = TestContext()
        config = context.load_config()
        domains = jobs.get_all_openedx_domains(config)
        self.assertTrue(domains)
        self.assertEqual(6, len(domains))
