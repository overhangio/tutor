.DEFAULT_GOAL := help
BLACK_OPTS = --exclude templates ./tutor ./tests

###### Development

compile-requirements: ## Compile requirements files
	pip-compile -o requirements/base.txt requirements/base.in
	pip-compile -o requirements/dev.txt requirements/dev.in
	pip-compile -o requirements/docs.txt requirements/docs.in

test: test-lint test-unit test-format ## Run all tests by decreasing order or priority

test-format: ## Run code formatting tests
	black --check --diff $(BLACK_OPTS)

test-lint: ## Run code linting tests
	pylint --errors-only tutor

test-unit: ## Run unit tests
	python3 -m unittest discover tests

format: ## Format code automatically
	black $(BLACK_OPTS)

###### Deployment

bundle: ## Bundle the tutor package in a single "dist/tutor" executable
	pyinstaller --onefile --name=tutor --add-data=./tutor/templates:./tutor/templates ./bin/main
dist/tutor:
	$(MAKE) bundle

nightly: ## Create a "nightly" release
	$(MAKE) tag TAG=nightly

release: ## Create a release tag and push it to origin
	$(MAKE) tag TAG=v$(shell make version)

tag:
	@echo "=== Creating tag $(TAG)"
	git tag -d $(TAG) || true
	git tag $(TAG)
	@echo "=== Pushing tag $(TAG)"
	git push origin :$(TAG) || true
	git push origin $(TAG)

###### Continuous integration tasks

ci-info: ## Print info about environment
	python3 --version
	pip3 --version

ci-install: ## Install requirements
	pip3 install -U setuptools
	pip3 install -r requirements/dev.txt

ci-bundle: ## Create bundle and run basic tests
	$(MAKE) bundle
	mkdir -p releases/
	./dist/tutor --version
	./dist/tutor config printroot
	yes "" | ./dist/tutor config save
	./dist/tutor config save --yes --set ACTIVATE_NOTES=true --set ACTIVATE_XQUEUE=true

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
		--user regisb \
		--repo tutor \
		--tag "v$(shell make version)" \
		--name "v$(shell make version)" \
		--description "$$(cat releases/description.md)" || true
	./releases/github-release upload \
	    --user regisb \
	    --repo tutor \
	    --tag "v$(shell make version)" \
	    --name "tutor-$$(uname -s)_$$(uname -m)" \
	    --file ./dist/tutor \
		--replace

ci-images: ## Build and push docker images to hub.docker.com
	python setup.py develop
	tutor images build all
	tutor local databases
	docker login -u "$$DOCKER_USERNAME" -p "$$DOCKER_PASSWORD"
	tutor images push all

ci-pypi: ## Push release to pypi
	pip install twine
	python setup.py sdist
	twine upload dist/*.tar.gz

###### Additional commands

version: ## Print the current tutor version
	@python -c 'import io, os; about = {}; exec(io.open(os.path.join("tutor", "__about__.py"), "rt", encoding="utf-8").read(), about); print(about["__version__"])'

ESCAPE = 
help: ## Print this help
	@grep -E '^([a-zA-Z_-]+:.*?## .*|######* .+)$$' Makefile \
		| sed 's/######* \(.*\)/\n               $(ESCAPE)[1;31m\1$(ESCAPE)[0m/g' \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-30s\033[0m %s\n", $$1, $$2}'
