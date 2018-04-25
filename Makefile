.PHONY: all configure build migrate assets up daemon

USER_ID ?= $$(id -u)
DOCKER_COMPOSE_RUN = docker-compose run --rm -e USERID=$(USER_ID)
EDX_PLATFORM_SETTINGS ?= production
DOCKER_COMPOSE_RUN += -e SETTINGS=$(EDX_PLATFORM_SETTINGS)
ifneq ($(EDX_PLATFORM_PATH),)
	DOCKER_COMPOSE_RUN += --volume="$(EDX_PLATFORM_PATH):/openedx/edx-platform"
endif

DOCKER_COMPOSE_RUN_LMS = $(DOCKER_COMPOSE_RUN) -p 8000:8000 lms
DOCKER_COMPOSE_RUN_CMS = $(DOCKER_COMPOSE_RUN) -p 8001:8001 cms

all: configure build migrate assets daemon

##################### Bootstrapping

configure:
	./configure

build:
	docker-compose build

migrate:
	$(DOCKER_COMPOSE_RUN_LMS) bash -c "wait-for-greenlight.sh && ./manage.py lms migrate"
	$(DOCKER_COMPOSE_RUN_CMS) bash -c "wait-for-greenlight.sh && ./manage.py cms migrate"

assets:
	$(DOCKER_COMPOSE_RUN_LMS) paver update_assets lms --settings=$(EDX_PLATFORM_SETTINGS)
	$(DOCKER_COMPOSE_RUN_CMS) paver update_assets cms --settings=$(EDX_PLATFORM_SETTINGS)

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
	$(DOCKER_COMPOSE_RUN_CMS) /bin/bash -c "git clone https://github.com/edx/edx-demo-course ../edx-demo-course && git -C ../edx-demo-course checkout open-release/ginkgo.master && python ./manage.py cms import ../data ../edx-demo-course"

create-staff-user:
	$(DOCKER_COMPOSE_RUN_LMS) /bin/bash -c "./manage.py lms manage_user --superuser --staff ${USERNAME} ${EMAIL} && ./manage.py lms changepassword ${USERNAME}"


##################### Development

lms:
	$(DOCKER_COMPOSE_RUN_LMS) bash
cms:
	$(DOCKER_COMPOSE_RUN_CMS) bash

lms-shell:
	$(DOCKER_COMPOSE_RUN_LMS) ./manage.py lms shell
cms-shell:
	$(DOCKER_COMPOSE_RUN_LMS) ./manage.py cms shell
