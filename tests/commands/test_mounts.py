import os
import unittest

from tests.helpers import temporary_root
from tutor import config as tutor_config

from .base import TestCommandMixin


class MountsTests(unittest.TestCase, TestCommandMixin):
    def test_mounts_remove_all(self) -> None:
        with temporary_root() as root:
            path = os.path.join(root, "src")
            os.mkdir(path)
            self.invoke_in_root(root, ["mounts", "add", path, "lms:/a:/b"])
            self.assertEqual([path, "lms:/a:/b"], tutor_config.load(root)["MOUNTS"])
            result = self.invoke_in_root(root, ["mounts", "remove", "--all"])
            self.assertEqual(0, result.exit_code)
            self.assertEqual([], tutor_config.load(root)["MOUNTS"])

    def test_mounts_remove_all_with_args(self) -> None:
        with temporary_root() as root:
            result = self.invoke_in_root(root, ["mounts", "remove", "--all", "/a"])
            self.assertEqual(1, result.exit_code)
