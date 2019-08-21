.DEFAULT_GOAL := help
SRC_DIRS = ./tutor ./tests ./bin
BLACK_OPTS = --exclude templates ${SRC_DIRS}

###### Development

compile-requirements: ## Compile requirements files
	pip-compile -o requirements/base.txt requirements/base.in
	pip-compile -o requirements/dev.txt requirements/dev.in
	pip-compile -o requirements/docs.txt requirements/docs.in
	
package: ## Build a package ready to upload to pypi
	python3 setup.py sdist

test: test-lint test-unit test-format test-packages ## Run all tests by decreasing order or priority

test-format: ## Run code formatting tests
	black --check --diff $(BLACK_OPTS)

test-lint: ## Run code linting tests
	pylint --errors-only --ignore=templates ${SRC_DIRS}

test-unit: ## Run unit tests
	python3 -m unittest discover tests

test-packages: package ## Test that package can be uploaded to pypi
	twine check dist/tutor-*.tar.gz

format: ## Format code automatically
	black $(BLACK_OPTS)

###### Deployment

bundle: ## Bundle the tutor package in a single "dist/tutor" executable
	pyinstaller tutor.spec
dist/tutor:
	$(MAKE) bundle

nightly: ## Create a "nightly" release
	$(MAKE) tag TAG=nightly

release: ## Create a release tag and push it to origin
	$(MAKE) retag release-origin release-overhangio TAG=v$(shell make version)

retag:
	@echo "=== Creating tag $(TAG)"
	git tag -d $(TAG) || true
	git tag $(TAG)
release-origin:
	@echo "=== Pushing tag $(TAG) to origin"
	git push origin :$(TAG) || true
	git push origin $(TAG)
release-overhangio:
	@echo "=== Pushing tag $(TAG) to overhangio"
	git push overhangio :$(TAG) || true
	git push overhangio $(TAG)

###### Continuous integration tasks

ci-info: ## Print info about environment
	python3 --version
	pip3 --version

ci-install-dev: ## Install requirements
	pip3 install -U setuptools twine
	pip3 install -r requirements/dev.txt
	pip3 install -r requirements/plugins.txt

ci-install:
	pip3 install -U setuptools twine
	pip3 install -r requirements/base.txt
	pip3 install -r requirements/plugins.txt

ci-bundle: ## Create bundle and run basic tests
	$(MAKE) bundle
	mkdir -p releases/
	./dist/tutor --version
	./dist/tutor config printroot
	yes "" | ./dist/tutor config save --interactive
	./dist/tutor config save
	./dist/tutor plugins enable discovery ecommerce minio notes xqueue

./releases/github-release: ## Download github-release binary
	cd releases/ \
		&& curl -sSL -o ./github-release.tar.bz2 "https://github.com/aktau/github-release/releases/download/v0.7.2/$(shell uname -s | tr "[:upper:]" "[:lower:]")-amd64-github-release.tar.bz2" \
		&& bzip2 -d -f ./github-release.tar.bz2 \
		&& tar xf github-release.tar \
		&& mv "bin/$(shell uname -s | tr "[:upper:]" "[:lower:]")/amd64/github-release" .

ci-github: ./releases/github-release ## Upload assets to github
	sed "s/TUTOR_VERSION/v$(shell make version)/g" docs/_release_description.md > releases/description.md
	git log -1 --pretty=format:%b >> releases/description.md
	./releases/github-release release \
		--user overhangio \
		--repo tutor \
		--tag "v$(shell make version)" \
		--name "v$(shell make version)" \
		--description "$$(cat releases/description.md)" || true
	./releases/github-release upload \
	    --user overhangio \
	    --repo tutor \
	    --tag "v$(shell make version)" \
	    --name "tutor-$$(uname -s)_$$(uname -m)" \
	    --file ./dist/tutor \
			--replace

ci-bootstrap-images:
	pip install -r requirements/plugins.txt
	tutor config save

ci-build-images: ci-bootstrap-images ## Build docker images
	tutor images build all

ci-push-images: ci-bootstrap-images ## Push docker images to hub.docker.com
		docker login -u "$$DOCKER_USERNAME" -p "$$DOCKER_PASSWORD"
		tutor images push all

ci-pypi: ## Push packages to pypi
	twine upload --skip-existing dist/tutor-*.tar.gz

###### Additional commands

version: ## Print the current tutor version
	@python -c 'import io, os; about = {}; exec(io.open(os.path.join("tutor", "__about__.py"), "rt", encoding="utf-8").read(), about); print(about["__version__"])'

ESCAPE = 
help: ## Print this help
	@grep -E '^([a-zA-Z_-]+:.*?## .*|######* .+)$$' Makefile \
		| sed 's/######* \(.*\)/\n               $(ESCAPE)[1;31m\1$(ESCAPE)[0m/g' \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-30s\033[0m %s\n", $$1, $$2}'
