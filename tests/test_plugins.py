from typing import Any, Dict
import unittest
from unittest.mock import Mock, patch

from tutor import config as tutor_config
from tutor import exceptions
from tutor import fmt
from tutor import plugins


class PluginsTests(unittest.TestCase):
    def setUp(self) -> None:
        plugins.Plugins.clear()

    @patch.object(plugins.DictPlugin, "iter_installed", return_value=[])
    def test_iter_installed(self, _dict_plugin_iter_installed: Mock) -> None:
        with patch.object(plugins.pkg_resources, "iter_entry_points", return_value=[]):  # type: ignore
            self.assertEqual([], list(plugins.iter_installed()))

    def test_is_installed(self) -> None:
        self.assertFalse(plugins.is_installed("dummy"))

    @patch.object(plugins.DictPlugin, "iter_installed", return_value=[])
    def test_official_plugins(self, _dict_plugin_iter_installed: Mock) -> None:
        with patch.object(plugins.importlib, "import_module", return_value=42):  # type: ignore
            plugin1 = plugins.OfficialPlugin.load("plugin1")
        with patch.object(plugins.importlib, "import_module", return_value=43):  # type: ignore
            plugin2 = plugins.OfficialPlugin.load("plugin2")
        with patch.object(
            plugins.EntrypointPlugin,
            "iter_installed",
            return_value=[plugin1],
        ):
            self.assertEqual(
                [plugin1, plugin2],
                list(plugins.iter_installed()),
            )

    def test_enable(self) -> None:
        config: Dict[str, Any] = {plugins.CONFIG_KEY: []}
        with patch.object(plugins, "is_installed", return_value=True):
            plugins.enable(config, "plugin2")
            plugins.enable(config, "plugin1")
        self.assertEqual(["plugin1", "plugin2"], config[plugins.CONFIG_KEY])

    def test_enable_twice(self) -> None:
        config: Dict[str, Any] = {plugins.CONFIG_KEY: []}
        with patch.object(plugins, "is_installed", return_value=True):
            plugins.enable(config, "plugin1")
            plugins.enable(config, "plugin1")
        self.assertEqual(["plugin1"], config[plugins.CONFIG_KEY])

    def test_enable_not_installed_plugin(self) -> None:
        config: Dict[str, Any] = {"PLUGINS": []}
        with patch.object(plugins, "is_installed", return_value=False):
            self.assertRaises(exceptions.TutorError, plugins.enable, config, "plugin1")

    def test_disable(self) -> None:
        config: Dict[str, Any] = {"PLUGINS": ["plugin1", "plugin2"]}
        with patch.object(fmt, "STDOUT"):
            plugins.disable(config, "plugin1")
        self.assertEqual(["plugin2"], config["PLUGINS"])

    def test_disable_removes_set_config(self) -> None:
        with patch.object(
            plugins.Plugins,
            "iter_enabled",
            return_value=[
                plugins.DictPlugin(
                    {
                        "name": "plugin1",
                        "version": "1.0.0",
                        "config": {"set": {"KEY": "value"}},
                    }
                )
            ],
        ):
            config = {"PLUGINS": ["plugin1"], "KEY": "value"}
            with patch.object(fmt, "STDOUT"):
                plugins.disable(config, "plugin1")
            self.assertEqual([], config["PLUGINS"])
            self.assertNotIn("KEY", config)

    def test_none_plugins(self) -> None:
        config = {plugins.CONFIG_KEY: None}
        self.assertFalse(plugins.is_enabled(config, "myplugin"))

    def test_patches(self) -> None:
        class plugin1:
            patches = {"patch1": "Hello {{ ID }}"}

        with patch.object(
            plugins.Plugins,
            "iter_enabled",
            return_value=[plugins.BasePlugin("plugin1", plugin1)],
        ):
            patches = list(plugins.iter_patches({}, "patch1"))
        self.assertEqual([("plugin1", "Hello {{ ID }}")], patches)

    def test_plugin_without_patches(self) -> None:
        with patch.object(
            plugins.Plugins,
            "iter_enabled",
            return_value=[plugins.BasePlugin("plugin1", None)],
        ):
            patches = list(plugins.iter_patches({}, "patch1"))
        self.assertEqual([], patches)

    def test_configure(self) -> None:
        config = {"ID": "id"}
        defaults: Dict[str, Any] = {}

        class plugin1:
            config = {
                "add": {"PARAM1": "value1", "PARAM2": "value2"},
                "set": {"PARAM3": "value3"},
                "defaults": {"PARAM4": "value4"},
            }

        with patch.object(
            plugins.Plugins,
            "iter_enabled",
            return_value=[plugins.BasePlugin("plugin1", plugin1)],
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

    def test_configure_set_does_not_override(self) -> None:
        config = {"ID": "oldid"}

        class plugin1:
            config = {"set": {"ID": "newid"}}

        with patch.object(
            plugins.Plugins,
            "iter_enabled",
            return_value=[plugins.BasePlugin("plugin1", plugin1)],
        ):
            tutor_config.load_plugins(config, {})

        self.assertEqual({"ID": "oldid"}, config)

    def test_configure_set_random_string(self) -> None:
        config: Dict[str, Any] = {}

        class plugin1:
            config = {"set": {"PARAM1": "{{ 128|random_string }}"}}

        with patch.object(
            plugins.Plugins,
            "iter_enabled",
            return_value=[plugins.BasePlugin("plugin1", plugin1)],
        ):
            tutor_config.load_plugins(config, {})
        self.assertEqual(128, len(config["PARAM1"]))

    def test_configure_default_value_with_previous_definition(self) -> None:
        config: Dict[str, Any] = {}
        defaults = {"PARAM1": "value"}

        class plugin1:
            config = {"defaults": {"PARAM2": "{{ PARAM1 }}"}}

        with patch.object(
            plugins.Plugins,
            "iter_enabled",
            return_value=[plugins.BasePlugin("plugin1", plugin1)],
        ):
            tutor_config.load_plugins(config, defaults)
        self.assertEqual("{{ PARAM1 }}", defaults["PLUGIN1_PARAM2"])

    def test_configure_add_twice(self) -> None:
        config: Dict[str, Any] = {}

        class plugin1:
            config = {"add": {"PARAM1": "{{ 10|random_string }}"}}

        with patch.object(
            plugins.Plugins,
            "iter_enabled",
            return_value=[plugins.BasePlugin("plugin1", plugin1)],
        ):
            tutor_config.load_plugins(config, {})
        value1 = config["PLUGIN1_PARAM1"]
        with patch.object(
            plugins.Plugins,
            "iter_enabled",
            return_value=[plugins.BasePlugin("plugin1", plugin1)],
        ):
            tutor_config.load_plugins(config, {})
        value2 = config["PLUGIN1_PARAM1"]

        self.assertEqual(10, len(value1))
        self.assertEqual(10, len(value2))
        self.assertEqual(value1, value2)

    def test_hooks(self) -> None:
        class plugin1:
            hooks = {"init": ["myclient"]}

        with patch.object(
            plugins.Plugins,
            "iter_enabled",
            return_value=[plugins.BasePlugin("plugin1", plugin1)],
        ):
            self.assertEqual(
                [("plugin1", ["myclient"])], list(plugins.iter_hooks({}, "init"))
            )

    def test_plugins_are_updated_on_config_change(self) -> None:
        config: Dict[str, Any] = {"PLUGINS": []}
        plugins1 = plugins.Plugins(config)
        self.assertEqual(0, len(list(plugins1.iter_enabled())))
        config["PLUGINS"].append("plugin1")
        with patch.object(
            plugins.Plugins,
            "iter_installed",
            return_value=[plugins.BasePlugin("plugin1", None)],
        ):
            plugins2 = plugins.Plugins(config)
            self.assertEqual(1, len(list(plugins2.iter_enabled())))

    def test_dict_plugin(self) -> None:
        plugin = plugins.DictPlugin(
            {"name": "myplugin", "config": {"set": {"KEY": "value"}}, "version": "0.1"}
        )
        self.assertEqual("myplugin", plugin.name)
        self.assertEqual({"KEY": "value"}, plugin.config_set)
