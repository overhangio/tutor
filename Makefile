.PHONY: all android configure build update migrate run
.DEFAULT_GOAL := help


PWD ?= $$(pwd)
USERID ?= $$(id -u)
EDX_PLATFORM_SETTINGS ?= universal.production
DOCKER_COMPOSE = docker-compose -f docker-compose.yml
-include $(PWD)/config/Makefile.env

post_configure_targets =
ifneq ($(DISABLE_STATS), 1)
	post_configure_targets += stats
endif
ifeq ($(ACTIVATE_HTTPS), 1)
	post_configure_targets += https-certificate
endif
extra_migrate_targets = 
ifeq ($(ACTIVATE_XQUEUE), 1)
	extra_migrate_targets += migrate-xqueue
	DOCKER_COMPOSE += -f docker-compose-xqueue.yml
endif
ifeq ($(ACTIVATE_NOTES), 1)
	extra_migrate_targets += migrate-notes
	DOCKER_COMPOSE += -f docker-compose-notes.yml
endif
ifeq ($(ACTIVATE_PORTAINER), 1)
	DOCKER_COMPOSE += -f docker-compose-portainer.yml
endif

DOCKER_COMPOSE_RUN = $(DOCKER_COMPOSE) run --rm
DOCKER_COMPOSE_RUN_OPENEDX = $(DOCKER_COMPOSE_RUN) -e USERID=$(USERID) -e SETTINGS=$(EDX_PLATFORM_SETTINGS)
ifneq ($(EDX_PLATFORM_PATH),)
	DOCKER_COMPOSE_RUN_OPENEDX += --volume="$(EDX_PLATFORM_PATH):/openedx/edx-platform"
endif

DOCKER_COMPOSE_RUN_LMS = $(DOCKER_COMPOSE_RUN_OPENEDX) -p 8000:8000 lms
DOCKER_COMPOSE_RUN_CMS = $(DOCKER_COMPOSE_RUN_OPENEDX) -p 8001:8001 cms

##################### Running Open edX

# other targets are not listed as requirements in order to reload the env file
all: configure ## Configure and run a full-featured platform
	@$(MAKE) post_configure
	@$(MAKE) update
	@$(MAKE) databases
	@$(MAKE) assets
	@$(MAKE) daemonize
	@echo "All set \o/ You can access the LMS at http://localhost and the CMS at http://studio.localhost"

run: ## Run the complete platform
	$(DOCKER_COMPOSE) up
up: run

daemonize: ## Run the complete platform, with daemonization
	$(DOCKER_COMPOSE) up -d
	@echo "Daemon is up and running"
daemon: daemonize

stop: ## Stop all services
	$(DOCKER_COMPOSE) rm --stop --force

##################### Configuration

configure: build-configurator ## Configure the environment prior to running the platform
	docker run --rm -it --volume="$(PWD)/config:/openedx/config" \
		-e USERID=$(USERID) -e SILENT=$(SILENT) $(CONFIGURE_OPTS) \
		regis/openedx-configurator:hawthorn

post_configure: $(post_configure_targets)

##################### Database

databases: provision-databases migrate provision-oauth2 ## Bootstrap databases

provision-databases: ## Create necessary databases and users
	$(DOCKER_COMPOSE_RUN) lms /openedx/config/provision.sh
provision-oauth2: ## Create users for SSO between services
	$(DOCKER_COMPOSE_RUN) lms /openedx/config/oauth2.sh

migrate: migrate-openedx migrate-forum $(extra_migrate_targets) ## Perform all database migrations
migrate-openedx: ## Perform database migrations on LMS/CMS
	$(DOCKER_COMPOSE_RUN) lms bash -c "dockerize -wait tcp://mysql:3306 -timeout 20s && ./manage.py lms migrate"
	$(DOCKER_COMPOSE_RUN) cms bash -c "dockerize -wait tcp://mysql:3306 -timeout 20s && ./manage.py cms migrate"
	$(MAKE) reindex-courses
migrate-forum: ## Perform database migrations on discussion forums
	$(DOCKER_COMPOSE_RUN) forum bash -c "bundle exec rake search:initialize && \
		bundle exec rake search:rebuild_index"
migrate-notes: ## Perform database migrations for the Notes service
	$(DOCKER_COMPOSE_RUN) notes ./manage.py migrate
migrate-xqueue: ## Perform database migrations for the XQueue service
	$(DOCKER_COMPOSE_RUN) xqueue ./manage.py migrate
reindex-courses: ## Refresh course index so they can be found in the LMS search engine
	$(DOCKER_COMPOSE_RUN) cms ./manage.py cms reindex_course --all --setup

