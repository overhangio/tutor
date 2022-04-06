# Changelog (nightly branch)

Note: Breaking changes between versions are indicated by "💥".

- [Improvement] For Tutor Nightly (and only Nightly), official plugins are now installed from their nightly branches on GitHub instead of a version range on PyPI. This will allow Nightly users to install all official plugins by running ``pip install -e ".[full]"``.
- [Bugfix] Remove edX references from bulk emails ([issue](https://github.com/openedx/build-test-release-wg/issues/100)).
- [Bugfix] Update ``celery`` invocations for lms-worker and cms-worker to be compatible with Celery 5 CLI.
- [Improvement] Point CMS at its config file using ``CMS_CFG`` environment variable instead of deprecated ``STUDIO_CFG``.
- [Bugfix] Start MongoDB when running migrations, because a new data migration fails if MongoDB is not running
