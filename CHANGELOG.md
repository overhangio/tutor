# Changelog

This file includes a history of past releases. Changes that were not yet added to a release are in the [changelog.d/](./changelog.d) folder.

<!--
⚠️ DO NOT ADD YOUR CHANGES TO THIS FILE! (unless you want to modify existing changelog entries in this file)
Changelog entries are managed by scriv. After you have made some changes to Tutor, create a changelog entry with:

    make changelog-entry

Edit and commit the newly-created file in changelog.d.

If you need to create a new release, create a separate commit just for that. It is important to respect these
instructions, because git commits are used to generate release notes:
  - Collect changelog entries with `make changelog`
  - The title of the commit should be the same as the CHANGELOG.md file section title: "vX.Y.Z (year-month-day)".
  - The commit message should be copy-pasted from the release section.
  - Have a look at other release commits for reference.
-->

<!-- scriv-insert-here -->

<a id='changelog-16.1.5'></a>
## v16.1.5 (2023-10-30)

- [Bugfix] Fix ORA2 file uploads in CMS. As the cache settings are shared between CMS and LMS, the settings are moved from `common_lms.py` to `common_all.py`. (by @FatemeKhodayari)

<a id='changelog-16.1.4'></a>
## v16.1.4 (2023-10-13)

- [Improvement] No more large dev images. This was fixed by adding `--no-log-init` option to useradd command and reducing space usage of `/var/log/faillog`. (by @CodeWithEmad)
- [Improvement] Upgrade the Open edX default version to open-release/palm.3. (by @regisb)

<a id='changelog-16.1.3'></a>
## v16.1.3 (2023-10-10)

- [Improvement] Adds `connect=False` to the LMS and CMS' MongoDB connection to prevent `ServerSelectionError` after a cluster failover. (by @open-craft)
- [Bugfix] Override `CMS_BASE` setting in Studio for the development environment. Without this, parts of Studio will try to use the devstack default of localhost:8010 instead. (by @ormsbee)
- [Bugfix] Fix build error caused by py2neo package that was abruptly pulled from pypi and GitHub. (by @regisb)

<a id='changelog-16.1.2'></a>
## v16.1.2 (2023-10-02)

- [Bugfix] Render config settings that are inside lists. (by @regisb)
- [Bugfix] Correctly parse strings prefixed with pound "#" key in `tutor config save --set KEY=#value` commands. (by @regisb)
- [Feature] New action introduced: `CONFIG_LOADED`. This action is called whenever the config is loaded and makes it possible to verify the validity of configuration settings at runtime. (by @CodeWithEmad)
- [Bugfix] Fix file upload in open response assessments. (by @regisb)

<a id='changelog-16.1.1'></a>
## v16.1.1 (2023-08-29)

- 💥[Bugfix] Apply "fix mysql crash after upgrade to Palm" from 16.1.0 to `tutor k8s` deployments, as well. Users previously running `tutor k8s` with `RUN_MYSQL: true`, with any version between 16.0.0 and 16.1.0 including, might have to fix their data manually. For users running `tutor local`, this change has no effect, as the underlying issue was already fixed in 16.1.0. For users running `tutor k8s` with `RUN_MYSQL: false`, this change is also a no-op. (by @fghaas)

<a id='changelog-16.1.0'></a>
## v16.1.0 (2023-08-16)

- [Improvement] Improve support of legacy non-BuildKit mode: (by @regisb)
  - [Bugfix] Fix building of openedx Docker image.
  - [Improvement] Remove `--cache-from` build option.
  - [Improvement] Add a warning concerning the lack of support of the `--build-context` option.
- 💥[Bugfix] Fix mysql crash after upgrade to Palm. After an upgrade to Palm, the mysql client run by Django defaults to a utf8mb4 character set and collation, but the mysql server still runs with utf8mb3. This causes broken data during migration from Olive to Palm, and more generally when data is written to the database. To resolve this issue, we explicitely set the utf8mb3 charset and collation in the client. Users who were running Palm might have to fix their data manually. In the future we will upgrade the mysql server to utf8mb4. (by @regisb)
- [Improvement] We upgrade to MySQL 8.1.0 to avoid having to restart the server after the upgrade.
- [Bugfix] Ask whether user wants to run locally during `tutor local launch`. (by @regisb)
- [Bugfix] Fix a race condition that could prevent a newly provisioned Studio container from starting due to a FileExistsError when creating logs directory.

<a id='changelog-16.0.5'></a>
## v16.0.5 (2023-08-09)

- [Improvement] Upgrade the Open edX default version to open-release/palm.2. (by @regisb)

<a id='changelog-16.0.4'></a>
## v16.0.4 (2023-08-03)

- [Feature] Add support for HTTP/3, which considerably improves performance for Open edX. (by @regisb and @ghassanmas)
- [Bugfix] Do not display discussion units when the forum is not enabled. (by @regisb)
- [Improvement] Remove references to the wizard edition. (by @CodeWithEmad)

<a id='changelog-16.0.3'></a>
## v16.0.3 (2023-07-28)

