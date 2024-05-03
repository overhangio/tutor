import os
import tempfile
import unittest
from io import StringIO
from unittest.mock import Mock, patch

from tests.helpers import PluginsTestCase, temporary_root
from tutor import config as tutor_config
from tutor import env, exceptions, fmt, plugins
from tutor.__about__ import __version__
from tutor.plugins.v0 import DictPlugin
from tutor.types import Config


class EnvTests(PluginsTestCase):
    def test_walk_templates(self) -> None:
        renderer = env.Renderer()
        templates = list(renderer.walk_templates("local"))
        self.assertIn("local/docker-compose.yml", templates)

    def test_walk_templates_partials_are_ignored(self) -> None:
        template_name = "apps/openedx/settings/partials/common_all.py"
        renderer = env.Renderer()
        templates = list(renderer.walk_templates("apps"))
        self.assertIn(template_name, renderer.environment.loader.list_templates())
        self.assertNotIn(template_name, templates)

    def test_files_are_rendered(self) -> None:
        self.assertTrue(env.is_rendered("some/file"))
        self.assertFalse(env.is_rendered(".git"))
        self.assertFalse(env.is_rendered(".git/subdir"))
        self.assertFalse(env.is_rendered("directory/.git"))
        self.assertFalse(env.is_rendered("directory/.git/somefile"))
        self.assertFalse(env.is_rendered("directory/somefile.pyc"))
        self.assertTrue(env.is_rendered("directory/somedir.pyc/somefile"))
        self.assertFalse(env.is_rendered("directory/__pycache__"))
        self.assertFalse(env.is_rendered("directory/__pycache__/somefile"))
        self.assertFalse(env.is_rendered("directory/partials/extra.scss"))
        self.assertFalse(env.is_rendered("directory/partials"))
        self.assertFalse(env.is_rendered("partials/somefile"))

    def test_is_binary_file(self) -> None:
        self.assertTrue(env.is_binary_file("/home/somefile.ico"))

    def test_find_os_path(self) -> None:
        environment = env.JinjaEnvironment()
        path = environment.find_os_path("local/docker-compose.yml")
        self.assertTrue(os.path.exists(path))

    def test_pathjoin(self) -> None:
        with temporary_root() as root:
            self.assertEqual(
                os.path.join(env.base_dir(root), "dummy"), env.pathjoin(root, "dummy")
            )

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
        self.assertEqual(["x", "ac"], env.render_unknown(config, ["x", "{{ var1 }}c"]))

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
        tutor_config.update_with_base(config)
        tutor_config.update_with_defaults(config)
        tutor_config.render_full(config)

        config["MYSQL_ROOT_PASSWORD"] = "testpassword"
        rendered = env.render_file(config, "jobs", "init", "mysql.sh")
        self.assertIn("testpassword", rendered)

    @patch.object(fmt, "echo")
    def test_render_file_missing_configuration(self, _: Mock) -> None:
        self.assertRaises(
            exceptions.TutorError, env.render_file, {}, "local", "docker-compose.yml"
        )

    def test_save_full(self) -> None:
        with temporary_root() as root:
            config = tutor_config.load_full(root)
            with patch.object(fmt, "STDOUT"):
                env.save(root, config)
            self.assertTrue(
                os.path.exists(
                    os.path.join(env.base_dir(root), "local", "docker-compose.yml")
                )
            )

    def test_save_full_with_https(self) -> None:
        with temporary_root() as root:
            config = tutor_config.load_full(root)
            config["ENABLE_HTTPS"] = True
            with patch.object(fmt, "STDOUT"):
                env.save(root, config)
                with open(
                    os.path.join(env.base_dir(root), "apps", "caddy", "Caddyfile"),
                    encoding="utf-8",
                ) as f:
                    self.assertIn("www.myopenedx.com{$default_site_port}", f.read())

    def test_patch(self) -> None:
        patches = {"plugin1": "abcd", "plugin2": "efgh"}
        with patch.object(
            plugins, "iter_patches", return_value=patches.values()
        ) as mock_iter_patches:
            rendered = env.render_str({}, '{{ patch("location") }}')
            mock_iter_patches.assert_called_once_with("location")
        self.assertEqual("abcd\nefgh", rendered)

    def test_patch_separator_suffix(self) -> None:
        patches = {"plugin1": "abcd", "plugin2": "efgh"}
        with patch.object(plugins, "iter_patches", return_value=patches.values()):
            rendered = env.render_str(
                {}, '{{ patch("location", separator=",\n", suffix=",") }}'
            )
        self.assertEqual("abcd,\nefgh,", rendered)

    def test_plugin_templates(self) -> None:
        with tempfile.TemporaryDirectory() as plugin_templates:
            DictPlugin(
                {"name": "plugin1", "version": "0", "templates": plugin_templates}
            )
            # Create two templates
            os.makedirs(os.path.join(plugin_templates, "plugin1", "apps"))
            with open(
                os.path.join(plugin_templates, "plugin1", "unrendered.txt"),
                "w",
                encoding="utf-8",
            ) as f:
                f.write("This file should not be rendered")
            with open(
                os.path.join(plugin_templates, "plugin1", "apps", "rendered.txt"),
                "w",
                encoding="utf-8",
            ) as f:
                f.write("Hello my ID is {{ ID }}")

            # Render templates
            with temporary_root() as root:
                # Create configuration
                config: Config = tutor_config.load_full(root)
                config["ID"] = "Hector Rumblethorpe"
                plugins.load("plugin1")
                tutor_config.save_enabled_plugins(config)

                # Render environment
                with patch.object(fmt, "STDOUT"):
                    env.save(root, config)

                # Check that plugin template was rendered
                root_env = os.path.join(root, "env")
                dst_unrendered = os.path.join(
                    root_env, "plugins", "plugin1", "unrendered.txt"
                )
                dst_rendered = os.path.join(
                    root_env, "plugins", "plugin1", "apps", "rendered.txt"
                )
                self.assertFalse(os.path.exists(dst_unrendered))
                self.assertTrue(os.path.exists(dst_rendered))
                with open(dst_rendered, encoding="utf-8") as f:
                    self.assertEqual("Hello my ID is Hector Rumblethorpe", f.read())

    def test_renderer_is_reset_on_config_change(self) -> None:
        with tempfile.TemporaryDirectory() as plugin_templates:
            plugin1 = DictPlugin(
                {"name": "plugin1", "version": "0", "templates": plugin_templates}
            )

            # Create one template
            os.makedirs(os.path.join(plugin_templates, plugin1.name))
            with open(
                os.path.join(plugin_templates, plugin1.name, "myplugin.txt"),
                "w",
                encoding="utf-8",
            ) as f:
                f.write("some content")

            # Load env once
            config: Config = {"PLUGINS": []}
            env1 = env.Renderer(config).environment

            # Enable plugins
            plugins.load("plugin1")

            # Load env a second time
            config["PLUGINS"] = ["myplugin"]
            env2 = env.Renderer(config).environment

            self.assertNotIn("plugin1/myplugin.txt", env1.loader.list_templates())
            self.assertIn("plugin1/myplugin.txt", env2.loader.list_templates())

    def test_iter_values_named(self) -> None:
        config: Config = {
            "something0_test_app": 0,
            "something1_test_not_app": 1,
            "notsomething_test_app": 2,
            "something3_test_app": 3,
        }
        renderer = env.Renderer(config)
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


