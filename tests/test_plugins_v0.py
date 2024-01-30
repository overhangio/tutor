from __future__ import annotations

from unittest.mock import patch

from tests.helpers import PluginsTestCase, temporary_root
from tutor import config as tutor_config
from tutor import exceptions, fmt, hooks, plugins
from tutor.plugins import v0 as plugins_v0
from tutor.types import Config, get_typed


class PluginsV0Tests(PluginsTestCase):
    def test_iter_installed(self) -> None:
        self.assertEqual([], list(plugins.iter_installed()))

    def test_is_installed(self) -> None:
        self.assertFalse(plugins.is_installed("dummy"))

    def test_official_plugins(self) -> None:
        # Create 2 official plugins
        plugins_v0.OfficialPlugin("plugin1")
        plugins_v0.OfficialPlugin("plugin2")
        self.assertEqual(
            ["plugin1", "plugin2"],
            list(plugins.iter_installed()),
        )

    def test_load(self) -> None:
        config: Config = {tutor_config.PLUGINS_CONFIG_KEY: []}
        plugins_v0.DictPlugin({"name": "plugin1"})
        plugins_v0.DictPlugin({"name": "plugin2"})
        plugins.load("plugin2")
        plugins.load("plugin1")
        tutor_config.save_enabled_plugins(config)
        self.assertEqual(
            ["plugin1", "plugin2"], config[tutor_config.PLUGINS_CONFIG_KEY]
        )

    def test_enable_twice(self) -> None:
        plugins_v0.DictPlugin({"name": "plugin1"})
        plugins.load("plugin1")
        plugins.load("plugin1")
        config: Config = {tutor_config.PLUGINS_CONFIG_KEY: []}
        tutor_config.save_enabled_plugins(config)
        self.assertEqual(["plugin1"], config[tutor_config.PLUGINS_CONFIG_KEY])

    def test_load_not_installed_plugin(self) -> None:
        self.assertRaises(exceptions.TutorError, plugins.load, "plugin1")

    def test_disable(self) -> None:
        plugins_v0.DictPlugin(
            {
                "name": "plugin1",
                "version": "1.0.0",
                "config": {"set": {"KEY": "value"}},
            }
        )
        plugins_v0.DictPlugin(
            {
                "name": "plugin2",
                "version": "1.0.0",
            }
        )
        config: Config = {"PLUGINS": ["plugin1", "plugin2"]}
        tutor_config.enable_plugins(config)
        with patch.object(fmt, "STDOUT"):
            hooks.Actions.PLUGIN_UNLOADED.do("plugin1", "", config)
        self.assertEqual(["plugin2"], config["PLUGINS"])

    def test_disable_removes_set_config(self) -> None:
        plugins_v0.DictPlugin(
            {
                "name": "plugin1",
                "version": "1.0.0",
                "config": {"set": {"KEY": "value"}},
            }
        )
        config: Config = {"PLUGINS": ["plugin1"], "KEY": "value"}
        tutor_config.enable_plugins(config)
        with patch.object(fmt, "STDOUT"):
            hooks.Actions.PLUGIN_UNLOADED.do("plugin1", "", config)
        self.assertEqual([], config["PLUGINS"])
        self.assertNotIn("KEY", config)

    def test_patches(self) -> None:
        plugins_v0.DictPlugin(
            {"name": "plugin1", "patches": {"patch1": "Hello {{ ID }}"}}
        )
        plugins.load_all(["plugin1"])
        patches = list(plugins.iter_patches("patch1"))
        self.assertEqual(["Hello {{ ID }}"], patches)

    def test_plugin_without_patches(self) -> None:
        plugins_v0.DictPlugin({"name": "plugin1"})
        plugins.load_all(["plugin1"])
        patches = list(plugins.iter_patches("patch1"))
        self.assertEqual([], patches)

    def test_configure(self) -> None:
        plugins_v0.DictPlugin(
            {
                "name": "plugin1",
                "config": {
                    "add": {"PARAM1": "value1", "PARAM2": "value2"},
                    "set": {"PARAM3": "value3"},
                    "defaults": {"PARAM4": "value4"},
                },
            }
        )
        plugins.load("plugin1")

        base = tutor_config.get_base()
        defaults = tutor_config.get_defaults()

        self.assertEqual(base["PARAM3"], "value3")
        self.assertEqual(base["PLUGIN1_PARAM1"], "value1")
        self.assertEqual(base["PLUGIN1_PARAM2"], "value2")
        self.assertEqual(defaults["PLUGIN1_PARAM4"], "value4")

    def test_configure_set_does_not_override(self) -> None:
        config: Config = {"ID1": "oldid"}

        plugins_v0.DictPlugin(
            {"name": "plugin1", "config": {"set": {"ID1": "newid", "ID2": "id2"}}}
        )
        plugins.load("plugin1")
        tutor_config.update_with_base(config)

        self.assertEqual("oldid", config["ID1"])
        self.assertEqual("id2", config["ID2"])

    def test_configure_set_random_string(self) -> None:
        plugins_v0.DictPlugin(
            {
                "name": "plugin1",
                "config": {"set": {"PARAM1": "{{ 128|random_string }}"}},
            }
        )
        plugins.load("plugin1")
        config = tutor_config.get_base()
        tutor_config.render_full(config)

        self.assertEqual(128, len(get_typed(config, "PARAM1", str)))

    def test_configure_default_value_with_previous_definition(self) -> None:
        config: Config = {"PARAM1": "value"}
        plugins_v0.DictPlugin(
            {"name": "plugin1", "config": {"defaults": {"PARAM2": "{{ PARAM1 }}"}}}
        )
        plugins.load("plugin1")
        tutor_config.update_with_defaults(config)
        self.assertEqual("{{ PARAM1 }}", config["PLUGIN1_PARAM2"])

    def test_config_load_from_plugins(self) -> None:
        config: Config = {}

        plugins_v0.DictPlugin(
            {"name": "plugin1", "config": {"add": {"PARAM1": "{{ 10|random_string }}"}}}
        )
        plugins.load("plugin1")

        tutor_config.update_with_base(config)
        tutor_config.update_with_defaults(config)
        tutor_config.render_full(config)
        value1 = get_typed(config, "PLUGIN1_PARAM1", str)

        self.assertEqual(10, len(value1))

    def test_init_tasks(self) -> None:
        plugins_v0.DictPlugin({"name": "plugin1", "hooks": {"init": ["myclient"]}})
        with patch.object(
            plugins_v0.env, "read_template_file", return_value="echo hello"
        ) as mock_read_template:
            plugins.load("plugin1")
            mock_read_template.assert_called_once_with(
                "plugin1", "hooks", "myclient", "init"
            )

        self.assertIn(
            ("myclient", "echo hello"),
            list(hooks.Filters.CLI_DO_INIT_TASKS.iterate()),
        )

    def test_plugins_are_updated_on_config_change(self) -> None:
        config: Config = {}
        plugins_v0.DictPlugin({"name": "plugin1"})
        tutor_config.enable_plugins(config)
        plugins1 = list(plugins.iter_loaded())
        config["PLUGINS"] = ["plugin1"]
        tutor_config.enable_plugins(config)
        plugins2 = list(plugins.iter_loaded())

        self.assertEqual([], plugins1)
        self.assertEqual(1, len(plugins2))

    def test_dict_plugin(self) -> None:
        plugin = plugins_v0.DictPlugin(
            {"name": "myplugin", "config": {"set": {"KEY": "value"}}, "version": "0.1"}
        )
        plugins.load("myplugin")
        overriden_items = hooks.Filters.CONFIG_OVERRIDES.apply([])
        versions = list(plugins.iter_info())
        self.assertEqual("myplugin", plugin.name)
        self.assertEqual([("myplugin", "0.1")], versions)
        self.assertEqual([("KEY", "value")], overriden_items)

    def test_config_disable_plugin(self) -> None:
        plugins_v0.DictPlugin(
            {"name": "plugin1", "config": {"set": {"KEY1": "value1"}}}
        )
        plugins_v0.DictPlugin(
            {"name": "plugin2", "config": {"set": {"KEY2": "value2"}}}
        )
        plugins.load("plugin1")
        plugins.load("plugin2")

        with temporary_root() as root:
            config = tutor_config.load_minimal(root)
            config_pre = config.copy()
            with patch.object(fmt, "STDOUT"):
                hooks.Actions.PLUGIN_UNLOADED.do("plugin1", "", config)
            config_post = tutor_config.load_minimal(root)

        self.assertEqual("value1", config_pre["KEY1"])
        self.assertEqual("value2", config_pre["KEY2"])
        self.assertNotIn("KEY1", config)
        self.assertNotIn("KEY1", config_post)
        self.assertEqual("value2", config["KEY2"])
