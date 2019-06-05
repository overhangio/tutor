import unittest
import unittest.mock

from tutor import config as tutor_config
from tutor import exceptions
from tutor import plugins


class PluginsTests(unittest.TestCase):
    def setUp(self):
        plugins.Patches.CACHE.clear()

    def test_iter_installed(self):
        with unittest.mock.patch.object(
            plugins.pkg_resources, "iter_entry_points", return_value=[]
        ):
            self.assertEqual([], list(plugins.iter_installed()))

    def test_is_installed(self):
        self.assertFalse(plugins.is_installed("dummy"))

    def test_enable(self):
        config = {plugins.CONFIG_KEY: []}
        with unittest.mock.patch.object(plugins, "is_installed", return_value=True):
            plugins.enable(config, "plugin2")
            plugins.enable(config, "plugin1")
        self.assertEqual(["plugin1", "plugin2"], config[plugins.CONFIG_KEY])

    def test_enable_twice(self):
        config = {plugins.CONFIG_KEY: []}
        with unittest.mock.patch.object(plugins, "is_installed", return_value=True):
            plugins.enable(config, "plugin1")
            plugins.enable(config, "plugin1")
        self.assertEqual(["plugin1"], config[plugins.CONFIG_KEY])

    def test_enable_not_installed_plugin(self):
        config = {"PLUGINS": []}
        with unittest.mock.patch.object(plugins, "is_installed", return_value=False):
            self.assertRaises(exceptions.TutorError, plugins.enable, config, "plugin1")

    def test_disable(self):
        config = {"PLUGINS": ["plugin1", "plugin2"]}
        plugins.disable(config, "plugin1")
        self.assertEqual(["plugin2"], config["PLUGINS"])

    def test_patches(self):
        class plugin1:
            patches = {"patch1": "Hello {{ ID }}"}

        with unittest.mock.patch.object(
            plugins, "iter_enabled", return_value=[("plugin1", plugin1)]
        ):
            patches = list(plugins.iter_patches({}, "patch1"))
        self.assertEqual([("plugin1", "Hello {{ ID }}")], patches)

    def test_plugin_without_patches(self):
        class plugin1:
            pass

        with unittest.mock.patch.object(
            plugins, "iter_enabled", return_value=[("plugin1", plugin1)]
        ):
            patches = list(plugins.iter_patches({}, "patch1"))
        self.assertEqual([], patches)

    def test_configure(self):
        config = {"ID": "id"}
        defaults = {}

        class plugin1:
            config = {
                "add": {"PARAM1": "value1", "PARAM2": "value2"},
                "set": {"PARAM3": "value3"},
                "defaults": {"PARAM4": "value4"},
            }

        with unittest.mock.patch.object(
            plugins, "iter_enabled", return_value=[("plugin1", plugin1)]
        ):
            tutor_config.load_plugins(config, defaults)

        self.assertEqual(
            {
                "ID": "id",
                "PARAM3": "value3",
                "PLUGIN1_PARAM1": "value1",
                "PLUGIN1_PARAM2": "value2",
            },
            config,
        )
        self.assertEqual({"PLUGIN1_PARAM4": "value4"}, defaults)

    def test_configure_set_does_not_override(self):
        config = {"ID": "oldid"}

        class plugin1:
            config = {"set": {"ID": "newid"}}

        with unittest.mock.patch.object(
            plugins, "iter_enabled", return_value=[("plugin1", plugin1)]
        ):
            tutor_config.load_plugins(config, {})

        self.assertEqual({"ID": "oldid"}, config)

    def test_configure_set_random_string(self):
        config = {}

        class plugin1:
            config = {"set": {"PARAM1": "{{ 128|random_string }}"}}

        with unittest.mock.patch.object(
            plugins, "iter_enabled", return_value=[("plugin1", plugin1)]
        ):
            tutor_config.load_plugins(config, {})
        self.assertEqual(128, len(config["PARAM1"]))

    def test_configure_default_value_with_previous_definition(self):
        config = {}
        defaults = {"PARAM1": "value"}

        class plugin1:
            config = {"defaults": {"PARAM2": "{{ PARAM1 }}"}}

        with unittest.mock.patch.object(
            plugins, "iter_enabled", return_value=[("plugin1", plugin1)]
        ):
            tutor_config.load_plugins(config, defaults)
        self.assertEqual("{{ PARAM1 }}", defaults["PLUGIN1_PARAM2"])

    def test_scripts(self):
        class plugin1:
            scripts = {"init": ["myclient"]}

        with unittest.mock.patch.object(
            plugins, "iter_enabled", return_value=[("plugin1", plugin1)]
        ):
            self.assertEqual(
                [("plugin1", "myclient")], list(plugins.iter_scripts({}, "init"))
            )
    
    def test_iter_templates(self):
        class plugin1:
            templates = "/tmp/templates"
        with unittest.mock.patch.object(
            plugins, "iter_enabled", return_value=[("plugin1", plugin1)]
        ):
            self.assertEqual(
                [("plugin1", "/tmp/templates")], list(plugins.iter_templates({}))
            )