class CurrentVersionTests(unittest.TestCase):
    def test_current_version_in_empty_env(self) -> None:
        with temporary_root() as root:
            self.assertIsNone(env.current_version(root))
            self.assertIsNone(env.get_env_release(root))
            self.assertIsNone(env.should_upgrade_from_release(root))
            self.assertTrue(env.is_up_to_date(root))

    def test_current_version_in_lilac_env(self) -> None:
        with temporary_root() as root:
            os.makedirs(env.base_dir(root))
            with open(
                os.path.join(env.base_dir(root), env.VERSION_FILENAME),
                "w",
                encoding="utf-8",
            ) as f:
                f.write("12.0.46")
            self.assertEqual("12.0.46", env.current_version(root))
            self.assertEqual("lilac", env.get_env_release(root))
            self.assertEqual("lilac", env.should_upgrade_from_release(root))
            self.assertFalse(env.is_up_to_date(root))

    def test_current_version_in_latest_env(self) -> None:
        with temporary_root() as root:
            os.makedirs(env.base_dir(root))
            with open(
                os.path.join(env.base_dir(root), env.VERSION_FILENAME),
                "w",
                encoding="utf-8",
            ) as f:
                f.write(__version__)
            self.assertEqual(__version__, env.current_version(root))
            self.assertEqual("redwood", env.get_env_release(root))
            self.assertIsNone(env.should_upgrade_from_release(root))
            self.assertTrue(env.is_up_to_date(root))


