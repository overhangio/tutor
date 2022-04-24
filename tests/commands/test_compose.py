import unittest

from click.exceptions import ClickException

from tutor.commands import compose


class ComposeTests(unittest.TestCase):
    def test_mount_option_parsing(self) -> None:
        param = compose.MountParam()

        self.assertEqual(
            [("lms", "/path/to/edx-platform", "/openedx/edx-platform")],
            param("lms:/path/to/edx-platform:/openedx/edx-platform"),
        )
        self.assertEqual(
            [
                ("lms", "/path/to/edx-platform", "/openedx/edx-platform"),
                ("cms", "/path/to/edx-platform", "/openedx/edx-platform"),
            ],
            param("lms,cms:/path/to/edx-platform:/openedx/edx-platform"),
        )
        self.assertEqual(
            [
                ("lms", "/path/to/edx-platform", "/openedx/edx-platform"),
                ("cms", "/path/to/edx-platform", "/openedx/edx-platform"),
            ],
            param("lms, cms:/path/to/edx-platform:/openedx/edx-platform"),
        )
        self.assertEqual(
            [
                ("lms", "/path/to/edx-platform", "/openedx/edx-platform"),
                ("lms-worker", "/path/to/edx-platform", "/openedx/edx-platform"),
            ],
            param("lms,lms-worker:/path/to/edx-platform:/openedx/edx-platform"),
        )
        with self.assertRaises(ClickException):
            param("lms,:/path/to/edx-platform:/openedx/edx-platform")
