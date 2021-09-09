# Changelog

Note: Breaking changes between versions are indicated by "💥".

## Unreleased

- [Feature] Add "openedx-dockerfile-post-git-checkout" patch.
- [Improvement] In the "openedx" Docker images, convert git patches to cherry-picks for a cleaner source tree.
- 💥[Feature] Make it possible to override local job configuration. This deprecates the older model for running jobs which dates back from a long time ago.

## v12.0.4 (2021-08-12)

- [Security] Apply security patch [28442](https://github.com/edx/edx-platform/pull/28442).

## v12.0.3 (2021-08-10)

- [Improvement] Upgrade all services to open-release/lilac.2.
- [Bugfix] Fix "`sh` is not a recognized command" in some plugins, including minio.
- [Improvement] Set the default contact mailing email address
- [Bugfix] Fix minio initialisation in Kubernetes.

## v12.0.2 (2021-07-06)

- [Bugfix] Fix "Invalid command argument" during upgrade from Koa to Lilac.
- [Bugfix] Fix mysql initialisation in docker-compose==2.0.0beta4.
- [Improvement] Tutor is now published on pypi as "tutor".

## v12.0.1 (2021-06-22)

- [Bugfix] Fix double pulling mongodb image when upgrading from Koa to Lilac.
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

- [Feature] Add redis database configuration for both cache and celery.

## v11.2.10 (2021-05-17)

- [Security] Apply Django security patches by upgrading from 2.2.20 to 2.2.23.
- [Bugfix] Fix video unit completion (see [pull request](https://github.com/edx/edx-platform/pull/27230)).

## v11.2.9 (2021-05-12)

- [Bugfix] Fix crashing installation because of a major release of all Pallets projects.
- [Bugfix] Fix crash in `local quickstart -p` command.
- [Bugfix] Fix 502 error on request to lms with header larger than the maximum uwsgi buffer size.

## v11.2.8 (2021-04-27)

- [Bugfix] Fix parsing of YAML-formatted values in ``config save --set KEY=VALUE`` commands, in use for instance with Ecommerce.

## v11.2.7 (2021-04-23)

- [Security] Apply security patch [27394](https://github.com/edx/edx-platform/pull/27394).
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
- [Improvement] Add openedx patches to add settings during build process.

## v11.2.3 (2021-02-20)

- [Bugfix] Make LMS celery workers actually process LMS tasks, and not CMS tasks.

## v11.2.2 (2021-02-17)

- [Security] Apply security patch [26592](https://github.com/edx/edx-platform/pull/26592).

## v11.2.1 (2021-02-16)

- [Bugfix] Actually persist Redis data.

## v11.2.0 (2021-02-10)

- [Bugfix] Upgrade all services to open-release/koa.2.

## v11.1.5 (2021-02-09)

- [Security] Apply security patch [26432](https://github.com/edx/edx-platform/pull/26432).
- [Bugfix] Print warnings to stderr.

## v11.1.4 (2021-02-04)

- [Security] Apply security patch [26358](https://github.com/edx/edx-platform/pull/26358).

## v11.1.3 (2021-01-31)

- [Security] Apply security patch [26253](https://github.com/edx/edx-platform/pull/26253).

## v11.1.2 (2021-01-29)

- [Bugfix] Fix django setting value and static asset loading in openedx-dev image.

## v11.1.1 (2021-01-20)

- [Feature] Add a `tutor images build --target=...` argument for [multi-stage Docker builds](https://docs.docker.com/develop/develop-images/multistage-build/).
- [Feature] Create a test version of the openedx-dev Docker image for running edx-platform unit tests.
- [Security] Apply security patch [26112](https://github.com/edx/edx-platform/pull/26112).
- [Bugfix] Fix `local exec` command which crashed with a `AttributeError`.

## v11.1.0 (2021-01-13)

- [Bugfix] Fix "Read-only file system" errors when running `tutor dev runserver` commands on Mac OS (again, see #392).
- [Feature] Automatically bind-mount volumes from the `volumes/` directory with the `--volume=/...` syntax.

## v11.0.7 (2021-01-11)

- [Security] Apply security patch [26029](https://github.com/edx/edx-platform/pull/26029).

## v11.0.6 (2021-01-05)

- [Security] Apply security patch [25974](https://github.com/edx/edx-platform/pull/25974).

## v11.0.5 (2020-12-30)

- [Bugfix] Fix "Invalid type for parameter ContentType" error on js upload in Scorm xblock ([openedx-scorm-xblock #16](https://github.com/overhangio/openedx-scorm-xblock/issues/16)).

## v11.0.4 (2020-12-17)

- [Bugfix] Fix "Read-only file system" errors when running `tutor dev runserver` commands on Mac OS (#392).

## v11.0.3 (2020-12-15)

- [Bugfix] Fix upload of video transcripts to S3 (again).

## v11.0.2 (2020-12-12)

- [Bugfix] Fix missing celery tasks from edx-platform (see [upstream PR](https://github.com/edx/edx-platform/pull/25840)).

## v11.0.1 (2020-12-10)

- [Security] Apply security patch [25834](https://github.com/edx/edx-platform/pull/25834).
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
            - Nginx no longer listens to port 443 for https traffic.
            - The Caddy configuration file comes with a new ``caddyfile`` patch for much simpler SSL/TLS management.
            - Configuration files for web proxies are no longer provided.
            - Kubernetes deployment no longer requires setting up a custom Ingress resource or custom manager.
        - Gunicorn and Whitenoise are replaced by uwsgi: this increases boostrap performance and makes it no longer necessary to mount media folders in the Nginx container.
        - Replace memcached and rabbitmq by redis.
    - Additional features:
        - Make it possible to disable all plugins at once with ``plugins disable all``.
        - Add ``tutor k8s wait`` command to wait for a pod to become ready.
        - Faster, more reliable static assets with local memory caching.
    - Deprecation: proxy files for Apache and Nginx are no longer provided out of the box.
    - Removed plugin `{{ patch (...) }}` statements:
        - "https-create", "k8s-ingress-rules", "k8s-ingress-tls-hosts": these are no longer necessary. Instead, declare your app in the "caddyfile" patch.
        - "local-docker-compose-nginx-volumes": this patch was primarily used to serve media assets. The recommended is now to serve assets with uwsgi.

## v10.5.3 (2020-12-09)

- [Security] Apply upstream edx-platform [security patch](https://github.com/edx/edx-platform/pull/25782).

## v10.5.2 (2020-12-07)

- [Improvement] Increase the timeout of the gunicorn worker command in openedx Dockerfile.

## v10.5.1 (2020-11-30)

- [Bugfix] Fix Dockerfile parsing on Windows.
- [Improvement] Add option to patch lms and cms nginx server blocks.

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
- [Bugfix] Fix podman compatibility by replacing `docker-compose rm` command by `docker-compose stop` when stopping containers.
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
- [Security] Apply javascript security patch ([pull request](https://github.com/edx/edx-platform/pull/24762)).
- [Bugfix] Fix "FileError" on Scorm package upload in Scorm XBlock.
- 💥[Improvement] Serve openedx static assets with [whitenoise](http://whitenoise.evans.io/en/stable/) instead of nginx. This removes the `k8s-deployments-nginx-init-containers` patch. Plugins are encouraged to implement static asset serving with Whitenoise as well.
- [Bugfix] Fix dependency on mysql service when mysql is not activated.
- [Improvement] Improve openedx Docker image build time and size with multi-stage build.
- 💥[Feature] Get rid of outdated sysadmin dashboard in LMS at /sysadmin.

## v10.1.0 (2020-07-23)

- [Security] Apply edx-platform upstream xss security fixes ([pull request](https://github.com/edx/edx-platform/pull/24568)).
- 💥[Feature] Make it possible to override the docker registry for just a few services by setting `DOCKER_IMAGE_SERVICENAME` values.

## v10.0.11 (2020-07-16)

- [Feature] Upgrade all repositories to open-release/juniper.3.
- [Bugfix] Fix `reload-gunicorn` command.
- [Feature] Enable sysadmin dashboard in LMS at /sysadmin.

## v10.0.10 (2020-07-01)

- [Bugfix] Fix pycontracts installation error when building openedx Docker image.
- [Bugfix] Fix access to dicussion forum in development mode.

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

- [Security] Apply edx-platform upstream xss security fixes ([pull request](https://github.com/edx/edx-platform/pull/24258)).

## v10.0.4 (2020-06-19)

- [Bugfix] Fix broken `tutor ui` command in binary.

## v10.0.3 (2020-06-19)

- [Bugfix] Fix error on android user creation.

## v10.0.2 (2020-06-17)

- [Bugfix] Fix crash when viewing problem in LMS.
- [Bugfix] Fix missing webpack-stats.json in openedx Docker image.

## v10.0.1 (2020-06-15)

- [Bugfix] Fix KeyError when running ``local quickstart`` for the first time.

## v10.0.0 (2020-06-15)

- 💥[Improvement] Upgrade to Juniper 🍾.
- [Bugfix] Fix nginx resolver address to address container restarts.
- [Feature] Add `--limit=myplugin` option to `init` commands to limit execution of initialisation to certain services and plugins.

## v3.12.6 (2020-06-01)

- [Improvement] Add `dig`, `ping` utilities to openedx-dev Docker image.
- [Bugfix] Resolve "Can't connect to MySQL server" on init.
- [Improvement] Make it possible to customize the MySQL root username, for connecting to external MySQL databases.

## v3.12.5 (2020-05-20)

- [Improvement] Upgrade Android app to v2.21.1 and enable many features, such as downloading videos to SD card. Thanks for the help @ejklock!.
- [Bugfix] Fix Android app crash when accessing course.

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

- 💥[Improvement] Do not deploy an ingress or SSL/TLS certificate issuer ressource by default in Kubernetes.
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

- [Feature] Add `encrypt` template filter to conveniently add htpasswd-based authentication to nginx.
- [Bugfix] Fix "missing tty" during init in cron jobs.

## v3.11.7 (2020-04-01)

- [Bugfix] Fix missing js translations.
- [Bugfix] Fix tls certificate generation in cron jobs.

## v3.11.6 (2020-03-13)

- [Bugfix] Fix "Unable to resolve dependency" error during forum initialisation.
- [Feature] Add `settheme` command to easily assign a theme to a domain name.
- [Improvement] Modify nginx access logs to include request scheme and server name (plugin developers should use the "tutor" log format).
- [Bugfix] Fix DNS resolution of restarted service.
- [Feature] Restart multiple services with `local restart`.
- [Feature] Make it possible to easily reload openedx gunicorn process with `tutor local exec lms reload-gunicorn`.
- [Improvement] Rename lms/cms_worker to lms/cms-worker in local deployment.
- [Improvement] Add the management plugin to the rabbitmq container.
- [Improvement] Make it possible to run an Elasticsearch service on https.

## v3.11.5 (2020-02-27)

- [Improvement] Switch edx-platform from open-release/ironwood.2 tag to the open-release/ironwood.master branch.
- [Security] Upgrade django to 1.11.28.
- [Improvement] Make it possible to configure the elasticsearch heap size.
- [Bugfix] Fix broken elasticsearch environment variables.
- [Improvement] Restore more recent Android app version (#289).

## v3.11.4 (2020-02-16)

- [Bugfix] Fix auth problem in Android app (#289).

## 3.11.3 (2020-01-21)

- [Bugfix] Fix incorrectly parsed empty strings for `config save --set ...=...` commands.

## 3.11.2 (2020-01-17)

- [Bugfix] Make sure `docker-compose.override.yml` are loaded in dev and local contexts.

## 3.11.1 (2020-01-16)

- [Feature] Add `config render` command.

## 3.11.0 (2020-01-14)

- [Feature] Add support for simple, YAML-based plugins.
- 💥[Improvement] The output of `plugins list` now includes plugin version numbers.

## 3.10.1 (2020-01-13)

- [Improvement] Explicitly point to docker.io images, when necessary, for [podman](https://podman.io/) compatibility.

## 3.10.0 (2020-01-10)

- [Bugfix] Fix oauth authentication in dev mode.
- [Improvement] Upgrade to the 3.7 docker-compose syntax.
- [Improvement] The `dev runserver` command can now be run for just any service.
- 💥[Feature] `dev run/exec` commands now support generic options which are passed to docker-compose. Consequently, defining the `TUTOR_EDX_PLATFORM_PATH` environment variable no longer works. Instead, users are encouraged to explicitly pass the `-v` option, define a command alias or create a `docker-compose.override.yml` file.

## 3.9.1 (2020-01-08)

- [Improvement] Make it possible to override the project name in development mode.
- [Bugfix] Fix user switching in development mode.
- [Bugfix] Fix "k8s quickstart" crash.

## 3.9.0 (2019-12-21)

- [Security] Apply django 1.11.21 -> 1.11.27 security patches.
- [Bugfix] Fix running dev image with `sudo`.
- [Improvement] Add `cms/lms-env-features` patches (#276).
- [Feature] Add plugin subcommands.
- 💥[Improvement] Move ``-r/--root`` option to parent command level.
- [Bugfix] Fix course about page visibility.
- [Improvement] Print gunicorn access logs in the console.
- 💥[Improvement] Get rid of the `indexcourses` and `portainer` command (#269).

## 3.8.0 (2019-11-22)

- [Improvement] Add `k8s-deployments-nginx-volume-mounts` patch.
- [Bugfix] Fix running forum locally when both elasticsearch and mongodb are not activated (#266).
- [Bugfix] Fix MongoDb url in forum when running separate service (#267).
- 💥[Improvement] Better `dev` commands, with dedicated development docker image. One of the consequences is that the `dev watchthemes` command is replaced by `dev run lms watchthemes`.
- [Improvement] `images` commands now accept multiple `image` arguments.

## 3.7.4 (2019-10-19)

- [Bugfix] Fix missing requirements file in pypi package (#261).
- [Improvement] Add missing cms/lms production/development setting patches.
- [Improvement] Allow SigV4 authentication for video upload to S3.
- [Bugfix] Fix cms development settings.

## 3.7.3 (2019-10-17)

- [Improvement] Upgrade openedx locales to Ironwood.

## 3.7.2 (2019-10-09)

- [Improvement] Properly set studio title (#246).
- [Improvement] Enable Mysql strict mode.

## 3.7.1 (2019-10-06)

- [Feature] Introduce tutor docker image.
- [Feature] Introduce `local hook` command for plugin development.
- [Bugfix] Persist `private.txt` file between two runs of `config save` (#247).
- [Improvement] Added configuration values to limit the number of gunicorn workers for the LMS and CMS.

## 3.7.0 (2019-09-03)

- 💥[Improvement] Get rid of mysql-client container.
- [Improvement] Add "local-docker-compose-lms/cms-dependencies" plugin patches.
- [Improvement] Use "exec" instead of "run" to initialise local platform.

## 3.6.3 (2019-08-31)

- [Security] Fix CustomTagModule mako template injection.
- [Improvement] Move all plugins outside of the tutor repo.
- [Bugfix/Improvement] Add all plugins (with data) into binary bundle (#242).

## 3.6.2 (2019-08-07)

- [Bugfix] Fix missing templates in bundled plugins.
- [Bugfix] Enable html certificate view.

## 3.6.1 (2019-07-27)

- [Bugfix] Fix missing patches from minio plugin (thanks @Wejie!).

## 3.6.0 (2019-07-11)

- [Feature] Modify ``createuser`` commands to define a password from the command line.
- [Improvement] Better yaml value parsing from command line.
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

## 3.5.3 (2019-07-05)

- [Bugfix] Add pre-init hook for correct initialisation of minio.

## 3.5.2 (2019-07-05)

- [Security] Apply certificate XSS security patch.

## 3.5.1 (2019-07-04)

- [Feature] Make it possible for plugins to patch the build templates.
- [Improvement] Move Xqueue and Student notes to a dedicated plugin.

## 3.4.3 (2019-06-24)

- [Bugfix] Fix missing password values from generated configuration.

## 3.4.2 (2019-06-23)

- [Bugfix] Fix incorrect settings during lms/cms init (#224).

## 3.4.1 (2019-06-23)

- [Bugfix] Fix install from pypi.
- [Improvement] Get rid of kubernetes python package dependency.

## 3.4.0 (2019-06-17)

- [Feature] Creation of a plugin system.
- [Feature] Kubernetes support out of beta.
- [Improvement] Switch to pinned image tags for easier upgrades.
- 💥[Improvement] Remove the `-y/--yes` option: `tutor config save` is now non-interactive by default. Use `-i/--interactive` to force interactive mode.
- 💥[Improvement] Replace the `databases` command by `init`.
- [Improvement] Upgrade to ironwood.2.
- [Improvement] Add `-y/--yes` option to `local quickstart` for non-interactive quickstart.
- [Improvement] Persist LMS/CMS logs to disk by default (with collaboration from @silviot 💪).
- [Bugfix] Fix installing a locally cloned requirement repository.
- [Improvement] Add `--no-cache` option to `images build`.
- [Improvement] Make it possible to configure the notes service hostname.
- [Improvement] Better, more robust MySQL initialisation.

## 3.3.10 (2019-05-15)

- [Bugfix] Fix boolean configuration choices.

## 3.3.9 (2019-05-13)
- [Improvement] Add `local exec` command for running commands inside existing containers.
- [Bugfix] Fix triple display of courses in LMS search (upstream patch, #189).

## 3.3.8 (2019-04-28)

- [Bugfix] Reduce the number of gunicorn workers to address RAM usage (#207).

## 3.3.7 (2019-04-28)

- [Bugfix] Fix "Timeout after 20s" on running migrations.

## 3.3.6 (2019-04-27)

- [Bugfix] Fix KeyError on first quickstart.
- [Improvement] De-duplication of prod/dev settings. Thanks @silviot! 😺.

## 3.3.5 (2019-04-22)

- [Feature] Pluggable LMS/CMS/forum.
- [Improvement] Safer environment overwrite. Thanks @silviot! 👐.
- [Security] Fix Jinja2 vulnerability.
- [Improvement] Improve CLI cold start performance.
- [Improvement] Allow uppercase "Y" and "N" as answers to boolean questions.

## 3.3.4 (2019-04-09)

- [Improvement] Rename `--silent` option to `-y/--yes`.
- [Bugfix] Fix (again) login from studio when https is activated (#193).

## 3.3.3 (2019-03-29)

- [Bugfix] Fix `pip install tutor-openedx`.

## 3.3.2 (2019-03-27)

- [Bugfix] Fix login from localhost.
- [Bugfix] Fix Android app image build.

## 3.3.1 (2019-03-25)

- [Improvement] Improve assets building for development.
- [Improvement] Support CMS login when the CMS is not a subdomain of the LMS.

## 3.3.0 (2019-03-22)

- [Feature] Upgrade from Hawthorn to Ironwood.

## 3.2.2 (2019-03-21)

- [Feature] Multiple platforms on a single server \o/.
- [Feature] Easily configure web proxy on the host.
- [Bugfix] Fix `images pull all` command which failed on "all" image.
- [Improvement] Add configurable mongodb, SMTP and rabbitmq authentication.
- [Improvement] Harmonize mysql username/password configuration parameters.
- [Feature] Configurable and pluggable data storage backends (#114).

## 3.2.1 (2019-03-19)

- [Feature] Enable grade downloads by default (#143).
- [Improvement] Remove orphan containers on `local start`.

## 3.2.0 (2019-03-18)

- [Improvement] `images pull` now also pulls vendor images.
- [Feature] Add convenient `config printvalue` command.
- [Feature] Customize docker registry.
- [Feature] Load configuration parameters from the system environment.
- [Improvement] Automatic environment re-generation after re-configuration.
- [Improvement] Error and interrupt handling in UI and web UI.
- [Bugfix] Fix missing webui env directory.

## 3.1.0 (2019-03-09)

- [Improvement] Install python requirements in virtual env in docker image.
- [Bugfix] Add missing volume for theme development.
- [Improvement] Rename "config [non]interactive" command to "config save [--silent]".
- [Improvement] More explicit logging during environment generation.
- [Improvement] Configurable docker images (#122).
- [Bugfix] Fix "android pullimage" command.
- [Improvement] Do not upgrade images as part of quickstart.
- [Bugfix] Fix USERID setup in development mode and various dev-related docs (#177).

## 3.0.6 (2019-02-26)

- [Bugfix] Fix import/export of demo course (#175).

## 3.0.5 (2019-02-14)

- [Feature] Add cloud deployment script.
- [Improvement] Run `images pull` command.
- [Improvement] Run `indexcourses` on importing demo course.
- [Improvement] Add `runserver stop` command.

## 3.0.4 (2019-02-13)

- [Minor] Minimum required `click` version is 7.0 (#171).
- [Bugfix] Fix `runserver` dev command (#172).
- [Minor] Fix non-https link to documentation in pypi.
- [Minor] Fix `createuser` documentation.

## 3.0.3 (2019-02-12)

- [Bugfix] Add missing template data to pypi package.
- [Bugfix] Fix quickstart on Kubernetes (#164).
- [Improvement] Add datatases task to Kubernetes quickstart (#167).

## 3.0.2 (2019-02-12)

- [Bugfix] Fix import paths -- 🚀 thanks @silviot!.
- [Bugfix] Properly set docker project name in mysql logs -- 🦊 thanks again @silviot!.

## 3.0.1 (2019-02-11)

- [Bugfix] fix mysql initialisation (#159, #160).
- [Improvement] Better handling of continuous integration.
- [Bugfix] fix `tutor --version` (#156).
- [Improvement] Absolute settings imports -- 📯 thanks @tonytan4ever!.

## 3.0.0 (2019-02-09)

- [Improvement] Complete rewrite of Tutor: switch from a make-based project to a single binary which runs all commands.
- [Feature] An web user interface can be created with `tutor webui start`.
- [Bugfix] Add missing elasticsearch to Kubernetes deployment (#147).
- [Improvement] Upload `tutor-openedx` to pypi.

## Older changes

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
- 2018-11-17 [Improvement] Custom nginx port mapping. :crossed_swords: @frob @frohro.
- 2018-11-17 [Improvement] Add "make restart-openedx" command. :+1: @frob.
- 2018-11-13 [Improvement] Facilitate install of extra XBlocks. Thanks @frob!.
- 2018-10-30 [Bugfix] Fix rabbitmq restart policy.
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
- 2018-08-27 [Bugfix] Upgrade mongodb.
- 2018-08-19 [Improvement] Make Xqueue an optional feature.
- 2018-08-16 [Feature] Add HTTPS support.
