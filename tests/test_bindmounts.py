import unittest

from tutor import bindmounts
from tutor.exceptions import TutorError


class BindMountsTests(unittest.TestCase):
    def test_get_name(self):
        self.assertEqual("venv", bindmounts.get_name("/openedx/venv"))
        self.assertEqual("venv", bindmounts.get_name("/openedx/venv/"))

    def test_get_name_root_folder(self):
        with self.assertRaises(TutorError):
            bindmounts.get_name("/")
        with self.assertRaises(TutorError):
            bindmounts.get_name("")

    def test_parse_volumes(self):
        volume_args, non_volume_args = bindmounts.parse_volumes(
            [
                "run",
                "--volume=/openedx/venv",
                "-v",
                "/tmp/openedx:/openedx",
                "lms",
                "echo",
                "boom",
            ]
        )
        self.assertEqual(("/openedx/venv", "/tmp/openedx:/openedx"), volume_args)
        self.assertEqual(("run", "lms", "echo", "boom"), non_volume_args)
