import os
import tempfile
import unittest
from tests.test import TestContext
from tutor.commands.context import Context

CONTEXT = Context(os.path.join(tempfile.gettempdir(), "tutor"))

class TestContextTests(unittest.TestCase):
    def test_create_testcontext(self) -> None:
        with TestContext() as context:
            self.assertEqual(context.root, context._tempDir.name)
            self.assertTrue(context.config)
            self.assertTrue(context.runner)
        self.assertFalse(os.path.exists(context._tempDir.name))

