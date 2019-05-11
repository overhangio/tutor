import unittest
import unittest.mock

from tutor.commands import config as tutor_config
from tutor import env
from tutor import scripts


class ScriptsTests(unittest.TestCase):
    def test_run_script(self):
        config = {}
        defaults = tutor_config.load_defaults()
        tutor_config.merge(config, defaults)

        rendered_script = env.render_file(
            config, "scripts", "create_databases.sh"
        ).strip()
        run_func = unittest.mock.Mock()
        scripts.run_script(
            "/tmp", config, "someservice", "create_databases.sh", run_func
        )
        run_func.assert_called_once_with("/tmp", "someservice", rendered_script)