##################### Static assets

# To collect assets we don't rely on the "paver update_assets" command because
# webpack collection incorrectly sets the NODE_ENV variable when using custom
# settings. Thus, each step must be performed separately. This should be fixed
# in the next edx-platform release thanks to https://github.com/edx/edx-platform/pull/18430/
#assets-lms: ## Collect static assets for the LMS
	#$(DOCKER_COMPOSE_RUN_OPENEDX) lms -e NO_PREREQ_INSTALL=True lms paver update_assets lms --settings=$(EDX_PLATFORM_SETTINGS)
#assets-cms: ## Collect static assets for the CMS
	#$(DOCKER_COMPOSE_RUN_OPENEDX) cms -e NO_PREREQ_INSTALL=True cms paver update_assets cms --settings=$(EDX_PLATFORM_SETTINGS)

assets: assets-lms assets-cms ## Generate production-ready static assets
assets-development: assets-development-lms assets-development-cms ## Generate static assets for local development

assets-lms:
	$(DOCKER_COMPOSE_RUN_OPENEDX) lms bash -c \
		"NODE_ENV=production ./node_modules/.bin/webpack --config=webpack.prod.config.js \
		&& ./manage.py lms --settings=$(EDX_PLATFORM_SETTINGS) compile_sass lms \
		&& python -c \"import pavelib.assets; pavelib.assets.collect_assets(['lms'], '$(EDX_PLATFORM_SETTINGS)')\""
assets-cms:
	$(DOCKER_COMPOSE_RUN_OPENEDX) cms bash -c \
		"NODE_ENV=production ./node_modules/.bin/webpack --config=webpack.prod.config.js \
		&& ./manage.py cms --settings=$(EDX_PLATFORM_SETTINGS) compile_sass studio \
		&& python -c \"import pavelib.assets; pavelib.assets.collect_assets(['studio'], '$(EDX_PLATFORM_SETTINGS)')\""
assets-development-lms:
	$(DOCKER_COMPOSE_RUN_OPENEDX) lms bash -c \
		"xmodule_assets common/static/xmodule \
		&& python -c \"import pavelib.assets; pavelib.assets.process_npm_assets()\"
		&& NODE_ENV=development ./node_modules/.bin/webpack --config=webpack.dev.config.js \
		&& ./manage.py lms --settings=$(EDX_PLATFORM_SETTINGS) compile_sass lms \
		&& python -c \"import pavelib.assets; pavelib.assets.collect_assets(['lms'], '$(EDX_PLATFORM_SETTINGS)')\""
assets-development-cms:
	$(DOCKER_COMPOSE_RUN_OPENEDX) cms bash -c \
		"xmodule_assets common/static/xmodule \
		&& python -c \"import pavelib.assets; pavelib.assets.process_npm_assets()\"
		&& NODE_ENV=development ./node_modules/.bin/webpack --config=webpack.dev.config.js \
		&& ./manage.py cms --settings=$(EDX_PLATFORM_SETTINGS) compile_sass studio \
		&& python -c \"import pavelib.assets; pavelib.assets.collect_assets(['studio'], '$(EDX_PLATFORM_SETTINGS)')\""
	

##################### Information

