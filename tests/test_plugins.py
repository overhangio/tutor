import unittest
import unittest.mock

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
        config = {"ID": "oldid"}

        class plugin1:
            config = {
                "add": {"PARAM1": "value1", "PARAM2": "value2"},
                "set": {"ID": "newid"},
                "defaults": {"PARAM3": "value3"},
            }

        with unittest.mock.patch.object(
            plugins, "iter_enabled", return_value=[("plugin1", plugin1)]
        ):
            add_config, set_config, defaults_config = plugins.load_config(config)
        self.assertEqual(
            {"PLUGIN1_PARAM1": "value1", "PLUGIN1_PARAM2": "value2"}, add_config
        )
        self.assertEqual({"ID": "newid"}, set_config)
        self.assertEqual({"PLUGIN1_PARAM3": "value3"}, defaults_config)

    def test_scripts(self):
        class plugin1:
            scripts = {"init": [{"service": "myclient", "command": "init command"}]}

        with unittest.mock.patch.object(
            plugins, "iter_enabled", return_value=[("plugin1", plugin1)]
        ):
            self.assertEqual(
                [("plugin1", "myclient", "init command")],
                list(plugins.iter_scripts({}, "init")),
            )
