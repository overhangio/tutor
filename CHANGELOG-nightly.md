# Changelog (nightly branch)

<!--
This changelog is for tracking changes made to the nightly branch (see:
https://docs.tutor.overhang.io/tutorials/nightly.html). The format of this file is identical
to the CHANGELOG.md file, except that there are no release or "Unrelased" sections. Entries
will be backported to the master branch at every major release.
When backporting changes to master, we should keep only the entries that correspond to user-
facing changes.
-->
- 💥[Feature] Add an extensible `local/dev/k8s do ...` command to trigger custom job commands. These commands are used to run a series of bash scripts in designated containers. Any plugin can add custom jobs thanks to the `CLI_DO_COMMANDS` filter. This causes the following breaking changes:
    - The "init", "createuser", "settheme", "importdemocourse" commands were all migrated to this new interface. For instance,  `tutor local init` was replaced by `tutor local do init`.
    - Plugin developers are encouraged to replace calls to the `COMMANDS_INIT` and `COMMANDS_PRE_INIT` filters by `CLI_DO_INIT_TASKS`.
- [Feature] Implement hook filter priorities, which work like action priorities. (by @regisb)
- 💥[Improvement] Remove the `local/dev bindmount` commands, which have been marked as deprecated for some time. The `--mount` option should be used instead.
- 💥[Bugfix] Fix local installation requirements. Plugins that implemented the "openedx-dockerfile-post-python-requirements" patch and that needed access to the edx-platform repo will no longer work. Instead, these plugins should implement the "openedx-dockerfile-pre-assets" patch. This scenario should be very rare, though. (by @regisb)
- 💥[Improvement] Rename the implementation of tutor <mode> quickstart to tutor <mode> launch. (by @Carlos-Muniz)
- 💥[Improvement] Remove the implementation of tutor dev runserver. (by @Carlos-Muniz)
- [Bugfix] Fix MongoDB replica set connection error resulting from edx-platform's pymongo (3.10.1 -> 3.12.3) upgrade ([edx-platform#30569](https://github.com/openedx/edx-platform/pull/30569)). (by @ormsbee)
- [Improvement] For Tutor Nightly (and only Nightly), official plugins are now installed from their nightly branches on GitHub instead of a version range on PyPI. This will allow Nightly users to install all official plugins by running ``pip install -e ".[full]"``.
- [Bugfix] Remove edX references from bulk emails ([issue](https://github.com/openedx/build-test-release-wg/issues/100)).
- [Bugfix] Update ``celery`` invocations for lms-worker and cms-worker to be compatible with Celery 5 CLI.
- [Improvement] Point CMS at its config file using ``CMS_CFG`` environment variable instead of deprecated ``STUDIO_CFG``.
- [Bugfix] Start MongoDB when running migrations, because a new data migration fails if MongoDB is not running

