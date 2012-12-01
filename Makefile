# Magical make incantations...
.DEFAULT_GOAL := all

.PHONY: assets build clean deps dist run


REV=$(shell git rev-parse --short HEAD)
TIMESTAMP=$(shell date +'%s')
RUN=foreman run
SETUP=$(RUN) python setup.py
MANAGE=$(RUN) python manage.py


all: deps assets

assets:
	@$(MANAGE) assets rebuild

build: clean assets
	@$(SETUP) build

clean:
	@find . -name "*.py[co]" -exec rm -rf {} \;
	@$(SETUP) clean
	@rm -rf dist build

deps:
	@$(SETUP) dev

dist: clean assets
	@$(SETUP) sdist

run:
	@foreman start -f Procfile.dev
