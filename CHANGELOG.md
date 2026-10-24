# Changelog

This project follows [Semantic Versioning](https://semver.org/) for research
releases: a patch is an erratum, a minor version is new evidence or analysis,
and a major version changes a conclusion.

## [0.2.0] - unreleased

The first standalone, reproducible edition.

- Integrated the four part manuscripts into one paper with a new introduction
  and conclusion, built from source by CI into PDF, HTML, DOCX and JATS.
- The repository holds knowledge and data only (house rule
  science-engineering-operations-parameterize-in-order). Every computation is a
  pinned Red Cup Engineering service: claims and tables
  (`research-claim-reproduction-service`), Vega-Lite figures
  (`chart-specification-rendering-service`), rendering with shipped filters
  (`project-document-through-pandoc-service`), release metadata, CSL-YAML,
  ontology and record conformance, and PROV-O composition.
- Added reproduction of all 26 quantitative claims stated as data, byte-reproducible
  figures, a Frictionless Data Package, CSL-YAML references projected from the
  Sociology Science bibliography, an OWL/SKOS vocabulary, W3C PROV-O build
  provenance, REUSE licensing and a CARE data-governance statement.
- Release metadata (CITATION.cff, .zenodo.json, codemeta.json, schema.org
  JSON-LD, publication.json) is now generated from `paper.yaml` and checked in CI.
- Moved the research dossier, source records and working-paper PDFs out of
  Sociology Science into this repository, with full history. Sociology Science
  mounts this repository as a submodule at `publications/white-repopulation`.
- Resolved the v0.1.0 manifest's CSV size discrepancy: its digests were
  computed over CRLF line endings, and the tests now reproduce them.

## [0.1.0] - 2026-10-17 (release candidate, never published)

Prepared reading edition, credits and qualifications, quantitative tables and
deposit preparation. Preserved unchanged in `archive/v0.1.0-release-candidate/`.