- [Bugfix] Improve `tutor ... do settheme default` so that it reverts to the default theme rather than trying to switch to a nonexistent theme named "default". This will clear up some error noise from LMS/CMS logs. (by @kdmccormick)
- [Security] Fix content libraries creation by unprivileged users in studio (see [security advisory](https://github.com/openedx/edx-platform/security/advisories/GHSA-3q74-3rfh-g37j)). (by @regisb)

<a id='changelog-16.0.2'></a>
## v16.0.2 (2023-06-22)

- [Bugfix] On Kubernetes, fix mysql deployment by removing the `--ignore-db-dir` option, which no longer exists on MySQL 8. (by @regisb)

<a id='changelog-16.0.1'></a>
## v16.0.1 (2023-06-16)

- [Bugfix] Fix loading default Kubernetes config. (by @regisb)

<a id='changelog-16.0.0'></a>
## v16.0.0 (2023-06-14)
- 💥[Feature] Upgrade to Palm. (by @regisb)
    - [Bugfix] Rename ORA2 file upload folder from "SET-ME-PLEASE (ex. bucket-name)" to "openedxuploads". This has the effect of moving the corresponding folder from the `<tutor root>/data/lms/ora2` directory. MinIO users were not affected by this bug.
    - 💥[Improvement] During registration, the honor code and terms of service links are no longer visible by default. For most platforms, these links did not work anyway.
    - 💥[Deprecation] Halt support for Python 3.7. The binary release of Tutor is also no longer compatible with macOS 10.
    - 💥[Deprecation] Drop support for `docker-compose`, also known as Compose V1. The `docker compose` (no hyphen) plugin must be installed.
    - 💥[Refactor] We simplify the hooks API by getting rid of the `ContextTemplate`, `FilterTemplate` and `ActionTemplate` classes. As a consequences, the following changes occur:
        - `APP` was previously a ContextTemplate, and is now a dictionary of contexts indexed by name. Developers who implemented this context should replace `Contexts.APP(...)` by `Contexts.app(...)`.
        - Removed the `ENV_PATCH` filter, which was for internal use only anyway.
        - The `PLUGIN_LOADED` ActionTemplate is now an Action which takes a single argument. (the plugin name)
    - 💥[Refactor] We refactored the hooks API further by removing the static hook indexes and the hooks names. As a consequence, the syntactic sugar functions from the "filters" and "actions" modules were all removed: `get`, `add*`, `iterate*`, `apply*`, `do*`, etc.
    - 💥[Deprecation] The obsolete filters `COMMANDS_PRE_INIT` and `COMMANDS_INIT` have been removed. Plugin developers should instead use `CLI_DO_INIT_TASKS` (with suitable priorities).
    - 💥[Feature] The "openedx" Docker image is no longer built with docker-compose in development on `tutor dev start`. This used to be the case to make sure that it was always up-to-date, but it introduced a discrepancy in how images were build (`docker compose build` vs `docker build`). As a consequence:
        - The "openedx" Docker image in development can be built with `tutor images build openedx-dev`.
        - The `tutor dev/local start --skip-build` option is removed. It is replaced by opt-in `--build`.
    - [Improvement] The `IMAGES_BUILD` filter now supports relative paths as strings, and not just as tuple of strings.
    - [Improvement] Auto-complete the image names in the `images build/pull/push/printtag` commands.
    - [Deprecation] For local installations, Docker v20.10.15 and Compose v2.0.0 are now the minimum required versions.
    - [Bugfix] Make `tutor config printvalue ...` print actual yaml-formatted values, such as "true" and "null"
    - 💥[Improvement] MongoDb was upgraded to 4.4.
- 💥[Improvement] Deprecate the `RUN_LMS` and `RUN_CMS` tutor settings, which should be mostly unused. (by @regisb)
- [Improvement] Greatly simplify ownership of bind-mounted volumes with docker-compose. Instead of running one service per application, we run just a single "permissions" service. This change should be backward-compatible. (by @regisb)
- [Feature] Add a `config save -a/--append -A/--remove` options to conveniently append and remove values to/from list entries. (by @regisb)
- [Improvement] Considerably accelerate building the "openedx" Docker image with `RUN --mount=type=cache`. This feature is only for Docker with BuildKit, so detection is performed at build-time. (by @regisb)
- [Improvement] Automatically pull Docker image cache from the remote registry. Again, this will considerably improve image build-time, particularly in "cold-start" scenarios, where the images need to be built from scratch. The registry cache can be disabled with the `tutor images build --no-registry-cache` option. (by @regisb)
- [Feature] Automatically mount host folders *at build time*. This is a really important feature, as it allows us to transparently build images using local forks of remote repositories. (by @regisb)
- 💥[Deprecation] Remove the various `--mount` options. These options are replaced by persistent mounts, which are managed by the `tutor mounts` commands. (by @regisb)
- [Feature] Add the `do importdemocourse --repo-dir=...` option, to import courses from subdirectories of git repositories. This allows us to import the openedx-test-course in Palm with: `tutor local do importdemocourse --repo=https://github.com/openedx/openedx-test-course --version=o
pen-release/palm.master --repo-dir=test-course/course`. (by @regisb)

<a id='changelog-15.3.7'></a>
## v15.3.7 (2023-06-13)

- [Bugfix] Change `authSource` to `authsource`(LOWERCASE) in mongo db parameters. This allow to authenticate with credentials in openedx code.(by @johanv26)
 - [Feature] Add support for loading in-cluster config when running inside a pod. In certain scenarios, Tutor may operate within a pod that has access to a cluster through role binding and a service account. In these instances, the ./kube/config file may not be present, but kubectl commands can still execute without any problems. (by @CodeWithEmad)
- [Improvement] Bump the default MongoDB Docker image reference from version 4.2.17 to 4.2.24. (by @fghaas)

<a id='changelog-15.3.6'></a>
## v15.3.6 (2023-05-22)

- [Feature] Upgrade to open-release/olive.4. (by @regisb)

<a id='changelog-15.3.5'></a>
## v15.3.5 (2023-04-28)

- [Feature] Make it possible to import the demo course from a different git repository or version. (by @regisb)
- [Feature] Add a convenient `do print-edx-platform-setting` command to print the value of an edx-platform setting. (by @regisb)
- [Improvement] Improve edx-platform logging by silencing a couple deprecation warnings. (by @regisb)
- [Feature] Add a convenient `do sqlshell` command to enter a SQL shell as root. (by @regisb)

<a id='changelog-15.3.4'></a>
## v15.3.4 (2023-04-13)

- [Feature] Upgrade to open-release/olive.3. (by @regisb)

<a id='changelog-15.3.3'></a>
## v15.3.3 (2023-03-22)

- [Improvement] Make it possible to extend or override the configuration of the uWSGI server. (by @MoisesGSalas)
- [Improvement] Running `tutor dev launch --mount=edx-platform` now performs all necessary setup for a local edx-platform development. This includes running setup.py, installing node modules, and building assets; previously, those steps had to be run explicitly after bind-mounting a local copy of edx-platform (by @kdmccormick).
- [Bugfix] Running jobs in development mode with `tutor dev do ...` will now correctly use the development image. Previously, it used the production image, just like `tutor local do ...`. (by @kdmccormick)
- [Improvement] Faster build with `npm clean-install` instead of `npm install` in the openedx Docker image. This may change the version of npm packages installed next to edx-platform. (by @regisb)
- [Feature] Introduce the `DOCKER_BUILD_COMMAND` filter which makes it possible to customize the `docker build` command. (by @regisb)
- [Improvement] During openedx image build, copy `dockerize` utility from Docker registry for better efficiency. (by @regisb)
- [Improvement] Better highlight enabled plugins in `tutor plugins list`. (by @regisb)

- [Bugfix] Make sure that v0 plugin patches are applied in the same order as plugins are listed. (by @regisb)

<a id='changelog-15.3.1'></a>
## v15.3.2 (2023-03-13)

- [Bugfix] Use supported YouTube API for transcripts imports. (by @mariajgrimaldi)
- [Feature] Add `tutor config patches list` CLI for listing available patches. (by @mafermazu)
- [Bugfix] Add the missing `UWSGI_WORKERS` env variables to the lms and cms k8s deployments. (by @MoisesGSalas)

<a id='changelog-15.3.1'></a>
## v15.3.1 (2023-02-28)

- [Bugfix] `patchStrategicMerge` can now be applied to jobs. (by @keithgg)

<a id='changelog-15.3.0'></a>
## v15.3.0 (2023-02-10)

- [Feature] Introduce plugin indexes, described in this [Tutor enhancement proposal](https://discuss.openedx.org/t/tutor-enhancement-proposal-tep-plugin-indices/8182). This new feature introduces a lot of new ``plugins`` commands. See the docs for more information. (by @regisb)
- [Improvement] Add the `plugins list --enabled` option. (by @regisb)
- 💥[Improvement] Modify the output of `plugins list`. Enabled plugins are indicated as "enabled". Installed but not enabled plugins are no longer indicated as "disabled" but as "installed".

- 💥[Feature] Simplify the hooks API. The modules `tutor.hooks.actions`, `tutor.hooks.filters`, and `tutor.hooks.contexts` are no longer part of the API. This change should not affect most developers, who only use the `Actions` and `Filters` classes (notice the plural) from `tutor.hooks`. (by @regisb)
    - Instead of `tutor.hooks.actions.get("some:action")`, use `tutor.hooks.Actions.SOME_ACTION`.
    - Instead of `tutor.hooks.filters.get("some:filter")`, use `tutor.hooks.Filters.SOME_FILTER`.
    - Instead of `tutor.hooks.actions.add("some:action")`, use `tutor.hooks.Actions.SOME_ACTION.add()`. The same applies to the `do` method.
    - Instead of `tutor.hooks.filters.add("some:filter")`, use `tutor.hooks.Filters.SOME_FILTER.add()`. The same applies to the `add_item`, `add_items`, `apply`, and `iterate` methods.
    - Instead of `tutor.hooks.contexts.enter`, use `tutor.core.hooks.contexts.enter`.

- [Improvement] Make it possible to override the max upload size in the LMS and the CMS. This is achieved by moving the "caddyfile-lms" and "caddyfile-cms" patches just before the `import proxy` declarations. We also wrap the `request_body` directives within `handle` statements, which means that the `max_body` sizes can be overridden for specific paths. (by @regisb)

- [Security] Fix grading issue in LTI consumer XBlock. See [security advisory](https://github.com/openedx/xblock-lti-consumer/security/advisories/GHSA-7j9p-67mm-5g87). (by @regisb)

- [Feature] Upgrade all Open edX services to open-release/olive.2. (by @regisb)

<a id='changelog-15.2.0'></a>
## v15.2.0 (2023-01-19)

- 💥[Bugfix] Fix "example.com" links in registration emails. This is a breaking change for platforms that have modified the "id" field of the LMS site object in the database. These platforms should set `SITE_ID=1` in the common settings via a plugin. (by @regisb)
- [Bugfix] Running `tutor k8s upgrade --from=maple` won't apply and won't wait for the MySQL deployment to be ready if `RUN_MYSQL: false` (When you host your MySQL somewhere else like RDS) (by @CodeWithEmad)
- [Bugfix] Fix HTML component editing in studio by cherry-picking [upstream fix](https://github.com/openedx/edx-platform/pull/31500). (by @regisb)
- [Improvement] Changes annotations from `typing` to use built-in generic types from `__future__.annotations` (by @Carlos-Muniz)
- [Improvement] Resolve `CORS_ORIGIN_WHITELIST` warnings that pollute the LMS and CMS logs. As far as we know they were not causing any issue, apart from being a nuisance. (by @regisb)

<a id='changelog-15.1.0'></a>
## v15.1.0 (2022-12-13)

- [Improvement] Upgrade ipdb and ipython packages in the openedx development image. (by @regisb)
- [Improvement] Skip unnecessary image building in development. This should make `tutor dev launch` slightly faster. (by @regisb)
- [Bugfix] Fix Authn MFE login in development by disabling enterprise integration. (by @regisb)
- [Bugfix] Fix "Invalid value for ‘--from’" when running `tutor local upgrade --from=nutmeg`. If you are facing this error, just run `tutor local launch` and your platform should be automatically upgraded.
- [Bugfix] Fix "TypeError: Parameters to Generic[...] must all be type variables" error. This error may occur when upgrading from a very old installation of Tutor. It is due to an old version of the typing-extensions package.
- 💥[Deprecation] Get rid of the `quickstart` command. v15.0.0 introduced a deprecation warning, but we actually want users to stop using this command. Instead, use `launch` (by @regisb).
- [Improvement] Backfill persistent grades during upgrade from Nutmeg. If you observe missing grades after the upgrade from Nutmeg, run `tutor local upgrade --from=nutmeg`. (by @regisb)

<a id='changelog-15.0.0'></a>
## v15.0.0 (2022-12-06)

- 💥[Feature] Upgrade to Olive (by @regisb):
  - Mypy type checking options were modified: developers are encouraged to add the `--implicit-reexport` option to their IDE.
- [Bugfix] Update problem templates according newer python versions. (by @mariajgrimaldi)
- [Improvement] Add the `-h` help option to all commands and subcommands. Previously, we could only use `--help`, which is quite long for lazy fingers. (by @regisb)
- 💥[Feature] Add an extensible `local/dev/k8s do ...` command to trigger custom job commands. These commands are used to run a series of bash scripts in designated containers. Any plugin can add custom jobs thanks to the `CLI_DO_COMMANDS` filter. This causes the following breaking changes:
    - The "init", "createuser", "settheme", "importdemocourse" commands were all migrated to this new interface. For instance, `tutor local init` was replaced by `tutor local do init`.
    - Plugin developers are encouraged to replace calls to the `COMMANDS_INIT` and `COMMANDS_PRE_INIT` filters by `CLI_DO_INIT_TASKS`.
- [Feature] Implement hook filter priorities, which work like action priorities. (by @regisb)
- 💥[Improvement] Remove the `local/dev bindmount` commands, which have been marked as deprecated for some time. The `--mount` option should be used instead.
- 💥[Bugfix] Fix local installation requirements. Plugins that implemented the "openedx-dockerfile-post-python-requirements" patch and that needed access to the edx-platform repo will no longer work. Instead, these plugins should implement the "openedx-dockerfile-pre-assets" patch. This scenario should be very rare, though. (by @regisb)
- 💥[Improvement] Rename the implementation of tutor <mode> quickstart to tutor <mode> launch. (by @Carlos-Muniz)
- 💥[Improvement] Remove the implementation of tutor dev runserver. (by @Carlos-Muniz)
- [Bugfix] Fix MongoDB replica set connection error resulting from edx-platform's pymongo (3.10.1 -> 3.12.3) upgrade ([edx-platform#30569](https://github.com/openedx/edx-platform/pull/30569)). (by @ormsbee)
- [Bugfix] Update ``celery`` invocations for lms-worker and cms-worker to be compatible with Celery 5 CLI.
- [Improvement] Point CMS at its config file using ``CMS_CFG`` environment variable instead of deprecated ``STUDIO_CFG``.

<a id='changelog-14.2.3'></a>
## v14.2.3 (2022-12-06)

- [Security] Fix rotation of JWT tokens for disabled users. (by @regisb)

<a id='changelog-14.2.2'></a>
## v14.2.2 (2022-11-29)

- [Bugfix] Fix `jinja2.exceptions.TemplateSyntaxError: expected token 'end of statement block', got '|'` error by bumping the minimum required version of the Jinja2 package.

- [Feature] Add support for MongoDB SSL, authentication source, mechanism and replica set via the `MONGODB_USE_SSL`, `MONGODB_AUTH_MECHANISM`, `MONGODB_AUTH_SOURCE`, `MONGODB_REPLICA_SET` settings. (by @zakum1 and @regisb)

- [Bugfix] Fix tag of "openedx" development Docker image. Previously, this Docker tag did not include the Tutor version. As a consequence, a different cached image could be used in some cases. For instance: when running `tutor dev run` commands. Now, the image tag is "openedx-dev:TUTOR_VERSION".

- [Bugfix] Fix name of Swahili locale: it is "sw-ke" and not "sw" (by @regisb).

- [Security] Apply drag-n-drop v2 xblock [security patch](https://discuss.openedx.org/t/upcoming-security-release-xblock-drag-and-drop-v2/8768/7). (by @regisb)

<a id='changelog-14.2.0'></a>
## v14.2.1 (2022-11-24)

- [Improvement] Auto-completion of `plugins` and `config` arguments: `plugins enable/disable NAME`, `plugins install PATH`, `config save --set KEY=VAL`, `config save --unset KEY`, `config printvalue KEY`. (by @regisb)
- [Bugfix] Fix minimum click version (>= 8.0.0) when installing tutor from pip.
- [Improvement] Enable CORS by default for both LMS and CMS by moving those settings to the `common_all` partial. (by @arbrandes)

## v14.2.0 (2022-11-21)

- [Improvement] Auto-complete implicit `local/dev --mount /path/to/...` options. (by @regisb)
- 💥[Feature] Strong typing of action and filter hooks: this allows us to detect incorrect calls to `actions.add` or `filters.add` early. Strong typing forces us to break the `do` and `apply` API by removing the `context` named argument. Developers should replace `do(context=...)` by `do_from_context(..., )` (and similar for `apply`).

## v14.1.2 (2022-11-02)

- [Security] Fix edx-platform XSS vulnerability on "next" parameter. (by @regisb)

## v14.1.1 (2022-10-25)

- [Deprecation] Tutor is no longer compatible with Python 3.6. (by @regisb)
- [Security] Fix xblock ajax handler vulnerability. (by @regisb)
- [Improvement] Use web proxy gzip encoding to improve bandwidth. We observe a 75% size reduction on the LMS dashboard. (by @ghassanmas)

## v14.1.0 (2022-10-10)

- [Improvement] Upgrade Scorm XBlock to v14.0.0. (by @regisb)
- 💥[Improvement] The Richie plugin was transferred to the Openfun organization; thus, it is no longer officially supported and it is removed from the default set of plugins that ships with `pip install tutor[full]` or the Tutor pre-compiled binary. Users are encouraged to uninstall the `tutor-richie` Python package and install the `tutor-contrib-richie` package instead.
- [Feature] Upgrade edx-platform i18n strings to nutmeg.2. (by @regisb)

## v14.0.5 (2022-08-29)

- [Bugfix] Fix MongoDB replica set connection error resulting from edx-platform's pymongo (3.10.1 -> 3.12.3) upgrade ([edx-platform#30569](https://github.com/openedx/edx-platform/pull/30569)). (by @ormsbee)
- [Feature] Upgrade all applications to open-release/nutmeg.2. (by @BbrSofiane)

## v14.0.4 (2022-07-29)

- [Feature] Add the `-m/--mount` option to `tutor dev quickstart`. (by @regisb)
- [Bugfix] Fix `tutor dev start -m /path/to/frontend-app-learning` by introducing dev-specific `COMPOSE_DEV_TMP` and `COMPOSE_DEV_JOBS_TMP` filters (by @regisb).
- [Bugfix] Log the shell commands that Tutor executes more accurately. (by @kdmccormick)
- [Bugfix] `tutor dev quickstart` would fail under certain versions of docker-compose due to a bug in the logic that handled volume mounting. (by @kdmccormick)
- [Bugfix] The `tutor k8s start` command will succeed even when `k8s-override` and `kustomization-patches-strategic-merge` are not specified. (by @edazzocaisser)
- [BugFix] `kubectl wait` checks deployments instead of pods as it could hang indefinitely if there are extra pods in a broken state. (by @keithgg)

## v14.0.3 (2022-07-09)

- [Bugfix] Build openedx-dev Docker image even when the host user is root, for instance on Windows. (by @regisb)
- [Bugfix] Patch nutmeg.1 release with [LTI 1.3 fix](https://github.com/openedx/edx-platform/pull/30716). (by @ormsbee)
- [Improvement] Make it possible to override k8s resources in plugins using `k8s-override` patch. (by @foadlind)

## v14.0.2 (2022-06-27)

- [Bugfix] Update problem with hint template so it works with newer python versions. (by @mariajgrimaldi)
- [Feature] Add default PYTHONBREAKPOINT to openedx/Dockerfile (by @Carlos-Muniz)
- [Bugfix] Fix smtp server port in `cms.yml` which was causing email sending failures in the Studio. (by @regisb)
- [Bugfix] Skip waiting for MongoDB if it is served using SRV records. (by @gabor-boros)
- [Improvement] Use `git am` instead of `cherry-pick` to simplify patching process.
- [Improvement] Tutor is now compatible with Docker Compose subcommand.

## v14.0.1 (2022-06-13)

- [Bugfix] Fix missing tables on migration from maple ([#689](https://github.com/overhangio/tutor/issues/689)). (by @ibrmora)
- [Bugfix] Fix plugin patches in cms.env.yml template.

## v14.0.0 (2022-06-09)

- 💥[Feature] Upgrade to Nutmeg: (by @regisb)
  - 💥[Feature] Hide a course from the `/course` search page in the LMS when the course visibility is set to "none" in the Studio. (thanks @ghassanmas!)
  - 💥[Improvement] The `lms.env.json` and `cms.env.json` files are moved to `lms.env.yml` and `cms.env.yml`. As a consequence, plugin developers must reformat the following patches to use YAML format, and not JSON: "common-env-features", "lms-env-features", "cms-env-features", "lms-env", "cms-env", "openedx-auth".
  - 💥[Feature] Persistent grades are now enabled by default.
  - [Bugfix] Remove edX references from bulk emails ([issue](https://github.com/openedx/build-test-release-wg/issues/100)).
  - [Improvement] For Tutor Nightly (and only Nightly), official plugins are now installed from their nightly branches on GitHub instead of a version range on PyPI. This will allow Nightly users to install all official plugins by running ``pip install -e ".[full]"``.
  - [Bugfix] Start MongoDB when running migrations, because a new data migration fails if MongoDB is not running

## v13.3.1 (2022-06-06)

- [Bugfix] Crashing celery workers in development (#681). (by @regisb)
- [Bugfix] Fix studio logout issue. (by @Alec4r)

## v13.3.0 (2022-06-03)

- [Security] Apply logout redirect url security fix. (by @regisb)
- [Feature] Make it possible to force the rendering of a given template, even when the template path matches an ignore pattern. (by @regisb)
- 💥[Bugfix] Get rid of the `tutor config render` command, which is useless now that themes can be implemented as plugins. (by @regisb)

## v13.2.3 (2022-05-30)

- [Bugfix] Truncate site display name to 50 characters with a warning, fixing data too long error for long site names. (by @navinkarkera)
- [Feature] Add patch to allow overriding final openedx docker image CMD.
- [Bugfix] Ignore Python plugins that cannot be loaded. (by @regisb)
- [Improvement] Faster and more reliable builds with `npm clean-install` instead of `npm install`. (by @regisb. Thanks @ghassanmas!)
- [Bugfix] Fix 500 error during studio login. (by @regisb)
- [Bugfix] Fix updates for the Caddy deployment in multi-node Kubernetes clusters (#660). Previously, Caddy configuration updates might fail if the Kubernetes cluster had more than one worker node. (by @fghaas)

## v13.2.2 (2022-05-06)

- [Bugfix] Mounts were broken in dev mode. (by @kdmccormick)

## v13.2.1 (2022-05-06)

- [Bugfix] Fix broken file upload in studio because of unpinned studio-frontend requirement (see [discussion](https://discuss.overhang.io/t/missing-js-css-files-missing-from-openedx-docker-image-in-studio/2629) and [pull request](https://github.com/openedx/edx-platform/pull/30309)) (by @regisb. Thanks @uetuluk!).
- [Bugfix] "The Compose file is invalid" error on mounting dev-only folders. (by @regisb)
- [Bugfix] CMS settings in development. (by @regisb)

## v13.2.0 (2022-04-24)

- [Improvement] Add the `COMPOSE_PROJECT_STARTED` action and run `dev stop` on `local start` (and vice versa). (by @regisb)
- [Feature] Introduce `local/dev copyfrom` command to copy contents from a container. (by @regisb)
- [Bugfix] Fix a race condition that could prevent a newly provisioned LMS container from starting due to a `FileExistsError` when creating data folders.
- [Deprecation] Mark `tutor dev runserver` as deprecated in favor of `tutor dev start`. Since `start` now supports bind-mounting and breakpoint debugging, `runserver` is redundant and will be removed in a future release. (by @kdmccormick)
- [Improvement] Allow breakpoint debugging when attached to a service via `tutor dev start SERVICE`. (by @kdmccormick)
- [Security] Apply rate limiting security fix (see [commit](https://github.com/overhangio/edx-platform/commit/b5723e416e628cac4fa84392ca13e1b72817674f)). (by @regisb)
- [Feature] Introduce the ``-m/--mount`` option in ``local`` and ``dev`` commands to auto-magically bind-mount folders from the host. (by @regisb)
- [Feature] Add `tutor dev quickstart` command, which is similar to `tutor local quickstart`, except that it uses dev containers instead of local production ones and includes some other small differences for the convience of Open edX developers. This should remove some friction from the Open edX development setup process, which previously required that users provision using local producation containers (`tutor local quickstart`) but then stop them and switch to dev containers (`tutor local stop && tutor dev start -d`). (by @kdmccormick)
- 💥[Improvement] Make it possible to run `tutor k8s exec <command with multiple arguments>` (#636). As a consequence, it is no longer possible to run quoted commands: `tutor k8s exec "<some command>"`. Instead, you should remove the quotes: `tutor k8s exec <some command>`. (by @regisb)
- 💥[Deprecation] Drop support for the `TUTOR_EDX_PLATFORM_SETTINGS` environment variable. It is now recommended to create a plugin instead. (by @regisb)
- 💥[Improvement] Complete overhaul of the plugin extension mechanism. Tutor now has a hook-based Python API: actions can be triggered at different points of the application life cycle and data can be modified thanks to custom filters. The v0 plugin API is still supported, for backward compatibility, but plugin developers are encouraged to migrate their plugins to the new API. See the new plugin tutorial for more information. (by @regisb)
- [Improvement] Improved the output of `tutor plugins list`. (by @regisb)
- [Feature] Add `tutor [dev|local|k8s] status` command, which provides basic information about the platform's status. (by @kdmccormick)

## v13.1.11 (2022-04-12)

- [Security] Apply SAML security fix.
- [Improvement] In addition to the Docker build arguments `EDX_PLATFORM_REPOSITORY` and `NPM_REGISTRY`, also support two corresponding and identically-named `config.yml` values serving the same purpose.

## v13.1.10 (2022-04-11)

- [Feature] Upgrade all applications to open-release/maple.3.

## v13.1.9 (2022-04-06)

- [Security] Fix open redirect vulnerability in inactive user flow (see [commit](https://github.com/rgraber/edx-platform/commit/fbbcfe71832e700f16aad3636b0ccb35585d1c95))

## v13.1.8 (2022-03-18)

- [Bugfix] Fix "evalsymlink failure" during `k8s quickstart` (#611).
- [Bugfix] Fix "TypeError: upgrade() got an unexpected keyword argument 'non_interactive'" during `local upgrade`.

## v13.1.7 (2022-03-17)

- [Bugfix] Fix dockerize on arm64 by switching to the [powerman/dockerize](https://github.com/powerman/dockerize) fork (#591).
- [Bugfix] Fix "Unexpected args" error during service initialisation on Kubernetes (#611).

## v13.1.6 (2022-03-15)

- [Bugfix] Fix `local/k8s quickstart` commands when upgrading from an older release (#595).
- [Bugfix] Fix running the default exim-relay SMTP server on arm64 (#600).
- [Feature] Add `tutor k8s apply` command, which is a direct interface with `kubectl apply`.
- [Feature] Add `openedx-dockerfile-minimal` patch, which you can use to install custom packages and run commands as root in the Docker image.

## v13.1.5 (2022-02-14)

- [Improvement] Upgrade all services to open-release/maple.2.

## v13.1.4 (2022-02-08)

- [Security] Fix vulnerability in redirect URL during authentication (see [commit](https://github.com/overhangio/edx-platform/commit/06550411e34c04376fa3d757e1f068f464f816e6)).

## v13.1.3 (2022-02-01)

- [Security] Fix vulnerability in call to invalid enrollment API (see [commit](https://github.com/openedx/edx-platform/commit/a140c674799c527e961e37c5e46cb7dc1ffef5ac)).
- [Bugfix] Fix "Internal Server Error / AttributeError / object has no attribute 'get_metadata'" in learning MFE.
- [Improvement] Replace all links to github.com/edx by github.com/openedx, following the migration of all repositories.
- [Bugfix] Fix `k8s start caddy` command.

## v13.1.2 (2022-01-30)

- [Bugfix] Fix auto-renewal of certificates revoked by Let's Encrypt (see [discussion](https://community.letsencrypt.org/t/questions-about-renewing-before-tls-alpn-01-revocations/170449/21)).

## v13.1.1 (2022-01-25)

- [Bugfix] Fix authentication in development due to missing SameSite policy on session ID cookie.
- [Bugfix] Display properly themed favicon.ico image in LMS, Studio, and microfrontends.
- [Bugfix] Fix "LazyStaticAbsoluteUrl is not JSON serializable" error when sending bulk emails.
- [Bugfix] Fix `tutor local importdemocourse` fails when the platform is not up.

## v13.1.0 (2022-01-08)

- [Improvement] Provide much more comprehensive instructions when upgrading.
- [Bugfix] During the upgrade, make sure that the environment is up-to-date before prompting to rebuild the custom images.
- [Bugfix] Fix ownership of MySQL data, in particular when upgrading a Kubernetes cluster to Maple.
- [Bugfix] Ensure that ``tutor k8s upgrade`` is run during ``tutor k8s quickstart``, when necessary.
- 💥[Bugfix] By default, detect the current version during ``tutor k8s/local upgrade``.
- [Bugfix] Fix upgrading from Lilac to Maple on Kubernetes by deleting deployments and services.

## v13.0.3 (2022-01-04)

- [Security] Upgrade Django to 3.2.11 in edx-platform.
- [Security] Prevent non-staff users from searching usernames by email by abusing the logout URL.

## v13.0.2 (2021-12-22)

- [Security] Prevent non-staff users from searching usernames by email.

## v13.0.1 (2021-12-20)

- [Bugfix] Missing requirements file in `pip install tutor[full]`.

## v13.0.0 (2021-12-20)

- 💥[Improvement] Upgrade to Maple
  - Install all official plugins as part of the `tutor[full]` package.
  - Don't print error messages about loading plugins during autocompletion.
  - Prompt for image building when upgrading from one release to the next.
  - 💥 Allow concurrent logins to the LMS and the CMS.
  - Add `tutor local start --skip-build` option to skip building Docker images.
- [Feature] Better support of Caddy as a load balancer in Kubernetes:
  - Make it possible to start/stop a selection of resources with ``tutor k8s start/stop [names...]``.
  - Make it easy to deploy an independent LoadBalancer by converting the caddy service to a ClusterIP when ``ENABLE_WEB_PROXY=false``.
  - Add a ``app.kubernetes.io/component: loadbalancer`` label to the LoadBalancer service.
  - Add ``app.kubernetes.io/name`` labels to all services.
  - Preserve the LoadBalancer service in ``tutor k8s stop`` commands.
  - Wait for the caddy deployment to be ready before running initialisation jobs.
  - Fix running Caddy container in k8s, which should always be the case even if `ENABLE_WEB_PROXY` is false.
- [Security] On Kubernetes, convert all NodePort services to ClusterIP to guarantee network isolation from outside the cluster.
- 💥[Improvement] Move the Open edX forum to a [dedicated plugin](https://github.com/overhangio/tutor-forum/) (#450).
- 💥[Improvement] Drop Python 3.5 compatibility.
- 💥[Bugfix] No longer track the Tutor version number in resource labels (and label selectors, which breaks the update of Deployment resources), but instead do so in resource annotations.
- 💥[Improvement] Get rid of the "tutor-openedx" package, which is no longer supported.
- 💥[Improvement] Run all services as unprivileged containers, for better security. This has multiple consequences:
  - The "openedx-dev" image is now built with `tutor dev dc build lms`.
  - The "smtp" service now runs the "devture/exim-relay" Docker image, which is unprivileged. Also, the default SMTP port is now 8025.
- 💥[Feature] Get rid of the Nginx container and service, which is now replaced by Caddy. this has the following consequences:
    - Patches "nginx-cms", "nginx-lms", "nginx-extra", "local-docker-compose-nginx-aliases" are replaced by "caddyfile-cms", "caddyfile-lms", "caddyfile", " local-docker-compose-caddy-aliases".
    - Patches "k8s-deployments-nginx-volume-mounts", "k8s-deployments-nginx-volumes" were obsolete and are removed.
    - The `NGINX_HTTP_PORT` setting is renamed to `CADDY_HTTP_PORT`.
- [Bugfix] Fix building of the `openedx` image on ARM64 due to missing `libgeos-dev`

## v12.2.0 (2021-12-08)

- [Bugfix] Fix incorrect "from" address in course bulk emails (see [pull request](https://github.com/openedx/edx-platform/pull/29001)).
- 💥[Improvement] Fail on incorrect image name argument in `images build/pull/push/printtag` commands.
- [Bugfix] Remove trailing slashes in docker-compose files for [compatibility with docker-compose v2 in WSL](https://github.com/docker/compose/issues/8558).
- [Improvement] `settheme` now works with the preview domain.
- [Feature] Allow specifying extra pip packages through config.yml.

## v12.1.7 (2021-11-18)

- [Security] Timed exam security fix [29347](https://github.com/openedx/edx-platform/pull/29347).
- [Feature] Add [tutor-richie](https://github.com/overhangio/tutor-richie) to the plugins that are bundled with the tutor binary.
- [Improvement] Make `tutor plugins list` print plugins sorted by name.
- [Improvement] Ignore Python plugins that cannot be loaded.
- [Bugfix] When configured with `RUN_FORUM: false`, omit forum-related [Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/) from the manifests that `tutor k8s` generates. (#525)

## v12.1.6 (2021-11-02)

- [Improvement] Upgrade all services to open-release/lilac.3.
- [Feature] Make it possible to override job configuration in development: if they exist, `dev/docker-compose.jobs.yml` and `dev/docker-compose.jobs.override.yml` will be loaded when running jobs.
- [Improvement] Faster `tutor local start` by building only necessary images.

## v12.1.5 (2021-10-25)

- 💥[Improvement] Change the `settheme` command such that, by default, a custom theme is assigned to the LMS and the CMS, both in production and development mode.
- [Bugfix] Change the `local quickstart` command to check for adequate Docker memory allocation on macOS (#463)

## v12.1.4 (2021-10-11)

- [Feature] Add configuration setting `PREVIEW_LMS_BASE` for custom preview domain.
- [Improvement] Enable milestones application flag `MILESTONES_APP` and prerequisite courses feature flags `ENABLE_PREREQUISITE_COURSES` by default.

## v12.1.3 (2021-09-28)

- [Bugfix] Fix 500 error during user registration.
- [Bugfix] Fix Mongodb compatibility version upgrade when upgrading from Koa to Lilac.
- [Feature] Ability to pass [docker build options](https://docs.docker.com/engine/reference/commandline/build/#options) via ``--docker-arg`` option in ``tutor images build`` command.

## v12.1.2 (2021-09-18)

- [Bugfix] Fix (again) forum starting issue: "NoMethodError: undefined method 'encode' for nil:NilClass".

## v12.1.1 (2021-09-17)

- [Bugfix] Fix forum starting issue: "NoMethodError: undefined method 'encode' for nil:NilClass".

## v12.1.0 (2021-09-17)

- [Improvement] Make it easier to run edx-platform unit tests.
- [Bugfix] Fix segmentation fault during `tutor config save` on Mac OS M1 (#473). Thanks @ghassanmas!
- [Bugfix] Fix a bug that prevented connecting to external MongoDB instances.
- [Improvement] Make sure that the logo included in email notifications (including discussion responses) is the same as the site logo.
- [Bugfix] Install IPython directly from PyPI instead of installing it from source (the reason it was installed from source is no longer relevant). The effect of this shall speed up the process of building the openedx-dev Docker image.
- [Feature] Add "openedx-dockerfile-post-git-checkout" patch.
- [Improvement] In the "openedx" Docker images, convert git patches to cherry-picks for a cleaner source tree.
- 💥[Feature] Make it possible to override local job configuration. This deprecates the older model for running jobs which dates back from a long time ago.

## v12.0.4 (2021-08-12)

- [Security] Apply security patch [28442](https://github.com/openedx/edx-platform/pull/28442).

## v12.0.3 (2021-08-10)

- [Improvement] Upgrade all services to open-release/lilac.2.
- [Bugfix] Fix "`sh` is not a recognized command" in some plugins, including minio.
- [Improvement] Set the default contact mailing email address
- [Bugfix] Fix minio initialisation in Kubernetes.

## v12.0.2 (2021-07-06)

- [Bugfix] Fix "Invalid command argument" during upgrade from Koa to Lilac.
- [Bugfix] Fix MySQL initialisation in docker-compose==2.0.0beta4.
- [Improvement] Tutor is now published on PyPI as "tutor".

## v12.0.1 (2021-06-22)

- [Bugfix] Fix double pulling MongoDB image when upgrading from Koa to Lilac.
- [Improvement] Better logging during `plugins disable`.
- [Bugfix] Fix "upstream sent too big header" error during login of existing users after a Koa to Lilac upgrade.
- [Feature] Added the ability to skip `config.yml` file modification while running `tutor config save` command with `-e` or `--env-only` flag.
- [Feature] Add new config value `FORUM_MONGODB_DATABASE` to set the forum database name.

## v12.0.0 (2021-06-09)

- 💥[Improvement] Upgrade all services to open-release/lilac.master.
- 💥[Feature] Migrate Android app building and the WebUI frontend away from core Tutor and to dedicated plugins (see [TEP](https://discuss.overhang.io/c/community/tep/9)). The `DOCKER_IMAGE_ANDROID` setting is thus renamed to `ANDROID_DOCKER_IMAGE`.
- [Feature] Run `docker-compose build` as part of `tutor local start`.

## v11.3.1 (2021-06-08)

- [Improvement] Avoid permission issues in Kubernetes/Openshift for users who do not have the rights to edit their namespace.
- [Improvement] Better Kubernetes object creation.

## v11.3.0 (2021-06-06)

- 💥[Security] Disable python-evaluated input by default as we don't run codejail.
- [Bugfix] Fix missing discussion notifications.
- [Improvement] Better error logging when loading a plugin from an incompatible version.

## v11.2.11 (2021-05-18)

- [Feature] Add Redis database configuration for both cache and celery.

## v11.2.10 (2021-05-17)

- [Security] Apply Django security patches by upgrading from 2.2.20 to 2.2.23.
- [Bugfix] Fix video unit completion (see [pull request](https://github.com/openedx/edx-platform/pull/27230)).

## v11.2.9 (2021-05-12)

- [Bugfix] Fix crashing installation because of a major release of all Pallets projects.
- [Bugfix] Fix crash in `local quickstart -p` command.
- [Bugfix] Fix 502 error on request to lms with header larger than the maximum uwsgi buffer size.

## v11.2.8 (2021-04-27)

- [Bugfix] Fix parsing of YAML-formatted values in ``config save --set KEY=VALUE`` commands, in use for instance with Ecommerce.

## v11.2.7 (2021-04-23)

- [Security] Apply security patch [27394](https://github.com/openedx/edx-platform/pull/27394).
- [Feature] Add patches to extend python requirements installation process in openedx and openedx-dev Dockerfiles.
- [Improvement] Apply edx-platform patches during Docker image build using tutor patch 'openedx-dockerfile-git-patches-default'.

## v11.2.6 (2021-04-09)

- [Improvement] Upgrade all services to open-release/koa.3.
- [Feature] Make it possible to build the openedx Docker image with a custom openedx-i18n version with the ``--build-arg OPENEDX_I18N_VERSION=custom`` command line argument.

## v11.2.5 (2021-03-30)

- [Bugfix] Fix edge case where `PLUGINS` entry is null in config.yml.
- [Bugfix] Fix missing py2neo dependency in `images build openedx` (#411).

## v11.2.4 (2021-03-17)

- [Bugfix] Fix "Invalid Request" error during SAML authentication (thanks @Ant1x!).
- [Feature] Add `make pull-base-images` command to update base images.
- [Improvement] Annotate types all over the Tutor code base.
- [Bugfix] Fix parsing of YAML CLI arguments that include equal "=" signs.
- [Bugfix] Fix minor edge case in `long_to_base64` utility function.
- [Improvement] Add openedx patches to add settings during the build process.

## v11.2.3 (2021-02-20)

- [Bugfix] Make LMS celery workers actually process LMS tasks and not CMS tasks.

## v11.2.2 (2021-02-17)

- [Security] Apply security patch [26592](https://github.com/openedx/edx-platform/pull/26592).

## v11.2.1 (2021-02-16)

- [Bugfix] Actually persist Redis data.

## v11.2.0 (2021-02-10)

- [Bugfix] Upgrade all services to open-release/koa.2.

## v11.1.5 (2021-02-09)

- [Security] Apply security patch [26432](https://github.com/openedx/edx-platform/pull/26432).
- [Bugfix] Print warnings to stderr.

## v11.1.4 (2021-02-04)

- [Security] Apply security patch [26358](https://github.com/openedx/edx-platform/pull/26358).

## v11.1.3 (2021-01-31)

- [Security] Apply security patch [26253](https://github.com/openedx/edx-platform/pull/26253).

## v11.1.2 (2021-01-29)

- [Bugfix] Fix django setting value and static asset loading in openedx-dev image.

## v11.1.1 (2021-01-20)

- [Feature] Add a `tutor images build --target=...` argument for [multi-stage Docker builds](https://docs.docker.com/develop/develop-images/multistage-build/).
- [Feature] Create a test version of the openedx-dev Docker image for running edx-platform unit tests.
- [Security] Apply security patch [26112](https://github.com/openedx/edx-platform/pull/26112).
- [Bugfix] Fix `local exec` command which crashed with a `AttributeError`.

## v11.1.0 (2021-01-13)

- [Bugfix] Fix "Read-only file system" errors when running `tutor dev runserver` commands on Mac OS (again, see #392).
- [Feature] Automatically bind-mount volumes from the `volumes/` directory with the `--volume=/...` syntax.

## v11.0.7 (2021-01-11)

- [Security] Apply security patch [26029](https://github.com/openedx/edx-platform/pull/26029).

## v11.0.6 (2021-01-05)

- [Security] Apply security patch [25974](https://github.com/openedx/edx-platform/pull/25974).

## v11.0.5 (2020-12-30)

- [Bugfix] Fix "Invalid type for parameter ContentType" error on js upload in Scorm xblock ([openedx-scorm-xblock #16](https://github.com/overhangio/openedx-scorm-xblock/issues/16)).

## v11.0.4 (2020-12-17)

- [Bugfix] Fix "Read-only file system" errors when running `tutor dev runserver` commands on Mac OS (#392).

## v11.0.3 (2020-12-15)

- [Bugfix] Fix upload of video transcripts to S3 (again).

## v11.0.2 (2020-12-12)

- [Bugfix] Fix missing celery tasks from edx-platform (see [upstream PR](https://github.com/openedx/edx-platform/pull/25840)).

## v11.0.1 (2020-12-10)

- [Security] Apply security patch [25834](https://github.com/openedx/edx-platform/pull/25834).
- [Bugfix] Fix Android apk directory mount path.

## v11.0.0 (2020-12-09)

- 💥[Improvement] Upgrade Open edX to Koa.
    - 💥 Setting changes:
        - The ``ACTIVATE_HTTPS`` setting was renamed to ``ENABLE_HTTPS``.
        - Other ``ACTIVATE_*`` variables were all renamed to ``RUN_*``.
        - The ``WEB_PROXY`` setting was removed and ``RUN_CADDY`` was added.
        - The ``NGINX_HTTPS_PORT`` setting is deprecated.
    - Architectural changes:
        - Use Caddy as a web proxy for automated SSL/TLS certificate generation:
            - Nginx no longer listens to port 443 for HTTPS traffic.
            - The Caddy configuration file comes with a new ``caddyfile`` patch for much simpler SSL/TLS management.
            - Configuration files for web proxies are no longer provided.
            - Kubernetes deployment no longer requires setting up a custom Ingress resource or custom manager.
        - Gunicorn and Whitenoise are replaced with uwsgi: this increases bootstrap performance and makes it no longer necessary to mount media folders in the Nginx container.
        - Replace Memcached and RabbitMQ with Redis.
    - Additional features:
        - Make it possible to disable all plugins at once with ``plugins disable all``.
        - Add ``tutor k8s wait`` command to wait for a pod to become ready.
        - Faster, more reliable static assets with local memory caching.
    - Deprecation: proxy files for Apache and Nginx are no longer provided out of the box.
    - Removed plugin `{{ patch (...) }}` statements:
        - "https-create", "k8s-ingress-rules", "k8s-ingress-tls-hosts": these are no longer necessary. Instead, declare your app in the "caddyfile" patch.
        - "local-docker-compose-nginx-volumes": this patch was primarily used to serve media assets. The recommended solution is now to serve assets with uwsgi.

## v10.5.3 (2020-12-09)

- [Security] Apply upstream edx-platform [security patch](https://github.com/openedx/edx-platform/pull/25782).

## v10.5.2 (2020-12-07)

- [Improvement] Increase the timeout of the gunicorn worker command in openedx Dockerfile.

## v10.5.1 (2020-11-30)

- [Bugfix] Fix Dockerfile parsing on Windows.
- [Improvement] Add option to patch lms and cms Nginx server blocks.

## v10.5.0 (2020-11-19)

- 💥[Improvement] Remove `dev/local pullimages`. Instead, run `dev/local dc pull`.
- 💥[Improvement] Add `dev dc` and `local dc` commands as thin wrappers of the `docker-compose` CLI.
- 💥[Improvement] Remove the undocumented `local run_hook` command. Instead, run `local init --limit=...`.
- 💥[Improvement] Remove `tutor android pullimage` command. Instead, run `tutor images pull android`.
- [Bugfix] Fix `config save` on Windows.
- [Bugfix] Fix platform checking in user ID function.

## v10.4.1 (2020-11-11)

- [Bugfix] Fix dependency error during `pip install tutor` due to urllib3 incompatibility.
- [Bugfix] Fix user ID checking under Windows.
- [Bugfix] Fix template rendering for Windows users.
- [Improvement] Switch to `bcrypt` for htpasswd password generation, for better portability on Windows.
- [Improvement] In the openedx production docker image, add some jitter to the gunicorn worker restart process to prevent all workers from restarting at the same time.

## v10.4.0 (2020-10-30)

**Note for users of the [Tutor AMI](https://aws.amazon.com/marketplace/pp/B07PV3TB8X):** To upgrade from a previous v10 release, run:

    curl -fsSL https://overhang.io/tutor/ami/upgrade.sh | sh

- [Improvement] Mount config and setting files in read-only mode.
- 💥[Improvement] Enable unit completion tracking by default.
- [Bugfix] Run `apt update` before `apt install` when installing deps in the openedx Dockerfile.

## v10.3.1 (2020-10-16)

- [Improvement] Make all commands considerably faster.
- [Improvement] Make it easier to override Mongodb connection parameters.
- [Bugfix] Add support for .woff and .woff2 font files in themes (thanks @mrtndwrd!).

## v10.3.0 (2020-10-13)

- 💥[Improvement] Simplify CORS configuration.

## v10.2.4 (2020-10-06)

- [Bugfix] Fix Apache proxy configuration when HTTPS is enabled (#370).

## v10.2.3 (2020-10-02)

- [Feature] Add ``images printtag`` command.
- [Improvement] Make it possible to override individual contact email addresses with plugins.
- [Bugfix] Replace "no-reply@LMS_BASE" email address by regular contact email address.
- [Bugfix] Disable learner records globally by default.
- [Improvement] Upgrade to the latest release of MySQL 5.6.
- [Improvement] Non-plugin settings added by "set" directives are now automatically removed when the plugin is disabled (#241).

## v10.2.2 (2020-09-05)

- [Improvement] Add CORS basic configuration to LMS for subdomains of the LMS.
- [Feature] Add support for `images build --add-host` option (thanks @grinderz!).
- [Bugfix] Fix podman compatibility by replacing `docker-compose rm` command with `docker-compose stop` when stopping containers.
- [Improvement] Improve plugin data deletion.
- [Improvement] Introduce the `OPENEDX_COMMON_VERSION` setting.
- [Bugfix] Make it possible to run init jobs without starting the entire platform.
- [Improvement] Reduce "openedx" Docker image size with static asset de-duplication.

## v10.2.1 (2020-08-27)

- [Bugfix] Upgrade all services to open-release/juniper.3.
- [Bugfix] Fix upload of video transcripts to S3.
- [Improvement] Memorize whether the user is running a production platform during interactive configuration.

## v10.2.0 (2020-08-16)

- [Bugfix] Fix incorrect loading of some resources from localhost:18000 in development.
- [Bugfix] Fix Samesite=None Secure=False cookie error for users accessing the LMS with the latest release of Google Chrome.
- [Security] Apply javascript security patch ([pull request](https://github.com/openedx/edx-platform/pull/24762)).
- [Bugfix] Fix "FileError" on Scorm package upload in Scorm XBlock.
- 💥[Improvement] Serve openedx static assets with [whitenoise](http://whitenoise.evans.io/en/stable/) instead of Nginx. This removes the `k8s-deployments-nginx-init-containers` patch. Plugins are encouraged to implement static asset serving with Whitenoise as well.
- [Bugfix] Fix dependency on MySQL service when MySQL is not activated.
- [Improvement] Improve openedx Docker image build time and size with the multi-stage build.
- 💥[Feature] Get rid of outdated sysadmin dashboard in LMS at /sysadmin.

## v10.1.0 (2020-07-23)

- [Security] Apply edx-platform upstream xss security fixes ([pull request](https://github.com/openedx/edx-platform/pull/24568)).
- 💥[Feature] Make it possible to override the docker registry for just a few services by setting `DOCKER_IMAGE_SERVICENAME` values.

## v10.0.11 (2020-07-16)

- [Feature] Upgrade all repositories to open-release/juniper.3.
- [Bugfix] Fix `reload-gunicorn` command.
- [Feature] Enable sysadmin dashboard in LMS at /sysadmin.

## v10.0.10 (2020-07-01)

- [Bugfix] Fix pycontracts installation error when building openedx Docker image.
- [Bugfix] Fix access to the discussion forum in development mode.

## v10.0.9 (2020-07-01)

- [Bugfix] Share grade download settings between the LMS and the CMS.

## v10.0.8 (2020-06-23)

- [Bugfix] Fix android user creation during init.
- [Bugfix] Fix undefined settings in k8s scripts, such as `createuser`.

## v10.0.7 (2020-06-22)

- [Bugfix] Fix TypeError on viewing xblock.
- [Bugfix] Fix authentication in Android mobile application.

## v10.0.6 (2020-06-22)

- [Bugfix] Fix unsent activation emails and other asynchronous tasks.

## v10.0.5 (2020-06-21)

- [Security] Apply edx-platform upstream xss security fixes ([pull request](https://github.com/openedx/edx-platform/pull/24258)).

## v10.0.4 (2020-06-19)

- [Bugfix] Fix broken `tutor ui` command in binary.

## v10.0.3 (2020-06-19)

- [Bugfix] Fix error on android user creation.

## v10.0.2 (2020-06-17)

- [Bugfix] Fix crash when viewing the problem in LMS.
- [Bugfix] Fix missing webpack-stats.json in openedx Docker image.

## v10.0.1 (2020-06-15)

- [Bugfix] Fix KeyError when running ``local quickstart`` for the first time.

## v10.0.0 (2020-06-15)

- 💥[Improvement] Upgrade to Juniper 🍾.
- [Bugfix] Fix Nginx resolver address to address container restarts.
- [Feature] Add `--limit=myplugin` option to `init` commands to limit the execution of initialisation to certain services and plugins.

## v3.12.6 (2020-06-01)

- [Improvement] Add `dig`, `ping` utilities to openedx-dev Docker image.
- [Bugfix] Resolve "Can't connect to MySQL server" on init.
- [Improvement] Make it possible to customise the MySQL root username, for connecting to external MySQL databases.

## v3.12.5 (2020-05-20)

- [Improvement] Upgrade Android app to v2.21.1 and enable many features, such as downloading videos to SD card. Thanks for the help @ejklock!.
- [Bugfix] Fix Android app crash when accessing the course.

## v3.12.4 (2020-05-18)

- [Improvement] Add ability to rescore SCORM units.
- [Bugfix] Fix scoring of graded SCORM units.
- [Improvement] Increase maximum uploaded file size in the CMS from 10 to 100 Mb.

## v3.12.3 (2020-05-05)

- [Security] Apply most recent edx-platform [security patches](https://discuss.openedx.org/t/security-patch-for-edit-chapter-xss-lint-issues/2030).

## v3.12.2 (2020-04-29)

- [Bugfix] Fix oauth2 authentication with 3rd-party services, such as discovery.
- [Bugfix] Upgrade scorm xblock to solve caching issue.

## v3.12.1 (2020-04-27)

- [Improvement] Increase max upload allowed size to 250Mb in CMS.

## v3.12.0 (2020-04-26)

- 💥[Improvement] Do not deploy an ingress or SSL/TLS certificate issuer resource by default in Kubernetes.
- [Improvement] Fix tls certificate generation in k8s.
- 💥[Improvement] Radically change the way jobs are run: we no longer "exec", but instead run a dedicated container.
- 💥[Improvement] Upgrade k8s certificate issuer to cert-manager.io/v1alpha2.
- [Feature] Add SCORM XBlock to default openedx docker image.

## v3.11.12 (2020-04-16)

- [Feature] Make it easy to add custom translation strings to the openedx Docker image.
- [Improvement] Make it possible to rely on a different npm registry for faster image building.

## v3.11.11 (2020-04-15)

- [Bugfix] Make sure all emails (including "password reset") are properly saved to a local file in development mode (#315).
- [Improvement] Add `openedx-development-settings` patch to patch the LMS and the CMS simultaneously in development.
- [Bugfix] Fix missing celery tasks in the CMS.

## v3.11.10 (2020-04-14)

- [Bugfix] Fix updates to the course structure in the LMS (#302).

## v3.11.9 (2020-04-07)

- [Bugfix] Fix Android app build for domain names that include a dash ("-").

## v3.11.8 (2020-04-06)

- [Feature] Add `encrypt` template filter to conveniently add htpasswd-based authentication to Nginx.
- [Bugfix] Fix "missing tty" during init in cron jobs.

## v3.11.7 (2020-04-01)

- [Bugfix] Fix missing js translations.
- [Bugfix] Fix tls certificate generation in cron jobs.

## v3.11.6 (2020-03-13)

- [Bugfix] Fix "Unable to resolve dependency" error during forum initialisation.
- [Feature] Add `settheme` command to easily assign a theme to a domain name.
- [Improvement] Modify Nginx access logs to include request scheme and server name (plugin developers should use the "tutor" log format).
- [Bugfix] Fix DNS resolution of restarted service.
- [Feature] Restart multiple services with `local restart`.
- [Feature] Make it possible to easily reload the openedx gunicorn process with `tutor local exec lms reload-gunicorn`.
- [Improvement] Rename lms/cms_worker to lms/cms-worker in local deployment.
- [Improvement] Add the management plugin to the RabbitMQ container.
- [Improvement] Make it possible to run an Elasticsearch service on HTTPS.

## v3.11.5 (2020-02-27)

- [Improvement] Switch edx-platform from open-release/ironwood.2 tag to the open-release/ironwood.master branch.
- [Security] Upgrade django to 1.11.28.
- [Improvement] Make it possible to configure the Elasticsearch heap size.
- [Bugfix] Fix broken Elasticsearch environment variables.
- [Improvement] Restore more recent Android app version (#289).

## v3.11.4 (2020-02-16)

- [Bugfix] Fix auth problem in Android app (#289).

## v3.11.3 (2020-01-21)

- [Bugfix] Fix incorrectly parsed empty strings for `config save --set ...=...` commands.

## v3.11.2 (2020-01-17)

- [Bugfix] Make sure `docker-compose.override.yml` is loaded in dev and local contexts.

## v3.11.1 (2020-01-16)

- [Feature] Add `config render` command.

## v3.11.0 (2020-01-14)

- [Feature] Add support for simple, YAML-based plugins.
- 💥[Improvement] The output of `plugins list` now includes plugin version numbers.

## v3.10.1 (2020-01-13)

- [Improvement] Explicitly point to docker.io images, when necessary, for [podman](https://podman.io/) compatibility.

## v3.10.0 (2020-01-10)

- [Bugfix] Fix OAuth authentication in dev mode.
- [Improvement] Upgrade to the 3.7 docker-compose syntax.
- [Improvement] The `dev runserver` command can now be run for just any service.
- 💥[Feature] `dev run/exec` commands now support generic options which are passed to docker-compose. Consequently, defining the `TUTOR_EDX_PLATFORM_PATH` environment variable no longer works. Instead, users are encouraged to explicitly pass the `-v` option, define a command alias or create a `docker-compose.override.yml` file.

## v3.9.1 (2020-01-08)

- [Improvement] Make it possible to override the project name in development mode.
- [Bugfix] Fix user switching in development mode.
- [Bugfix] Fix "k8s quickstart" crash.

## v3.9.0 (2019-12-21)

- [Security] Apply django 1.11.21 -> 1.11.27 security patches.
- [Bugfix] Fix running dev image with `sudo`.
- [Improvement] Add `cms/lms-env-features` patches (#276).
- [Feature] Add plugin subcommands.
- 💥[Improvement] Move ``-r/--root`` option to parent command level.
- [Bugfix] Fix course about page visibility.
- [Improvement] Print gunicorn access logs in the console.
- 💥[Improvement] Get rid of the `indexcourses` and `portainer` command (#269).

## v3.8.0 (2019-11-22)

- [Improvement] Add `k8s-deployments-nginx-volume-mounts` patch.
- [Bugfix] Fix running forum locally when both Elasticsearch and MongoDB are not activated (#266).
- [Bugfix] Fix MongoDB URL in the forum when running a separate service (#267).
- 💥[Improvement] Better `dev` commands, with dedicated development docker image. One of the consequences is that the `dev watchthemes` command is replaced by `dev run lms watchthemes`.
- [Improvement] `images` commands now accept multiple `image` arguments.

## v3.7.4 (2019-10-19)

- [Bugfix] Fix missing requirements file in PyPI package (#261).
- [Improvement] Add missing cms/lms production/development setting patches.
- [Improvement] Allow SigV4 authentication for video upload to S3.
- [Bugfix] Fix cms development settings.

## v3.7.3 (2019-10-17)

- [Improvement] Upgrade openedx locales to Ironwood.

## v3.7.2 (2019-10-09)

- [Improvement] Properly set studio title (#246).
- [Improvement] Enable Mysql strict mode.

## v3.7.1 (2019-10-06)

- [Feature] Introduce tutor docker image.
- [Feature] Introduce `local hook` command for plugin development.
- [Bugfix] Persist `private.txt` file between two runs of `config save` (#247).
- [Improvement] Added configuration values to limit the number of gunicorn workers for the LMS and CMS.

## v3.7.0 (2019-09-03)

- 💥[Improvement] Get rid of mysql-client container.
- [Improvement] Add "local-docker-compose-lms/cms-dependencies" plugin patches.
- [Improvement] Use "exec" instead of "run" to initialise local platform.

## v3.6.3 (2019-08-31)

- [Security] Fix CustomTagModule mako template injection.
- [Improvement] Move all plugins outside of the tutor repo.
- [Bugfix/Improvement] Add all plugins (with data) into binary bundle (#242).

## v3.6.2 (2019-08-07)

- [Bugfix] Fix missing templates in bundled plugins.
- [Bugfix] Enable HTML certificate view.

## v3.6.1 (2019-07-27)

- [Bugfix] Fix missing patches from minio plugin (thanks @Wejie!).

## v3.6.0 (2019-07-11)

- [Feature] Modify ``createuser`` commands to define a password from the command line.
- [Improvement] Better YAML value parsing from the command line.
- [Feature] Add `dev exec` command.
- [Bugfix] Fix incorrect notes settings definition.
- [Improvement] Make it possible to start/stop/reboot a selection of services.
- [Improvement] Add `local/k8s reboot` commands.
- [Improvement] Add `-U/--unset` option to `config save`.
- [Bugfix] Fix insecure static asset loading when web proxy is enabled.
- [Improvement] Rename `SECRET_KEY` configuration parameter to `OPENEDX_SECRET_KEY`.
- [Improvement] Add support for SSL and TLS in external SMTP server (#231).
- [Bugfix] Fix missing video transcripts in LMS (#229).
- [Improvement] Make it possible to enable/disable multiple plugins at once.
- [Improvement] Add a few local and k8s patches for plugins.

## v3.5.3 (2019-07-05)

- [Bugfix] Add pre-init hook for correct initialisation of minio.

## v3.5.2 (2019-07-05)

- [Security] Apply certificate XSS security patch.

## v3.5.1 (2019-07-04)

- [Feature] Make it possible for plugins to patch the build templates.
- [Improvement] Move Xqueue and Student notes to a dedicated plugin.

## v3.4.3 (2019-06-24)

- [Bugfix] Fix missing password values from generated configuration.

## v3.4.2 (2019-06-23)

- [Bugfix] Fix incorrect settings during lms/cms init (#224).

## v3.4.1 (2019-06-23)

- [Bugfix] Fix install from PyPI.
- [Improvement] Get rid of Kubernetes python package dependency.

## v3.4.0 (2019-06-17)

- [Feature] Creation of a plugin system.
- [Feature] Kubernetes support out of beta.
- [Improvement] Switch to pinned image tags for easier upgrades.
- 💥[Improvement] Remove the `-y/--yes` option: `tutor config save` is now non-interactive by default. Use `-i/--interactive` to force interactive mode.
- 💥[Improvement] Replace the `databases` command with `init`.
- [Improvement] Upgrade to ironwood.2.
- [Improvement] Add `-y/--yes` option to `local quickstart` for non-interactive quickstart.
- [Improvement] Persist LMS/CMS logs to disk by default (with collaboration from @silviot 💪).
- [Bugfix] Fix installing a locally cloned requirement repository.
- [Improvement] Add `--no-cache` option to `images build`.
- [Improvement] Make it possible to configure the notes service hostname.
- [Improvement] Better, more robust MySQL initialisation.

## v3.3.10 (2019-05-15)

- [Bugfix] Fix boolean configuration choices.

## v3.3.9 (2019-05-13)
- [Improvement] Add `local exec` command for running commands inside existing containers.
- [Bugfix] Fix triple display of courses in LMS search (upstream patch, #189).

## v3.3.8 (2019-04-28)

- [Bugfix] Reduce the number of gunicorn workers to address RAM usage (#207).

## v3.3.7 (2019-04-28)

- [Bugfix] Fix "Timeout after 20s" on running migrations.

## v3.3.6 (2019-04-27)

- [Bugfix] Fix KeyError on the first quickstart.
- [Improvement] De-duplication of prod/dev settings. Thanks, @silviot! 😺.

## v3.3.5 (2019-04-22)

- [Feature] Pluggable LMS/CMS/forum.
- [Improvement] Safer environment overwrite. Thanks, @silviot! 👐.
- [Security] Fix Jinja2 vulnerability.
- [Improvement] Improve CLI cold start performance.
- [Improvement] Allow uppercase "Y" and "N" as answers to boolean questions.

## v3.3.4 (2019-04-09)

- [Improvement] Rename `--silent` option to `-y/--yes`.
- [Bugfix] Fix (again) login from studio when HTTPS is activated (#193).

## v3.3.3 (2019-03-29)

- [Bugfix] Fix `pip install tutor-openedx`.

## v3.3.2 (2019-03-27)

- [Bugfix] Fix login from localhost.
- [Bugfix] Fix Android app image build.

## v3.3.1 (2019-03-25)

- [Improvement] Improve assets building for development.
- [Improvement] Support CMS login when the CMS is not a subdomain of the LMS.

## v3.3.0 (2019-03-22)

- [Feature] Upgrade from Hawthorn to Ironwood.

## v3.2.2 (2019-03-21)

- [Feature] Multiple platforms on a single server \o/.
- [Feature] Easily configure web proxy on the host.
- [Bugfix] Fix `images pull all` command which failed on "all" image.
- [Improvement] Add configurable MongoDB, SMTP and RabbitMQ authentication.
- [Improvement] Harmonize MySQL username/password configuration parameters.
- [Feature] Configurable and pluggable data storage backends (#114).

## v3.2.1 (2019-03-19)

- [Feature] Enable grade downloads by default (#143).
- [Improvement] Remove orphan containers on `local start`.

## v3.2.0 (2019-03-18)

- [Improvement] `images pull` now also pulls vendor images.
- [Feature] Add convenient `config printvalue` command.
- [Feature] Customise docker registry.
- [Feature] Load configuration parameters from the system environment.
- [Improvement] Automatic environment re-generation after re-configuration.
- [Improvement] Error and interrupt handling in UI and web UI.
- [Bugfix] Fix missing webui env directory.

## v3.1.0 (2019-03-09)

- [Improvement] Install python requirements in virtual env in docker image.
- [Bugfix] Add missing volume for theme development.
- [Improvement] Rename "config [non]interactive" command to "config save [--silent]".
- [Improvement] More explicit logging during environment generation.
- [Improvement] Configurable docker images (#122).
- [Bugfix] Fix "android pullimage" command.
- [Improvement] Do not upgrade images as part of quickstart.
- [Bugfix] Fix USERID setup in development mode and various dev-related docs (#177).

## v3.0.6 (2019-02-26)

- [Bugfix] Fix import/export of demo course (#175).

## v3.0.5 (2019-02-14)

- [Feature] Add cloud deployment script.
- [Improvement] Run `images pull` command.
- [Improvement] Run `indexcourses` on importing demo course.
- [Improvement] Add `runserver stop` command.

## v3.0.4 (2019-02-13)

- [Minor] Minimum required `click` version is 7.0 (#171).
- [Bugfix] Fix `runserver` dev command (#172).
- [Minor] Fix non-https link to documentation in PyPI.
- [Minor] Fix `createuser` documentation.

## v3.0.3 (2019-02-12)

- [Bugfix] Add missing template data to the PyPI package.
- [Bugfix] Fix quickstart on Kubernetes (#164).
- [Improvement] Add databases task to Kubernetes quickstart (#167).

## v3.0.2 (2019-02-12)

- [Bugfix] Fix import paths -- 🚀 thanks @silviot!.
- [Bugfix] Properly set docker project name in MySQL logs -- 🦊 thanks again @silviot!.

## v3.0.1 (2019-02-11)

- [Bugfix] fix MySQL initialisation (#159, #160).
- [Improvement] Better handling of continuous integration.
- [Bugfix] fix `tutor --version` (#156).
- [Improvement] Absolute settings imports -- 📯 thanks @tonytan4ever!.

## v3.0.0 (2019-02-09)

- [Improvement] Complete rewrite of Tutor: switch from a make-based project to a single binary that runs all commands.
- [Feature] An web user interface can be created with `tutor webui start`.
- [Bugfix] Add missing Elasticsearch to Kubernetes deployment (#147).
- [Improvement] Upload `tutor-openedx` to PyPI .

## Older changes (< 3.0.0)

- 2019-01-27 [Bugfix] Fix video transcript/srt upload and download of user-uploaded files. Thanks @dannielariola!.
- 2019-01-20 [Improvement] Make it easy to load custom settings for the local production install.
- 2019-01-19 [Improvement] Upgrade to Ironwood.
- 2019-01-16 [Improvement] Switch license from MIT to AGPL.
- 2019-01-04 [Bugfix] Fix xqueue consumer command.
- 2018-12-26 [Improvement] Upgrade nodejs to 5.5.1.
- 2018-12-07 [Improvement] Bundle theme and production static assets in the openedx docker image.
- 2018-12-02 [Feature] Download extra locales from [openedx-i18n](https://github.com/openedx/openedx-i18n/) to the Open edX Docker image.
- 2018-11-28 [Feature] Easily change openedx docker image.
- 2018-11-28 [Feature] Enable comprehensive theming!.
- 2018-11-28 [Improvement] Get rid of datadog.
- 2018-11-28 [Improvement] Upgrade docker images to ubuntu 18.04 for android, forum, notes, xqueue.
- 2018-11-28 [Feature] Make it possible to define default platform language interactively.
- 2018-11-26 [Improvement] Make it easier to run a forked version of edx-platform.
- 2018-11-25 [Feature] Use local filesystem for open assessment file upload.
- 2018-11-23 [Improvement] Faster container bootstrapping without "chmod", as suggested by @silviot.
- 2018-11-20 [Bugfix] Fix cross-platform theme assets generation.
- 2018-11-17 [Improvement] Custom Nginx port mapping. :crossed_swords: @frob @frohro.
- 2018-11-17 [Improvement] Add "make restart-openedx" command. :+1: @frob.
- 2018-11-13 [Improvement] Facilitate install of extra XBlocks. Thanks @frob!.
- 2018-10-30 [Bugfix] Fix RabbitMQ restart policy.
- 2018-10-03 [Improvement/Bugfix] Fix and accelerate Android application build.
- 2018-10-02 [Improvement] Bump Open edX version to hawthorn.2.
- 2018-09-30 [Bugfix] Fix CMS celery worker, including export tasks.
- 2018-09-30 [Improvement] Simplify boolean feature flags definition.
- 2018-09-29 [Improvement] Add logging commands.
- 2018-09-29 [Improvement] Add self-documented help with "make help".
- 2018-09-29 [Feature] Add [Portainer](https://portainer.io) as an optional web UI to administer docker containers.
- 2018-09-15 [Feature] Add student notes as an optional feature.
- 2018-09-15 [Feature] Add templates to configurator container, which can now be run separately.
- 2018-09-15 [Improvement] Rename "up" and "daemon" commands to "run" and "daemonize".
- 2018-09-15 [Feature] Activate course search and discovery.
- 2018-09-15 [Bugfix] Deduplicate console logs from lms/cms.
- 2018-09-05 [Improvement] Use a single email address for all inbound email.
- 2018-09-04 [Bugfix] Get make commands to work with 'sudo'.
- 2018-09-02 [Bugfix] Get HTTPS to work for CMS. Thanks @flytreeleft!.
- 2018-08-28 [Bugfix] Fix certbot image updating.
- 2018-08-27 [Improvement] Add development requirements to openedx image.
- 2018-08-27 [Bugfix] Upgrade MongoDB.
- 2018-08-19 [Improvement] Make Xqueue an optional feature.
- 2018-08-16 [Feature] Add HTTPS support.
