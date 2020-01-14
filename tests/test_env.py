import os
import tempfile
import unittest
import unittest.mock

from tutor import config as tutor_config
from tutor import env
from tutor import exceptions


class EnvTests(unittest.TestCase):
    def setUp(self):
        env.Renderer.reset()

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

    def test_common_domain(self):
        self.assertEqual(
            "mydomain.com",
            env.render_str(
                {"d1": "d1.mydomain.com", "d2": "d2.mydomain.com"},
                "{{ d1|common_domain(d2) }}",
            ),
        )

    def test_render_str_missing_configuration(self):
        self.assertRaises(exceptions.TutorError, env.render_str, {}, "hello {{ name }}")

    def test_render_file(self):
        config = {}
        tutor_config.merge(config, tutor_config.load_defaults())
        config["MYSQL_ROOT_PASSWORD"] = "testpassword"
        rendered = env.render_file(config, "hooks", "mysql", "init")
        self.assertIn("testpassword", rendered)

    @unittest.mock.patch.object(tutor_config.fmt, "echo")
    def test_render_file_missing_configuration(self, _):
        self.assertRaises(
            exceptions.TutorError, env.render_file, {}, "local", "docker-compose.yml"
        )

    def test_render_full(self):
        defaults = tutor_config.load_defaults()
        with tempfile.TemporaryDirectory() as root:
            env.render_full(root, defaults)
            self.assertTrue(os.path.exists(os.path.join(root, "env", "version")))
            self.assertTrue(
                os.path.exists(os.path.join(root, "env", "local", "docker-compose.yml"))
            )

    def test_render_full_with_https(self):
        defaults = tutor_config.load_defaults()
        defaults["ACTIVATE_HTTPS"] = True
        with tempfile.TemporaryDirectory() as root:
            env.render_full(root, defaults)

    def test_patch(self):
        patches = {"plugin1": "abcd", "plugin2": "efgh"}
        with unittest.mock.patch.object(
            env.plugins, "iter_patches", return_value=patches.items()
        ) as mock_iter_patches:
            rendered = env.render_str({}, '{{ patch("location") }}')
            mock_iter_patches.assert_called_once_with({}, "location")
        self.assertEqual("abcd\nefgh", rendered)

    def test_patch_separator_suffix(self):
        patches = {"plugin1": "abcd", "plugin2": "efgh"}
        with unittest.mock.patch.object(
            env.plugins, "iter_patches", return_value=patches.items()
        ):
            rendered = env.render_str(
                {}, '{{ patch("location", separator=",\n", suffix=",") }}'
            )
        self.assertEqual("abcd,\nefgh,", rendered)

    def test_plugin_templates(self):
        with tempfile.TemporaryDirectory() as plugin_templates:
            # Create two templates
            os.makedirs(os.path.join(plugin_templates, "plugin1", "apps"))
            with open(
                os.path.join(plugin_templates, "plugin1", "unrendered.txt"), "w"
            ) as f:
                f.write("This file should not be rendered")
            with open(
                os.path.join(plugin_templates, "plugin1", "apps", "rendered.txt"), "w"
            ) as f:
                f.write("Hello my ID is {{ ID }}")

            # Create configuration
            config = {"ID": "abcd"}

            # Create a single plugin
            with unittest.mock.patch.object(
                env.plugins,
                "iter_template_roots",
                return_value=[("plugin1", plugin_templates)],
            ):
                with tempfile.TemporaryDirectory() as root:
                    # Render plugin templates
                    env.save_plugin_templates("plugin1", plugin_templates, root, config)

                    # Check that plugin template was rendered
                    dst_unrendered = os.path.join(
                        root, "env", "plugins", "plugin1", "unrendered.txt"
                    )
                    dst_rendered = os.path.join(
                        root, "env", "plugins", "plugin1", "apps", "rendered.txt"
                    )
                    self.assertFalse(os.path.exists(dst_unrendered))
                    self.assertTrue(os.path.exists(dst_rendered))
                    with open(dst_rendered) as f:
                        self.assertEqual("Hello my ID is abcd", f.read())

    def test_renderer_is_reset_on_config_change(self):
        with tempfile.TemporaryDirectory() as plugin_templates:
            # Create one template
            with open(os.path.join(plugin_templates, "myplugin.txt"), "w") as f:
                f.write("some content")

                # Load env once
                config = {"PLUGINS": []}
                env1 = env.Renderer.environment(config)

                with unittest.mock.patch.object(
                    env.plugins,
                    "iter_template_roots",
                    return_value=[("myplugin", plugin_templates)],
                ):
                    # Load env a second time
                    config["PLUGINS"].append("myplugin")
                    env2 = env.Renderer.environment(config)

                self.assertNotIn("myplugin.txt", env1.loader.list_templates())
                self.assertIn("myplugin.txt", env2.loader.list_templates())
