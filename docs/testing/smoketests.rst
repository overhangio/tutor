.. _testing:

======================
Platform Testing
======================

Tutor includes a pluggable testing system that lets you verify a running Open edX platform. Core test suites are built in, and plugins can register their own test files without any changes to Tutor itself.

Running tests
-------------

The ``tests`` sub-command is available under each deployment mode::

    tutor local do tests
    tutor dev do tests
    tutor k8s do tests

Pass a suite name to run only tests belonging to that suite::

    tutor local do tests smoke

Providing credentials
~~~~~~~~~~~~~~~~~~~~~

Tests that exercise authenticated API endpoints require credentials. The recommended approach is an env file:

.. code-block:: yaml

    # tests-env.yaml
    TEST_USERNAME: admin
    TEST_EMAIL: admin@example.com
    TEST_PASSWORD: "yourpassword"
    OAUTH2_CLIENT_ID: tutor-tests
    OAUTH2_CLIENT_SECRET: "yoursecret"
    TEST_COURSE_ID: course-v1:OpenedX+DemoX+DemoCourse

Then run::

    tutor local do tests --env-file tests-env.yaml --setup smoke

The ``--setup`` flag creates (or updates) the test admin user and OAuth2 client before the test run. Setup is idempotent — re-running it is safe.

For CI or headless environments, pass credentials inline without a file::

    tutor local do tests \
      -e TEST_PASSWORD="$SECRET" \
      -e OAUTH2_CLIENT_SECRET="$OAUTH_SECRET" \
      --setup --non-interactive smoke

CLI reference
~~~~~~~~~~~~~

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Option
     - Description
   * - ``[SUITE]``
     - Suite name to run (e.g. ``smoke``). Omit to run all registered tests.
   * - ``--limit PLUGIN``
     - Run only tests registered by the named plugin or service context (e.g. ``lms``, ``cms``, ``myplugin``).
   * - ``--env-file FILE``
     - Path to a YAML file of ``KEY: value`` pairs passed as environment variables to the test process. Plugins document their own required keys.
   * - ``-e KEY=VALUE``
     - Set a single test environment variable. Can be repeated. Overrides ``--env-file`` values.
   * - ``--setup / --no-setup``
     - Create the test admin user and OAuth2 client before running tests. Requires ``TEST_USERNAME``, ``TEST_EMAIL``, ``TEST_PASSWORD``, ``OAUTH2_CLIENT_ID``, and ``OAUTH2_CLIENT_SECRET`` in the merged env. Default: ``--no-setup``.
   * - ``--cleanup / --no-cleanup``
     - Delete smoke test artifacts from the database after the run. Use ``--no-cleanup`` to inspect state after a failure. Default: ``--cleanup``.
   * - ``-I, --non-interactive``
     - Skip confirmation prompts. Required for CI/headless scripts.
   * - ``-s, --service``
     - Service container to run test setup in (default: ``lms``).

Environment variables
~~~~~~~~~~~~~~~~~~~~~

Tutor automatically sets ``LMS_HOST``, ``CMS_HOST``, and ``ENABLE_HTTPS`` from your Tutor config — these always reflect the running platform and cannot be overridden via ``--env-file`` or ``-e``. The following variables have defaults that can be overridden:

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - Variable
     - Default
     - Description
   * - ``TEST_USERNAME``
     - ``admin``
     - Admin username for authenticated tests.
   * - ``TEST_EMAIL``
     - ``admin@example.com``
     - Admin email address.
   * - ``TEST_PASSWORD``
     - *(auto-generated)*
     - Admin password. Auto-generated if not provided — Tutor will print the
       value and ask you to save it.
   * - ``OAUTH2_CLIENT_ID``
     - ``tutor-tests``
     - OAuth2 client ID for JWT token acquisition.
   * - ``OAUTH2_CLIENT_SECRET``
     - *(auto-generated)*
     - OAuth2 client secret. Auto-generated if not provided — Tutor will print
       the value and ask you to save it.
   * - ``TEST_COURSE_ID``
     - ``course-v1:OpenedX+DemoX+DemoCourse``
     - Course ID used in enrollment and content tests.
   * - ``SMOKE_USERNAME``
     - ``tutor_smoke_user``
     - Username of the transient user created by the smoke tests.
   * - ``SMOKE_COURSE_ID``
     - ``course-v1:TutorSmokeOrg+SMOKE101+smoke``
     - Course ID of the transient course created by the smoke tests.

Built-in test suites
--------------------

Tutor ships with a ``smoke`` suite that verifies a freshly deployed platform:

