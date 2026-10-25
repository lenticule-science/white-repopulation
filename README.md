# White Repopulation: Reproduction without Preservation

*The future white, captive births, and the transatlantic reproduction of settler rule*

[![Build](https://github.com/lenticule-science/white-repopulation/actions/workflows/build.yml/badge.svg)](https://github.com/lenticule-science/white-repopulation/actions/workflows/build.yml)
[![Text: CC BY 4.0](https://img.shields.io/badge/text-CC%20BY%204.0-2a78d6)](LICENSES/CC-BY-4.0.txt)
[![Code: MIT](https://img.shields.io/badge/code-MIT-2a78d6)](LICENSES/MIT.txt)
[![REUSE](https://img.shields.io/badge/REUSE-compliant-2a78d6)](REUSE.toml)
[![Indigenous data: CARE](https://img.shields.io/badge/Indigenous%20data-CARE-4b6f44)](docs/data-governance.md)
[![Status: preprint, not peer reviewed](https://img.shields.io/badge/status-preprint%2C%20not%20peer%20reviewed-52514e)](docs/review-status.md)

**Morgan Sennhauser** (Lenticule Science) and **Codex 6.1** (disclosed AI research collaborator). Research direction: an anonymous contributor. [AI disclosure](docs/ai-disclosure.md).

## Abstract

Settler institutions in the United States have described their future as the increase of a white population. That description joins four histories that move independently: the births and survival of people counted as white; the changing rules for who counts; eligibility to found a preferred future population; and the reproduction of property, jurisdiction and labor relations. This study separates them and asks which one institutions preserved when they conflicted.

Across four kinds of evidence, the institutions examined preserved the authority to classify people and to appropriate reproduction more reliably than the reproductive opportunities of every person they classified as white. The stronger proposition, that a deferred ideal can exhaust the population it claims to protect, remains a conditional hypothesis. The paper states the evidence that would test it.

## Findings and their evidence status

| Finding | Part | Status |
|---|---|---|
| Virginia's 1924 purity law carried an ancestry exception protecting favored genealogies. In 1926 the House approved widening it and the Senate postponed it indefinitely; distinct rules were enacted in 1930. | I | Observed |
| 5,167,522 of 30,038,000 U.S. births in 1800–1849 (**17.20%**) were births into hereditary slavery; 16.82% in 1790–1859 with an assumed 1790s denominator. | II | Observed (modeled series) |
| Antebellum law separated a child's status at birth, title to the child, claims on unconceived issue, and manumission. Outcomes varied, including a successful freedom claim. | III | Observed (7 documents, 21 observations; not a sample) |
| Net migration was 11.9% of national growth in 1790–1800 and 32.3% in 1850–1860. Most nineteenth-century growth was natural increase. | IV | Observed (national, not white-specific) |
| Settler institutions preserved classification authority and appropriated reproduction over the reproductive chances of all white-classified people. | All | Mechanistically plausible |
| A deferred ideal exhausts the actual white-classified population. | — | **Not established** |

None of the figures estimates directed conception or the share of all births on Indigenous lands.

## Read

Each [release](https://github.com/lenticule-science/white-repopulation/releases) attaches the paper as PDF, HTML, DOCX and JATS XML, with a build receipt and SHA-256 digests. The source is in [`manuscript/`](manuscript/).

## Reproduce

This repository holds the paper's knowledge and data only. Every step runs a FOSS
service from Red Cup Engineering, pinned by commit in `package.json` (Node) or
installed from its repository (Python):

| Step | Data here | Service |
|---|---|---|
| Recompute all 26 stated numbers, tables, Appendix A | `claims/` | `research-claim-reproduction-service` |
| Figures | `figures/*.vl.json` (Vega-Lite) | `chart-specification-rendering-service` |
| Paper in PDF, HTML, DOCX, JATS | `manuscript/manuscript.json`, `paper.yaml` | `project-document-through-pandoc-service` |
| Citation and archive metadata | `paper.yaml` | `research-release-metadata-service` |
| Bibliography | Sociology Science records | `bibliography-engineering-services-section`, `csl-yaml-services-section` |
| Ontology and record validation | `ontology/conformance.json` | `rdf-vocabulary-conformance-service` |
| W3C PROV-O provenance | `provenance/agents.json` + the build receipt | `prov-o-provenance-service` |

```sh
npm install                       # the Engineering services (devDependencies)
pip install "git+https://github.com/red-cup-engineering/rdf-vocabulary-conformance-service"
make check                        # every number, figure, metadata file and record
make paper provenance             # build/white-repopulation.{pdf,html,docx,xml}, build/prov.nt
```

See [docs/reproducibility.md](docs/reproducibility.md).

## Repository

| Path | Contents |
|---|---|
| `manuscript/` | Introduction, Parts I–IV, conclusion, appendices (Pandoc Markdown) |
| `references/` | CSL-YAML bibliography projected from the Sociology Science corpus; pinned CSL style |
| `data/records/` | Source records with reading grades and stated limits |
| `data/derived/` | Tables and `claims.json` generated from `claims/` by `research-claim-reproduction-service` |
| `datapackage.json` | Frictionless Data Package describing every table and record |
| `claims/` | Every quantitative claim and derived table, stated as data |
| `figures/` | Vega-Lite specifications and their byte-reproducible SVG renders |
| `ontology/` | OWL ontology, SKOS concept scheme, SHACL shapes and conformance tests under `https://561.group/knowledge/white-repopulation` |
| `provenance/` | The agents this paper declares; each build composes them with the renderer's receipt into W3C PROV-O |
| `research/` | Research dossier, source-criticism notes, evidence crosswalk, per-part process records |
| `archive/` | Unreleased v0.1.0 candidate record and the two 2026-10-17 working-paper PDFs |
| `paper.yaml` | The one metadata source; CITATION.cff, .zenodo.json, codemeta.json and JSON-LD are generated from it |

## Cite

Use the **Cite this repository** button (from [`CITATION.cff`](CITATION.cff)). The v0.2.0 release is archived by Software Heritage as [`swh:1:rel:38fe7c944eb716249e88dbf8511acdd1ade7e809`](https://archive.softwareheritage.org/swh:1:rel:38fe7c944eb716249e88dbf8511acdd1ade7e809), a persistent identifier that resolves to the exact tagged source. No DOI is assigned.

## Licenses and governance

Text, figures and data are CC-BY-4.0; code is MIT; see [`REUSE.toml`](REUSE.toml). Quoted historical documents keep their own rights. Data governance follows the CARE and FAIR principles ([docs/data-governance.md](docs/data-governance.md)). Corrections and counterevidence are welcome ([CONTRIBUTING.md](CONTRIBUTING.md)).

## Home

This repository belongs to [Lenticule Science](https://github.com/lenticule-science/science-services-section) › Social Science › [Sociology Science](https://github.com/lenticule-science/sociology-science-services-section). Sociology Science mounts it at `publications/white-repopulation` and holds the bibliography and glossary corpus this paper projects.
