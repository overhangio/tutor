# Changelog

## v3.3.3 (2019-03-27)

- [Bugfix] Fix login from localhost

## v3.3.2 (2019-03-27)

- [Bugfix] Fix Android app image build

## 3.3.1 (2019-03-25)

- [Improvement] Improve assets building for development
- [Improvement] Support CMS login when the CMS is not a subdomain of the LMS

## 3.3.0 (2019-03-22)

- [Feature] Upgrade from Hawthorn to Ironwood

## 3.2.2 (2019-03-21)

- [Feature] Multiple platforms on a single server \o/
- [Feature] Easily configure web proxy on the host
- [Bugfix] Fix `images pull all` command which failed on "all" image
- [Improvement] Add configurable mongodb, SMTP and rabbitmq authentication
- [Improvement] Harmonize mysql username/password configuration parameters
- [Feature] Configurable and pluggable data storage backends (#114)

## 3.2.1 (2019-03-19)

- [Feature] Enable grade downloads by default (#143)
- [Improvement] Remove orphan containers on `local start`

## 3.2.0 (2019-03-18)

- [Improvement] `images pull` now also pulls vendor images
- [Feature] Add convenient `config printvalue` command
- [Feature] Customize docker registry
- [Feature] Load configuration parameters from the system environment
- [Improvement] Automatic environment re-generation after re-configuration
- [Improvement] Error and interrupt handling in UI and web UI
- [Bugfix] Fix missing webui env directory

## 3.1.0 (2019-03-09)

- [Improvement] Install python requirements in virtual env in docker image
- [Bugfix] Add missing volume for theme development
- [Improvement] Rename "config [non]interactive" command to "config save [--silent]"
- [Improvement] More explicit logging during environment generation
- [Improvement] Configurable docker images (#122)
- [Bugfix] Fix "android pullimage" command
- [Improvement] Do not upgrade images as part of quickstart
- [Bugfix] Fix USERID setup in development mode and various dev-related docs (#177)

## 3.0.6 (2019-02-26)

- [Bugfix] Fix import/export of demo course (#175)

## 3.0.5 (2019-02-14)

- [Feature] Add cloud deployment script
- [Improvement] Run `images pull` command
- [Improvement] Run `indexcourses` on importing demo course 
- [Improvement] Add `runserver stop` command

## 3.0.4 (2019-02-13)

- [Minor] Minimum required `click` version is 7.0 (#171)
- [Bugfix] Fix `runserver` dev command (#172)
- [Minor] Fix non-https link to documentation in pypi
- [Minor] Fix `createuser` documentation

## 3.0.3 (2019-02-12)

- [Bugfix] Add missing template data to pypi package
- [Bugfix] Fix quickstart on Kubernetes (#164)
- [Improvement] Add datatases task to Kubernetes quickstart (#167)

## 3.0.2 (2019-02-12)

- [Bugfix] Fix import paths -- 🚀 thanks @silviot!
- [Bugfix] Properly set docker project name in mysql logs -- 🦊 thanks again @silviot!

## 3.0.1 (2019-02-11)

- [Bugfix] fix mysql initialization (#159, #160)
- [Improvement] Better handling of continuous integration
- [Bugfix] fix `tutor --version` (#156)
- [Improvement] Absolute settings imports -- 📯 thanks @tonytan4ever!

## 3.0.0 (2019-02-09)

- [Improvement] Complete rewrite of Tutor: switch from a make-based project to a single binary which runs all commands.
- [Feature] An web user interface can be created with `tutor webui start`
- [Bugfix] Add missing elasticsearch to Kubernetes deployment (#147)
- [Improvement] Upload `tutor-openedx` to pypi

## Older changes

- 2019-01-27 [Bugfix] Fix video transcript/srt upload and download of user-uploaded files. Thanks @dannielariola!
- 2019-01-20 [Improvement] Make it easy to load custom settings for the local production install
- 2019-01-19 [Improvement] Upgrade to Ironwood
- 2019-01-16 [Improvement] Switch license from MIT to AGPL
- 2019-01-04 [Bugfix] Fix xqueue consumer command
- 2018-12-26 [Improvement] Upgrade nodejs to 5.5.1
- 2018-12-07 [Improvement] Bundle theme and production static assets in the openedx docker image
- 2018-12-02 [Feature] Download extra locales from [openedx-i18n](https://github.com/regisb/openedx-i18n/) to the Open edX Docker image
- 2018-11-28 [Feature] Easily change openedx docker image
- 2018-11-28 [Feature] Enable comprehensive theming!
- 2018-11-28 [Improvement] Get rid of datadog
- 2018-11-28 [Improvement] Upgrade docker images to ubuntu 18.04 for android, forum, notes, xqueue
- 2018-11-28 [Feature] Make it possible to define default platform language interactively
- 2018-11-26 [Improvement] Make it easier to run a forked version of edx-platform
- 2018-11-25 [Feature] Use local filesystem for open assessment file upload
- 2018-11-23 [Improvement] Faster container bootstrapping without "chmod", as suggested by @silviot
- 2018-11-20 [Bugfix] Fix cross-platform theme assets generation
- 2018-11-17 [Improvement] Custom nginx port mapping. :crossed_swords: @frob @frohro
- 2018-11-17 [Improvement] Add "make restart-openedx" command. :+1: @frob
- 2018-11-13 [Improvement] Facilitate install of extra XBlocks. Thanks @frob!
- 2018-10-30 [Bugfix] Fix rabbitmq restart policy
- 2018-10-03 [Improvement/Bugfix] Fix and accelerate Android application build
- 2018-10-02 [Improvement] Bump Open edX version to hawthorn.2
- 2018-09-30 [Bugfix] Fix CMS celery worker, including export tasks
- 2018-09-30 [Improvement] Simplify boolean feature flags definition
- 2018-09-29 [Improvement] Add logging commands
- 2018-09-29 [Improvement] Add self-documented help with "make help"
- 2018-09-29 [Feature] Add [Portainer](https://portainer.io) as an optional web UI to administer docker containers
- 2018-09-15 [Feature] Add student notes as an optional feature
- 2018-09-15 [Feature] Add templates to configurator container, which can now be run separately
- 2018-09-15 [Improvement] Rename "up" and "daemon" commands to "run" and "daemonize"
- 2018-09-15 [Feature] Activate course search and discovery
- 2018-09-15 [Bugfix] Deduplicate console logs from lms/cms
- 2018-09-05 [Improvement] Use a single email address for all inbound email
- 2018-09-04 [Bugfix] Get make commands to work with 'sudo'
- 2018-09-02 [Bugfix] Get HTTPS to work for CMS. Thanks @flytreeleft!
- 2018-08-28 [Bugfix] Fix certbot image updating
- 2018-08-27 [Improvement] Add development requirements to openedx image
- 2018-08-27 [Bugfix] Upgrade mongodb
- 2018-08-19 [Improvement] Make Xqueue an optional feature
- 2018-08-16 [Feature] Add HTTPS support
