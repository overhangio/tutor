.PHONY: all android configure build update migrate assets up daemon

PWD ?= $$(pwd)
USERID ?= $$(id -u)
EDX_PLATFORM_SETTINGS ?= universal.production
DOCKER_COMPOSE = docker-compose -f docker-compose.yml

post_configure_targets = 
ifeq ($(ACTIVATE_HTTPS), 1)
	post_configure_targets += https-certificate
endif
extra_migrate_targets = 
ifeq ($(ACTIVATE_XQUEUE), 1)
	extra_migrate_targets += migrate-xqueue
	DOCKER_COMPOSE += -f docker-compose-xqueue.yml
endif

DOCKER_COMPOSE_RUN = $(DOCKER_COMPOSE) run --rm
DOCKER_COMPOSE_RUN_OPENEDX = $(DOCKER_COMPOSE_RUN) -e USERID=$(USERID) -e SETTINGS=$(EDX_PLATFORM_SETTINGS)
ifneq ($(EDX_PLATFORM_PATH),)
	DOCKER_COMPOSE_RUN_OPENEDX += --volume="$(EDX_PLATFORM_PATH):/openedx/edx-platform"
endif

DOCKER_COMPOSE_RUN_LMS = $(DOCKER_COMPOSE_RUN_OPENEDX) -p 8000:8000 lms
DOCKER_COMPOSE_RUN_CMS = $(DOCKER_COMPOSE_RUN_OPENEDX) -p 8001:8001 cms

all: configure $(post_configure_targets) update migrate assets daemon
	@echo "All set \o/ You can access the LMS at http://localhost and the CMS at http://studio.localhost"

##################### Bootstrapping

configure:
	docker run --rm -it --volume="$(PWD)/config:/openedx/config" \
		-e USERID=$(USERID) -e SILENT=$(SILENT) -e ACTIVATE_HTTPS=$(ACTIVATE_HTTPS) -e ACTIVATE_XQUEUE=$(ACTIVATE_XQUEUE) \
		regis/openedx-configurator

update:
	$(DOCKER_COMPOSE) pull
	docker pull regis/openedx-configurator:hawthorn

provision:
	$(DOCKER_COMPOSE_RUN) lms bash -c "dockerize -wait tcp://mysql:3306 -timeout 20s && bash /openedx/config/provision.sh"

migrate: provision migrate-openedx migrate-forum $(extra_migrate_targets)

migrate-openedx:
	$(DOCKER_COMPOSE_RUN_OPENEDX) lms bash -c "dockerize -wait tcp://mysql:3306 -timeout 20s && ./manage.py lms migrate"
	$(DOCKER_COMPOSE_RUN_OPENEDX) cms bash -c "dockerize -wait tcp://mysql:3306 -timeout 20s && ./manage.py cms migrate"

migrate-forum:
	$(DOCKER_COMPOSE_RUN) forum bash -c "bundle exec rake search:initialize && \
		bundle exec rake search:rebuild_index"

migrate-xqueue:
	$(DOCKER_COMPOSE_RUN) xqueue bash -c "./manage.py migrate"

assets:
	$(DOCKER_COMPOSE_RUN_OPENEDX) -e NO_PREREQ_INSTALL=True lms paver update_assets lms --settings=$(EDX_PLATFORM_SETTINGS)
	$(DOCKER_COMPOSE_RUN_OPENEDX) -e NO_PREREQ_INSTALL=True cms paver update_assets cms --settings=$(EDX_PLATFORM_SETTINGS)

##################### Running

up:
	$(DOCKER_COMPOSE) up

daemon:
	$(DOCKER_COMPOSE) up -d && \
	echo "Daemon is up and running"

stop:
	$(DOCKER_COMPOSE) rm --stop --force

##################### Extra
info:
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

import-demo-course:
	$(DOCKER_COMPOSE_RUN_OPENEDX) cms /bin/bash -c "git clone https://github.com/edx/edx-demo-course ../edx-demo-course && git -C ../edx-demo-course checkout open-release/hawthorn.beta1 && python ./manage.py cms import ../data ../edx-demo-course"

create-staff-user:
	$(DOCKER_COMPOSE_RUN_OPENEDX) lms /bin/bash -c "./manage.py lms manage_user --superuser --staff ${USERNAME} ${EMAIL} && ./manage.py lms changepassword ${USERNAME}"


##################### HTTPS
https_command = docker run --rm -it \
		--volume="$(PWD)/config/letsencrypt/:/openedx/letsencrypt/config/" \
		--volume="$(PWD)/data/letsencrypt/:/etc/letsencrypt/" \
		-p "80:80"
certbot_image = certbot/certbot:latest

https-certificate:
	$(https_command) --entrypoint "/openedx/letsencrypt/config/certonly.sh" $(certbot_image)

https-certificate-renew:
	$(https_command) $(certbot_image) renew

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

#################### Build images
build: build-openedx build-configurator build-forum build-xqueue

build-openedx:
	docker build -t regis/openedx:latest -t regis/openedx:hawthorn openedx/
build-configurator:
	docker build -t regis/openedx-configurator:latest -t regis/openedx-configurator:hawthorn configurator/
build-forum:
	docker build -t regis/openedx-forum:latest -t regis/openedx-forum:hawthorn forum/
build-xqueue:
	docker build -t regis/openedx-xqueue:latest -t regis/openedx-xqueue:hawthorn xqueue/

#################### Deploying to docker hub
push: push-openedx push-forum push-xqueue
push-openedx:
	docker push regis/openedx:hawthorn
	docker push regis/openedx:latest
push-configurator:
	docker push regis/openedx-configurator:hawthorn
	docker push regis/openedx-configurator:latest
push-forum:
	docker push regis/openedx-forum:hawthorn
	docker push regis/openedx-forum:latest
push-xqueue:
	docker push regis/openedx-xqueue:hawthorn
	docker push regis/openedx-xqueue:latest

dockerhub: build push
