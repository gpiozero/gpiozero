# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
BUILDDIR      = ../build
PY_SOURCES    := $(wildcard ../gpiozero/*.py ../gpiozero/pins/*.py)
DOT_DIAGRAMS  := $(wildcard images/*.dot images/*/*.dot)
MSC_DIAGRAMS  := $(wildcard images/*.mscgen images/*/*.mscgen)
GPI_DIAGRAMS  := $(wildcard images/*.gpi images/*/*.gpi)
SVG_IMAGES    := $(wildcard images/*.svg images/*/*.svg) $(DOT_DIAGRAMS:%.dot=%.svg) $(MSC_DIAGRAMS:%.mscgen=%.svg)
PNG_IMAGES    := $(wildcard images/*.png images/*/*.png) $(GPI_DIAGRAMS:%.gpi=%.png) $(SVG_IMAGES:%.svg=%.png)
PDF_IMAGES    := $(SVG_IMAGES:%.svg=%.pdf) $(GPI_DIAGRAMS:%.gpi=%.pdf) $(DOT_DIAGRAMS:%.dot=%.pdf) $(MSC_DIAGRAMS:%.mscgen=%.pdf)
INKSCAPE_VER  := $(shell inkscape --version | sed -ne '/^Inkscape/ s/^Inkscape \([0-9]\+\)\..*$$/\1/p')