# Obtained by running "echo '\033' in a shell
ESCAPE = 
help: ## Print this help
	@grep -E '^([a-zA-Z_-]+:.*?## .*|######* .+)$$' Makefile \
		| sed 's/######* \(.*\)/\n               $(ESCAPE)[1;31m\1$(ESCAPE)[0m/g' \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-30s\033[0m %s\n", $$1, $$2}'

info: ## Print some information about the current install, for debugging
	uname -a
	@echo "-------------------------"
	git rev-parse HEAD
	@echo "-------------------------"
	docker version
	@echo "-------------------------"
	docker-compose --version
	@echo "-------------------------"
	echo $$EDX_PLATFORM_PATH
	echo $$EDX_PLATFORM_SETTINGS


#################### Logging

logs: ## Print all logs from a service since it started. E.g: "make logs service=lms", "make logs service=nginx"
	$(DOCKER_COMPOSE) logs $(service)
tail: ## Similar to "tail" on the logs of a service. E.g: "make tail service=lms", "make tail service=nginx"
	$(DOCKER_COMPOSE) logs --tail=10 $(service)
tail-follow: ## Similar to "tail -f" on the logs of a service. E.g: "make tail-follow service=lms", "make tail-follow service=nginx"
	$(DOCKER_COMPOSE) logs --tail=10 -f $(service)

#################### Docker image building & updating

update: ## Download most recent images
	$(DOCKER_COMPOSE) pull

build: build-openedx build-configurator build-forum build-notes build-xqueue build-android ## Build all docker images
build-openedx: ## Build the Open edX docker image
	docker build -t regis/openedx:latest -t regis/openedx:hawthorn openedx/
build-configurator: ## Build the configurator docker image
	docker build -t regis/openedx-configurator:latest -t regis/openedx-configurator:hawthorn configurator/
build-forum: ## Build the forum docker image
	docker build -t regis/openedx-forum:latest -t regis/openedx-forum:hawthorn forum/
build-notes: ## Build the Notes docker image
	docker build -t regis/openedx-notes:latest -t regis/openedx-notes:hawthorn notes/
build-xqueue: ## Build the Xqueue docker image
	docker build -t regis/openedx-xqueue:latest -t regis/openedx-xqueue:hawthorn xqueue/
build-android: ## Build the docker image for Android 
	docker build -t regis/openedx-android:latest android/

################### Pushing images to docker hub

push: push-openedx push-configurator push-forum push-notes push-xqueue push-android ## Push all images to dockerhub
push-openedx: ## Push Open edX images to dockerhub
	docker push regis/openedx:hawthorn
	docker push regis/openedx:latest
push-configurator: ## Push configurator image to dockerhub
	docker push regis/openedx-configurator:hawthorn
	docker push regis/openedx-configurator:latest
push-forum: ## Push forum image to dockerhub
	docker push regis/openedx-forum:hawthorn
	docker push regis/openedx-forum:latest
push-notes: ## Push notes image to dockerhub
	docker push regis/openedx-notes:hawthorn
	docker push regis/openedx-notes:latest
push-xqueue: ## Push Xqueue image to dockerhub
	docker push regis/openedx-xqueue:hawthorn
	docker push regis/openedx-xqueue:latest
push-android: ## Push the Android image to dockerhub
	docker push regis/openedx-android:latest

dockerhub: build push ## Build and push all images to dockerhub

##################### Development

lms: ## Open a bash shell in the LMS
	$(DOCKER_COMPOSE_RUN_LMS) bash
cms: ## Open a bash shell in the CMS
	$(DOCKER_COMPOSE_RUN_CMS) bash

lms-python: ## Open a python shell in the LMS
	$(DOCKER_COMPOSE_RUN_OPENEDX) lms ./manage.py lms shell
lms-shell: lms-python
cms-python: ## Open a python shell in the CMS
	$(DOCKER_COMPOSE_RUN_OPENEDX) cms ./manage.py cms shell
cms-shell: cms-python

restart-openedx: ## Restart lms, cms, and workers
	docker-compose restart lms lms_worker cms cms_worker

##################### SSL/TLS (HTTPS certificates)

https_command = docker run --rm -it \
		--volume="$(PWD)/config/letsencrypt/:/openedx/letsencrypt/config/" \
		--volume="$(PWD)/data/letsencrypt/:/etc/letsencrypt/" \
		-p "80:80"
certbot_image = certbot/certbot:latest

https-certificate: ## Generate https certificates
	$(https_command) --entrypoint "/openedx/letsencrypt/config/certonly.sh" $(certbot_image)

https-certificate-renew: ## Renew https certificates
	$(https_command) $(certbot_image) renew

#################### Android application

android: ## Build the Android app, for development
	@docker-compose -f docker-compose-android.yml run --rm android
	@echo "Your APK file is ready: ./data/android/$(shell ls data/android/*.apk)"

android-release: ## Build the final Android app (beta)
	# Note that this requires that you edit ./config/android/gradle.properties
	docker-compose -f docker-compose-android.yml run --rm android ./gradlew assembleProdRelease

##################### Additional commands

stats: ## Collect anonymous information about the platform
	@docker run --rm -it --volume="$(PWD)/config:/openedx/config" \
		regis/openedx-configurator:hawthorn /openedx/config/openedx/stats 2> /dev/null|| true

import-demo-course: ## Import the demo course from edX
	$(DOCKER_COMPOSE_RUN_OPENEDX) cms /bin/bash -c "git clone https://github.com/edx/edx-demo-course ../edx-demo-course && git -C ../edx-demo-course checkout open-release/hawthorn.beta1 && python ./manage.py cms import ../data ../edx-demo-course"

create-staff-user: ## Create a user with admin rights
	$(DOCKER_COMPOSE_RUN_OPENEDX) lms /bin/bash -c "./manage.py lms manage_user --superuser --staff ${USERNAME} ${EMAIL} && ./manage.py lms changepassword ${USERNAME}"
