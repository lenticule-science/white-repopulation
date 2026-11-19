# White Repopulation build parameters. This repository holds knowledge and
# data; every step runs a Red Cup Engineering service named in package.json
# (Node) or installed from its repository (Python). `make check` runs what CI runs.
SHELL := /bin/bash
.SHELLFLAGS := -eo pipefail -c
export SOURCE_DATE_EPOCH ?= $(shell git log -1 --format=%ct 2>/dev/null || date +%s)
export TZ := UTC

NPX         ?= npx --no-install
CLAIMS      ?= $(NPX) reproduce-paper-claims
CHARTS      ?= $(NPX) render-chart-specifications
RENDER      ?= $(NPX) render-manuscript
COMPOSE     ?= $(NPX) compose-provenance-manifest
PROV        ?= $(NPX) project-provenance-as-prov-o
METADATA    ?= $(NPX)
CONFORMANCE ?= check-vocabulary-conformance

FIGURES := $(wildcard figures/*.vl.json)
PAPER_REQUEST := jq -Rsc '{paperYaml: .}' paper.yaml

.PHONY: all data figures paper provenance metadata check check-claims check-figures check-metadata check-ontology clean

all: check paper provenance

data:
	$(CLAIMS) --root . --spec claims/claims.json

figures:
	$(CHARTS) --root . $(FIGURES)

paper: data figures
	@mkdir -p build
	$(RENDER) --request manuscript/manuscript.json --receipt build/receipt.json --source-date-epoch $(SOURCE_DATE_EPOCH)

# PROV-O: the renderer's receipt composed with the people this paper declares.
provenance: build/receipt.json
	jq -c -n --slurpfile receipt build/receipt.json --slurpfile people provenance/agents.json \
	  '{fragments: [$$receipt[0].provenance, $$people[0]], baseIri: "https://561.group/knowledge/white-repopulation/build/"}' \
	  | $(COMPOSE) | jq -c '.manifest' | $(PROV) > build/prov.json
	jq -r '.turtle' build/prov.json > build/prov.nt
	jq '.jsonLd' build/prov.json > build/prov.jsonld

# Release metadata generated from paper.yaml by research-release-metadata-service.
metadata:
	@mkdir -p metadata
	$(PAPER_REQUEST) | $(METADATA) project-citation-cff | jq -j '.text' > CITATION.cff
	$(PAPER_REQUEST) | $(METADATA) project-zenodo-metadata | jq -j '.text' > .zenodo.json
	$(PAPER_REQUEST) | $(METADATA) project-codemeta | jq -j '.text' > codemeta.json
	$(PAPER_REQUEST) | $(METADATA) project-scholarly-article-json-ld | jq -j '.text' > metadata/scholarly-article.jsonld

check: check-claims check-figures check-metadata check-ontology

check-claims:
	$(CLAIMS) --root . --spec claims/claims.json --check

check-figures:
	$(CHARTS) --root . --check $(FIGURES)

check-metadata: metadata
	git diff --exit-code -- CITATION.cff .zenodo.json codemeta.json metadata/

check-ontology:
	$(CONFORMANCE) --root . --config ontology/conformance.json

clean:
	find build -type f -delete 2>/dev/null || true
