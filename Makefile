.PHONY: all configure build update migrate assets up daemon

USERID ?= $$(id -u)
DOCKER_COMPOSE_RUN = docker-compose run --rm -e USERID=$(USERID)
EDX_PLATFORM_SETTINGS ?= universal.production
DOCKER_COMPOSE_RUN += -e SETTINGS=$(EDX_PLATFORM_SETTINGS)
ifneq ($(EDX_PLATFORM_PATH),)
	DOCKER_COMPOSE_RUN += --volume="$(EDX_PLATFORM_PATH):/openedx/edx-platform"
endif

DOCKER_COMPOSE_RUN_LMS = $(DOCKER_COMPOSE_RUN) -p 8000:8000 lms
DOCKER_COMPOSE_RUN_CMS = $(DOCKER_COMPOSE_RUN) -p 8001:8001 cms

all: configure update migrate assets daemon

##################### Bootstrapping

configure:
	./configure

update:
	docker-compose pull

migrate:
	$(DOCKER_COMPOSE_RUN) lms bash -c "wait-for-greenlight.sh && ./manage.py lms migrate"
	$(DOCKER_COMPOSE_RUN) cms bash -c "wait-for-greenlight.sh && ./manage.py cms migrate"

assets:
	$(DOCKER_COMPOSE_RUN) lms paver update_assets lms --settings=$(EDX_PLATFORM_SETTINGS)
	$(DOCKER_COMPOSE_RUN) cms paver update_assets cms --settings=$(EDX_PLATFORM_SETTINGS)

##################### Running

up:
	docker-compose up

daemon:
	docker-compose up -d && \
	echo "Daemon is up and running"

stop:
	docker-compose stop

##################### Extra

import-demo-course:
	$(DOCKER_COMPOSE_RUN) cms /bin/bash -c "git clone https://github.com/edx/edx-demo-course ../edx-demo-course && git -C ../edx-demo-course checkout open-release/ginkgo.master && python ./manage.py cms import ../data ../edx-demo-course"

create-staff-user:
	$(DOCKER_COMPOSE_RUN) lms /bin/bash -c "./manage.py lms manage_user --superuser --staff ${USERNAME} ${EMAIL} && ./manage.py lms changepassword ${USERNAME}"


##################### Development

lms:
	$(DOCKER_COMPOSE_RUN_LMS) bash
cms:
	$(DOCKER_COMPOSE_RUN_CMS) bash

lms-shell:
	$(DOCKER_COMPOSE_RUN) lms ./manage.py lms shell
cms-shell:
	$(DOCKER_COMPOSE_RUN) cms ./manage.py cms shell


#################### Deploying to docker hub

build:
	docker-compose build

tag:
	docker tag openedx overhangio/openedx:ginkgo
	docker tag openedx overhangio/openedx:latest

push:
	docker push overhangio/openedx:ginkgo
	docker push overhangio/openedx:latest

dockerhub: build tag push
