# Changelog (nightly branch)

<!--
This changelog is for tracking changes made to the nightly branch (see:
https://docs.tutor.overhang.io/tutorials/nightly.html). The format of this file is identical
to the CHANGELOG.md file, except that there are no release or "Unrelased" sections. Entries
will be backported to the master branch at every major release.
When backporting changes to master, we should keep only the entries that correspond to user-
facing changes.
-->

- [Bugfix] Fix MongoDB replica set connection error resulting from edx-platform's pymongo (3.10.1 -> 3.12.3) upgrade ([edx-platform#30569](https://github.com/openedx/edx-platform/pull/30569)). (by @ormsbee)
- [Improvement] For Tutor Nightly (and only Nightly), official plugins are now installed from their nightly branches on GitHub instead of a version range on PyPI. This will allow Nightly users to install all official plugins by running ``pip install -e ".[full]"``.
- [Bugfix] Remove edX references from bulk emails ([issue](https://github.com/openedx/build-test-release-wg/issues/100)).
- [Bugfix] Update ``celery`` invocations for lms-worker and cms-worker to be compatible with Celery 5 CLI.
- [Improvement] Point CMS at its config file using ``CMS_CFG`` environment variable instead of deprecated ``STUDIO_CFG``.
- [Bugfix] Start MongoDB when running migrations, because a new data migration fails if MongoDB is not running

