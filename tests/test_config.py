import unittest
import unittest.mock
import tempfile

from tutor import config as tutor_config
from tutor import env
from tutor import interactive


class ConfigTests(unittest.TestCase):
    def setUp(self):
        # This is necessary to avoid cached mocks
        env.Renderer.reset()

    def test_version(self):
        defaults = tutor_config.load_defaults()
        self.assertNotIn("TUTOR_VERSION", defaults)

    def test_merge(self):
        config1 = {"x": "y"}
        config2 = {"x": "z"}
        tutor_config.merge(config1, config2)
        self.assertEqual({"x": "y"}, config1)

    def test_merge_render(self):
        config = {}
        defaults = tutor_config.load_defaults()
        with unittest.mock.patch.object(
            tutor_config.utils, "random_string", return_value="abcd"
        ):
            tutor_config.merge(config, defaults)

        self.assertEqual("abcd", config["MYSQL_ROOT_PASSWORD"])

    @unittest.mock.patch.object(tutor_config.fmt, "echo")
    def test_update_twice(self, _):
        with tempfile.TemporaryDirectory() as root:
            tutor_config.update(root)
            config1 = tutor_config.load_user(root)

            tutor_config.update(root)
            config2 = tutor_config.load_user(root)

        self.assertEqual(config1, config2)

    @unittest.mock.patch.object(tutor_config.fmt, "echo")
    def test_removed_entry_is_added_on_save(self, _):
        with tempfile.TemporaryDirectory() as root:
            with unittest.mock.patch.object(
                tutor_config.utils, "random_string"
            ) as mock_random_string:
                mock_random_string.return_value = "abcd"
                config1, _ = tutor_config.load_all(root)
                password1 = config1["MYSQL_ROOT_PASSWORD"]

                config1.pop("MYSQL_ROOT_PASSWORD")
                tutor_config.save_config_file(root, config1)

                mock_random_string.return_value = "efgh"
                config2, _ = tutor_config.load_all(root)
                password2 = config2["MYSQL_ROOT_PASSWORD"]

        self.assertEqual("abcd", password1)
        self.assertEqual("efgh", password2)

    def test_interactive_load_all(self):
        with tempfile.TemporaryDirectory() as rootdir:
            config, defaults = interactive.load_all(rootdir, interactive=False)

        self.assertIn("MYSQL_ROOT_PASSWORD", config)
        self.assertEqual(8, len(config["MYSQL_ROOT_PASSWORD"]))
        self.assertNotIn("LMS_HOST", config)
        self.assertEqual("www.myopenedx.com", defaults["LMS_HOST"])
        self.assertEqual("studio.{{ LMS_HOST }}", defaults["CMS_HOST"])

    def test_is_service_activated(self):
        config = {"ACTIVATE_SERVICE1": True, "ACTIVATE_SERVICE2": False}

        self.assertTrue(tutor_config.is_service_activated(config, "service1"))
        self.assertFalse(tutor_config.is_service_activated(config, "service2"))
