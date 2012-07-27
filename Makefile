.DEFAULT_GOAL := dev

.PHONY: clean dev install tests

clean:
	@@find . -type f -name "*$py.class" | grep -E '\./tests' | xargs rm
	@echo "Cleaned."

dev:
	python setup.py dev

install:
	python setup.py install

tests:
	nosetests -v