class PatchRendererTests(unittest.TestCase):
    def setUp(self) -> None:
        self.render = env.PatchRenderer()
        self.render.current_template = "current_template"
        return super().setUp()

    @patch("tutor.env.Renderer.render_template")
    def test_render_template(self, render_template_mock: Mock) -> None:
        """Test that render_template changes the current template and
        calls once render_template from Renderer with the current template."""
        self.render.render_template("new_template")

        self.assertEqual(self.render.current_template, "new_template")
        render_template_mock.assert_called_once_with("new_template")

    @patch("tutor.env.Renderer.patch")
    def test_patch_with_first_patch(self, patch_mock: Mock) -> None:
        """Test that patch is called from Renderer and adds patches_locations
        when we didn't have that patch."""
        self.render.patches_locations = {}

        self.render.patch("first_patch")

        patch_mock.assert_called_once_with("first_patch", separator="\n", suffix="")
        self.assertEqual(
            self.render.patches_locations,
            {"first_patch": [self.render.current_template]},
        )

    def test_patch_with_patch_multiple_locations(self) -> None:
        """Test add more locations to a patch."""
        self.render.patches_locations = {"first_patch": ["template_1"]}

        self.render.patch("first_patch")

        self.assertEqual(
            self.render.patches_locations,
            {"first_patch": ["template_1", "current_template"]},
        )

    @patch("tutor.env.plugins.iter_patches")
    def test_patch_with_custom_patch_in_a_plugin_patch(
        self, iter_patches_mock: Mock
    ) -> None:
        """Test the patch function with a plugin with a custom patch.
        Examples:
        - When first_patch is in a plugin patches and has a 'custom_patch',
        the patches_locations will reflect that 'custom_patch' is from
        first_patch location.
        - If in tutor-mfe/tutormfe/patches/caddyfile you add a custom patch
        inside the caddyfile patch, the patches_locations will reflect that.

        Expected behavior:
        - Process the first_patch and find the custom_patch in a plugin with
        first_patch patch.
        - Process the custom_patch and add "within patch: first_patch" in the
        patches_locations."""
        iter_patches_mock.side_effect = [
            ["""{{ patch('custom_patch')|indent(4) }}"""],
            [],
        ]
        self.render.patches_locations = {}
        calls = [unittest.mock.call("first_patch"), unittest.mock.call("custom_patch")]

        self.render.patch("first_patch")

        iter_patches_mock.assert_has_calls(calls)
        self.assertEqual(
            self.render.patches_locations,
            {
                "first_patch": ["current_template"],
                "custom_patch": ["within patch: first_patch"],
            },
        )

    @patch("tutor.env.plugins.iter_patches")
    def test_patch_with_processed_patch_in_a_plugin_patch(
        self, iter_patches_mock: Mock
    ) -> None:
        """Test the patch function with a plugin with a processed patch.
        Example:
        - When first_patch was processed and the second_patch is used in a
        plugin and call the first_patch again. Then the patches_locations will
        reflect that first_patch also have a location from second_patch."""
        iter_patches_mock.side_effect = [
            ["""{{ patch('first_patch')|indent(4) }}"""],
            [],
        ]
        self.render.patches_locations = {"first_patch": ["current_template"]}

        self.render.patch("second_patch")

        self.assertEqual(
            self.render.patches_locations,
            {
                "first_patch": ["current_template", "within patch: second_patch"],
                "second_patch": ["current_template"],
            },
        )

    @patch("tutor.env.Renderer.iter_templates_in")
    @patch("tutor.env.PatchRenderer.render_template")
    def test_render_all(
        self, render_template_mock: Mock, iter_templates_in_mock: Mock
    ) -> None:
        """Test render_template was called for templates in iter_templates_in."""
        iter_templates_in_mock.return_value = ["template_1", "template_2"]
        calls = [unittest.mock.call("template_1"), unittest.mock.call("template_2")]

        self.render.render_all()

        iter_templates_in_mock.assert_called_once()
        render_template_mock.assert_has_calls(calls)

    @patch("sys.stdout", new_callable=StringIO)
    @patch("tutor.env.PatchRenderer.render_all")
    def test_print_patches_locations(
        self, render_all_mock: Mock, stdout_mock: Mock
    ) -> None:
        """Test render_all was called and the output of print_patches_locations."""
        self.render.patches_locations = {"first_patch": ["template_1", "template_2"]}

        self.render.print_patches_locations()

        render_all_mock.assert_called_once()
        self.assertEqual(
            """
PATCH      	LOCATIONS
first_patch	template_1
           	template_2
""".strip(),
            stdout_mock.getvalue().strip(),
        )
