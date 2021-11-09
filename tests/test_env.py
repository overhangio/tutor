import os
import tempfile
import unittest
from unittest.mock import patch, Mock

from tutor import config as tutor_config
from tutor import env
from tutor import fmt
from tutor import exceptions
from tutor.types import Config


class EnvTests(unittest.TestCase):
    def test_walk_templates(self) -> None:
        renderer = env.Renderer({}, [env.TEMPLATES_ROOT])
        templates = list(renderer.walk_templates("local"))
        self.assertIn("local/docker-compose.yml", templates)

    def test_walk_templates_partials_are_ignored(self) -> None:
        template_name = "apps/openedx/settings/partials/common_all.py"
        renderer = env.Renderer({}, [env.TEMPLATES_ROOT], ignore_folders=["partials"])
        templates = list(renderer.walk_templates("apps"))
        self.assertIn(template_name, renderer.environment.loader.list_templates())
        self.assertNotIn(template_name, templates)

    def test_is_binary_file(self) -> None:
        self.assertTrue(env.is_binary_file("/home/somefile.ico"))

    def test_find_os_path(self) -> None:
        renderer = env.Renderer({}, [env.TEMPLATES_ROOT])
        path = renderer.find_os_path("local/docker-compose.yml")
        self.assertTrue(os.path.exists(path))

    def test_pathjoin(self) -> None:
        self.assertEqual(
            "/tmp/env/target/dummy", env.pathjoin("/tmp", "target", "dummy")
        )
        self.assertEqual("/tmp/env/dummy", env.pathjoin("/tmp", "dummy"))

    def test_render_str(self) -> None:
        self.assertEqual(
            "hello world", env.render_str({"name": "world"}, "hello {{ name }}")
        )

    def test_render_unknown(self) -> None:
        config: Config = {
            "var1": "a",
        }
        self.assertEqual("ab", env.render_unknown(config, "{{ var1 }}b"))
        self.assertEqual({"x": "ac"}, env.render_unknown(config, {"x": "{{ var1 }}c"}))

    def test_common_domain(self) -> None:
        self.assertEqual(
            "mydomain.com",
            env.render_str(
                {"d1": "d1.mydomain.com", "d2": "d2.mydomain.com"},
                "{{ d1|common_domain(d2) }}",
            ),
        )

    def test_render_str_missing_configuration(self) -> None:
        self.assertRaises(exceptions.TutorError, env.render_str, {}, "hello {{ name }}")

    def test_render_file(self) -> None:
        config: Config = {}
        tutor_config.merge(config, tutor_config.load_defaults())
        config["MYSQL_ROOT_PASSWORD"] = "testpassword"
        rendered = env.render_file(config, "hooks", "mysql", "init")
        self.assertIn("testpassword", rendered)

    @patch.object(tutor_config.fmt, "echo")
    def test_render_file_missing_configuration(self, _: Mock) -> None:
        self.assertRaises(
            exceptions.TutorError, env.render_file, {}, "local", "docker-compose.yml"
        )

    def test_save_full(self) -> None:
        defaults = tutor_config.load_defaults()
        with tempfile.TemporaryDirectory() as root:
            config = tutor_config.load_current(root, defaults)
            tutor_config.merge(config, defaults)
            with patch.object(fmt, "STDOUT"):
                env.save(root, config)
            self.assertTrue(
                os.path.exists(os.path.join(root, "env", "local", "docker-compose.yml"))
            )

    def test_save_full_with_https(self) -> None:
        defaults = tutor_config.load_defaults()
        with tempfile.TemporaryDirectory() as root:
            config = tutor_config.load_current(root, defaults)
            tutor_config.merge(config, defaults)
            config["ENABLE_HTTPS"] = True
            with patch.object(fmt, "STDOUT"):
                env.save(root, config)
                with open(os.path.join(root, "env", "apps", "caddy", "Caddyfile")) as f:
                    self.assertIn("www.myopenedx.com{$default_site_port}", f.read())

    def test_patch(self) -> None:
        patches = {"plugin1": "abcd", "plugin2": "efgh"}
        with patch.object(
            env.plugins, "iter_patches", return_value=patches.items()
        ) as mock_iter_patches:
            rendered = env.render_str({}, '{{ patch("location") }}')
            mock_iter_patches.assert_called_once_with({}, "location")
        self.assertEqual("abcd\nefgh", rendered)

    def test_patch_separator_suffix(self) -> None:
        patches = {"plugin1": "abcd", "plugin2": "efgh"}
        with patch.object(env.plugins, "iter_patches", return_value=patches.items()):
            rendered = env.render_str(
                {}, '{{ patch("location", separator=",\n", suffix=",") }}'
            )
        self.assertEqual("abcd,\nefgh,", rendered)

    def test_plugin_templates(self) -> None:
        with tempfile.TemporaryDirectory() as plugin_templates:
            # Create plugin
            plugin1 = env.plugins.DictPlugin(
                {"name": "plugin1", "version": "0", "templates": plugin_templates}
            )

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
            config: Config = {"ID": "abcd"}

            # Render templates
            with patch.object(
                env.plugins,
                "iter_enabled",
                return_value=[plugin1],
            ):
                with tempfile.TemporaryDirectory() as root:
                    # Render plugin templates
                    env.save_plugin_templates(plugin1, root, config)

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

    def test_renderer_is_reset_on_config_change(self) -> None:
        with tempfile.TemporaryDirectory() as plugin_templates:
            plugin1 = env.plugins.DictPlugin(
                {"name": "plugin1", "version": "0", "templates": plugin_templates}
            )
            # Create one template
            os.makedirs(os.path.join(plugin_templates, plugin1.name))
            with open(
                os.path.join(plugin_templates, plugin1.name, "myplugin.txt"), "w"
            ) as f:
                f.write("some content")

            # Load env once
            config: Config = {"PLUGINS": []}
            env1 = env.Renderer.instance(config).environment

            with patch.object(
                env.plugins,
                "iter_enabled",
                return_value=[plugin1],
            ):
                # Load env a second time
                config["PLUGINS"] = ["myplugin"]
                env2 = env.Renderer.instance(config).environment

            self.assertNotIn("plugin1/myplugin.txt", env1.loader.list_templates())
            self.assertIn("plugin1/myplugin.txt", env2.loader.list_templates())

    def test_iter_values_named(self) -> None:
        config: Config = {
            "something0_test_app": 0,
            "something1_test_not_app": 1,
            "notsomething_test_app": 2,
            "something3_test_app": 3,
        }
        renderer = env.Renderer.instance(config)
        self.assertEqual([2, 3], list(renderer.iter_values_named(suffix="test_app")))
        self.assertEqual([1, 3], list(renderer.iter_values_named(prefix="something")))
        self.assertEqual(
            [0, 3],
            list(
                renderer.iter_values_named(
                    prefix="something", suffix="test_app", allow_empty=True
                )
            ),
        )
