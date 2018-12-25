.PHONY: env
PWD = $$(pwd)

env: ## Create the platform environment
	@$(MAKE) -s -C .. substitute TEMPLATES=$(PWD)/templates OUTPUT=$(PWD)/env
