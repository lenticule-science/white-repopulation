# References

`references.yaml` is the paper's consolidated bibliography in CSL-YAML
(Pandoc's `references:` form). It is **generated**, not hand-edited: a
projection of the Sociology Science bibliography records this research
consulted.

| Input | Value |
|---|---|
| Corpus | `lenticule-science/science-services-section`, `services/social-science-services-section/services/sociology-science-services-section/content/text/documents/articles/bibliographies/` |
| Corpus revision | `c34995483f7d971554913c9d8f6a00f1a4348f57` |
| Records | the 60 records referencing this research; 58 projected |
| Record migration | `@red-cup-engineering/bibliography-engineering-services-section` 0.6.0 `migrate-reference-records-to-bibliography-records`, with `reference-types.json` |
| Projection | `@red-cup-engineering/csl-yaml-services-section` 0.1.0 `project-bibliography-records-as-csl-yaml` (byte-deterministic; round-trips through `decode-csl-yaml` with 0 warnings) |
| Style | `chicago-author-date.csl` from citation-style-language/styles at the commit in `chicago-author-date.csl.source-commit` |

Two records are not yet projected because their filenames are not
citekeys: `nps-racial-integrity` and `virginia-domestic-slave-trade`. They
are renamed in the corpus first, then included.

Each source's reading grade (how much of it was read) is in
`research/evidence-crosswalk.md`, not in the CSL data.
