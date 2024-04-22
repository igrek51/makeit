.PHONY: setup test clean build dist

setup:
	python3 -m venv venv &&\
	. venv/bin/activate &&\
	pip install --upgrade pip &&\
	pip install -r requirements.txt -r requirements-dev.txt &&\
	python -m pip install -e .

run:
	python makeit/__main__.py

install-local:
	python -m pip install -e .

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf ./*.egg-info

build:
	python3 -m build --sdist --wheel

# use token from .pypirc
release: clean build
	python3 -m twine upload -u __token__ dist/*
