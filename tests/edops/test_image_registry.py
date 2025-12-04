"""Tests for image registry functionality."""
from pathlib import Path
from tempfile import TemporaryDirectory

from tutor.edops.image_registry import DeployHistory, DeployRecord


def test_deploy_history_add_record():
    """Test adding records to deploy history."""
    with TemporaryDirectory() as tmpdir:
        history_file = Path(tmpdir) / "deploy-history.yml"
        history = DeployHistory(history_file)

        # Add a record
        history.add_record(
            module="common",
            service="ly-ac-gateway-svc",
            image="ly-ac-gateway-svc",
            tag="v1.0.0",
            operation="deploy",
        )

        assert len(history.records) == 1
        assert history.records[0].module == "common"
        assert history.records[0].tag == "v1.0.0"


def test_deploy_history_persistence():
    """Test that history is persisted to disk."""
    with TemporaryDirectory() as tmpdir:
        history_file = Path(tmpdir) / "deploy-history.yml"

        # Create and add record
        history1 = DeployHistory(history_file)
        history1.add_record(
            module="base",
            service="zhjx-nacos",
            image="nacos-server",
            tag="2.0.2",
            operation="deploy",
        )

        # Load in new instance
        history2 = DeployHistory(history_file)
        assert len(history2.records) == 1
        assert history2.records[0].service == "zhjx-nacos"


def test_get_module_history():
    """Test filtering history by module."""
    with TemporaryDirectory() as tmpdir:
        history_file = Path(tmpdir) / "deploy-history.yml"
        history = DeployHistory(history_file)

        history.add_record("base", "svc1", "img1", "v1", "deploy")
        history.add_record("common", "svc2", "img2", "v1", "deploy")
        history.add_record("base", "svc3", "img3", "v2", "deploy")

        base_history = history.get_module_history("base")
        assert len(base_history) == 2
        assert all(r.module == "base" for r in base_history)


def test_get_last_deployment():
    """Test getting the last deployment for a module."""
    with TemporaryDirectory() as tmpdir:
        history_file = Path(tmpdir) / "deploy-history.yml"
        history = DeployHistory(history_file)

        history.add_record("common", "svc1", "img1", "v1.0", "deploy")
        history.add_record("common", "svc1", "img1", "v1.1", "deploy")
        history.add_record("common", "svc1", "img1", "v1.2", "deploy")

        last = history.get_last_deployment("common")
        assert last is not None
        assert last.tag == "v1.2"


def test_registry_client_initialization():
    """Test registry client can be initialized."""
    from tutor.edops.image_registry import RegistryClient

    client = RegistryClient(
        registry="example.com",
        username="user",
        password="pass",
    )

    assert client.registry == "example.com"
    assert client.username == "user"

