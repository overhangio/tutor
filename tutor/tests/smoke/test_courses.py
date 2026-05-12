"""Course API tests: list courses, verify demo course, create a new course in Studio."""

from __future__ import annotations

import urllib.parse

import pytest
import requests

from .conftest import HTTP_TIMEOUT, TEST_COURSE_ID

_SMOKE_ORG = "TutorSmokeOrg"
_SMOKE_NUMBER = "SMOKE101"
_SMOKE_RUN = "smoke"
_SMOKE_COURSE_ID = f"course-v1:{_SMOKE_ORG}+{_SMOKE_NUMBER}+{_SMOKE_RUN}"


class TestCoursesAPI:
    def test_course_list_unauthenticated(
        self, http_session: requests.Session, lms_url: str
    ) -> None:
        resp = http_session.get(
            f"{lms_url}/api/courses/v1/courses/", timeout=HTTP_TIMEOUT
        )
        assert resp.status_code == 200, f"Course list returned HTTP {resp.status_code}"
        data = resp.json()
        assert "results" in data

    def test_course_list_authenticated(
        self, auth_session: requests.Session, lms_url: str
    ) -> None:
        resp = auth_session.get(
            f"{lms_url}/api/courses/v1/courses/", timeout=HTTP_TIMEOUT
        )
        assert resp.status_code == 200
        assert "results" in resp.json()

    def test_course_list_pagination(
        self, http_session: requests.Session, lms_url: str
    ) -> None:
        resp = http_session.get(
            f"{lms_url}/api/courses/v1/courses/",
            params={"page_size": 1},
            timeout=HTTP_TIMEOUT,
        )
        assert resp.status_code == 200
        data = resp.json()
        pagination = data.get("pagination", data)
        assert "count" in pagination or "num_pages" in pagination


class TestDemoCourse:
    def test_demo_course_exists(
        self, auth_session: requests.Session, lms_url: str
    ) -> None:
        """
        Verify the demo course is present on the platform.
        Skipped if the course has not been imported yet — run
        `tutor local do importdemocourse` to import it.
        """
        if not TEST_COURSE_ID:
            pytest.skip("TEST_COURSE_ID not set.")
        encoded = urllib.parse.quote(TEST_COURSE_ID, safe="")
        resp = auth_session.get(
            f"{lms_url}/api/courses/v1/courses/{encoded}/", timeout=HTTP_TIMEOUT
        )
        if resp.status_code == 404:
            pytest.skip(
                f"Demo course '{TEST_COURSE_ID}' not found. "
                "Run `tutor local do importdemocourse` to import it first."
            )
        assert resp.status_code == 200, (
            f"Demo course detail returned HTTP {resp.status_code}: {resp.text[:300]}"
        )

    def test_demo_course_has_required_fields(
        self, auth_session: requests.Session, lms_url: str
    ) -> None:
        if not TEST_COURSE_ID:
            pytest.skip("TEST_COURSE_ID not set.")
        encoded = urllib.parse.quote(TEST_COURSE_ID, safe="")
        resp = auth_session.get(
            f"{lms_url}/api/courses/v1/courses/{encoded}/", timeout=HTTP_TIMEOUT
        )
        if resp.status_code == 404:
            pytest.skip(f"Demo course '{TEST_COURSE_ID}' not imported yet.")
        assert resp.status_code == 200
        data = resp.json()
        for field in ("id", "name", "org", "number", "start"):
            assert field in data, (
                f"Demo course response missing field '{field}': {data}"
            )


class TestCreateCourse:
    def test_create_course_in_studio(
        self, auth_session: requests.Session, cms_url: str
    ) -> None:
        """
        Create a course via the Studio REST API.
        Skipped if the course already exists so the test is safe to re-run.
        """
        check = auth_session.get(
            f"{cms_url}/api/v1/course_runs/{_SMOKE_COURSE_ID}/",
            timeout=HTTP_TIMEOUT,
        )
        if check.status_code == 200:
            pytest.skip(f"Course '{_SMOKE_COURSE_ID}' already exists")

        resp = auth_session.post(
            f"{cms_url}/api/v1/course_runs/",
            json={
                "title": "Tutor Smoke Test Course",
                "org": _SMOKE_ORG,
                "number": _SMOKE_NUMBER,
                "run": _SMOKE_RUN,
            },
            timeout=HTTP_TIMEOUT,
        )
        assert resp.status_code in (200, 201), (
            f"Course creation failed: HTTP {resp.status_code} — {resp.text[:500]}"
        )

    def test_created_course_is_listed(
        self, auth_session: requests.Session, cms_url: str
    ) -> None:
        """After creation (or if already present) the course must appear in the Studio list."""
        resp = auth_session.get(
            f"{cms_url}/api/v1/course_runs/{_SMOKE_COURSE_ID}/",
            timeout=HTTP_TIMEOUT,
        )
        assert resp.status_code == 200, (
            f"Course '{_SMOKE_COURSE_ID}' not found in Studio: HTTP {resp.status_code}"
        )
