.. _smoketests:

===================
Smoke Tests
===================

Tutor includes a pluggable smoke test system that lets you verify a running Open edX platform and allows plugins to contribute their own tests.

Running smoke tests
-------------------

The ``tests`` sub-command is available under each deployment mode::

    tutor local tests smoke
    tutor dev tests smoke
    tutor k8s tests smoke

This collects all pytest test paths registered under the ``smoke`` suite and runs them against your live platform. By default the tests only check unauthenticated endpoints. To exercise authenticated APIs as well, provide credentials::

    tutor local tests smoke \
        --admin-password=yourpassword \
        --oauth-client-secret=yoursecret

When ``--admin-password`` is supplied, Tutor automatically creates (or ensures the existence of) a test admin user and an OAuth2 client before the tests run. All setup is idempotent — running the command twice is safe.

CLI options
~~~~~~~~~~~

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Option
     - Description
   * - ``[SUITE]``
     - Suite name to run (default: all suites). Currently ``smoke`` is the only built-in suite.
   * - ``--limit PLUGIN``
     - Run only tests registered by the named plugin or service context (e.g. ``lms``, ``cms``, ``myplugin``).
   * - ``--admin-username``
     - Username for the test admin account (default: ``admin``).
   * - ``--admin-email``
     - Email for the test admin account (default: ``admin@example.com``).
   * - ``--admin-password``
     - Password for the test admin account. When provided, the account and OAuth2 client are created/updated before tests run.
   * - ``--oauth-client-id``
     - OAuth2 client ID used by the test suite (default: ``tutor-tests``).
   * - ``--oauth-client-secret``
     - OAuth2 client secret. Required for authenticated API tests.
   * - ``--course-id``
     - Demo course ID used in enrollment tests (default: ``course-v1:OpenedX+DemoX+DemoCourse``).

Examples
~~~~~~~~

Run only unauthenticated health checks::

    tutor local tests smoke

Run the full suite with credentials::

    tutor local tests smoke \
        --admin-password=s3cr3t \
        --oauth-client-secret=oauth_s3cr3t

Run only the tests contributed by the ``cms`` context::

    tutor local tests smoke --limit=cms

Run only the tests contributed by a plugin named ``myplugin``::

    tutor local tests smoke --limit=myplugin

Built-in test suites
--------------------

Tutor registers the following test files under the ``smoke`` suite:

* **LMS & CMS accessibility** — homepage, login/register pages, heartbeat endpoints.
* **OAuth2 authentication** — token endpoint, JWT issuance, invalid-credential rejection.
* **User API** — ``/api/user/v1/me``, ``/api/user/v1/accounts``, user creation (idempotent).
* **Enrollment API** — enrollment listing, enrollment modes, user enrollment (idempotent).
* **Courses API** — course listing (authenticated & unauthenticated), pagination, demo course verification, course creation in Studio (idempotent).

LMS-focused tests are registered under the ``lms`` context; Studio/course-management tests are registered under the ``cms`` context. Use ``--limit=lms`` or ``--limit=cms`` to run each group independently.

Adding tests from a plugin
--------------------------

Plugins register test paths via the ``TESTS`` filter. Each item is a ``(suite, path)`` tuple where ``suite`` is a string (e.g. ``"smoke"``) and ``path`` is an absolute filesystem path to a pytest file or directory.

.. code-block:: python

    # tutormyplugin/plugin.py
    import importlib.resources as _pkg
    from tutor import hooks

    hooks.Filters.TESTS.add_item(
        ("smoke", str(_pkg.files("tutormyplugin") / "tests" / "smoke")),
    )

Because hooks registered at the plugin module level are automatically tagged with the plugin's own context, the tests above will be selected when the user passes ``--limit=myplugin``.

Limiting tests to a service context
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your plugin tests are only meaningful against a specific service (e.g. the CMS), wrap the registration in the appropriate context::

    with hooks.Contexts.app("cms").enter():
        hooks.Filters.TESTS.add_items([
            ("smoke", str(_pkg.files("tutormyplugin") / "tests" / "smoke" / "test_cms.py")),
        ])

Writing plugin tests
--------------------

Plugin tests are ordinary pytest files. They receive the platform coordinates via environment variables set by the ``tests`` command:

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Variable
     - Description
   * - ``LMS_HOST``
     - Hostname of the LMS (e.g. ``local.openedx.io``).
   * - ``CMS_HOST``
     - Hostname of Studio.
   * - ``ENABLE_HTTPS``
     - ``"true"`` or ``"false"``.
   * - ``TEST_USERNAME``
     - Admin username passed via ``--admin-username``.
   * - ``TEST_PASSWORD``
     - Admin password passed via ``--admin-password``.
   * - ``OAUTH2_CLIENT_ID``
     - OAuth2 client ID passed via ``--oauth-client-id``.
   * - ``OAUTH2_CLIENT_SECRET``
     - OAuth2 client secret passed via ``--oauth-client-secret``.
   * - ``TEST_EMAIL``
     - Admin email passed via ``--admin-email``.
   * - ``TEST_COURSE_ID``
     - Demo course ID passed via ``--course-id``.

Because plugin tests run in an isolated pytest invocation (not inside a container), they must be self-contained: define their own fixtures and read configuration from the environment variables above rather than importing from Tutor internals.

A minimal example:

.. code-block:: python

    # tutormyplugin/tests/smoke/test_myplugin.py
    import os
    import requests
    import pytest

    _HTTPS = os.environ.get("ENABLE_HTTPS", "").lower() in ("1", "true", "yes")
    _SCHEME = "https" if _HTTPS else "http"
    LMS_BASE_URL = f"{_SCHEME}://{os.environ.get('LMS_HOST', 'local.openedx.io')}"
    HTTP_TIMEOUT = (10, 30)


    @pytest.fixture(scope="session")
    def http_session():
        session = requests.Session()
        session.verify = _HTTPS
        return session


    class TestMypluginPlatformHealth:
        def test_lms_reachable(self, http_session):
            resp = http_session.get(f"{LMS_BASE_URL}/", timeout=HTTP_TIMEOUT, allow_redirects=True)
            assert resp.status_code == 200

        def test_heartbeat(self, http_session):
            resp = http_session.get(f"{LMS_BASE_URL}/heartbeat", timeout=HTTP_TIMEOUT)
            assert resp.status_code == 200

Use ``pytest.skip()`` for tests that depend on resources that may not exist yet — for example, skipping enrollment tests when no credentials are provided::

    if not TEST_PASSWORD:
        pytest.skip("No credentials set — skipping authenticated tests.")
