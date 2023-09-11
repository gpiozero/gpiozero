# vim: set noet sw=4 ts=4 fileencoding=utf-8:

# External utilities
PYTHON ?= python3
PIP ?= pip
PYTEST ?= pytest
TWINE ?= twine
PYFLAGS ?=
DEST_DIR ?= /

# Calculate the base names of the distribution, the location of all source,
# documentation, packaging, icon, and executable script files
NAME:=$(shell $(PYTHON) $(PYFLAGS) setup.py --name)
WHEEL_NAME:=$(subst -,_,$(NAME))
VER:=$(shell $(PYTHON) $(PYFLAGS) setup.py --version)
PY_SOURCES:=$(shell \
	$(PYTHON) $(PYFLAGS) setup.py egg_info >/dev/null 2>&1 && \
	cat $(WHEEL_NAME).egg-info/SOURCES.txt | grep -v "\.egg-info"  | grep -v "\.mo$$")
DOC_SOURCES:=docs/conf.py \
	$(wildcard docs/*.png) \
	$(wildcard docs/*.svg) \
	$(wildcard docs/*.dot) \
	$(wildcard docs/*.mscgen) \
	$(wildcard docs/*.gpi) \
	$(wildcard docs/*.rst) \
	$(wildcard docs/*.pdf)
SUBDIRS:=

# Calculate the name of all outputs
DIST_WHEEL=dist/$(WHEEL_NAME)-$(VER)-py3-none-any.whl
DIST_TAR=dist/$(NAME)-$(VER).tar.gz
DIST_ZIP=dist/$(NAME)-$(VER).zip
MAN_PAGES=man/pinout.1 man/pintest.1 man/remote-gpio.7 man/gpiozero-env.7


# Default target
all:
	@echo "make install - Install on local system"
	@echo "make develop - Install symlinks for development"
	@echo "make test - Run tests"
	@echo "make doc - Generate HTML and PDF documentation"
	@echo "make source - Create source package"
	@echo "make wheel - Generate a PyPI wheel package"
	@echo "make zip - Generate a source zip package"
	@echo "make tar - Generate a source tar package"
	@echo "make dist - Generate all packages"
	@echo "make clean - Get rid of all generated files"
	@echo "make release - Create and tag a new release"
	@echo "make upload - Upload the new release to repositories"

install: $(SUBDIRS)
	$(PYTHON) $(PYFLAGS) setup.py install --root $(DEST_DIR)

doc: $(DOC_SOURCES)
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(MAKE) -C docs epub
	$(MAKE) -C docs latexpdf
	$(MAKE) $(MAN_PAGES)

preview:
	$(MAKE) -C docs preview

source: $(DIST_TAR) $(DIST_ZIP)

wheel: $(DIST_WHEEL)

zip: $(DIST_ZIP)

tar: $(DIST_TAR)

dist: $(DIST_WHEEL) $(DIST_TAR) $(DIST_ZIP)

develop:
	@# These have to be done separately to avoid a cockup...
	$(PIP) install -U setuptools
	$(PIP) install -U pip
	$(PIP) install -U twine
	$(PIP) install -U tox
	$(PIP) install -e .[doc,test]

test:
	$(PYTEST)

clean:
	rm -fr dist/ build/ man/ .pytest_cache/ .mypy_cache/ $(WHEEL_NAME).egg-info/ tags .coverage*
	for dir in $(SUBDIRS); do \
		$(MAKE) -C $$dir clean; \
	done
	find $(CURDIR) -name "*.pyc" -delete
	find $(CURDIR) -name "__pycache__" -delete

tags: $(PY_SOURCES)
	ctags -R --languages="Python" $(PY_SOURCES)

lint: $(PY_SOURCES)
	pylint $(WHEEL_NAME)

$(SUBDIRS):
	$(MAKE) -C $@

$(MAN_PAGES): $(DOC_SOURCES)
	$(MAKE) -C docs man
	mkdir -p man/
	cp build/man/*.[0-9] man/

$(DIST_TAR): $(PY_SOURCES) $(SUBDIRS)
	$(PYTHON) $(PYFLAGS) setup.py sdist --formats gztar

$(DIST_ZIP): $(PY_SOURCES) $(SUBDIRS)
	$(PYTHON) $(PYFLAGS) setup.py sdist --formats zip

$(DIST_WHEEL): $(PY_SOURCES) $(SUBDIRS)
	$(PYTHON) $(PYFLAGS) setup.py bdist_wheel

release:
	$(MAKE) clean
	test -z "$(shell git status --porcelain)"
	git tag -s v$(VER) -m "Release v$(VER)"
	git push origin v$(VER)

upload: $(DIST_TAR) $(DIST_WHEEL)
	$(TWINE) check $(DIST_TAR) $(DIST_WHEEL)
	$(TWINE) upload $(DIST_TAR) $(DIST_WHEEL)

.PHONY: all install develop test doc source wheel zip tar dist clean tags release upload $(SUBDIRS)
