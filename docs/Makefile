.DEFAULT_GOAL := html
.PHONY: help

html:
	sphinx-build -b html -a -E -n -W "." "_build/html"

browse:
	sensible-browser _build/html/index.html

watch: html browse
	while true; do inotifywait -e modify *.rst */*.rst */*/*.rst ../*.rst conf.py; $(MAKE) html; done
