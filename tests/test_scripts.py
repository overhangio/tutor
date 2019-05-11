import unittest
import unittest.mock

from tutor.config import load_defaults
from tutor import env
from tutor import scripts


class ScriptsTests(unittest.TestCase):
    def test_run_script(self):
        config = {}
        load_defaults({})
        rendered_script = env.render_file("scripts", "create_databases.sh")
        with unittest.mock.Mock() as run_func:
            scripts.run_script(
                "/tmp", config, "someservice", "create_databases.sh", run_func
            )
            run_func.assert_called_once_with(
                "/tmp", config, "someservice", rendered_script
            )
