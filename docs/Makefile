.DEFAULT_GOAL := html
.PHONY: help

html:
	sphinx-build -b html -a -E "." "_build/html"

browse:
	sensible-browser _build/html/index.html

watch: html browse
	while true; do inotifywait -e modify *.rst; $(MAKE) html; done
