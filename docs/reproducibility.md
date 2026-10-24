# Reproducing the paper

This repository holds knowledge and data. Every computation is done by a FOSS
Red Cup Engineering service, pinned by commit (`package.json`, and the
conformance service in `.github/workflows/build.yml`), so the paper and its
tooling are versioned separately and each tool can be reused for other papers.

    npm install
    pip install "git+https://github.com/red-cup-engineering/rdf-vocabulary-conformance-service@9dc0e77e9b165d61969b2146e78bdac0f74ac749"
    make check                 # claims, figures, metadata, ontology, records
    make paper provenance      # the paper in four formats, its receipt, PROV-O

## Numbers

`claims/claims.json` restates each of the paper's 26 quantitative claims as an
expression over JSON Pointers into `data/records/` (exact decimal arithmetic,
half-even rounding). `research-claim-reproduction-service` evaluates them and
fails on any disagreement; `claims/tables.json` defines the derived CSVs and
Appendix A. `data/derived/claims.json` lists every claim, the stated value, the
derived value and its basis.

## Figures

`figures/*.vl.json` are Vega-Lite specifications over `data/`;
`chart-specification-rendering-service` renders them to SVG with fixed text
metrics, so the bytes do not depend on installed fonts.

## Manuscript

`manuscript/manuscript.json` is the render request for
`project-document-through-pandoc-service`: parts, metadata, bibliography,
style, formats, filters and the required pandoc version (3.1.3). The renderer
writes `build/receipt.json` with the toolchain, every argument vector and the
`ni:` address of every input and output. HTML, DOCX and JATS are
byte-reproducible under `SOURCE_DATE_EPOCH`; the XeLaTeX PDF is reproducible on
the pinned toolchain (fixed trailer /ID), and each release lists its digest.

## Provenance

`make provenance` composes the renderer's receipt with `provenance/agents.json`
(`compose-provenance-manifest`) and projects it as W3C PROV-O
(`project-provenance-as-prov-o`): `build/prov.nt` (RDFC-1.0 canonical) and
`build/prov.jsonld`.

## Provenance of the v0.1.0 bundle

The unreleased v0.1.0 candidate bundle recorded SHA-256 digests for its CSV
tables. Those digests were computed over CRLF line endings. `claims/tables.json` declares a CRLF digest check for both tables, so
`make check` reproduces those exact digests.
