import unittest
from types import SimpleNamespace
from unittest.mock import patch

from tests.helpers import temporary_root
from tutor import config as tutor_config
from tutor import env, serialize
from tutor.commands import k8s
from tutor.types import Config

from .base import TestCommandMixin


def _job(name: str, active: int, owner_kind: str = "") -> SimpleNamespace:
    owners = [SimpleNamespace(kind=owner_kind)] if owner_kind else None
    return SimpleNamespace(
        metadata=SimpleNamespace(name=name, owner_references=owners),
        status=SimpleNamespace(active=active),
    )


def _config() -> Config:
    config: Config = {}
    tutor_config.update_with_base(config)
    tutor_config.update_with_defaults(config)
    tutor_config.render_full(config)
    return config


class K8sTests(unittest.TestCase, TestCommandMixin):
    def test_k8s_help(self) -> None:
        result = self.invoke(["k8s", "--help"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)

    def test_active_job_names_ignores_cronjob_jobs(self) -> None:
        jobs = [
            _job("lms-job-20261113", active=1),
            _job("cms-reindex-courses-29387", active=1, owner_kind="CronJob"),
            _job("cms-job-20261112", active=0),
        ]
        with temporary_root() as root:
            runner = k8s.K8sTaskRunner(root, _config())
            with patch.object(k8s.K8sClients, "instance") as clients:
                clients.return_value.batch_api.list_namespaced_job.return_value = (
                    SimpleNamespace(items=jobs)
                )
                self.assertEqual(["lms-job-20261113"], runner.active_job_names())

    def test_reindex_courses_cronjob(self) -> None:
        config = _config()
        self.assertNotIn(
            "k8s/cronjobs.yml", env.render_file(config, "kustomization.yml")
        )

        config["OPENEDX_REINDEX_COURSES_SCHEDULE"] = '0 1 * * * "quoted"'
        self.assertIn("k8s/cronjobs.yml", env.render_file(config, "kustomization.yml"))
        rendered = env.render_file(config, "k8s", "cronjobs.yml")
        assert isinstance(rendered, str)
        manifests = list(serialize.load_all(rendered))
        cronjobs = [m for m in manifests if m and m["kind"] == "CronJob"]
        self.assertEqual(1, len(cronjobs))
        self.assertEqual('0 1 * * * "quoted"', cronjobs[0]["spec"]["schedule"])

    def test_init_reindex_courses(self) -> None:
        config = _config()
        self.assertIn(
            "reindex_course --active",
            env.render_file(config, "jobs", "init", "cms.sh"),
        )
        config["OPENEDX_INIT_REINDEX_COURSES"] = False
        self.assertNotIn(
            "reindex_course --active",
            env.render_file(config, "jobs", "init", "cms.sh"),
        )
