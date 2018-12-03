.PHONY: env
PWD = $$(pwd)

configure:
	@$(MAKE) -s -C .. configure

env: configure ## Create the platform environment
	@docker run --rm -it \
		--volume="$(PWD)/../:/openedx/config/" \
		--volume="$(PWD)/templates/apps:/openedx/templates" \
		--volume="$(PWD)/env:/openedx/output" \
		-e USERID=$(USERID) -e SILENT=$(SILENT) $(CONFIGURE_OPTS) \
		regis/openedx-configurator:hawthorn \
		configurator substitute /openedx/templates/ /openedx/output/
	@docker run --rm -it \
		--volume="$(PWD)/../:/openedx/config/" \
		--volume="$(PWD)/templates/project:/openedx/templates" \
		--volume="$(PWD):/openedx/output" \
		-e USERID=$(USERID) -e SILENT=$(SILENT) $(CONFIGURE_OPTS) \
		regis/openedx-configurator:hawthorn \
		configurator substitute /openedx/templates/ /openedx/output/