# User-friendly check for sphinx-build
ifeq ($(shell which $(SPHINXBUILD) >/dev/null 2>&1; echo $$?), 1)
$(error The '$(SPHINXBUILD)' command was not found. Make sure you have Sphinx installed, then set the SPHINXBUILD environment variable to point to the full path of the '$(SPHINXBUILD)' executable. Alternatively you can add the directory with the executable to your PATH. If you don't have Sphinx installed, grab it from http://sphinx-doc.org/)
endif

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .
# the i18n builder cannot share the environment and doctrees with the others
I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html       to make standalone HTML files"
	@echo "  preview    to start a web-server that watches for file changes"
	@echo "             and re-builds the docs when required"
	@echo "  json       to make JSON files"
	@echo "  epub       to make an epub"
	@echo "  latex      to make LaTeX files, you can set PAPER=a4 or PAPER=letter"
	@echo "  latexpdf   to make LaTeX files and run them through pdflatex"
	@echo "  text       to make text files"
	@echo "  man        to make manual pages"
	@echo "  gettext    to make PO message catalogs"
	@echo "  changes    to make an overview of all changed/added/deprecated items"
	@echo "  xml        to make Docutils-native XML files"
	@echo "  pseudoxml  to make pseudoxml-XML files for display purposes"
	@echo "  linkcheck  to check all external links for integrity"
	@echo "  doctest    to run all doctests embedded in the documentation (if enabled)"

clean:
	rm -rf $(BUILDDIR)/*

html: $(SVG_IMAGES) $(PNG_IMAGES)
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

json:
	$(SPHINXBUILD) -b json $(ALLSPHINXOPTS) $(BUILDDIR)/json
	@echo
	@echo "Build finished; now you can process the JSON files."

epub:
	$(SPHINXBUILD) -b epub $(ALLSPHINXOPTS) $(BUILDDIR)/epub
	@echo
	@echo "Build finished. The epub file is in $(BUILDDIR)/epub."

latex: $(PDF_IMAGES)
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(BUILDDIR)/latex
	@echo
	@echo "Build finished; the LaTeX files are in $(BUILDDIR)/latex."
	@echo "Run \`make' in that directory to run these through (pdf)latex" \
	      "(use \`make latexpdf' here to do that automatically)."

latexpdf: $(PDF_IMAGES)
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(BUILDDIR)/latex
	@echo "Running LaTeX files through pdflatex..."
	$(MAKE) -C $(BUILDDIR)/latex all-pdf
	@echo "pdflatex finished; the PDF files are in $(BUILDDIR)/latex."

text:
	$(SPHINXBUILD) -b text $(ALLSPHINXOPTS) $(BUILDDIR)/text
	@echo
	@echo "Build finished. The text files are in $(BUILDDIR)/text."

man:
	$(SPHINXBUILD) -b man $(ALLSPHINXOPTS) $(BUILDDIR)/man
	@echo
	@echo "Build finished. The manual pages are in $(BUILDDIR)/man."

gettext:
	$(SPHINXBUILD) -b gettext $(I18NSPHINXOPTS) $(BUILDDIR)/locale
	@echo
	@echo "Build finished. The message catalogs are in $(BUILDDIR)/locale."

changes:
	$(SPHINXBUILD) -b changes $(ALLSPHINXOPTS) $(BUILDDIR)/changes
	@echo
	@echo "The overview file is in $(BUILDDIR)/changes."

linkcheck:
	$(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) $(BUILDDIR)/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
	      "or in $(BUILDDIR)/linkcheck/output.txt."

doctest:
	$(SPHINXBUILD) -b doctest $(ALLSPHINXOPTS) $(BUILDDIR)/doctest
	@echo "Testing of doctests in the sources finished, look at the " \
	      "results in $(BUILDDIR)/doctest/output.txt."

xml:
	$(SPHINXBUILD) -b xml $(ALLSPHINXOPTS) $(BUILDDIR)/xml
	@echo
	@echo "Build finished. The XML files are in $(BUILDDIR)/xml."

pseudoxml:
	$(SPHINXBUILD) -b pseudoxml $(ALLSPHINXOPTS) $(BUILDDIR)/pseudoxml
	@echo
	@echo "Build finished. The pseudo-XML files are in $(BUILDDIR)/pseudoxml."

preview:
	../scripts/previewer $(BUILDDIR)/html

images/device_hierarchy.dot: $(PY_SOURCES)
	../scripts/class_graph \
		-i Device \
		-i SharedMixin \
		-x SPI -x SPISoftwareBus > $@

images/composite_device_hierarchy.dot: $(PY_SOURCES)
	../scripts/class_graph \
		-i CompositeDevice \
		-i Energenie \
		-i LedBord \
		-x Motor \
		-x PhaseEnableMotor \
		-x Servo \
		-o SourceMixin > $@

images/spi_device_hierarchy.dot: $(PY_SOURCES)
	../scripts/class_graph -i SPIDevice > $@

images/output_device_hierarchy.dot: $(PY_SOURCES)
	../scripts/class_graph \
		-i OutputDevice \
		-i RGBLED \
		-i Servo \
		-i Motor \
		-i PhaseEnableMotor \
		-i TonalBuzzer \
		-x LedBorg \
		-x SPI -o SourceMixin > $@

images/input_device_hierarchy.dot: $(PY_SOURCES)
	../scripts/class_graph -i InputDevice -o EventsMixin -o HoldMixin > $@

images/internal_device_hierarchy.dot: $(PY_SOURCES)
	../scripts/class_graph -i InternalDevice -o EventsMixin > $@

%.svg: %.mscgen
	mscgen -T svg -o $@ $<

%.svg: %.dot
	dot -T svg -o $@ $<

%.png: %.gpi
	gnuplot -e "set term pngcairo transparent size 400,400" $< > $@

ifeq ($(INKSCAPE_VER),0)
%.png: %.svg
	inkscape --export-dpi 150 -e $@ $<

%.pdf: %.svg
	inkscape -A $@ $<
else
%.png: %.svg
	inkscape --export-dpi 150 --export-type png -o $@ $<

%.pdf: %.svg
	inkscape --export-type pdf -o $@ $<
endif

%.pdf: %.gpi
	gnuplot -e "set term pdfcairo size 5cm,5cm" $< > $@

%.pdf: %.mscgen
	mscgen -T eps -o - $< | ps2pdf -dEPSCrop - $@

.PHONY: help clean html preview json epub latex latexpdf text man changes linkcheck doctest gettext
