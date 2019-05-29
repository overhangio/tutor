import unittest

from tutorminio import plugin


class PluginTests(unittest.TestCase):
    def test_patches(self):
        patches = dict(plugin.patches())
        self.assertIn("docker-compose-services", patches)
        self.assertTrue(patches["docker-compose-services"].startswith("minio:\n"))
