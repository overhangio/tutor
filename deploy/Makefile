.PHONY: env
PWD = $$(pwd)

env: ## Generate the environment from templates and configuration values
	@$(MAKE) -s -C .. substitute TEMPLATES=$(PWD)/templates OUTPUT=$(PWD)/env
