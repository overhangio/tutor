PWD ?= $$(pwd)
.DEFAULT_GOAL := help

all: environment update android ## Configure and build a development Android app

env: ## Generate the environment
	@$(MAKE) -s -C .. substitute TEMPLATES=$(PWD)/templates OUTPUT=$(PWD)/config

update: ## Download most recent Android image
	docker pull regis/openedx-android:latest

android: ## Build the Android app, for development
	docker run --rm -it \
		--volume=$(PWD)/config/:/openedx/config/ \
      	--volume=$(PWD)/data/:/openedx/data \
		regis/openedx-android:latest
	@echo "Your development APK file is ready in $(PWD)/data/"

android-release: ## Build the final Android app (beta)
	# Note that this requires that you edit ./config/android/gradle.properties
	docker run --rm -it \
		--volume=$(PWD)/config/:/openedx/config/ \
      	--volume=$(PWD)/data/:/openedx/data \
		regis/openedx-android:latest \
		./gradlew assembleProdRelease
	@echo "Your production APK file is ready in $(PWD)/data/"

ESCAPE = 
help: ## Print this help
	@grep -E '^([a-zA-Z_-]+:.*?## .*|######* .+)$$' Makefile \
		| sed 's/######* \(.*\)/\n               $(ESCAPE)[1;31m\1$(ESCAPE)[0m/g' \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-30s\033[0m %s\n", $$1, $$2}'
