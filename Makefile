# White Repopulation build. `make check` runs everything CI runs.
SHELL := /bin/bash
PYTHON ?= python3
PANDOC ?= pandoc
export SOURCE_DATE_EPOCH ?= $(shell git log -1 --format=%ct 2>/dev/null || date +%s)
export TZ := UTC

PARTS := manuscript/01-introduction.md \
         manuscript/02-the-future-white.md \
         manuscript/03-birth-into-captivity.md \
         manuscript/04-whose-future-increase.md \
         manuscript/05-transatlantic-population-circuits.md \
         manuscript/06-conclusion.md \
         manuscript/90-appendix-a-tables.md \
         manuscript/91-appendix-b-bibliography.md
PANDOC_ARGS := --metadata-file=paper.yaml --metadata-file=manuscript/build.yaml \
               --lua-filter=manuscript/filters/paper-metadata.lua \
               --citeproc --resource-path=.:figures --standalone
OUT := build/white-repopulation

.PHONY: all data figures paper check test drift clean

all: check paper

data:
	$(PYTHON) -m analysis.reproduce

figures: data
	$(PYTHON) -m analysis.figures

paper: data
	@mkdir -p build
	$(PANDOC) $(PANDOC_ARGS) --to=html5 --embed-resources --mathml -o $(OUT).html $(PARTS)
	$(PANDOC) $(PANDOC_ARGS) --to=docx -o $(OUT).docx $(PARTS)
	$(PANDOC) $(PANDOC_ARGS) --to=jats_archiving -o $(OUT).xml $(PARTS)
	$(PANDOC) $(PANDOC_ARGS) --pdf-engine=lualatex -o $(OUT).pdf $(PARTS)
	$(PYTHON) -m analysis.build_receipt $(OUT).html $(OUT).docx $(OUT).xml $(OUT).pdf > build/build-receipt.json

test: data
	$(PYTHON) -m unittest discover -s tests -t .

# Generated files are committed; fail if regenerating them changes anything.
drift: figures
	git diff --exit-code -- data/derived figures manuscript/90-appendix-a-tables.md

check: test drift

clean:
	find build -type f -delete 2>/dev/null || true
