import unittest

from tutorminio import plugin


class PluginTests(unittest.TestCase):
    def test_patches(self):
        patches = dict(plugin.patches())
        self.assertIn("local-docker-compose-services", patches)
        self.assertTrue(
            patches["local-docker-compose-services"].startswith("# MinIO\n")
        )
