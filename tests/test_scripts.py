import unittest
import unittest.mock

from tutor import config as tutor_config
from tutor import scripts


class ScriptsTests(unittest.TestCase):
    def test_is_activated(self):
        config = {"ACTIVATE_SERVICE1": True, "ACTIVATE_SERVICE2": False}
        runner = scripts.BaseRunner("/tmp", config)

        self.assertTrue(runner.is_activated("service1"))
        self.assertFalse(runner.is_activated("service2"))
