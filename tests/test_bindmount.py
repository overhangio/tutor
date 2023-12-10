from __future__ import annotations

import unittest

from tutor import bindmount


class BindmountTests(unittest.TestCase):
    def test_parse_explicit(self) -> None:
        self.assertEqual(
            [("lms", "/path/to/edx-platform", "/openedx/edx-platform")],
            bindmount.parse_explicit_mount(
                "lms:/path/to/edx-platform:/openedx/edx-platform"
            ),
        )
        self.assertEqual(
            [
                ("lms", "/path/to/edx-platform", "/openedx/edx-platform"),
                ("cms", "/path/to/edx-platform", "/openedx/edx-platform"),
            ],
            bindmount.parse_explicit_mount(
                "lms,cms:/path/to/edx-platform:/openedx/edx-platform"
            ),
        )
        self.assertEqual(
            [
                ("lms", "/path/to/edx-platform", "/openedx/edx-platform"),
                ("cms", "/path/to/edx-platform", "/openedx/edx-platform"),
            ],
            bindmount.parse_explicit_mount(
                "lms, cms:/path/to/edx-platform:/openedx/edx-platform"
            ),
        )
        self.assertEqual(
            [
                ("lms", "/path/to/edx-platform", "/openedx/edx-platform"),
                ("lms-worker", "/path/to/edx-platform", "/openedx/edx-platform"),
            ],
            bindmount.parse_explicit_mount(
                "lms,lms-worker:/path/to/edx-platform:/openedx/edx-platform"
            ),
        )
        self.assertEqual(
            [("lms", "/path/to/edx-platform", "/openedx/edx-platform")],
            bindmount.parse_explicit_mount(
                "lms,:/path/to/edx-platform:/openedx/edx-platform"
            ),
        )

    def test_parse_implicit(self) -> None:
        # Import module to make sure filter is created
        # pylint: disable=import-outside-toplevel,unused-import
        import tutor.commands.compose

        self.assertEqual(
            [("openedx", "/path/to/edx-platform", "/openedx/edx-platform")],
            bindmount.parse_implicit_mount("/path/to/edx-platform"),
        )
