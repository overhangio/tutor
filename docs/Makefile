.DEFAULT_GOAL := html
.PHONY: help

build:
	sphinx-build -b html -a -E -n $(BUILD_ARGS) "." "_build/html"

html:
	$(MAKE) build BUILD_ARGS="-W"

browse:
	sensible-browser _build/html/index.html

watch: build browse
	while true; do inotifywait -e modify *.rst */*.rst */*/*.rst ../*.rst conf.py; $(MAKE) build || true; done
