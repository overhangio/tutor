import os
import unittest

from tests.helpers import TestJobContext, TestJobRunner, temporary_root
from tutor import config as tutor_config


class TestJobContextTests(unittest.TestCase):
    def test_create_testjobcontext(self) -> None:
        with temporary_root() as root:
            context = TestJobContext(root, {})
            runner = context.job_runner()
            self.assertTrue(os.path.exists(context.root))
            self.assertFalse(
                os.path.exists(os.path.join(context.root, tutor_config.CONFIG_FILENAME))
            )
            self.assertTrue(isinstance(runner, TestJobRunner))
