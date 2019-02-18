.DEFAULT_GOAL := help

compile-requirements: ## Compile requirements files
	pip-compile -o requirements/base.txt requirements/base.in
	pip-compile -o requirements/dev.txt requirements/dev.in

bundle: ## Bundle the tutor package in a single "dist/tutor" executable
	pyinstaller --onefile --name=tutor --add-data=./tutor/templates:./tutor/templates ./bin/main

tag: ## Create a release, update the "latest" tag and push them to origin
	$(MAKE) retag TAG=$(TAG)
	$(MAKE) retag TAG=latest

retag:
	@echo "=== Creating tag $(TAG)"
	git tag -d $(TAG) || true
	git tag $(TAG)
	@echo "=== Pushing tag $(TAG)"
	git push origin :$(TAG) || true
	git push origin $(TAG)

travis: bundle ## Run tests on travis-ci
	./dist/tutor config noninteractive
	./dist/tutor images env
	./dist/tutor images build all
	./dist/tutor local databases

ci-info: ## Print info about environment
	python3 --version
	pip3 --version

ci-bundle: ## Create bundle
	pip3 install -U setuptools
	pip3 install -r requirements/dev.txt
	$(MAKE) bundle
	mkdir -p releases/
	cp ./dist/tutor ./releases/tutor-$$(uname -s)_$$(uname -m)

ci-test: ## Run basic tests
	./dist/tutor config noninteractive
	./dist/tutor images env
	./dist/tutor local env

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

ESCAPE = 
help: ## Print this help
	@grep -E '^([a-zA-Z_-]+:.*?## .*|######* .+)$$' Makefile \
		| sed 's/######* \(.*\)/\n               $(ESCAPE)[1;31m\1$(ESCAPE)[0m/g' \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-30s\033[0m %s\n", $$1, $$2}'
