"""Tests for health check functionality."""
from tutor.edops.health import HealthCheckDef, HealthCheckType, HealthChecker


def test_health_check_def_creation():
    """Test creating a health check definition."""
    hc = HealthCheckDef(
        service="test-service",
        type=HealthCheckType.HTTP,
        url="http://localhost:8080/health",
        timeout=30,
    )

    assert hc.service == "test-service"
    assert hc.type == HealthCheckType.HTTP
    assert hc.url == "http://localhost:8080/health"
    assert hc.timeout == 30


def test_health_checker_creation():
    """Test creating a health checker."""
    checker = HealthChecker(verbose=True)
    assert checker.verbose is True

    checker2 = HealthChecker(verbose=False)
    assert checker2.verbose is False


def test_health_check_types():
    """Test that all health check types are defined."""
    assert hasattr(HealthCheckType, "HTTP")
    assert hasattr(HealthCheckType, "TCP")
    assert hasattr(HealthCheckType, "CONTAINER")

    assert HealthCheckType.HTTP.value == "http"
    assert HealthCheckType.TCP.value == "tcp"
    assert HealthCheckType.CONTAINER.value == "container"

