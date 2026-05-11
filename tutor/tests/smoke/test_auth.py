"""OAuth2 token endpoint and JWT verification."""

from __future__ import annotations

import base64

import requests

from .conftest import HTTP_TIMEOUT, OAUTH2_CLIENT_ID, OAUTH2_CLIENT_SECRET


class TestOAuth2:
    def test_token_endpoint_exists(self, http_session: requests.Session, lms_url: str) -> None:
        """POST with no credentials should return 400/401, not 404."""
        resp = http_session.post(
            f"{lms_url}/oauth2/access_token",
            data={"grant_type": "client_credentials"},
            timeout=HTTP_TIMEOUT,
        )
        assert resp.status_code in (400, 401), (
            f"/oauth2/access_token returned unexpected HTTP {resp.status_code}"
        )

    def test_jwt_token_obtained(self, jwt_token: str) -> None:
        assert isinstance(jwt_token, str) and len(jwt_token) > 20
        assert len(jwt_token.split(".")) == 3, "Token does not look like a JWT"

    def test_invalid_credentials_rejected(
        self, http_session: requests.Session, lms_url: str
    ) -> None:
        bad = base64.b64encode(b"bad_id:bad_secret").decode()
        resp = http_session.post(
            f"{lms_url}/oauth2/access_token",
            headers={"Authorization": f"Basic {bad}"},
            data={"grant_type": "client_credentials", "token_type": "jwt"},
            timeout=HTTP_TIMEOUT,
        )
        assert resp.status_code in (400, 401), (
            f"Expected 400/401 for invalid credentials, got {resp.status_code}"
        )
