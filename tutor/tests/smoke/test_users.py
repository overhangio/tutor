"""User API tests: read existing users and create a new test user."""

from __future__ import annotations

import pytest
import requests

from .conftest import HTTP_TIMEOUT, TEST_USERNAME

_SMOKE_USERNAME = "tutor_smoke_user"
_SMOKE_EMAIL = "tutor_smoke_user@example.com"
_SMOKE_PASSWORD = "SmokeTest@123!"


class TestUserAPI:
    def test_me_endpoint(self, auth_session: requests.Session, lms_url: str) -> None:
        resp = auth_session.get(f"{lms_url}/api/user/v1/me", timeout=HTTP_TIMEOUT)
        assert resp.status_code == 200, (
            f"/api/user/v1/me returned HTTP {resp.status_code}: {resp.text[:300]}"
        )
        assert "username" in resp.json()

    def test_account_endpoint(self, auth_session: requests.Session, lms_url: str) -> None:
        if not TEST_USERNAME:
            pytest.skip("TEST_USERNAME not set.")
        resp = auth_session.get(
            f"{lms_url}/api/user/v1/accounts/{TEST_USERNAME}", timeout=HTTP_TIMEOUT
        )
        assert resp.status_code == 200, (
            f"/api/user/v1/accounts/{TEST_USERNAME} returned HTTP {resp.status_code}"
        )
        assert resp.json().get("username") == TEST_USERNAME

    def test_registration_validation_endpoint(
        self, http_session: requests.Session, lms_url: str
    ) -> None:
        resp = http_session.post(
            f"{lms_url}/api/user/v1/validation/registration",
            json={"email": "not-an-email"},
            timeout=HTTP_TIMEOUT,
        )
        assert resp.status_code in (200, 400, 403)


class TestCreateUser:
    def test_create_new_user(
        self, auth_session: requests.Session, http_session: requests.Session, lms_url: str
    ) -> None:
        """
        Register a new user via the public registration API.
        Skipped if the user already exists so the test is safe to re-run.
        """
        check = auth_session.get(
            f"{lms_url}/api/user/v1/accounts/{_SMOKE_USERNAME}", timeout=HTTP_TIMEOUT
        )
        if check.status_code == 200:
            pytest.skip(f"User '{_SMOKE_USERNAME}' already exists")

        resp = http_session.post(
            f"{lms_url}/api/user/v2/account/registration/",
            data={
                "username": _SMOKE_USERNAME,
                "email": _SMOKE_EMAIL,
                "password": _SMOKE_PASSWORD,
                "name": "Tutor Smoke User",
                "terms_of_service": "true",
                "honor_code": "true",
            },
            timeout=HTTP_TIMEOUT,
        )
        assert resp.status_code == 200, (
            f"User registration failed: HTTP {resp.status_code} — {resp.text[:300]}"
        )

    def test_created_user_is_reachable(
        self, auth_session: requests.Session, lms_url: str
    ) -> None:
        """After creation (or if already present) the account endpoint must return 200."""
        resp = auth_session.get(
            f"{lms_url}/api/user/v1/accounts/{_SMOKE_USERNAME}", timeout=HTTP_TIMEOUT
        )
        assert resp.status_code == 200, (
            f"Could not fetch account for '{_SMOKE_USERNAME}': HTTP {resp.status_code}"
        )
