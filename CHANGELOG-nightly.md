# Changelog (nightly branch)

Note: Breaking changes between versions are indicated by "💥".

- [Bugfix] Remove edX references from bulk emails ([issue](https://github.com/openedx/build-test-release-wg/issues/100)).
- [Bugfix] Update ``celery`` invocations for lms-worker and cms-worker to be compatible with Celery 5 CLI.
- [Improvement] Point CMS at its config file using ``CMS_CFG`` environment variable instead of deprecated ``STUDIO_CFG``.
- [Bugfix] Start MongoDB when running migrations, because a new data migration fails if MongoDB is not running
