from __future__ import annotations

from tests.helpers import PluginsTestCase
from tutor import hooks, plugins


class PluginsTests(PluginsTestCase):
    def test_env_patches_updated_on_new_plugin(self) -> None:
        self.assertEqual([], list(plugins.iter_patches("mypatch")))

        hooks.Filters.ENV_PATCHES.add_item(("mypatch", "hello!"))

        # env patches cache should be cleared on new plugin
        hooks.Actions.PLUGIN_LOADED.do("dummyplugin")

        self.assertEqual(["hello!"], list(plugins.iter_patches("mypatch")))
