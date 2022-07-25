import typing as t
import unittest
from io import StringIO
from unittest.mock import patch

from click.exceptions import ClickException

from tutor import hooks
from tutor.commands import compose
from tutor.commands.local import LocalContext


class ComposeTests(unittest.TestCase):

    maxDiff = None  # Ensure we can see long diffs of YAML files.

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

    @patch("sys.stdout", new_callable=StringIO)
    def test_compose_local_tmp_generation(self, _mock_stdout: StringIO) -> None:
        """
        Ensure that docker-compose.tmp.yml is correctly generated.
        """
        param = compose.MountParam()
        mount_args = (
            # Auto-mounting of edx-platform to lms* and cms*
            param.convert_implicit_form("/path/to/edx-platform"),
            # Manual mounting of some other folder to mfe and lms
            param.convert_explicit_form(
                "mfe,lms:/path/to/something-else:/openedx/something-else"
            ),
        )
        # Mount volumes
        compose.mount_tmp_volumes(mount_args, LocalContext(""))

        compose_file: t.Dict[str, t.Any] = hooks.Filters.COMPOSE_LOCAL_TMP.apply({})
        actual_services: t.Dict[str, t.Any] = compose_file["services"]
        expected_services: t.Dict[str, t.Any] = {
            "cms": {"volumes": ["/path/to/edx-platform:/openedx/edx-platform"]},
            "cms-worker": {"volumes": ["/path/to/edx-platform:/openedx/edx-platform"]},
            "lms": {
                "volumes": [
                    "/path/to/edx-platform:/openedx/edx-platform",
                    "/path/to/something-else:/openedx/something-else",
                ]
            },
            "lms-worker": {"volumes": ["/path/to/edx-platform:/openedx/edx-platform"]},
            "mfe": {"volumes": ["/path/to/something-else:/openedx/something-else"]},
        }
        self.assertEqual(actual_services, expected_services)

        compose_jobs_file: t.Dict[
            str, t.Any
        ] = hooks.Filters.COMPOSE_LOCAL_JOBS_TMP.apply({})
        actual_jobs_services: t.Dict[str, t.Any] = compose_jobs_file["services"]
        expected_jobs_services: t.Dict[str, t.Any] = {
            "cms-job": {"volumes": ["/path/to/edx-platform:/openedx/edx-platform"]},
            "lms-job": {"volumes": ["/path/to/edx-platform:/openedx/edx-platform"]},
        }
        self.assertEqual(actual_jobs_services, expected_jobs_services)
