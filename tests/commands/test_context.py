import os
import unittest

from tests.helpers import TestContext, TestJobRunner, temporary_root
from tutor import config as tutor_config


class TestContextTests(unittest.TestCase):
    def test_create_testcontext(self) -> None:
        with temporary_root() as root:
            context = TestContext(root)
            config = tutor_config.load_full(root)
            runner = context.job_runner(config)
            self.assertTrue(os.path.exists(context.root))
            self.assertFalse(
                os.path.exists(os.path.join(context.root, tutor_config.CONFIG_FILENAME))
            )
            self.assertTrue(isinstance(runner, TestJobRunner))
