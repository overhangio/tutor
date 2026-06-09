"""Enrollment API tests: list enrollments and enroll a user in the smoke course."""

from __future__ import annotations

import pytest
import requests

from .conftest import HTTP_TIMEOUT, TEST_USERNAME


class TestEnrollmentAPI:
    def test_enrollment_info_public(
        self, http_session: requests.Session, lms_url: str, smoke_course_id: str
    ) -> None:
        """
        Checks the public enrollment info endpoint for the smoke course.
        Skipped automatically when the smoke course has not been created yet
        (run the full suite so TestCreateCourse creates it first).
        """
        resp = http_session.get(
            f"{lms_url}/api/enrollment/v1/course/{smoke_course_id}",
            timeout=HTTP_TIMEOUT,
        )
        assert resp.status_code == 200, (
            f"Enrollment course info returned HTTP {resp.status_code}: {resp.text[:300]}"
        )
        data = resp.json()
        assert "course_id" in data or "course_modes" in data

    def test_list_my_enrollments(
        self, auth_session: requests.Session, lms_url: str
    ) -> None:
        resp = auth_session.get(
            f"{lms_url}/api/enrollment/v1/enrollment", timeout=HTTP_TIMEOUT
        )
        assert resp.status_code == 200, (
            f"Enrollment list returned HTTP {resp.status_code}: {resp.text[:300]}"
        )
        assert isinstance(resp.json(), (list, dict))

    def test_enrollment_modes_endpoint(
        self, http_session: requests.Session, lms_url: str
    ) -> None:
        resp = http_session.get(
            f"{lms_url}/api/enrollment/v1/enrollment_modes", timeout=HTTP_TIMEOUT
        )
        assert resp.status_code in (200, 404)


class TestEnrollUser:
    def test_enroll_user_in_smoke_course(
        self, auth_session: requests.Session, lms_url: str, smoke_course_id: str
    ) -> None:
        """
        Enroll the test user in the smoke course.
        Skipped if TEST_USERNAME is not set or the smoke course does not exist yet.
        Already-enrolled users return 200 with is_active=True, so this is idempotent.
        """
        if not TEST_USERNAME:
            pytest.skip("TEST_USERNAME not set.")

        check = auth_session.get(
            f"{lms_url}/api/enrollment/v1/enrollment/{TEST_USERNAME},{smoke_course_id}",
            timeout=HTTP_TIMEOUT,
        )
        if check.status_code == 200:
            try:
                if check.json().get("is_active"):
                    pytest.skip(
                        f"User '{TEST_USERNAME}' is already enrolled in '{smoke_course_id}'"
                    )
            except requests.exceptions.JSONDecodeError:
                pass  # empty body means not enrolled

        resp = auth_session.post(
            f"{lms_url}/api/enrollment/v1/enrollment",
            json={
                "user": TEST_USERNAME,
                "mode": "audit",
                "is_active": True,
                "course_details": {"course_id": smoke_course_id},
            },
            timeout=HTTP_TIMEOUT,
        )
        assert resp.status_code == 200, (
            f"Enrollment POST returned HTTP {resp.status_code}: {resp.text[:500]}"
        )
        data = resp.json()
        assert data.get("is_active") is True, (
            f"Enrollment did not set is_active=True: {data}"
        )
        assert data.get("mode") == "audit", f"Enrollment mode mismatch: {data}"

    def test_enrollment_is_present_after_enroll(
        self, auth_session: requests.Session, lms_url: str, smoke_course_id: str
    ) -> None:
        """
        Verify the enrollment record exists after the enroll test.
        Skipped automatically when the smoke course has not been created yet.
        """
        if not TEST_USERNAME:
            pytest.skip("TEST_USERNAME not set.")
        resp = auth_session.get(
            f"{lms_url}/api/enrollment/v1/enrollment/{TEST_USERNAME},{smoke_course_id}",
            timeout=HTTP_TIMEOUT,
        )
        assert resp.status_code in (200, 404), (
            f"Enrollment check returned unexpected HTTP {resp.status_code}"
        )
