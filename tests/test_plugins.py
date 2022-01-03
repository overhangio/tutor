import unittest
from unittest.mock import Mock, patch

from tutor import config as tutor_config
from tutor import exceptions, fmt, plugins
from tutor.types import Config, get_typed


class PluginsTests(unittest.TestCase):
    def setUp(self) -> None:
        plugins.Plugins.clear()

    @patch.object(plugins.DictPlugin, "iter_installed", return_value=[])
    def test_iter_installed(self, dict_plugin_iter_installed: Mock) -> None:
        with patch.object(plugins.pkg_resources, "iter_entry_points", return_value=[]):  # type: ignore
            self.assertEqual([], list(plugins.iter_installed()))
            dict_plugin_iter_installed.assert_called_once()

    def test_is_installed(self) -> None:
        self.assertFalse(plugins.is_installed("dummy"))

    @patch.object(plugins.DictPlugin, "iter_installed", return_value=[])
    def test_official_plugins(self, dict_plugin_iter_installed: Mock) -> None:
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
        dict_plugin_iter_installed.assert_called_once()

    def test_enable(self) -> None:
        config: Config = {plugins.CONFIG_KEY: []}
        with patch.object(plugins, "is_installed", return_value=True):
            plugins.enable(config, "plugin2")
            plugins.enable(config, "plugin1")
        self.assertEqual(["plugin1", "plugin2"], config[plugins.CONFIG_KEY])

    def test_enable_twice(self) -> None:
        config: Config = {plugins.CONFIG_KEY: []}
        with patch.object(plugins, "is_installed", return_value=True):
            plugins.enable(config, "plugin1")
            plugins.enable(config, "plugin1")
        self.assertEqual(["plugin1"], config[plugins.CONFIG_KEY])

    def test_enable_not_installed_plugin(self) -> None:
        config: Config = {"PLUGINS": []}
        with patch.object(plugins, "is_installed", return_value=False):
            self.assertRaises(exceptions.TutorError, plugins.enable, config, "plugin1")

    @patch.object(
        plugins.Plugins,
        "iter_installed",
        return_value=[
            plugins.DictPlugin(
                {
                    "name": "plugin1",
                    "version": "1.0.0",
                    "config": {"set": {"KEY": "value"}},
                }
            ),
            plugins.DictPlugin(
                {
                    "name": "plugin2",
                    "version": "1.0.0",
                }
            ),
        ],
    )
    def test_disable(self, _iter_installed_mock: Mock) -> None:
        config: Config = {"PLUGINS": ["plugin1", "plugin2"]}
        with patch.object(fmt, "STDOUT"):
            plugin = plugins.get_enabled(config, "plugin1")
            plugins.disable(config, plugin)
        self.assertEqual(["plugin2"], config["PLUGINS"])

    @patch.object(
        plugins.Plugins,
        "iter_installed",
        return_value=[
            plugins.DictPlugin(
                {
                    "name": "plugin1",
                    "version": "1.0.0",
                    "config": {"set": {"KEY": "value"}},
                }
            ),
        ],
    )
    def test_disable_removes_set_config(self, _iter_installed_mock: Mock) -> None:
        config: Config = {"PLUGINS": ["plugin1"], "KEY": "value"}
        plugin = plugins.get_enabled(config, "plugin1")
        with patch.object(fmt, "STDOUT"):
            plugins.disable(config, plugin)
        self.assertEqual([], config["PLUGINS"])
        self.assertNotIn("KEY", config)

    def test_none_plugins(self) -> None:
        config: Config = {plugins.CONFIG_KEY: None}
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
        class plugin1:
            config: Config = {
                "add": {"PARAM1": "value1", "PARAM2": "value2"},
                "set": {"PARAM3": "value3"},
                "defaults": {"PARAM4": "value4"},
            }

        with patch.object(
            plugins.Plugins,
            "iter_enabled",
            return_value=[plugins.BasePlugin("plugin1", plugin1)],
        ):
            base = tutor_config.get_base({})
            defaults = tutor_config.get_defaults({})

        self.assertEqual(base["PARAM3"], "value3")
        self.assertEqual(base["PLUGIN1_PARAM1"], "value1")
        self.assertEqual(base["PLUGIN1_PARAM2"], "value2")
        self.assertEqual(defaults["PLUGIN1_PARAM4"], "value4")

    def test_configure_set_does_not_override(self) -> None:
        config: Config = {"ID1": "oldid"}

        class plugin1:
            config: Config = {"set": {"ID1": "newid", "ID2": "id2"}}

        with patch.object(
            plugins.Plugins,
            "iter_enabled",
            return_value=[plugins.BasePlugin("plugin1", plugin1)],
        ):
            tutor_config.update_with_base(config)

        self.assertEqual("oldid", config["ID1"])
        self.assertEqual("id2", config["ID2"])

    def test_configure_set_random_string(self) -> None:
        class plugin1:
            config: Config = {"set": {"PARAM1": "{{ 128|random_string }}"}}

        with patch.object(
            plugins.Plugins,
            "iter_enabled",
            return_value=[plugins.BasePlugin("plugin1", plugin1)],
        ):
            config = tutor_config.get_base({})
        tutor_config.render_full(config)

        self.assertEqual(128, len(get_typed(config, "PARAM1", str)))

    def test_configure_default_value_with_previous_definition(self) -> None:
        config: Config = {"PARAM1": "value"}

        class plugin1:
            config: Config = {"defaults": {"PARAM2": "{{ PARAM1 }}"}}

        with patch.object(
            plugins.Plugins,
            "iter_enabled",
            return_value=[plugins.BasePlugin("plugin1", plugin1)],
        ):
            tutor_config.update_with_defaults(config)
        self.assertEqual("{{ PARAM1 }}", config["PLUGIN1_PARAM2"])

    def test_config_load_from_plugins(self) -> None:
        config: Config = {}

        class plugin1:
            config: Config = {"add": {"PARAM1": "{{ 10|random_string }}"}}

        with patch.object(
            plugins.Plugins,
            "iter_enabled",
            return_value=[plugins.BasePlugin("plugin1", plugin1)],
        ):
            tutor_config.update_with_base(config)
            tutor_config.update_with_defaults(config)
        tutor_config.render_full(config)
        value1 = get_typed(config, "PLUGIN1_PARAM1", str)

        self.assertEqual(10, len(value1))

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
        config: Config = {"PLUGINS": []}
        plugins1 = plugins.Plugins(config)
        self.assertEqual(0, len(list(plugins1.iter_enabled())))
        config["PLUGINS"] = ["plugin1"]
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
