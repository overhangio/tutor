import re
import unittest
import unittest.mock
import tutor.jobs as jobs
from io import StringIO
from tests.test import TestContext


class JobsTests(unittest.TestCase):
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
