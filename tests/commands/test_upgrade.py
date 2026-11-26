import shlex
import unittest
from unittest.mock import Mock, patch

from tests.commands.base import TestCommandMixin
from tests.helpers import temporary_root
from tutor import config as tutor_config
from tutor import fmt
from tutor.commands import compose, k8s  # noqa: F401  # avoid circular imports
from tutor.commands.upgrade import compose as compose_upgrade
from tutor.commands.upgrade import k8s as k8s_upgrade
from tutor.types import Config


class UpgradeMongoDbTests(unittest.TestCase, TestCommandMixin):
    def config(self, username: str = "openedx", password: str = "secret") -> Config:
        return {
            "RUN_MONGODB": True,
            "MONGODB_USERNAME": username,
            "MONGODB_PASSWORD": password,
            "DOCKER_IMAGE_MONGODB": "mongo:7.0.39",
        }

    @patch.object(compose_upgrade, "sleep")
    @patch.object(compose_upgrade.tutor_env, "save")
    def test_compose_intermediate_version_runs_without_authentication(
        self, save: Mock, _sleep: Mock
    ) -> None:
        config = self.config()
        context = Mock()
        with patch.object(fmt, "echo"):
            compose_upgrade.upgrade_mongodb(context, config, "8.0.4", "8.0")

        saved_config = save.call_args[0][1]
        self.assertEqual("mongo:8.0.4", saved_config["DOCKER_IMAGE_MONGODB"])
        self.assertEqual("", saved_config["MONGODB_USERNAME"])
        self.assertEqual("", saved_config["MONGODB_PASSWORD"])
        # Later upgrade steps, which may save the environment again, keep running
        # without authentication: intermediate MongoDB images might not support it.
        self.assertEqual("", config["MONGODB_USERNAME"])
        self.assertEqual("", config["MONGODB_PASSWORD"])

    def test_k8s_instructions_disable_authentication(self) -> None:
        with patch.object(fmt, "echo_info") as echo_info:
            k8s_upgrade.upgrade_mongodb(self.config(), "8.0.4", "8.0")
        message = echo_info.call_args[0][0]
        self.assertIn(
            "tutor config save --set DOCKER_IMAGE_MONGODB=mongo:8.0.4"
            " --set MONGODB_PASSWORD=\n",
            message,
        )
        self.assertIn(
            "tutor config save --unset DOCKER_IMAGE_MONGODB --unset MONGODB_PASSWORD\n",
            message,
        )

    def test_k8s_instructions_without_authentication(self) -> None:
        with patch.object(fmt, "echo_info") as echo_info:
            k8s_upgrade.upgrade_mongodb(self.config("", ""), "8.0.4", "8.0")
        message = echo_info.call_args[0][0]
        self.assertIn(
            "tutor config save --set DOCKER_IMAGE_MONGODB=mongo:8.0.4\n", message
        )
        self.assertIn("tutor config save --unset DOCKER_IMAGE_MONGODB\n", message)
        self.assertNotIn("MONGODB_PASSWORD", message)

    def test_k8s_instructions_restore_authentication(self) -> None:
        with patch.object(fmt, "echo_info") as echo_info:
            k8s_upgrade.upgrade_mongodb(self.config(), "8.0.4", "8.0")
        commands = [
            shlex.split(line.strip())[1:]
            for line in echo_info.call_args[0][0].splitlines()
            if line.strip().startswith("tutor config save")
        ]
        self.assertEqual(2, len(commands))
        with temporary_root() as root:
            self.assertEqual(0, self.invoke_in_root(root, ["config", "save"]).exit_code)
            password = tutor_config.load_full(root)["MONGODB_PASSWORD"]

            # During the upgrade: no credentials
            result = self.invoke_in_root(root, commands[0])
            self.assertEqual(0, result.exit_code, result.output)
            config = tutor_config.load_full(root)
            self.assertEqual("mongo:8.0.4", config["DOCKER_IMAGE_MONGODB"])
            self.assertEqual("", config["MONGODB_USERNAME"])
            self.assertEqual("", config["MONGODB_PASSWORD"])

            # After the upgrade: the original credentials are back
            result = self.invoke_in_root(root, commands[1])
            self.assertEqual(0, result.exit_code, result.output)
            config = tutor_config.load_full(root)
            self.assertNotEqual("mongo:8.0.4", config["DOCKER_IMAGE_MONGODB"])
            self.assertEqual("openedx", config["MONGODB_USERNAME"])
            self.assertEqual(password, config["MONGODB_PASSWORD"])
