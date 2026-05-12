from __future__ import annotations

import base64
import os

import pytest
import requests

# ---------------------------------------------------------------------------
# Module-level config resolved from env vars set by `tutor local/dev/k8s tests`
# ---------------------------------------------------------------------------

_HTTPS: bool = os.environ.get("ENABLE_HTTPS", "").lower() in ("1", "true", "yes")
_SCHEME: str = "https" if _HTTPS else "http"

LMS_HOST: str = os.environ.get("LMS_HOST", "local.openedx.io").strip()
CMS_HOST: str = os.environ.get("CMS_HOST", f"studio.{LMS_HOST}").strip()
LMS_BASE_URL: str = f"{_SCHEME}://{LMS_HOST}"
CMS_BASE_URL: str = f"{_SCHEME}://{CMS_HOST}"

OAUTH2_CLIENT_ID: str = os.environ.get("OAUTH2_CLIENT_ID", "").strip()
OAUTH2_CLIENT_SECRET: str = os.environ.get("OAUTH2_CLIENT_SECRET", "").strip()
TEST_USERNAME: str = os.environ.get("TEST_USERNAME", "admin").strip()
TEST_PASSWORD: str = os.environ.get("TEST_PASSWORD", "").strip()
TEST_EMAIL: str = os.environ.get("TEST_EMAIL", "").strip()
TEST_COURSE_ID: str = os.environ.get(
    "TEST_COURSE_ID", "course-v1:OpenedX+DemoX+DemoCourse"
).strip()

HTTP_TIMEOUT: tuple[int, int] = (10, 30)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def lms_url() -> str:
    return LMS_BASE_URL


@pytest.fixture(scope="session")
def cms_url() -> str:
    return CMS_BASE_URL


@pytest.fixture(scope="session")
def http_session() -> requests.Session:
    session = requests.Session()
    session.verify = _HTTPS
    return session


@pytest.fixture(scope="session")
def jwt_token(http_session: requests.Session) -> str:
    if OAUTH2_CLIENT_ID and OAUTH2_CLIENT_SECRET:
        return _jwt_via_client_credentials(http_session)
    if TEST_USERNAME and TEST_PASSWORD:
        return _jwt_via_password_grant(http_session)
    pytest.skip(
        "No auth credentials available. "
        "Set OAUTH2_CLIENT_ID+OAUTH2_CLIENT_SECRET or TEST_USERNAME+TEST_PASSWORD."
    )


@pytest.fixture(scope="session")
def auth_session(http_session: requests.Session, jwt_token: str) -> requests.Session:
    session = requests.Session()
    session.verify = _HTTPS
    session.headers["Authorization"] = f"JWT {jwt_token}"
    return session


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------


def _jwt_via_client_credentials(session: requests.Session) -> str:
    encoded = base64.b64encode(
        f"{OAUTH2_CLIENT_ID}:{OAUTH2_CLIENT_SECRET}".encode()
    ).decode()
    resp = session.post(
        f"{LMS_BASE_URL}/oauth2/access_token",
        headers={"Authorization": f"Basic {encoded}", "Cache-Control": "no-cache"},
        data={"grant_type": "client_credentials", "token_type": "jwt"},
        timeout=HTTP_TIMEOUT,
    )
    assert resp.status_code == 200, (
        f"client_credentials grant failed: HTTP {resp.status_code} — {resp.text[:300]}"
    )
    token: str = resp.json().get("access_token")
    assert token, f"No access_token in response: {resp.json()}"
    return token


def _jwt_via_password_grant(session: requests.Session) -> str:
    client_id = OAUTH2_CLIENT_ID or "login-service-client-id"
    resp = session.post(
        f"{LMS_BASE_URL}/oauth2/access_token",
        data={
            "client_id": client_id,
            "grant_type": "password",
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
            "token_type": "JWT",
        },
        timeout=HTTP_TIMEOUT,
    )
    assert resp.status_code == 200, (
        f"password grant failed: HTTP {resp.status_code} — {resp.text[:300]}"
    )
    token: str = resp.json().get("access_token")
    assert token, f"No access_token in response: {resp.json()}"
    return token