* **LMS & CMS accessibility** — homepage, login/register pages, heartbeat endpoints.
* **OAuth2 authentication** — token endpoint, JWT issuance, invalid-credential rejection.
* **User API** — ``/api/user/v1/me``, account lookup, user registration.
* **Enrollment API** — enrollment listing, enrollment modes, user enrollment.
* **Courses API** — course listing (authenticated & unauthenticated), pagination, demo course verification, course creation in Studio.

LMS-focused tests run under the ``lms`` context; Studio/course tests run under the ``cms`` context::

    tutor local do tests smoke --limit=lms
    tutor local do tests smoke --limit=cms

After the suite finishes, the transient user and course created during the run are deleted from the database. Pass ``--no-cleanup`` to skip this step and inspect the database state manually.

Adding tests from a plugin
--------------------------

Plugins register test paths via the ``TESTS`` filter. Each entry is a ``(suite, path)`` tuple where ``suite`` is a string (e.g. ``"smoke"``) and ``path`` is an absolute filesystem path to a pytest file or directory.

.. code-block:: python

    # tutormyplugin/plugin.py
    import importlib.resources as _pkg
    from tutor import hooks

    hooks.Filters.TESTS.add_item(
        ("smoke", str(_pkg.files("tutormyplugin") / "tests" / "smoke")),
    )

Because hooks registered at the plugin module level are automatically tagged with the plugin's own context, the tests above will be selected when the user passes ``--limit=myplugin``.

To limit tests to a specific service context (e.g. only when testing the CMS), wrap the registration::

    with hooks.Contexts.app("cms").enter():
        hooks.Filters.TESTS.add_item(
            ("smoke", str(_pkg.files("tutormyplugin") / "tests" / "smoke" / "test_cms.py")),
        )

Writing plugin tests
--------------------

Plugin tests are ordinary pytest files. Because they run as a host-side process (not inside a container), they must be self-contained: define their own fixtures and read all configuration from environment variables.

A minimal example:

.. code-block:: python

    # tutormyplugin/tests/smoke/test_myplugin.py
    import os
    import pytest
    import requests

    _HTTPS = os.environ.get("ENABLE_HTTPS", "").lower() in ("1", "true", "yes")
    _SCHEME = "https" if _HTTPS else "http"
    LMS_HOST = os.environ.get("LMS_HOST", "local.openedx.io")
    LMS_BASE_URL = f"{_SCHEME}://{LMS_HOST}"
    TEST_PASSWORD = os.environ.get("TEST_PASSWORD", "")
    HTTP_TIMEOUT = (10, 30)


    @pytest.fixture(scope="session")
    def http_session() -> requests.Session:
        session = requests.Session()
        session.verify = _HTTPS
        return session


    class TestMypluginHealth:
        def test_heartbeat(self, http_session: requests.Session) -> None:
            resp = http_session.get(f"{LMS_BASE_URL}/heartbeat", timeout=HTTP_TIMEOUT)
            assert resp.status_code == 200

Plugin-specific environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your tests need additional configuration (API keys, feature flags, etc.), define them as custom environment variables and document them in your plugin's README. Users add them to their env file::

    # tests-env.yaml
    MYPLUGIN_API_KEY: my-api-key
    MYPLUGIN_FEATURE_FLAG: "true"

Read them in your tests the same way as the built-in vars::

    MYPLUGIN_API_KEY = os.environ.get("MYPLUGIN_API_KEY", "")

Best practices for idempotent tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests run against a live platform, so they must be safe to run repeatedly without corrupting state.

**Skip, don't fail, when a resource already exists.**
Before creating a test artifact, check whether it exists and call ``pytest.skip()`` if it does:

.. code-block:: python

    def test_create_widget(self, auth_session, lms_url):
        check = auth_session.get(f"{lms_url}/api/widgets/MY_SMOKE_WIDGET/")
        if check.status_code == 200:
            pytest.skip("Smoke widget already exists")
        resp = auth_session.post(f"{lms_url}/api/widgets/", json={"id": "MY_SMOKE_WIDGET"})
        assert resp.status_code == 201

**Use constant, predictable artifact names.**
Hard-code the names of any users, courses, or objects your tests create (e.g. ``myplugin_smoke_user``). This makes cleanup deterministic and prevents test runs from leaving behind an unbounded number of artifacts.

**Skip authenticated tests when no credentials are provided.**
Guard test classes or fixtures that need authentication:

.. code-block:: python

    @pytest.fixture(scope="session")
    def auth_session(http_session):
        if not os.environ.get("TEST_PASSWORD"):
            pytest.skip("No credentials — skipping authenticated tests.")
        # ... obtain token and return authenticated session

**Do not rely on pytest fixture teardown for hard cleanup.**
Open edX usually does not hard-delete resources via its REST API (users are deactivated, not removed). Cleanup that requires Django management commands must be done outside of pytest.