.PHONY: all android configure build update migrate assets up daemon

USERID ?= $$(id -u)
EDX_PLATFORM_SETTINGS ?= universal.production
DOCKER_COMPOSE_RUN = docker-compose run --rm
DOCKER_COMPOSE_RUN_OPENEDX = $(DOCKER_COMPOSE_RUN) -e USERID=$(USERID) -e SETTINGS=$(EDX_PLATFORM_SETTINGS)
ifneq ($(EDX_PLATFORM_PATH),)
	DOCKER_COMPOSE_RUN_OPENEDX += --volume="$(EDX_PLATFORM_PATH):/openedx/edx-platform"
endif

DOCKER_COMPOSE_RUN_LMS = $(DOCKER_COMPOSE_RUN_OPENEDX) -p 8000:8000 lms
DOCKER_COMPOSE_RUN_CMS = $(DOCKER_COMPOSE_RUN_OPENEDX) -p 8001:8001 cms

all: configure update migrate migrate-forum assets daemon

##################### Bootstrapping

configure:
	./configure

update:
	docker-compose pull

migrate:
	$(DOCKER_COMPOSE_RUN_OPENEDX) lms bash -c "wait-for-greenlight.sh && ./manage.py lms migrate"
	$(DOCKER_COMPOSE_RUN_OPENEDX) cms bash -c "wait-for-greenlight.sh && ./manage.py cms migrate"

migrate-forum:
	$(DOCKER_COMPOSE_RUN) forum bash -c "bundle exec rake search:initialize && \
		bundle exec rake search:rebuild_index"

assets:
	$(DOCKER_COMPOSE_RUN_OPENEDX) lms paver update_assets lms --settings=$(EDX_PLATFORM_SETTINGS)
	$(DOCKER_COMPOSE_RUN_OPENEDX) cms paver update_assets cms --settings=$(EDX_PLATFORM_SETTINGS)

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
	$(DOCKER_COMPOSE_RUN_OPENEDX) cms /bin/bash -c "git clone https://github.com/edx/edx-demo-course ../edx-demo-course && git -C ../edx-demo-course checkout open-release/ginkgo.master && python ./manage.py cms import ../data ../edx-demo-course"

create-staff-user:
	$(DOCKER_COMPOSE_RUN_OPENEDX) lms /bin/bash -c "./manage.py lms manage_user --superuser --staff ${USERNAME} ${EMAIL} && ./manage.py lms changepassword ${USERNAME}"


##################### Development

lms:
	$(DOCKER_COMPOSE_RUN_LMS) bash
cms:
	$(DOCKER_COMPOSE_RUN_CMS) bash

lms-shell:
	$(DOCKER_COMPOSE_RUN_OPENEDX) lms ./manage.py lms shell
cms-shell:
	$(DOCKER_COMPOSE_RUN_OPENEDX) cms ./manage.py cms shell


#################### Android app

android:
	docker-compose -f docker-compose-android.yml run --rm android
	@echo "Your APK file is ready: ./data/android/edx-prod-debuggable-2.14.0.apk"

android-release:
	# Note that this requires that you edit ./config/android/gradle.properties
	docker-compose -f docker-compose-android.yml run --rm android ./gradlew assembleProdRelease

android-build:
	docker build -t regis/openedx-android:latest android/
android-push:
	docker push regis/openedx-android:latest
android-dockerhub: android-build android-push


#################### Deploying to docker hub

build:
	# We need to build with docker, as long as docker-compose cannot push to dockerhub
	docker build -t regis/openedx:latest -t regis/openedx:ginkgo openedx/
	docker build -t regis/openedx-forum:latest -t regis/openedx-forum:ginkgo forum/

push:
	docker push regis/openedx:ginkgo
	docker push regis/openedx:latest
	docker push regis/openedx-forum:ginkgo
	docker push regis/openedx-forum:latest

dockerhub: build push
