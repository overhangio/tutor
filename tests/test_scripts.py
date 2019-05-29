import unittest
import unittest.mock

from tutor.commands import config as tutor_config
from tutor import scripts


class DummyRunner(scripts.BaseRunner):
    exec = unittest.mock.Mock()


class ScriptsTests(unittest.TestCase):
    def test_run(self):
        config = tutor_config.load_defaults()
        runner = DummyRunner("/tmp", config)
        rendered_script = runner.render("mysql-client", "createdatabases")
        runner.run("mysql-client", "createdatabases")
        runner.exec.assert_called_once_with("mysql-client", rendered_script)
