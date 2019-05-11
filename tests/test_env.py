import unittest

from tutor import env
from tutor import exceptions


class EnvTests(unittest.TestCase):
    def test_walk_templates(self):
        templates = list(env.walk_templates("local"))
        self.assertIn("local/docker-compose.yml", templates)

    def test_pathjoin(self):
        self.assertEqual(
            "/tmp/env/target/dummy", env.pathjoin("/tmp", "target", "dummy")
        )
        self.assertEqual("/tmp/env/dummy", env.pathjoin("/tmp", "dummy"))

    def test_render_str(self):
        self.assertEqual(
            "hello world", env.render_str({"name": "world"}, "hello {{ name }}")
        )

    def test_render_str_missing_configuration(self):
        self.assertRaises(exceptions.TutorError, env.render_str, {}, "hello {{ name }}")
