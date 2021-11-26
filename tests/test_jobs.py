import unittest
import tutor.jobs as jobs
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

    def test_import_demo_course(self) -> None:
        with TestContext() as context:
            jobs.import_demo_course(context.runner)
