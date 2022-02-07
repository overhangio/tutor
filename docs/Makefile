.DEFAULT_GOAL := html
.PHONY: help

build:
	sphinx-build -b html -a -E -n $(BUILD_ARGS) "." "_build/html"

html:
	$(MAKE) build BUILD_ARGS="-W"

browse:
	sensible-browser _build/html/index.html

watch: build browse
	while true; do $(MAKE) wait-for-change build || true; done

wait-for-change:
	inotifywait -e modify $(shell find . -name "*.rst") ../*.rst ../tutor/hooks/*.py conf.py
