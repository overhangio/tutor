"""LMS and CMS basic accessibility and heartbeat checks."""

from __future__ import annotations

import requests

from .conftest import HTTP_TIMEOUT


class TestLMSAccessibility:
    def test_homepage(self, http_session: requests.Session, lms_url: str) -> None:
        resp = http_session.get(
            f"{lms_url}/", timeout=HTTP_TIMEOUT, allow_redirects=True
        )
        assert resp.status_code == 200, f"LMS homepage returned HTTP {resp.status_code}"
        assert len(resp.text) > 100, "LMS homepage body is suspiciously short"

    def test_login_page(self, http_session: requests.Session, lms_url: str) -> None:
        resp = http_session.get(
            f"{lms_url}/login", timeout=HTTP_TIMEOUT, allow_redirects=True
        )
        assert resp.status_code == 200, f"LMS /login returned HTTP {resp.status_code}"

    def test_register_page(self, http_session: requests.Session, lms_url: str) -> None:
        resp = http_session.get(
            f"{lms_url}/register", timeout=HTTP_TIMEOUT, allow_redirects=True
        )
        assert resp.status_code == 200, (
            f"LMS /register returned HTTP {resp.status_code}"
        )

    def test_heartbeat(self, http_session: requests.Session, lms_url: str) -> None:
        resp = http_session.get(f"{lms_url}/heartbeat", timeout=HTTP_TIMEOUT)
        assert resp.status_code == 200, (
            f"LMS /heartbeat returned HTTP {resp.status_code}. Body: {resp.text[:300]}"
        )
        assert isinstance(resp.json(), dict), (
            "Heartbeat response should be a JSON object"
        )


class TestCMSAccessibility:
    def test_homepage(self, http_session: requests.Session, cms_url: str) -> None:
        resp = http_session.get(
            f"{cms_url}/", timeout=HTTP_TIMEOUT, allow_redirects=True
        )
        assert resp.status_code == 200, f"CMS homepage returned HTTP {resp.status_code}"

    def test_signin_page(self, http_session: requests.Session, cms_url: str) -> None:
        resp = http_session.get(
            f"{cms_url}/signin", timeout=HTTP_TIMEOUT, allow_redirects=True
        )
        assert resp.status_code == 200, f"CMS /signin returned HTTP {resp.status_code}"

    def test_heartbeat(self, http_session: requests.Session, cms_url: str) -> None:
        resp = http_session.get(f"{cms_url}/heartbeat", timeout=HTTP_TIMEOUT)
        assert resp.status_code == 200, (
            f"CMS /heartbeat returned HTTP {resp.status_code}. Body: {resp.text[:300]}"
        )
