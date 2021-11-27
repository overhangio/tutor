import os
import unittest
from tests.test import TestContext
from tutor import config as tutor_config


class TestContextTests(unittest.TestCase):
    def test_create_testcontext(self) -> None:
        context = TestContext()
        config = context.load_config()
        runner = context.job_runner(config)
        self.assertTrue(os.path.exists(context.root))
        self.assertTrue(
            os.path.exists(os.path.join(context.root, tutor_config._CONFIG_FILE))
        )
        self.assertTrue(config)
        self.assertTrue(runner)
