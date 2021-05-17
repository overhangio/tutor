.DEFAULT_GOAL := help
.PHONY: docs
SRC_DIRS = ./tutor ./tests ./bin
BLACK_OPTS = --exclude templates ${SRC_DIRS}

###### Development

docs: ## Build html documentation
	$(MAKE) -C docs

compile-requirements: ## Compile requirements files
	pip-compile requirements/base.in
	pip-compile requirements/dev.in
	pip-compile requirements/docs.in

upgrade-requirements: ## Upgrade requirements files
	pip-compile --upgrade requirements/base.in
	pip-compile --upgrade requirements/dev.in
	pip-compile --upgrade requirements/docs.in

build-pythonpackage: ## Build a python package ready to upload to pypi
	python setup.py sdist

push-pythonpackage: ## Push python package to pypi
	twine upload --skip-existing dist/tutor-openedx-$(shell make version).tar.gz

test: test-lint test-unit test-types test-format test-pythonpackage ## Run all tests by decreasing order or priority

test-format: ## Run code formatting tests
	black --check --diff $(BLACK_OPTS)

test-lint: ## Run code linting tests
	pylint --errors-only --enable=unused-import --ignore=templates ${SRC_DIRS}

test-unit: ## Run unit tests
	python -m unittest discover tests

test-types: ## Check type definitions
	mypy --exclude=templates --ignore-missing-imports --strict tutor/ tests/

test-pythonpackage: build-pythonpackage ## Test that package can be uploaded to pypi
	twine check dist/tutor-openedx-$(shell make version).tar.gz

format: ## Format code automatically
	black $(BLACK_OPTS)

bootstrap-dev: ## Install dev requirements
	pip install .
	pip install -r requirements/dev.txt

bootstrap-dev-plugins: bootstrap-dev ## Install dev requirement and all supported plugins
	pip install -r requirements/plugins.txt

###### Deployment

bundle: ## Bundle the tutor package in a single "dist/tutor" executable
	pyinstaller tutor.spec

release: test release-unsafe ## Create a release tag and push it to origin
release-unsafe:
	$(MAKE) release-tag release-push TAG=v$(shell make version)
release-tag:
	@echo "=== Creating tag $(TAG)"
	git tag -d $(TAG) || true
	git tag $(TAG)
release-push:
	@echo "=== Pushing tag $(TAG) to origin"
	git push origin
	git push origin :$(TAG) || true
	git push origin $(TAG)

release-description:  ## Write the current release description to a file
	sed "s/TUTOR_VERSION/v$(shell make version)/g" docs/_release_description.md > release_description.md
	git log -1 --pretty=format:%b >> release_description.md

###### Continuous integration tasks

pull-base-images: # Manually pull base images
	docker image pull docker.io/ubuntu:20.04
	docker image pull docker.io/python:3.7-alpine

ci-info: ## Print info about environment
	python --version
	pip --version

ci-test-bundle: ## Run basic tests on bundle
	ls -lh ./dist/tutor
	./dist/tutor --version
	./dist/tutor config printroot
	yes "" | ./dist/tutor config save --interactive
	./dist/tutor config save
	./dist/tutor plugins list
	# ./dist/tutor plugins enable discovery ecommerce figures license minio notes xqueue
	./dist/tutor plugins enable discovery ecommerce license minio notes xqueue
	./dist/tutor plugins list
	./dist/tutor license --help

ci-bootstrap-images:
	pip install .
	tutor config save

###### Additional commands

version: ## Print the current tutor version
	@python -c 'import io, os; about = {}; exec(io.open(os.path.join("tutor", "__about__.py"), "rt", encoding="utf-8").read(), about); print(about["__version__"])'

ESCAPE = 
help: ## Print this help
	@grep -E '^([a-zA-Z_-]+:.*?## .*|######* .+)$$' Makefile \
		| sed 's/######* \(.*\)/\n               $(ESCAPE)[1;31m\1$(ESCAPE)[0m/g' \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-30s\033[0m %s\n", $$1, $$2}'
