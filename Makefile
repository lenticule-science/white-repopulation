# White Repopulation build. `make check` runs everything CI runs.
SHELL := /bin/bash
PYTHON ?= python3
PANDOC ?= pandoc
export SOURCE_DATE_EPOCH ?= $(shell git log -1 --format=%ct 2>/dev/null || date +%s)
export TZ := UTC
# xdvipdfmx takes its PDF dates from SOURCE_DATE_EPOCH only when forced.
export FORCE_SOURCE_DATE := 1

PARTS := manuscript/01-introduction.md \
         manuscript/02-the-future-white.md \
         manuscript/03-birth-into-captivity.md \
         manuscript/04-whose-future-increase.md \
         manuscript/05-transatlantic-population-circuits.md \
         manuscript/06-conclusion.md \
         manuscript/90-appendix-a-tables.md \
         manuscript/91-appendix-b-bibliography.md
PANDOC_ARGS := --from=markdown+tex_math_single_backslash --metadata-file=paper.yaml --metadata-file=manuscript/build.yaml \
               --lua-filter=manuscript/filters/paper-metadata.lua \
               --citeproc --resource-path=.:figures --standalone
OUT := build/white-repopulation

.PHONY: all data figures paper metadata metadata-check check test drift clean

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
	$(PANDOC) $(PANDOC_ARGS) --pdf-engine=xelatex -o $(OUT).pdf $(PARTS)
	$(PYTHON) -m analysis.build_receipt $(OUT).html $(OUT).docx $(OUT).xml $(OUT).pdf > build/build-receipt.json

test: data
	$(PYTHON) -m unittest discover -s tests -t .

# Generated files are committed; fail if regenerating them changes anything.
drift: figures
	git diff --exit-code -- data/derived figures manuscript/90-appendix-a-tables.md

# Release metadata and references come from our research-publication services.
RELEASE_METADATA ?= npx --yes --package=github:red-cup-engineering/research-release-metadata-service\#872717faddfa4734bbf2ec0952af4a35882f428f
PAPER_REQUEST = python3 -c "import json;print(json.dumps({'paperYaml':open('paper.yaml').read()}))"
define project
	$(PAPER_REQUEST) | $(RELEASE_METADATA) $(1) | python3 -c "import json,sys;d=json.loads(sys.stdin.readline());assert 'refusal' not in d,d;open('$(2)','w').write(d.get('text') or json.dumps(d['value'],indent=2,ensure_ascii=False)+'\\n')"
endef

metadata:
	@mkdir -p metadata
	$(call project,project-citation-cff,CITATION.cff)
	$(call project,project-zenodo-metadata,.zenodo.json)
	$(call project,project-codemeta,codemeta.json)
	$(call project,project-scholarly-article-json-ld,metadata/scholarly-article.jsonld)

metadata-check: metadata
	git diff --exit-code -- CITATION.cff .zenodo.json codemeta.json metadata/

check: test drift

clean:
	find build -type f -delete 2>/dev/null || true
