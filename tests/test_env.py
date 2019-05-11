import tempfile
import unittest

from tutor.commands import config as tutor_config
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

    def test_render_file(self):
        config = {}
        tutor_config.merge(config, tutor_config.load_defaults())
        config["MYSQL_ROOT_PASSWORD"] = "testpassword"
        rendered = env.render_file(config, "scripts", "create_databases.sh")
        self.assertIn("testpassword", rendered)

    def test_render_file_missing_configuration(self):
        self.assertRaises(
            exceptions.TutorError, env.render_file, {}, "local", "docker-compose.yml"
        )
