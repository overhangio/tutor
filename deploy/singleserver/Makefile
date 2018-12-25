.PHONY: env
.DEFAULT_GOAL := help

PWD = $$(pwd)
USERID ?= $$(id -u)
EDX_PLATFORM_SETTINGS ?= tutor.production
-include $(PWD)/Makefile.env

DOCKER_COMPOSE_RUN = docker-compose run --rm
DOCKER_COMPOSE_RUN_OPENEDX = $(DOCKER_COMPOSE_RUN) -e SETTINGS=$(EDX_PLATFORM_SETTINGS) \
	--volume="$(PWD)/../../build/openedx/themes:/openedx/themes"
ifneq ($(EDX_PLATFORM_PATH),)
	DOCKER_COMPOSE_RUN_OPENEDX += -e USERID=$(USERID) --volume="$(EDX_PLATFORM_PATH):/openedx/edx-platform"
endif

DOCKER_COMPOSE_RUN_LMS = $(DOCKER_COMPOSE_RUN_OPENEDX) -p 8000:8000 lms
DOCKER_COMPOSE_RUN_CMS = $(DOCKER_COMPOSE_RUN_OPENEDX) -p 8001:8001 cms

##################### Running Open edX

all: env ## Configure and run a full-featured platform
	@$(MAKE) stats
	@$(MAKE) https-certificate
	@$(MAKE) update
	@$(MAKE) databases
	@$(MAKE) assets
	@$(MAKE) daemonize
	@echo "All set \o/ You can access the LMS at http://localhost and the CMS at http://studio.localhost"

run: ## Run the complete platform
	docker-compose up
up: run

daemonize: ## Run the complete platform, with daemonization
	docker-compose up -d
	@echo "Daemon is up and running"
daemon: daemonize

stop: ## Stop all services
	docker-compose rm --stop --force

##################### Docker image management

update: ## Download most recent images
	docker-compose pull

##################### Configuration

configure:
	@$(MAKE) -s -C ../.. --always-make config.json
	@$(MAKE) -s env

env:
	@$(MAKE) -s -C .. env
	@$(MAKE) -s -C ../.. substitute TEMPLATES=$(PWD)/templates OUTPUT=$(PWD)

##################### Database

databases: provision-databases migrate provision-oauth2 ## Bootstrap databases

provision-databases: ## Create necessary databases and users
	$(DOCKER_COMPOSE_RUN) lms /openedx/env/provision.sh
provision-oauth2: ## Create users for SSO between services
	$(DOCKER_COMPOSE_RUN) lms /openedx/env/oauth2.sh

migrate: migrate-openedx migrate-forum ## Perform all database migrations
	@if [ "$(ACTIVATE_XQUEUE)" = "1" ] ; then \
		$(MAKE) migrate-xqueue ;\
	fi
	@if [ "$(ACTIVATE_NOTES)" = "1" ] ; then \
		$(MAKE) migrate-notes ; \
	fi
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

assets: ## Generate production-ready static assets
	docker-compose -f scripts.yml run --rm \
		--volume=$(PWD)/../../data/openedx:/tmp/openedx/ openedx bash -c \
		"rm -rf /tmp/openedx/staticfiles \
		&& cp -r /openedx/staticfiles /tmp/openedx"
assets-development: ## Generate static assets for local development
	$(DOCKER_COMPOSE_RUN_OPENEDX) --no-deps lms bash -c "openedx-assets build --env=dev"
assets-development-lms:
	$(DOCKER_COMPOSE_RUN_OPENEDX) --no-deps lms bash -c "openedx-assets build --env=dev --system lms"
assets-development-cms:
	$(DOCKER_COMPOSE_RUN_OPENEDX) --no-deps lms bash -c "openedx-assets build --env=dev --system cms"
watch-themes: ## Watch for changes in your themes and build development assets
	$(DOCKER_COMPOSE_RUN_OPENEDX) --no-deps lms openedx-assets watch-themes --env dev

#################### Logging

logs: ## Print all logs from a service since it started. E.g: "make logs service=lms", "make logs service=nginx"
	docker-compose logs $(service)
tail: ## Similar to "tail" on the logs of a service. E.g: "make tail service=lms", "make tail service=nginx"
	docker-compose logs --tail=10 $(service)
tail-follow: ## Similar to "tail -f" on the logs of a service. E.g: "make tail-follow service=lms", "make tail-follow service=nginx"
	docker-compose logs --tail=10 -f $(service)

##################### Development

lms: ## Open a bash shell in the LMS
	$(DOCKER_COMPOSE_RUN_LMS) bash
cms: ## Open a bash shell in the CMS
	$(DOCKER_COMPOSE_RUN_CMS) bash

lms-python: ## Open a python shell in the LMS
	$(DOCKER_COMPOSE_RUN_OPENEDX) lms ./manage.py lms shell
lms-shell: lms-python
lms-runserver: ## Run a local webserver, useful for debugging
	$(DOCKER_COMPOSE_RUN_LMS) ./manage.py lms runserver 0.0.0.0:8000
cms-python: ## Open a python shell in the CMS
	$(DOCKER_COMPOSE_RUN_OPENEDX) cms ./manage.py cms shell
cms-shell: cms-python
cms-runserver: ## Run a local webserver, useful for debugging
	$(DOCKER_COMPOSE_RUN_CMS) ./manage.py cms runserver 0.0.0.0:8001

restart-openedx: ## Restart lms, cms, and workers
	docker-compose restart lms lms_worker cms cms_worker

##################### SSL/TLS (HTTPS certificates)

https_command = docker run --rm -it \
		--volume="$(PWD)/../env/letsencrypt/:/openedx/letsencrypt/env/" \
		--volume="$(PWD)/data/letsencrypt/:/etc/letsencrypt/" \
		-p "80:80"
certbot_image = certbot/certbot:latest

https-certificate: ## Generate https certificates
	@if [ "$(ACTIVATE_HTTPS)" = "1" ] ; then \
		$(https_command) --entrypoint "/openedx/letsencrypt/env/certonly.sh" $(certbot_image)
	fi

https-certificate-renew: ## Renew https certificates
	$(https_command) $(certbot_image) renew

##################### Additional commands

stats: ## Collect anonymous information about the platform
	@if [ "$(DISABLE_STATS)" != "1" ] ; then \
		docker run --rm -it --volume="$(PWD)/../env:/openedx/env" \
			regis/openedx-configurator:hawthorn /openedx/env/openedx/stats 2> /dev/null || true ; \
	fi

import-demo-course: ## Import the demo course from edX
	$(DOCKER_COMPOSE_RUN_OPENEDX) cms /bin/bash -c " \
		git clone https://github.com/edx/edx-demo-course --branch open-release/hawthorn.2 --depth 1 ../edx-demo-course \
		&& python ./manage.py cms import ../data ../edx-demo-course"

create-staff-user: ## Create a user with admin rights
	$(DOCKER_COMPOSE_RUN_OPENEDX) lms /bin/bash -c "./manage.py lms manage_user --superuser --staff ${USERNAME} ${EMAIL} && ./manage.py lms changepassword ${USERNAME}"

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
