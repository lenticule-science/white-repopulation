# Data governance: CARE and FAIR

This repository applies the **CARE Principles for Indigenous Data Governance**
(Collective benefit, Authority to control, Responsibility, Ethics; GIDA 2019)
together with the **FAIR principles** (Findable, Accessible, Interoperable,
Reusable). The machine-readable statement is the `care` block of
[`paper.yaml`](../paper.yaml), which is projected into the release metadata.

## What data this repository holds

- **Derived historical aggregates** (`data/derived/`): decade sums of published
  demographic reconstructions. They contain no person-level data.
- **Source records** (`data/records/`): structured extractions from published
  court reports, enslaver correspondence, a Federal Writers' Project interview,
  statutes and administrative reports. They name historical persons only as
  those persons appear in already public sources.
- **No Indigenous data are collected.** Passages on Indigenous nations rely on
  published scholarship and public records.

## How CARE applies

| Principle | Practice in this repository |
|---|---|
| Collective benefit | Open release (CC-BY-4.0 text and data, MIT code) so descendant communities and their scholars can use, contest and correct the work without cost or permission. |
| Authority to control | Colonial administrative recognition is never treated as Indigenous self-determination. A named nation may ask for any passage concerning it to be corrected, contextualized or withdrawn from future versions (see below). |
| Responsibility | Every record states what its source can and cannot show (`limits`, `forbidden_inferences`, `not_valid_for`), including the bias of court and enslaver records that seldom preserve the voices of enslaved mothers and children. |
| Ethics | Persons in historical records are not reduced to counts. The paper does not add identifying detail beyond its published sources. Counts of births into slavery are never presented as counts of directed conception. |

## Requests concerning a community or person

Open an issue labeled `governance`, or write to the accountable author named
in [`CITATION.cff`](../CITATION.cff). A request from a descendant community or
an Indigenous nation is acknowledged within 14 days and decided by the
accountable author. The decision and the change are recorded in
[`CHANGELOG.md`](../CHANGELOG.md). Released versions are archived and cannot be
altered, so a correction appears in the next version together with a
correction notice.

## FAIR

- **Findable:** persistent release tags; CITATION.cff, codemeta and Zenodo
  metadata; schema.org `ScholarlyArticle` JSON-LD.
- **Accessible:** plain-text and open formats (Markdown, CSV, JSON, Turtle,
  SVG); no account needed.
- **Interoperable:** Frictionless Data Package (`datapackage.json`), CSL-YAML
  references, an OWL/SKOS vocabulary under `https://561.group/`, and W3C PROV-O
  provenance.
- **Reusable:** explicit licenses per file (REUSE.toml), reading grades per
  source, and executable reproduction of every number.
