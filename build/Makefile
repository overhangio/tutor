#################### Docker image building
.DEFAULT_GOAL := help

build: build-openedx build-configurator build-forum build-notes build-xqueue build-android ## Build all docker images

openedx_build_args =
ifdef EDX_PLATFORM_REPOSITORY
	openedx_build_args += --build-arg="EDX_PLATFORM_REPOSITORY=$(EDX_PLATFORM_REPOSITORY)"
endif
ifdef EDX_PLATFORM_VERSION
	openedx_build_args += --build-arg="EDX_PLATFORM_VERSION=$(EDX_PLATFORM_VERSION)"
endif
ifdef THEMES
	openedx_build_args += --build-arg="THEMES=$(THEMES)"
endif

build-openedx: ## Build the Open edX docker image
	docker build -t regis/openedx:latest -t regis/openedx:hawthorn $(openedx_build_args) openedx/
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

##################### Information

ESCAPE = 
help: ## Print this help
	@grep -E '^([a-zA-Z_-]+:.*?## .*|######* .+)$$' Makefile \
		| sed 's/######* \(.*\)/\n               $(ESCAPE)[1;31m\1$(ESCAPE)[0m/g' \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-30s\033[0m %s\n", $$1, $$2}'
