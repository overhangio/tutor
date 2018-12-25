.PHONY: android build
.DEFAULT_GOAL := help

PWD = $$(pwd)
USERID ?= $$(id -u)

build: ## Build all docker images
	cd build/ && make build

config.json:
	@$(MAKE) -s -C build/ build-configurator 1> /dev/null
	@docker run --rm -it \
		--volume="$(PWD):/openedx/config/" \
		-e USERID=$(USERID) -e SILENT=$(SILENT) \
		regis/openedx-configurator:hawthorn

substitute: config.json
	@docker run --rm -it \
		--volume="$(PWD)/config.json:/openedx/config/config.json" \
		--volume="$(TEMPLATES):/openedx/templates" \
		--volume="$(OUTPUT):/openedx/output" \
		-e USERID=$(USERID) -e SILENT=$(SILENT) $(CONFIGURE_OPTS) \
		regis/openedx-configurator:hawthorn \
		configurator substitute /openedx/templates/ /openedx/output/

singleserver: ## Configure and run a ready-to-go Open edX platform
	cd deploy/ && make all

android: ## Configure and build a development Android app
	cd android/ && make all

travis:
	cd build && make build
	cd deploy/singleserver \
		&& make configure SILENT=1 CONFIGURE_OPTS="-e SETTING_ACTIVATE_NOTES=1 -e SETTING_ACTIVATE_XQUEUE=1" \
		&& make databases \
		&& make assets

upgrade-to-tutor:
	@(stat config/config.json > /dev/null 2>&1 && (\
		echo "You are running an older version of Tutor. Now migrating to the latest version" \
		&& echo "Moving config/config.json to ./config.json" && mv config/config.json config.json \
		&& echo "Moving config/ to deploy/env/" && mv config/ deploy/env/ \
		&& ((ls openedx/themes/* > /dev/null 2>&1 && echo "Moving openedx/themes/* to build/openedx/themes/" && mv openedx/themes/* build/openedx/themes/) || true) \
		&& echo "Done migrating to tutor. This command will not be run again."\
	)) || true

ESCAPE = 
help: ## Print this help
	@grep -E '^([a-zA-Z_-]+:.*?## .*|######* .+)$$' Makefile \
		| sed 's/######* \(.*\)/\n               $(ESCAPE)[1;31m\1$(ESCAPE)[0m/g' \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-30s\033[0m %s\n", $$1, $$2}'
